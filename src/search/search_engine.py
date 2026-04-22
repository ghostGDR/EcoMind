from typing import List, Dict, Any, Optional
from datetime import datetime
from src.storage.vector_store import HenryVectorStore
from src.storage.document_store import DocumentStore
from llama_index.core import VectorStoreIndex, Settings


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
        
        # Disable LLM for query engine (we only need vector retrieval, no synthesis)
        # This prevents OpenAI API key requirement
        Settings.llm = None
        
        # Create query engine with high similarity_top_k for internal retrieval
        # We'll filter and limit results in semantic_search method
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=20,
            response_mode="no_text"  # Return nodes only, no LLM synthesis
        )
        
        # Add document store for browsing
        self.document_store = DocumentStore()
    
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
        
        # Get embedding for query using the same model as indexing
        from llama_index.core import Settings
        query_embedding = Settings.embed_model.get_query_embedding(query)
        
        # Query Qdrant directly using the new API
        search_result = self.vector_store.client.query_points(
            collection_name="henry_knowledge_base",
            query=query_embedding,
            limit=20,  # Retrieve more internally for filtering
            with_payload=True,
            with_vectors=False
        )
        
        # Process results
        results = []
        for scored_point in search_result.points:
            score = scored_point.score
            
            # Filter by minimum score
            if score >= min_score:
                # Extract text and metadata from payload
                payload = scored_point.payload
                content = payload.get('text', '')
                metadata = payload.get('metadata', {})
                
                # If content or metadata is missing, try to parse from '_node_content'
                if '_node_content' in payload:
                    try:
                        import json
                        node_data = json.loads(payload['_node_content'])
                        if not content:
                            content = node_data.get('text', '')
                        # Also check for metadata in node_data
                        node_metadata = node_data.get('metadata', {})
                        if node_metadata:
                            # Merge, preferring node_data if current metadata is empty or sparse
                            for k, v in node_metadata.items():
                                if k not in metadata or not metadata[k]:
                                    metadata[k] = v
                    except Exception:
                        if not content:
                            content = payload['_node_content']
                
                results.append({
                    'content': content,
                    'score': float(score),
                    'metadata': metadata,
                    'node_id': scored_point.id
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
    
    def list_all_documents(self) -> List[Dict[str, Any]]:
        """
        列出所有文档及其元数据
        
        Returns:
            List of document metadata dicts with keys:
            - id: str (file path)
            - title: str (filename without extension)
            - file_type: str ('markdown' or 'excel')
            - topic: str (extracted from filename)
            - size_bytes: int
            - modified_date: str (ISO format)
            - relative_path: str
        """
        documents = self.document_store.list_documents()
        
        result = []
        for doc_path in documents:
            metadata = self.document_store.get_document_metadata(doc_path)
            
            # Extract topic from filename
            topic = self._extract_topic_from_filename(doc_path.name)
            
            # Convert to user-friendly format
            result.append({
                'id': str(doc_path),
                'title': doc_path.stem,  # filename without extension
                'file_type': 'markdown' if doc_path.suffix == '.md' else 'excel',
                'topic': topic,
                'size_bytes': metadata['size_bytes'],
                'modified_date': self._format_timestamp(metadata['modified_timestamp']),
                'relative_path': metadata['relative_path']
            })
        
        return result
    
    def list_documents_by_topic(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        按主题分组列出文档
        
        Returns:
            Dictionary mapping topic names to lists of document metadata
            Example: {
                'TikTok': [{doc1}, {doc2}],
                'AI工具': [{doc3}],
                ...
            }
        """
        all_docs = self.list_all_documents()
        
        by_topic = {}
        for doc in all_docs:
            topic = doc['topic']
            if topic not in by_topic:
                by_topic[topic] = []
            by_topic[topic].append(doc)
        
        return by_topic
    
    def get_document_stats(self) -> Dict[str, Any]:
        """
        获取文档统计信息
        
        Returns:
            Dictionary with document counts and topics
        """
        counts = self.document_store.get_document_count()
        by_topic = self.list_documents_by_topic()
        
        return {
            'total_documents': counts['total'],
            'markdown_count': counts['markdown'],
            'excel_count': counts['excel'],
            'topics': {topic: len(docs) for topic, docs in by_topic.items()},
            'topic_list': sorted(by_topic.keys())
        }
    
    def _extract_topic_from_filename(self, filename: str) -> str:
        """
        从文件名提取主题
        
        Args:
            filename: 文件名（包含扩展名）
        
        Returns:
            主题名称（中文）
        """
        filename_lower = filename.lower()
        
        # 主题关键词映射
        if 'tiktok' in filename_lower:
            return 'TikTok'
        elif 'ai' in filename_lower or 'chatgpt' in filename_lower or 'gpt' in filename_lower:
            return 'AI工具'
        elif '财务' in filename_lower or 'finance' in filename_lower or '税' in filename_lower:
            return '财务'
        elif '收款' in filename_lower or 'payment' in filename_lower or '支付' in filename_lower:
            return '收款'
        elif '流量' in filename_lower or 'traffic' in filename_lower:
            return '流量'
        elif '广告' in filename_lower or 'ads' in filename_lower or 'advertising' in filename_lower:
            return '广告投放'
        elif 'facebook' in filename_lower or 'fb' in filename_lower:
            return 'Facebook'
        elif 'google' in filename_lower:
            return 'Google'
        else:
            return '其他'
    
    def _format_timestamp(self, timestamp: float) -> str:
        """
        格式化时间戳为 ISO 格式
        
        Args:
            timestamp: Unix timestamp
        
        Returns:
            ISO format date string (YYYY-MM-DD)
        """
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    
    def close(self):
        """Close vector store connection"""
        if self._owns_vector_store and hasattr(self, 'vector_store'):
            self.vector_store.close()
