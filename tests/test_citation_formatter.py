"""Tests for citation formatting"""
import pytest
from src.rag.citation_formatter import CitationFormatter, format_citations


class TestCitationFormatter:
    """Test citation formatting functionality"""
    
    def test_format_citations_extracts_file_names(self):
        """Test 1: format_citations() extracts file names from source metadata"""
        sources = [
            {
                'content': 'TikTok 广告投放的最佳时间是晚上 8-10 点',
                'score': 0.85,
                'metadata': {'file_name': 'TikTok广告投放策略.md'},
                'node_id': 'node1'
            }
        ]
        
        result = format_citations(sources)
        
        assert 'TikTok广告投放策略.md' in result
        assert '来源：' in result
    
    def test_format_citations_creates_numbered_list(self):
        """Test 2: format_citations() creates numbered citation list"""
        sources = [
            {
                'content': 'Content 1',
                'score': 0.85,
                'metadata': {'file_name': 'File1.md'},
                'node_id': 'node1'
            },
            {
                'content': 'Content 2',
                'score': 0.72,
                'metadata': {'file_name': 'File2.md'},
                'node_id': 'node2'
            }
        ]
        
        result = format_citations(sources)
        
        assert '[1]' in result
        assert '[2]' in result
        assert 'File1.md' in result
        assert 'File2.md' in result
    
    def test_format_citations_includes_relevance_scores(self):
        """Test 3: format_citations() includes relevance scores"""
        sources = [
            {
                'content': 'Test content',
                'score': 0.8567,
                'metadata': {'file_name': 'Test.md'},
                'node_id': 'node1'
            }
        ]
        
        result = format_citations(sources)
        
        assert '0.86' in result or '0.85' in result  # Rounded to 2 decimals
        assert '相关度' in result
    
    def test_format_citations_truncates_long_content(self):
        """Test 4: format_citations() truncates long content snippets (max 200 chars)"""
        long_content = 'A' * 300  # 300 characters
        sources = [
            {
                'content': long_content,
                'score': 0.75,
                'metadata': {'file_name': 'Long.md'},
                'node_id': 'node1'
            }
        ]
        
        result = format_citations(sources)
        
        # Should be truncated with ellipsis
        assert '...' in result
        # Should not contain all 300 A's
        assert 'A' * 300 not in result
        # Should contain roughly 200 chars of content
        assert 'A' * 150 in result  # At least 150 chars present
    
    def test_format_citations_handles_empty_sources(self):
        """Test 5: format_citations() handles empty sources list"""
        sources = []
        
        result = format_citations(sources)
        
        assert result == ''
    
    def test_format_citations_deduplicates_same_file(self):
        """Test 6: format_citations() deduplicates sources from same file"""
        sources = [
            {
                'content': 'First chunk from file',
                'score': 0.85,
                'metadata': {'file_name': 'Same.md'},
                'node_id': 'node1'
            },
            {
                'content': 'Second chunk from file',
                'score': 0.72,
                'metadata': {'file_name': 'Same.md'},
                'node_id': 'node2'
            },
            {
                'content': 'Different file',
                'score': 0.80,
                'metadata': {'file_name': 'Different.md'},
                'node_id': 'node3'
            }
        ]
        
        result = format_citations(sources)
        
        # Should only have 2 citations (Same.md deduplicated)
        assert '[1]' in result
        assert '[2]' in result
        assert '[3]' not in result
        
        # Should keep the highest score from Same.md (0.85)
        assert 'Same.md' in result
        assert 'Different.md' in result
        # The first chunk (higher score) should be used
        assert 'First chunk from file' in result
        assert 'Second chunk from file' not in result
