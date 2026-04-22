import pytest
import tempfile
import os
from pathlib import Path
from src.storage.document_store import DocumentStore

@pytest.fixture
def temp_wiki_dir():
    """Create temporary wiki directory with test files"""
    temp_dir = tempfile.mkdtemp()
    wiki_path = Path(temp_dir) / "wiki"
    wiki_path.mkdir()
    
    # Create test markdown files
    (wiki_path / "test1.md").write_text("# Test Document 1\n\nContent here.")
    (wiki_path / "test2.md").write_text("# Test Document 2\n\nMore content.")
    
    # Create subdirectory with file
    subdir = wiki_path / "subdirectory"
    subdir.mkdir()
    (subdir / "test3.md").write_text("# Test Document 3\n\nSubdir content.")
    
    yield wiki_path
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)

def test_document_store_initialization(temp_wiki_dir):
    """Test DocumentStore initializes with wiki path"""
    store = DocumentStore(base_path=str(temp_wiki_dir))
    assert store.base_path == temp_wiki_dir
    assert store.base_path.exists()

def test_initialization_with_missing_directory():
    """Test handles missing directory gracefully with clear error"""
    with pytest.raises(FileNotFoundError) as exc_info:
        DocumentStore(base_path="/nonexistent/path")
    
    assert "Wiki directory not found" in str(exc_info.value)

def test_load_all_documents(temp_wiki_dir):
    """Test load_all_documents returns Document objects"""
    store = DocumentStore(base_path=str(temp_wiki_dir))
    documents = store.load_all_documents()
    
    assert len(documents) == 3
    assert all(hasattr(doc, 'text') for doc in documents)
    assert all(hasattr(doc, 'metadata') for doc in documents)

def test_list_documents(temp_wiki_dir):
    """Test list_documents returns file paths for .md files"""
    store = DocumentStore(base_path=str(temp_wiki_dir))
    files = store.list_documents()
    
    assert len(files) == 3
    assert all(isinstance(f, Path) for f in files)
    assert all(f.suffix == ".md" for f in files)
    
    # Check files are sorted
    file_names = [f.name for f in files]
    assert file_names == sorted(file_names)

def test_get_document_metadata(temp_wiki_dir):
    """Test get_document_metadata extracts file info"""
    store = DocumentStore(base_path=str(temp_wiki_dir))
    test_file = temp_wiki_dir / "test1.md"
    
    metadata = store.get_document_metadata(test_file)
    
    assert metadata["name"] == "test1.md"
    assert metadata["extension"] == ".md"
    assert metadata["size_bytes"] > 0
    assert "modified_timestamp" in metadata
    assert "relative_path" in metadata

def test_get_document_count(temp_wiki_dir):
    """Test get_document_count returns correct counts"""
    store = DocumentStore(base_path=str(temp_wiki_dir))
    counts = store.get_document_count()
    
    assert counts["markdown"] == 3
    assert counts["excel"] == 0
    assert counts["total"] == 3

def test_from_env(temp_wiki_dir, monkeypatch):
    """Test from_env creates store from environment variable"""
    monkeypatch.setenv("WIKI_PATH", str(temp_wiki_dir))
    
    store = DocumentStore.from_env()
    assert store.base_path == temp_wiki_dir

def test_recursive_directory_loading(temp_wiki_dir):
    """Test loads files from subdirectories"""
    store = DocumentStore(base_path=str(temp_wiki_dir))
    files = store.list_documents()
    
    # Should include file from subdirectory
    subdir_files = [f for f in files if "subdirectory" in str(f)]
    assert len(subdir_files) == 1
    assert subdir_files[0].name == "test3.md"
