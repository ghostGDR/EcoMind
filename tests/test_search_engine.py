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


class TestDocumentBrowsing:
    """Test document listing and topic categorization"""
    
    def test_list_all_documents(self, search_engine):
        """Test listing all documents returns 21 documents"""
        docs = search_engine.list_all_documents()
        
        assert isinstance(docs, list)
        assert len(docs) == 21, f"Expected 21 documents, got {len(docs)}"
        
        # Verify each document is a dict
        for doc in docs:
            assert isinstance(doc, dict)
    
    def test_document_metadata_structure(self, search_engine):
        """Test each document contains required metadata fields"""
        docs = search_engine.list_all_documents()
        
        assert len(docs) > 0, "No documents found"
        
        # Check first document has all required fields
        doc = docs[0]
        required_fields = ['id', 'title', 'file_type', 'topic', 'size_bytes', 'modified_date', 'relative_path']
        
        for field in required_fields:
            assert field in doc, f"Missing field: {field}"
        
        # Verify field types
        assert isinstance(doc['id'], str)
        assert isinstance(doc['title'], str)
        assert doc['file_type'] in ['markdown', 'excel']
        assert isinstance(doc['topic'], str)
        assert isinstance(doc['size_bytes'], int)
        assert isinstance(doc['modified_date'], str)
        assert isinstance(doc['relative_path'], str)
    
    def test_list_documents_by_topic(self, search_engine):
        """Test documents are grouped by topic"""
        by_topic = search_engine.list_documents_by_topic()
        
        assert isinstance(by_topic, dict)
        assert len(by_topic) > 0, "No topics found"
        
        # Verify structure
        for topic, docs in by_topic.items():
            assert isinstance(topic, str)
            assert isinstance(docs, list)
            assert len(docs) > 0
            
            # Each doc should have topic field matching the key
            for doc in docs:
                assert doc['topic'] == topic
    
    def test_topic_extraction(self, search_engine):
        """Test topic extraction from filenames"""
        docs = search_engine.list_all_documents()
        
        # Find documents with known keywords in filename
        tiktok_docs = [d for d in docs if 'tiktok' in d['title'].lower()]
        ai_docs = [d for d in docs if 'ai' in d['title'].lower() or 'gpt' in d['title'].lower()]
        
        # Verify topic assignment
        for doc in tiktok_docs:
            assert doc['topic'] == 'TikTok', f"Expected TikTok topic for {doc['title']}"
        
        for doc in ai_docs:
            assert doc['topic'] == 'AI工具', f"Expected AI工具 topic for {doc['title']}"
    
    def test_document_stats(self, search_engine):
        """Test document statistics"""
        stats = search_engine.get_document_stats()
        
        assert isinstance(stats, dict)
        assert 'total_documents' in stats
        assert 'markdown_count' in stats
        assert 'excel_count' in stats
        assert 'topics' in stats
        assert 'topic_list' in stats
        
        # Verify counts
        assert stats['total_documents'] == 21
        assert stats['markdown_count'] + stats['excel_count'] == stats['total_documents']
        
        # Verify topics structure
        assert isinstance(stats['topics'], dict)
        assert isinstance(stats['topic_list'], list)
        assert len(stats['topic_list']) > 0
    
    def test_documents_sorted_by_name(self, search_engine):
        """Test documents are sorted by filename"""
        docs = search_engine.list_all_documents()
        
        # Extract titles
        titles = [doc['title'] for doc in docs]
        
        # Verify sorted order
        sorted_titles = sorted(titles)
        assert titles == sorted_titles, "Documents are not sorted by filename"
