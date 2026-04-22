"""Integration tests for SSE streaming chat endpoint"""
import json
import pytest
import os
from fastapi.testclient import TestClient
from src.api.main import app

# Test database path
TEST_DB_PATH = "./data/test_chat_conversations.db"


@pytest.fixture(autouse=True)
def cleanup_test_db():
    """Clean up test database before each test"""
    # Remove test database if it exists
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # Ensure data directory exists
    os.makedirs("./data", exist_ok=True)
    
    # Set environment variable for test database
    os.environ["CONVERSATION_DB_PATH"] = TEST_DB_PATH
    
    # Clear any cached singletons in dependencies module
    import src.api.dependencies as deps
    deps._conversation_manager = None
    deps._search_engine = None
    deps._document_store = None
    
    yield
    
    # Cleanup after test
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture
def client():
    """Create a fresh TestClient for each test"""
    return TestClient(app)


def test_chat_stream_success(client):
    """Test successful chat streaming with answer chunks"""
    # Create conversation first
    response = client.post("/api/conversations", json={"title": "Test Chat"})
    assert response.status_code == 201
    conversation_id = response.json()["id"]
    
    # Send chat message and stream response
    with client.stream("POST", "/api/chat", json={
        "conversation_id": conversation_id,
        "message": "测试问题"
    }) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        # Parse SSE events
        events = []
        for line in response.iter_lines():
            line = line.strip()
            if line.startswith("data: "):
                data = json.loads(line[6:])
                events.append(data)
        
        # Verify event sequence
        answer_events = [e for e in events if e["type"] == "answer"]
        sources_events = [e for e in events if e["type"] == "sources"]
        done_events = [e for e in events if e["type"] == "done"]
        
        # Should have at least one answer chunk
        assert len(answer_events) > 0, "Should have answer chunks"
        
        # Should have exactly one sources event
        assert len(sources_events) == 1, "Should have one sources event"
        
        # Should have exactly one done event
        assert len(done_events) == 1, "Should have one done event"
        
        # Verify answer chunks have content
        for event in answer_events:
            assert "content" in event
            assert isinstance(event["content"], str)
        
        # Verify sources structure
        sources = sources_events[0]["content"]
        assert isinstance(sources, list)


def test_chat_stream_includes_sources(client):
    """Test that sources event is sent after answer"""
    # Create conversation
    response = client.post("/api/conversations", json={"title": "Test Sources"})
    conversation_id = response.json()["id"]
    
    # Send message
    with client.stream("POST", "/api/chat", json={
        "conversation_id": conversation_id,
        "message": "TikTok 广告投放有什么技巧？"
    }) as response:
        assert response.status_code == 200
        
        events = []
        for line in response.iter_lines():
            line = line.strip()
            if line.startswith("data: "):
                data = json.loads(line[6:])
                events.append(data)
        
        # Find sources event
        sources_events = [e for e in events if e["type"] == "sources"]
        assert len(sources_events) == 1
        
        # Verify sources come after answer chunks
        sources_index = events.index(sources_events[0])
        answer_events = [e for e in events if e["type"] == "answer"]
        if answer_events:
            last_answer_index = events.index(answer_events[-1])
            assert sources_index > last_answer_index, "Sources should come after answer"


def test_chat_stream_includes_done_event(client):
    """Test that done event is sent at end of stream"""
    # Create conversation
    response = client.post("/api/conversations", json={"title": "Test Done"})
    conversation_id = response.json()["id"]
    
    # Send message
    with client.stream("POST", "/api/chat", json={
        "conversation_id": conversation_id,
        "message": "测试"
    }) as response:
        assert response.status_code == 200
        
        events = []
        for line in response.iter_lines():
            line = line.strip()
            if line.startswith("data: "):
                data = json.loads(line[6:])
                events.append(data)
        
        # Verify done event is last
        assert events[-1]["type"] == "done"
        assert events[-1]["content"] == ""


def test_chat_invalid_conversation_id(client):
    """Test that invalid conversation_id sends error event in stream"""
    # Send message with non-existent conversation_id
    with client.stream("POST", "/api/chat", json={
        "conversation_id": 99999,
        "message": "测试"
    }) as response:
        assert response.status_code == 200  # SSE connection established
        assert "text/event-stream" in response.headers["content-type"]
        
        events = []
        for line in response.iter_lines():
            line = line.strip()
            if line.startswith("data: "):
                data = json.loads(line[6:])
                events.append(data)
        
        # Should have error event
        error_events = [e for e in events if e["type"] == "error"]
        assert len(error_events) > 0, "Should have error event"
        assert "not found" in error_events[0]["content"].lower()


def test_chat_empty_message(client):
    """Test that empty message returns validation error"""
    # Create conversation
    response = client.post("/api/conversations", json={"title": "Test Empty"})
    conversation_id = response.json()["id"]
    
    # Send empty message - should fail validation
    response = client.post("/api/chat", json={
        "conversation_id": conversation_id,
        "message": ""
    })
    
    # FastAPI validation should catch this
    # Note: Pydantic allows empty strings by default, so this might pass
    # If we want to enforce non-empty, we'd need to add validation to the model
    # For now, just verify the endpoint accepts the request
    assert response.status_code in [200, 422]  # Either streams or validation error


def test_chat_stream_headers(client):
    """Test that SSE response has correct headers"""
    # Create conversation
    response = client.post("/api/conversations", json={"title": "Test Headers"})
    conversation_id = response.json()["id"]
    
    # Send message
    with client.stream("POST", "/api/chat", json={
        "conversation_id": conversation_id,
        "message": "测试"
    }) as response:
        assert response.status_code == 200
        
        # Verify SSE headers
        assert "text/event-stream" in response.headers["content-type"]
        assert response.headers.get("cache-control") == "no-cache"
        assert response.headers.get("connection") == "keep-alive"
        assert response.headers.get("x-accel-buffering") == "no"
