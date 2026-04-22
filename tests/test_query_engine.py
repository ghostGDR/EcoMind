import pytest
from unittest.mock import Mock, MagicMock
from src.rag.query_engine import QueryEngine
from src.search.search_engine import SearchEngine
from src.llm.llm_client import LLMClient


class TestQueryEngine:
    """Test suite for RAG query engine"""
    
    def test_init_with_search_engine_and_llm_client(self):
        """Test 1: QueryEngine initializes with SearchEngine and LLMClient"""
        mock_search = Mock(spec=SearchEngine)
        mock_llm = Mock(spec=LLMClient)
        
        engine = QueryEngine(search_engine=mock_search, llm_client=mock_llm)
        
        assert engine.search_engine == mock_search
        assert engine.llm_client == mock_llm
        assert engine.top_k == 5
        assert engine.min_score == 0.5
    
    def test_query_retrieves_documents_using_hybrid_search(self):
        """Test 2: query() retrieves documents using hybrid_search"""
        mock_search = Mock(spec=SearchEngine)
        mock_llm = Mock(spec=LLMClient)
        
        # Mock search results
        mock_search.hybrid_search.return_value = [
            {
                'content': 'TikTok 广告投放的关键是精准定位受众',
                'score': 0.85,
                'metadata': {'file_name': 'tiktok_ads.md'},
                'node_id': 'node_1'
            }
        ]
        
        mock_llm.generate.return_value = '根据知识库，TikTok广告的关键是精准定位。'
        
        engine = QueryEngine(search_engine=mock_search, llm_client=mock_llm)
        result = engine.query('如何做好TikTok广告？')
        
        # Verify hybrid_search was called with correct parameters
        mock_search.hybrid_search.assert_called_once_with('如何做好TikTok广告？', top_k=5, min_score=0.5)
    
    def test_query_formats_context_from_retrieved_documents(self):
        """Test 3: query() formats context from retrieved documents"""
        mock_search = Mock(spec=SearchEngine)
        mock_llm = Mock(spec=LLMClient)
        
        # Mock multiple search results
        mock_search.hybrid_search.return_value = [
            {
                'content': 'TikTok 广告投放的关键是精准定位受众',
                'score': 0.85,
                'metadata': {'file_name': 'tiktok_ads.md'},
                'node_id': 'node_1'
            },
            {
                'content': 'ROI 优化需要持续测试和调整',
                'score': 0.75,
                'metadata': {'file_name': 'roi_optimization.md'},
                'node_id': 'node_2'
            }
        ]
        
        mock_llm.generate.return_value = '测试回答'
        
        engine = QueryEngine(search_engine=mock_search, llm_client=mock_llm)
        engine.query('如何优化广告？')
        
        # Verify LLM was called with formatted context
        call_args = mock_llm.generate.call_args
        prompt = call_args[0][0]
        
        # Check context formatting
        assert '[来源 1: tiktok_ads.md]' in prompt
        assert 'TikTok 广告投放的关键是精准定位受众' in prompt
        assert '[来源 2: roi_optimization.md]' in prompt
        assert 'ROI 优化需要持续测试和调整' in prompt
        assert '如何优化广告？' in prompt
    
    def test_query_sends_formatted_prompt_to_llm_and_returns_response(self):
        """Test 4: query() sends formatted prompt to LLM and returns response"""
        mock_search = Mock(spec=SearchEngine)
        mock_llm = Mock(spec=LLMClient)
        
        mock_search.hybrid_search.return_value = [
            {
                'content': 'Test content',
                'score': 0.8,
                'metadata': {'file_name': 'test.md'},
                'node_id': 'node_1'
            }
        ]
        
        mock_llm.generate.return_value = '这是基于知识库的回答'
        
        engine = QueryEngine(search_engine=mock_search, llm_client=mock_llm)
        result = engine.query('测试问题')
        
        # Verify response structure
        assert 'answer' in result
        assert 'sources' in result
        assert 'has_sources' in result
        assert result['answer'] == '这是基于知识库的回答'
        assert result['has_sources'] is True
        assert len(result['sources']) == 1
    
    def test_query_returns_no_information_message_when_no_documents_retrieved(self):
        """Test 5: query() returns 'no information' message when no documents retrieved"""
        mock_search = Mock(spec=SearchEngine)
        mock_llm = Mock(spec=LLMClient)
        
        # Mock empty search results (no documents above min_score)
        mock_search.hybrid_search.return_value = []
        
        engine = QueryEngine(search_engine=mock_search, llm_client=mock_llm)
        result = engine.query('完全无关的问题')
        
        # Verify no information message
        assert result['answer'] == '抱歉，我的知识库中暂时没有关于这个问题的信息。'
        assert result['sources'] == []
        assert result['has_sources'] is False
        
        # Verify LLM was NOT called (no point generating without context)
        mock_llm.generate.assert_not_called()
    
    def test_query_includes_source_metadata_in_response(self):
        """Test 6: query() includes source metadata in response for citation extraction"""
        mock_search = Mock(spec=SearchEngine)
        mock_llm = Mock(spec=LLMClient)
        
        mock_search.hybrid_search.return_value = [
            {
                'content': 'Content 1',
                'score': 0.9,
                'metadata': {'file_name': 'doc1.md', 'topic': 'TikTok'},
                'node_id': 'node_1'
            },
            {
                'content': 'Content 2',
                'score': 0.8,
                'metadata': {'file_name': 'doc2.md', 'topic': 'AI'},
                'node_id': 'node_2'
            }
        ]
        
        mock_llm.generate.return_value = '回答内容'
        
        engine = QueryEngine(search_engine=mock_search, llm_client=mock_llm)
        result = engine.query('测试')
        
        # Verify source metadata is preserved
        assert len(result['sources']) == 2
        assert result['sources'][0]['content'] == 'Content 1'
        assert result['sources'][0]['score'] == 0.9
        assert result['sources'][0]['metadata']['file_name'] == 'doc1.md'
        assert result['sources'][0]['metadata']['topic'] == 'TikTok'
        assert result['sources'][1]['metadata']['file_name'] == 'doc2.md'
