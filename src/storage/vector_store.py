import qdrant_client
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pathlib import Path
from typing import List, Optional

class HenryVectorStore:
    """Wrapper for Qdrant vector database operations"""
    
    def __init__(self, db_path: str = "./data/qdrant_db"):
        """Initialize Qdrant client in persistent mode"""
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Configure local embedding model (384-dimensional vectors)
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Initialize Qdrant client (persistent mode)
        self.client = qdrant_client.QdrantClient(path=str(self.db_path))
        
        # Create vector store wrapper with explicit parameters to avoid pydantic issue
        self.vector_store = QdrantVectorStore(
            collection_name="henry_knowledge_base",
            client=self.client,
            enable_hybrid=False,
            batch_size=64
        )
        
        # Configure chunk size for Chinese text
        Settings.chunk_size = 512
    
    def close(self):
        """Close the Qdrant client to release file locks"""
        if hasattr(self, 'client') and self.client:
            self.client.close()
    
    def get_storage_context(self) -> StorageContext:
        """Get storage context for LlamaIndex"""
        return StorageContext.from_defaults(vector_store=self.vector_store)
    
    def create_index(self, documents: List) -> VectorStoreIndex:
        """Create vector index from documents"""
        storage_context = self.get_storage_context()
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
        )
        return index
    
    def get_collection_info(self) -> dict:
        """Get collection metadata"""
        try:
            info = self.client.get_collection("henry_knowledge_base")
            return {
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception:
            return {"points_count": 0, "status": "not_created"}
