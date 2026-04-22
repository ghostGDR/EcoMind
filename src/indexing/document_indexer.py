"""
Document indexing pipeline for Henry knowledge base.

Orchestrates loading documents from DocumentStore and indexing them
into HenryVectorStore for semantic search.
"""

from typing import List, Optional
from llama_index.core import VectorStoreIndex, Document
from src.storage.document_store import DocumentStore
from src.storage.vector_store import HenryVectorStore


class DocumentIndexer:
    """Orchestrates document ingestion pipeline."""
    
    def __init__(self, document_store: DocumentStore, vector_store: HenryVectorStore):
        """Initialize indexer with storage components."""
        pass
    
    def index_all_documents(self) -> Optional[VectorStoreIndex]:
        """Load documents from store and create vector index."""
        pass
    
    def get_index_stats(self) -> dict:
        """Get indexing statistics."""
        pass
