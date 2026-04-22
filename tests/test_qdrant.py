import pytest
import tempfile
import shutil
from pathlib import Path
from src.storage.vector_store import HenryVectorStore
from llama_index.core import Document

@pytest.fixture
def temp_db_path():
    """Create temporary database directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_vector_store_initialization(temp_db_path):
    """Test Qdrant client initializes with persistent path"""
    store = HenryVectorStore(db_path=temp_db_path)
    assert store.client is not None
    assert store.vector_store is not None
    assert Path(temp_db_path).exists()

def test_collection_creation_and_indexing(temp_db_path):
    """Test collection creation with 384-dimensional vectors"""
    store = HenryVectorStore(db_path=temp_db_path)
    
    # Create test documents
    documents = [
        Document(text="TikTok 广告投放最佳时间是晚上 8-10 点"),
        Document(text="跨境电商需要注意收款风控问题"),
    ]
    
    # Create index (this creates collection and uploads vectors)
    index = store.create_index(documents)
    assert index is not None
    
    # Verify collection exists
    info = store.get_collection_info()
    assert info["points_count"] > 0
    assert info["status"] == "green"

def test_vector_query(temp_db_path):
    """Test vector query returns similar results"""
    store = HenryVectorStore(db_path=temp_db_path)
    
    documents = [
        Document(text="TikTok 广告投放策略"),
        Document(text="Facebook 广告优化技巧"),
        Document(text="财务报表分析方法"),
    ]
    
    index = store.create_index(documents)
    
    # Query for advertising-related content
    query_engine = index.as_query_engine()
    response = query_engine.query("如何优化广告投放？")
    
    assert response is not None
    assert len(response.source_nodes) > 0

def test_data_persistence(temp_db_path):
    """Test data persists after client restart"""
    # First session: create and populate
    store1 = HenryVectorStore(db_path=temp_db_path)
    documents = [Document(text="Test persistence")]
    store1.create_index(documents)
    info1 = store1.get_collection_info()
    
    # Second session: reconnect and verify
    store2 = HenryVectorStore(db_path=temp_db_path)
    info2 = store2.get_collection_info()
    
    assert info2["points_count"] == info1["points_count"]
    assert info2["points_count"] > 0
