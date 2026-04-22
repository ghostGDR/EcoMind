"""RAG query engine integrating search and LLM generation"""
from typing import Dict, Any, List, Optional
from src.search.search_engine import SearchEngine
from src.llm.llm_client import LLMClient
from src.llm.prompts import HENRY_SYSTEM_PROMPT, RAG_PROMPT_TEMPLATE
import logging

logger = logging.getLogger(__name__)


class QueryEngine:
    """RAG query engine that retrieves relevant documents and generates contextual answers"""
    
    def __init__(
        self,
        search_engine: Optional[SearchEngine] = None,
        llm_client: Optional[LLMClient] = None,
        top_k: int = 5,
        min_score: float = 0.5
    ):
        """
        Initialize RAG query engine
        
        Args:
            search_engine: SearchEngine instance for retrieval (creates default if None)
            llm_client: LLMClient instance for generation (creates default if None)
            top_k: Maximum number of documents to retrieve
            min_score: Minimum similarity score threshold (0.0-1.0)
        """
        # Use provided instances or create defaults
        if search_engine is None:
            self.search_engine = SearchEngine()
            self._owns_search_engine = True
        else:
            self.search_engine = search_engine
            self._owns_search_engine = False
        
        if llm_client is None:
            self.llm_client = LLMClient(provider='openai', model='gpt-4o-mini')
            self._owns_llm_client = True
        else:
            self.llm_client = llm_client
            self._owns_llm_client = False
        
        self.top_k = top_k
        self.min_score = min_score
    
    def query(self, user_query: str) -> Dict[str, Any]:
        """
        Execute RAG pipeline: retrieve → format context → generate answer
        
        Args:
            user_query: User's question
        
        Returns:
            Dictionary with:
                - answer: str (LLM-generated response)
                - sources: List[Dict] (Retrieved documents with metadata)
                - has_sources: bool (True if sources found, False if no relevant docs)
        """
        try:
            # Step 1: Retrieve relevant documents using hybrid search
            retrieved_docs = self.search_engine.hybrid_search(
                user_query, 
                top_k=self.top_k, 
                min_score=self.min_score
            )
            
            # Step 2: Check if any documents were retrieved
            if not retrieved_docs:
                return {
                    'answer': '抱歉，我的知识库中暂时没有关于这个问题的信息。',
                    'sources': [],
                    'has_sources': False
                }
            
            # Step 3: Format context from retrieved documents
            formatted_context = self._format_context(retrieved_docs)
            
            # Step 4: Build prompt using RAG template
            prompt = RAG_PROMPT_TEMPLATE.format(
                context=formatted_context,
                query=user_query
            )
            
            # Step 5: Generate answer using LLM
            answer = self.llm_client.generate(prompt, temperature=0.7)
            
            # Step 6: Return answer with source metadata
            return {
                'answer': answer,
                'sources': retrieved_docs,
                'has_sources': True
            }
        
        except Exception as e:
            # Handle errors gracefully
            logger.error(f"Error in RAG query pipeline: {e}")
            
            # Check if it's a search error
            if 'search' in str(e).lower() or 'vector' in str(e).lower():
                return {
                    'answer': '搜索知识库时出错，请稍后重试。',
                    'sources': [],
                    'has_sources': False
                }
            
            # Check if it's an LLM error
            if 'generate' in str(e).lower() or 'llm' in str(e).lower():
                return {
                    'answer': '生成回答时出错，请稍后重试。',
                    'sources': [],
                    'has_sources': False
                }
            
            # Generic error
            return {
                'answer': f'处理查询时出错：{str(e)}',
                'sources': [],
                'has_sources': False
            }
    
    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into context string for LLM
        
        Args:
            documents: List of retrieved documents with content and metadata
        
        Returns:
            Formatted context string with source labels
        """
        context_parts = []
        
        for idx, doc in enumerate(documents, start=1):
            # Extract file name from metadata
            file_name = doc['metadata'].get('file_name', '未知来源')
            
            # Format: [来源 N: filename]\ncontent\n
            context_parts.append(f"[来源 {idx}: {file_name}]")
            context_parts.append(doc['content'])
            context_parts.append("")  # Empty line between sources
        
        return "\n".join(context_parts)
    
    def close(self):
        """Close resources if owned by this instance"""
        if self._owns_search_engine and hasattr(self, 'search_engine'):
            self.search_engine.close()
