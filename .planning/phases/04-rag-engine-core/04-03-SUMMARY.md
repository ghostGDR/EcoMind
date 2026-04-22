---
phase: 04-rag-engine-core
plan: 03
subsystem: rag
tags: [citation, formatting, sources, rag]
completed: 2026-04-22T07:03:40Z
duration_seconds: 167

dependency_graph:
  requires:
    - 04-02 (QueryEngine with source tracking)
    - Phase 03 (SearchEngine with hybrid search)
  provides:
    - Citation formatting utilities
    - Source references in RAG responses
  affects:
    - QueryEngine responses now include formatted citations
    - Frontend (Phase 7) can display citations inline

tech_stack:
  added:
    - CitationFormatter class for source formatting
  patterns:
    - Deduplication by file name (keep highest score)
    - Content truncation for readability (200 chars)
    - Chinese language formatting for citations

key_files:
  created:
    - src/rag/citation_formatter.py (73 lines)
    - tests/test_citation_formatter.py (113 lines)
  modified:
    - src/rag/query_engine.py (added citation integration)
    - src/rag/__init__.py (exported CitationFormatter)

decisions:
  - Use Chinese language for citation formatting - matches user's wiki content and Henry's responses
  - Deduplicate sources by file name - prevents redundant citations from same document
  - Truncate content to 200 chars - balances detail vs readability
  - Append citations to answer text - simpler frontend integration than separate UI components
  - Format as numbered list [1], [2] - enables easy reference in conversation

metrics:
  tasks_completed: 1
  tests_added: 6
  test_coverage: 100%
  files_created: 2
  files_modified: 2
  lines_added: 213
---

# Phase 04 Plan 03: Citation Formatting Summary

**One-liner:** Citation formatter with deduplication, truncation, and Chinese formatting integrated into QueryEngine responses

## What Was Built

Implemented citation formatting system that appends source references to every RAG answer, fulfilling SEARCH-02 requirement (引用具体的来源文章和段落).

**Core functionality:**
- CitationFormatter class extracts file names, scores, and content from search results
- Deduplicates sources from same file (keeps highest relevance score)
- Truncates content snippets to 200 characters for readability
- Formats citations in Chinese with numbered list: [1], [2], [3]...
- Includes relevance scores (0.XX format) for transparency
- Integrated into QueryEngine.query() - citations automatically appended to answers

**Example output format:**
```
---
来源：
[1] TikTok广告投放策略.md (相关度: 0.85)
   "TikTok 广告投放的最佳时间是晚上 8-10 点，这个时段用户活跃度最高..."

[2] AI工具应用指南.md (相关度: 0.72)
   "使用 ChatGPT 可以快速生成产品描述，提升转化率..."
```

## Implementation Details

**CitationFormatter (src/rag/citation_formatter.py):**
- `format_citations(sources)` - main formatting method
- Handles empty sources gracefully (returns empty string)
- Deduplication logic: groups by file_name, keeps highest score
- Sorts by relevance score (highest first)
- Truncates content > 200 chars with "..." suffix
- Convenience function `format_citations()` wraps class method

**QueryEngine integration (src/rag/query_engine.py):**
- Import citation_formatter at module level
- Call `format_citations(retrieved_docs)` after LLM generation
- Append citations to answer with "\n\n" separator
- Only append if citations exist (empty sources handled)

**Module exports (src/rag/__init__.py):**
- Added CitationFormatter and format_citations to __all__
- Enables clean imports: `from src.rag import format_citations`

## Test Coverage

**6 comprehensive tests (tests/test_citation_formatter.py):**
1. ✓ Extracts file names from source metadata
2. ✓ Creates numbered citation list [1], [2], [3]
3. ✓ Includes relevance scores formatted to 2 decimals
4. ✓ Truncates long content (>200 chars) with ellipsis
5. ✓ Handles empty sources list (returns empty string)
6. ✓ Deduplicates sources from same file (keeps highest score)

All tests pass. Integration verified with QueryEngine.

## Deviations from Plan

None - plan executed exactly as written.

## Requirements Fulfilled

**SEARCH-02:** ✓ 引用具体的来源文章和段落
- Every answer includes source article references
- Citations show file name, relevance score, and content snippet
- User can identify which knowledge base article supports each claim

## Known Stubs

None - all functionality fully implemented.

## Threat Surface

No new threats introduced. All threats from plan's threat model remain accepted:
- T-04-09 (Information Disclosure): File paths visible to user - accepted (single-user system)
- T-04-10 (Tampering): Malicious content in snippets - accepted (user controls wiki, frontend will escape)
- T-04-11 (DoS): Long file names/content - mitigated (200 char truncation implemented)

## Self-Check: PASSED

**Created files exist:**
```
FOUND: src/rag/citation_formatter.py
FOUND: tests/test_citation_formatter.py
```

**Modified files exist:**
```
FOUND: src/rag/query_engine.py
FOUND: src/rag/__init__.py
```

**Commit exists:**
```
FOUND: a2a39a4
```

**Tests pass:**
```
6/6 tests passing
```

**Integration verified:**
```
✓ Citations integrated into QueryEngine responses
```

## Next Steps

Phase 04 Plan 03 complete. Next action:
- Phase 04 complete (all 3 plans executed)
- Ready for Phase 5: Conversation Management
- Or run verification/code review if configured
