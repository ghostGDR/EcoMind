"""Citation formatting utilities for RAG responses"""
from typing import List, Dict, Any


class CitationFormatter:
    """Format source documents into citation text"""
    
    def format_citations(self, sources: List[Dict[str, Any]]) -> str:
        """
        Format source documents into citation text
        
        Args:
            sources: List of search results from SearchEngine
        
        Returns:
            Formatted citation string in Chinese, e.g.:
            
            ---
            来源：
            [1] TikTok广告投放策略.md (相关度: 0.85)
               "TikTok 广告投放的最佳时间是晚上 8-10 点，这个时段用户活跃度最高..."
            
            [2] AI工具应用指南.md (相关度: 0.72)
               "使用 ChatGPT 可以快速生成产品描述，提升转化率..."
        """
        # Handle empty sources
        if not sources:
            return ''
        
        # Deduplicate: Group sources by file_name, keep highest score per file
        deduplicated = {}
        for source in sources:
            file_name = source['metadata'].get('file_name', '未知来源')
            
            # Keep the source with highest score for each file
            if file_name not in deduplicated or source['score'] > deduplicated[file_name]['score']:
                deduplicated[file_name] = source
        
        # Sort by relevance score (highest first)
        sorted_sources = sorted(deduplicated.values(), key=lambda x: x['score'], reverse=True)
        
        # Build citation text
        citation_lines = ['---', '来源：']
        
        for idx, source in enumerate(sorted_sources, start=1):
            file_name = source['metadata'].get('file_name', '未知来源')
            score = source['score']
            content = source['content']
            
            # Truncate content to 200 chars
            if len(content) > 200:
                content = content[:200] + '...'
            
            # Format citation
            citation_lines.append(f'[{idx}] {file_name} (相关度: {score:.2f})')
            citation_lines.append(f'   "{content}"')
            citation_lines.append('')  # Empty line between citations
        
        return '\n'.join(citation_lines)


def format_citations(sources: List[Dict[str, Any]]) -> str:
    """
    Convenience function wrapping CitationFormatter
    
    Args:
        sources: List of search results from SearchEngine
    
    Returns:
        Formatted citation string
    """
    formatter = CitationFormatter()
    return formatter.format_citations(sources)
