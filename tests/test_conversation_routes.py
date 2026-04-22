"""Integration tests for conversation management REST API endpoints"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
import os

# Use default database for testing (simpler than test isolation)
# Tests will create real conversations but that's acceptable for integration testing


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_create_conversation_success(client):
    """Test creating a new conversation with default title"""
    response = client.post(
        "/api/conversations",
        json={"title": "新对话"}
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert "id" in data
    assert data["title"] == "新对话"
    assert "created_at" in data
    assert isinstance(data["id"], int)


def test_create_conversation_with_custom_title(client):
    """Test creating a conversation with custom title"""
    custom_title = "TikTok 广告投放策略"
    
    response = client.post(
        "/api/conversations",
        json={"title": custom_title}
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["title"] == custom_title
    assert "id" in data
    assert "created_at" in data


def test_list_conversations(client):
    """Test listing conversations returns proper structure"""
    response = client.get("/api/conversations")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "conversations" in data
    assert "total" in data
    assert isinstance(data["conversations"], list)
    assert isinstance(data["total"], int)
    
    # Verify each conversation has required fields
    for conv in data["conversations"]:
        assert "id" in conv
        assert "title" in conv
        assert "created_at" in conv
        assert "message_count" in conv


def test_get_conversation_success(client):
    """Test retrieving a specific conversation by ID"""
    # Create a conversation
    create_response = client.post(
        "/api/conversations",
        json={"title": "测试对话"}
    )
    assert create_response.status_code == 201
    conversation_id = create_response.json()["id"]
    
    # Get the conversation
    response = client.get(f"/api/conversations/{conversation_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == conversation_id
    assert data["title"] == "测试对话"
    assert "created_at" in data
    assert "messages" in data
    assert isinstance(data["messages"], list)
    assert len(data["messages"]) == 0  # No messages yet


def test_get_conversation_not_found(client):
    """Test retrieving a non-existent conversation returns 404"""
    response = client.get("/api/conversations/99999")
    
    assert response.status_code == 404
    data = response.json()
    
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_conversation_response_structure(client):
    """Test that conversation response includes messages array"""
    # Create a conversation
    create_response = client.post(
        "/api/conversations",
        json={"title": "结构测试"}
    )
    assert create_response.status_code == 201
    conversation_id = create_response.json()["id"]
    
    # Get the conversation
    response = client.get(f"/api/conversations/{conversation_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == conversation_id
    assert data["title"] == "结构测试"
    assert "created_at" in data
    assert "messages" in data
    assert isinstance(data["messages"], list)
    # New conversation has no messages
    assert len(data["messages"]) == 0
