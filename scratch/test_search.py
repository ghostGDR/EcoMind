import os
from src.search.search_engine import SearchEngine
from src.api.dependencies import get_vector_store

def test_search():
    print("Testing search for: 'Facebook 广告投放策略'")
    
    # Manually initialize vector store to ensure settings are loaded
    vs = get_vector_store()
    
    # Initialize search engine
    search_engine = SearchEngine(vector_store=vs)
    
    # Run semantic search
    results = search_engine.semantic_search("Facebook 广告投放策略", top_k=5, min_score=0.2)
    
    print(f"\nFound {len(results)} results:")
    for i, res in enumerate(results):
        print(f"[{i+1}] Score: {res['score']:.4f}")
        print(f"    File: {res['metadata'].get('name', 'Unknown')}")
        print(f"    Content snippet: {res['content'][:100]}...")
        print("-" * 40)

if __name__ == "__main__":
    test_search()
