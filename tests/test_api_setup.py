"""Tests for FastAPI application setup"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.dependencies import get_conversation_manager


# Create test client
client = TestClient(app)


def test_app_starts_successfully():
    """Test that FastAPI app starts without errors"""
    assert app is not None
    assert app.title == "Henry API"
    assert app.version == "1.0.0"


def test_health_endpoint_returns_200():
    """Test GET /health returns 200 with correct JSON"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "henry-api"


def test_root_endpoint_returns_api_info():
    """Test GET / returns 200 with API info"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Henry API"
    assert data["docs"] == "/docs"


def test_docs_endpoint_accessible():
    """Test /docs endpoint is accessible (returns 200)"""
    response = client.get("/docs")
    
    assert response.status_code == 200
    # OpenAPI docs should return HTML
    assert "text/html" in response.headers["content-type"]


def test_dependency_injection_provides_conversation_manager():
    """Test dependency injection provides ConversationManager instance"""
    manager = get_conversation_manager()
    
    assert manager is not None
    assert hasattr(manager, 'start_conversation')
    assert hasattr(manager, 'send_message')
    assert hasattr(manager, 'list_conversations')
    
    # Verify singleton pattern - should return same instance
    manager2 = get_conversation_manager()
    assert manager is manager2


def test_error_handler_converts_value_error_to_400():
    """Test error handler converts ValueError to 400 response"""
    # Create a test endpoint that raises ValueError
    @app.get("/test-value-error")
    async def test_value_error():
        raise ValueError("Test error message")
    
    response = client.get("/test-value-error")
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Test error message"
