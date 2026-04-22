import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.search.search_engine import SearchEngine
from src.storage.vector_store import EcoMindVectorStore

def test_search():
    try:
        vector_store = EcoMindVectorStore()
        search_engine = SearchEngine(vector_store=vector_store)
        
        query = "仿牌能不能做"
        print(f"\nTesting query: {query}")
        
        # Test semantic search directly with lower threshold
        print("\n--- Semantic Search (threshold 0.3) ---")
        sem_results = search_engine.semantic_search(query, top_k=5, min_score=0.3)
        for r in sem_results:
            print(f"Score: {r['score']:.4f} | Content: {r['content'][:100]}...")
            
        # Test hybrid search
        print("\n--- Hybrid Search (threshold 0.3) ---")
        hyb_results = search_engine.hybrid_search(query, top_k=5, min_score=0.3)
        for r in hyb_results:
            print(f"Score: {r['score']:.4f} | Content: {r['content'][:100]}...")
            
        vector_store.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()
