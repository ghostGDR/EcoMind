import sys
from src.storage.vector_store import HenryVectorStore

vector_store = HenryVectorStore()
info = vector_store.get_collection_info()
print(f"Collection points count: {info.get('points_count', 0)}")
