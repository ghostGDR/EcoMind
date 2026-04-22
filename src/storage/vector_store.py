import qdrant_client
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pathlib import Path
from typing import List, Optional

class EcoMindVectorStore:
    """Wrapper for Qdrant vector database operations"""
    
    def __init__(self, db_path: str = "./data/qdrant_db"):
        """Initialize Qdrant client in persistent mode"""
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Configure local embedding model (384-dimensional vectors)
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        # Initialize Qdrant client (persistent mode)
        self.client = qdrant_client.QdrantClient(path=str(self.db_path))
        
        # Create vector store wrapper with explicit parameters to avoid pydantic issue
        self.vector_store = QdrantVectorStore(
            collection_name="ecomind_knowledge_base",
            client=self.client,
            enable_hybrid=False,
            batch_size=64
        )
        
        # Configure chunk size for Chinese text
        Settings.chunk_size = 512
        Settings.chunk_overlap = 50
        
        # Ensure full-text index exists for BM25-like search
        try:
            from qdrant_client.http import models as rest_models
            self.client.create_payload_index(
                collection_name="ecomind_knowledge_base",
                field_name="text",
                field_schema=rest_models.TextIndexParams(
                    type="text",
                    tokenizer=rest_models.TokenizerType.MULTILINGUAL,
                    lowercase=True,
                    cleansed=True,
                    index_params=rest_models.TextIndexParamsDiff(
                        on_disk=True
                    )
                )
            )
        except Exception:
            pass # Index might already exist or collection not created yet
    
    def close(self):
        """Close the Qdrant client to release file locks"""
        if hasattr(self, 'client') and self.client:
            self.client.close()
    
    def get_storage_context(self) -> StorageContext:
        """Get storage context for LlamaIndex"""
        return StorageContext.from_defaults(vector_store=self.vector_store)
        
    def clear_collection(self):
        """Delete the collection to clear all data"""
        from llama_index.vector_stores.qdrant import QdrantVectorStore
        try:
            self.client.delete_collection(collection_name="ecomind_knowledge_base")
        except Exception:
            pass
            
        # Recreate the vector store so it will initialize a new collection
        self.vector_store = QdrantVectorStore(
            collection_name="ecomind_knowledge_base",
            client=self.client,
            enable_hybrid=False,
            batch_size=64
        )
    
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
            info = self.client.get_collection("ecomind_knowledge_base")
            return {
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception:
            return {"points_count": 0, "status": "not_created"}
