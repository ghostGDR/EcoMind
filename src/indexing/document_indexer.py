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
        """
        Initialize indexer with storage components.
        
        Args:
            document_store: DocumentStore for loading documents
            vector_store: HenryVectorStore for vector indexing
        """
        self.document_store = document_store
        self.vector_store = vector_store
        self._document_count = 0
    
    def index_all_documents(self, clear_existing: bool = False) -> Optional[VectorStoreIndex]:
        """
        Load documents from store and create vector index.
        
        Args:
            clear_existing: If True, clear the existing index before adding new documents.
        
        Returns:
            VectorStoreIndex object or None if no documents found
            
        Raises:
            Exception: If document loading or indexing fails
        """
        try:
            if clear_existing:
                print("Clearing existing collection...")
                self.vector_store.clear_collection()

            # Load all documents from DocumentStore
            documents = self.document_store.load_all_documents()
            
            if not documents:
                raise ValueError("No documents found in document store")
            
            self._document_count = len(documents)
            print(f"Loaded {self._document_count} documents from store")
            
            # Enrich metadata with file type
            for doc in documents:
                if 'extension' in doc.metadata:
                    doc.metadata['file_type'] = 'markdown' if doc.metadata['extension'] == '.md' else 'excel'
            
            # Create vector index via HenryVectorStore
            index = self.vector_store.create_index(documents)
            
            print(f"Successfully indexed {self._document_count} documents")
            return index
            
        except Exception as e:
            raise Exception(f"Failed to index documents: {str(e)}") from e
    
    def get_index_stats(self) -> dict:
        """
        Get indexing statistics.
        
        Returns:
            Dictionary with total_documents, points_count, and collection_status
        """
        collection_info = self.vector_store.get_collection_info()
        
        return {
            'total_documents': self._document_count,
            'points_count': collection_info['points_count'],
            'collection_status': collection_info['status']
        }
