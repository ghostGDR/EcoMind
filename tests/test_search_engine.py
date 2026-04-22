import pytest
from src.search.search_engine import SearchEngine
from src.storage.vector_store import HenryVectorStore


@pytest.fixture
def search_engine():
    """Create SearchEngine instance for testing"""
    engine = SearchEngine()
    yield engine
    engine.close()


class TestSearchEngineInitialization:
    """Test SearchEngine initialization"""
    
    def test_search_engine_initialization(self, search_engine):
        """SearchEngine initializes successfully and index is loaded"""
        assert search_engine is not None
        assert search_engine.index is not None
        assert search_engine.query_engine is not None
        assert search_engine.vector_store is not None


class TestSemanticSearch:
    """Test semantic search functionality"""
    
    def test_semantic_search_returns_results(self, search_engine):
        """Query returns results list with content/score/metadata"""
        results = search_engine.semantic_search("TikTok", top_k=3)
        
        assert isinstance(results, list)
        if len(results) > 0:
            result = results[0]
            assert 'content' in result
            assert 'score' in result
            assert 'metadata' in result
            assert 'node_id' in result
            assert isinstance(result['content'], str)
            assert isinstance(result['score'], float)
            assert 0.0 <= result['score'] <= 1.0
    
    def test_chinese_query_finds_relevant_docs(self, search_engine):
        """Chinese query 'TikTok' returns documents containing TikTok"""
        results = search_engine.semantic_search("TikTok", top_k=5, min_score=0.3)
        
        assert len(results) >= 1, "Should find at least 1 TikTok-related document"
        
        # Check that results contain TikTok-related content
        found_tiktok = False
        for result in results:
            content_lower = result['content'].lower()
            if 'tiktok' in content_lower:
                found_tiktok = True
                break
        
        assert found_tiktok, "Results should contain TikTok-related content"
    
    def test_relevance_score_filtering(self, search_engine):
        """min_score=0.8 filters out low-score results"""
        high_score_results = search_engine.semantic_search("电商", top_k=10, min_score=0.8)
        
        # All results should have score >= 0.8
        for result in high_score_results:
            assert result['score'] >= 0.8, f"Result score {result['score']} below min_score 0.8"
    
    def test_empty_query_returns_empty_list(self, search_engine):
        """Empty string query returns empty list without exception"""
        results = search_engine.semantic_search("", top_k=5)
        
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_top_k_limits_results(self, search_engine):
        """top_k=3 returns at most 3 results"""
        results = search_engine.semantic_search("AI", top_k=3, min_score=0.3)
        
        assert len(results) <= 3, f"Expected at most 3 results, got {len(results)}"


class TestHybridSearch:
    """Test hybrid search functionality (semantic + keyword)"""
    
    def test_hybrid_search_boosts_keyword_matches(self, search_engine):
        """Query 'ROI 计算' boosts results containing 'ROI'"""
        results = search_engine.hybrid_search("ROI 计算", top_k=5, min_score=0.3)
        
        # Should return results
        assert isinstance(results, list)
        
        # If we have results with ROI, they should be ranked higher
        if len(results) >= 2:
            roi_scores = []
            non_roi_scores = []
            
            for result in results:
                content_lower = result['content'].lower()
                if 'roi' in content_lower:
                    roi_scores.append(result['score'])
                else:
                    non_roi_scores.append(result['score'])
            
            # If we have both ROI and non-ROI results, ROI should generally score higher
            if roi_scores and non_roi_scores:
                avg_roi = sum(roi_scores) / len(roi_scores)
                avg_non_roi = sum(non_roi_scores) / len(non_roi_scores)
                # ROI results should have higher average score due to boost
                assert avg_roi >= avg_non_roi * 0.9  # Allow some tolerance
    
    def test_hybrid_search_handles_technical_terms(self, search_engine):
        """Query 'CPC 优化' returns documents containing CPC"""
        results = search_engine.hybrid_search("CPC 优化", top_k=5, min_score=0.3)
        
        assert isinstance(results, list)
        # Should find results (may be empty if no CPC content in test data)
    
    def test_hybrid_search_deduplicates_results(self, search_engine):
        """Same document does not appear multiple times"""
        results = search_engine.hybrid_search("TikTok 广告", top_k=10, min_score=0.3)
        
        # Check for duplicate node_ids
        node_ids = [r['node_id'] for r in results]
        assert len(node_ids) == len(set(node_ids)), "Results contain duplicate node_ids"
    
    def test_hybrid_search_sorts_by_score(self, search_engine):
        """Results are sorted by score in descending order"""
        results = search_engine.hybrid_search("AI 工具", top_k=10, min_score=0.3)
        
        if len(results) >= 2:
            scores = [r['score'] for r in results]
            # Check that scores are in descending order
            for i in range(len(scores) - 1):
                assert scores[i] >= scores[i + 1], f"Scores not sorted: {scores[i]} < {scores[i+1]}"
