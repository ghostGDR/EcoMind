"""Integration tests for document management REST API endpoints"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

# Create test client
client = TestClient(app)


def test_list_documents_success():
    """Test GET /api/documents returns all documents with metadata"""
    response = client.get("/api/documents")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "documents" in data
    assert "total" in data
    assert isinstance(data["documents"], list)
    assert isinstance(data["total"], int)
    assert data["total"] > 0
    
    # Check document structure
    if data["documents"]:
        doc = data["documents"][0]
        assert "filename" in doc
        assert "file_path" in doc
        assert "topic" in doc
        assert "modified_at" in doc
        assert "size_kb" in doc
        assert isinstance(doc["size_kb"], float)


def test_list_documents_ordered_by_modified():
    """Test documents are ordered by modified_at DESC (newest first)"""
    response = client.get("/api/documents")
    
    assert response.status_code == 200
    data = response.json()
    
    documents = data["documents"]
    if len(documents) > 1:
        # Check that dates are in descending order
        for i in range(len(documents) - 1):
            current_date = documents[i]["modified_at"]
            next_date = documents[i + 1]["modified_at"]
            # Current should be >= next (newer or equal)
            assert current_date >= next_date


def test_list_documents_by_topic():
    """Test GET /api/documents/topics returns documents grouped by topic"""
    response = client.get("/api/documents/topics")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "topics" in data
    assert isinstance(data["topics"], dict)
    
    # Check that we have topics
    assert len(data["topics"]) > 0
    
    # Check each topic has a list of documents
    for topic, docs in data["topics"].items():
        assert isinstance(topic, str)
        assert isinstance(docs, list)
        
        # Check document structure
        if docs:
            doc = docs[0]
            assert "filename" in doc
            assert "file_path" in doc
            assert "topic" in doc
            assert doc["topic"] == topic  # Document topic matches group


def test_list_documents_by_topic_alphabetical():
    """Test topics are returned in alphabetical order"""
    response = client.get("/api/documents/topics")
    
    assert response.status_code == 200
    data = response.json()
    
    topics = list(data["topics"].keys())
    if len(topics) > 1:
        # Check alphabetical order
        assert topics == sorted(topics)


def test_search_documents_success():
    """Test GET /api/documents/search returns relevant results"""
    response = client.get("/api/documents/search?query=TikTok")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "results" in data
    assert "query" in data
    assert "total" in data
    assert data["query"] == "TikTok"
    assert isinstance(data["results"], list)
    assert isinstance(data["total"], int)
    
    # Check result structure if results exist
    if data["results"]:
        result = data["results"][0]
        assert "content" in result
        assert "score" in result
        assert "document_path" in result
        assert "chunk_id" in result
        assert isinstance(result["score"], float)
        assert 0.0 <= result["score"] <= 1.0


def test_search_documents_with_params():
    """Test search with custom top_k and min_score parameters"""
    response = client.get("/api/documents/search?query=AI&top_k=3&min_score=0.7")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that we respect top_k limit
    assert len(data["results"]) <= 3
    
    # Check that all results meet min_score threshold
    for result in data["results"]:
        assert result["score"] >= 0.7


def test_search_documents_empty_query():
    """Test GET /api/documents/search with empty query returns 400"""
    response = client.get("/api/documents/search?query=")
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_search_documents_no_results():
    """Test query with no matches returns empty results list"""
    # Use a very obscure query unlikely to match
    response = client.get("/api/documents/search?query=xyzabc123nonexistent&min_score=0.9")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return empty results, not an error
    assert "results" in data
    assert isinstance(data["results"], list)
    assert data["total"] == 0


def test_document_stats():
    """Test GET /api/documents/stats returns correct counts"""
    response = client.get("/api/documents/stats")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "total" in data
    assert "by_type" in data
    assert "by_topic" in data
    
    # Check by_type structure
    assert "markdown" in data["by_type"]
    assert "excel" in data["by_type"]
    assert isinstance(data["by_type"]["markdown"], int)
    assert isinstance(data["by_type"]["excel"], int)
    
    # Check by_topic structure
    assert isinstance(data["by_topic"], dict)
    
    # Verify total matches sum of types
    assert data["total"] == data["by_type"]["markdown"] + data["by_type"]["excel"]


def test_search_top_k_validation():
    """Test that top_k > 50 returns 422 (T-06-15 mitigation)"""
    response = client.get("/api/documents/search?query=test&top_k=100")
    
    # FastAPI returns 422 for parameter validation errors
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
