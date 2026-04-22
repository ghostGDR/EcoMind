from typing import List, Dict, Any, Optional
from src.storage.vector_store import HenryVectorStore
from llama_index.core import VectorStoreIndex


class SearchEngine:
    """Semantic search engine for Henry knowledge base"""
    
    def __init__(self, vector_store: Optional[HenryVectorStore] = None):
        """Initialize search engine with vector store
        
        Args:
            vector_store: Optional HenryVectorStore instance. If None, creates new instance.
            
        Raises:
            ValueError: If vector index is empty (no documents indexed)
        """
        # Create or use provided vector store
        if vector_store is None:
            self.vector_store = HenryVectorStore()
            self._owns_vector_store = True
        else:
            self.vector_store = vector_store
            self._owns_vector_store = False
        
        # Check if index has data
        collection_info = self.vector_store.get_collection_info()
        if collection_info['points_count'] == 0:
            raise ValueError("Vector index is empty. Run indexing first.")
        
        # Load existing index from vector store
        self.index = VectorStoreIndex.from_vector_store(
            self.vector_store.vector_store
        )
        
        # Create query engine with high similarity_top_k for internal retrieval
        # We'll filter and limit results in semantic_search method
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=20,
            response_mode="no_text"  # Return nodes only, no LLM synthesis
        )
    
    def semantic_search(self, query: str, top_k: int = 5, min_score: float = 0.5) -> List[Dict[str, Any]]:
        """Perform semantic search on knowledge base
        
        Args:
            query: Search query string
            top_k: Maximum number of results to return
            min_score: Minimum similarity score threshold (0.0-1.0)
            
        Returns:
            List of search results, each containing:
                - content: Document chunk text
                - score: Similarity score (0.0-1.0)
                - metadata: Document metadata
                - node_id: Unique node identifier
        """
        # Handle empty query
        if not query or not query.strip():
            return []
        
        # Execute query
        response = self.query_engine.query(query)
        
        # Process results
        results = []
        for node in response.source_nodes:
            # Filter by minimum score
            if node.score >= min_score:
                results.append({
                    'content': node.text,
                    'score': float(node.score),
                    'metadata': node.metadata,
                    'node_id': node.node_id
                })
        
        # Limit to top_k results
        return results[:top_k]
    
    def hybrid_search(self, query: str, top_k: int = 5, min_score: float = 0.5) -> List[Dict[str, Any]]:
        """Perform hybrid search combining semantic and keyword matching
        
        Args:
            query: Search query string
            top_k: Maximum number of results to return
            min_score: Minimum similarity score threshold (0.0-1.0)
            
        Returns:
            List of search results with keyword-boosted scores
        """
        # Handle empty query
        if not query or not query.strip():
            return []
        
        # Get semantic search results (retrieve more for keyword boosting)
        results = self.semantic_search(query, top_k=top_k * 2, min_score=min_score)
        
        # Extract keywords from query
        keywords = self._extract_keywords(query)
        
        # Boost results containing keywords
        if keywords:
            results = self._boost_keyword_matches(results, keywords)
        
        # Sort by score (descending)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top_k results
        return results[:top_k]
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract technical terms from query
        
        Args:
            query: Search query string
            
        Returns:
            List of technical keywords found in query
        """
        keywords = [
            'ROI', 'CPC', 'CPM', 'CTR', 'conversion', '转化率',
            'TikTok', 'AI', 'ChatGPT', 'Facebook', 'Google',
            'SEO', 'SEM', 'ROAS', 'LTV', 'CAC'
        ]
        
        found = []
        query_lower = query.lower()
        for keyword in keywords:
            if keyword.lower() in query_lower:
                found.append(keyword)
        
        return found
    
    def _boost_keyword_matches(self, results: List[Dict], keywords: List[str]) -> List[Dict]:
        """Boost scores for results containing keywords
        
        Args:
            results: List of search results
            keywords: List of keywords to match
            
        Returns:
            Results with boosted scores for keyword matches
        """
        for result in results:
            content_lower = result['content'].lower()
            metadata_str = str(result['metadata']).lower()
            
            # Check if any keyword appears in content or metadata
            for keyword in keywords:
                if keyword.lower() in content_lower or keyword.lower() in metadata_str:
                    # Boost score by 20%, cap at 1.0
                    result['score'] = min(result['score'] * 1.2, 1.0)
                    break  # Only boost once per result
        
        return results
    
    def close(self):
        """Close vector store connection"""
        if self._owns_vector_store and hasattr(self, 'vector_store'):
            self.vector_store.close()
