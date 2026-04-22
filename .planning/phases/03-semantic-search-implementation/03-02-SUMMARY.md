---
phase: 03-semantic-search-implementation
plan: 02
subsystem: search
tags: [document-browsing, topic-categorization, metadata]
completed: 2026-04-22T06:13:11Z
duration_minutes: 7

dependency_graph:
  requires:
    - 01-03 (DocumentStore interface)
  provides:
    - document_listing_api
    - topic_categorization
  affects:
    - search_engine

tech_stack:
  added:
    - datetime (timestamp formatting)
  patterns:
    - topic extraction from filenames
    - metadata enrichment

key_files:
  created: []
  modified:
    - src/search/search_engine.py
    - tests/test_search_engine.py

decisions:
  - decision: "Extract topics from filenames using keyword matching"
    rationale: "Simple pattern matching sufficient for known topic set (TikTok, AI, 财务, etc.)"
    alternatives: ["NLP-based classification", "Manual tagging"]
  - decision: "Return documents sorted by filename"
    rationale: "Consistent ordering, matches DocumentStore behavior"
    alternatives: ["Sort by date", "Sort by topic"]

metrics:
  tasks_completed: 1
  tests_added: 6
  tests_passing: 6
  files_modified: 2
  commits: 3
---

# Phase 03 Plan 02: Document Browsing Summary

**One-liner:** Document listing and topic categorization with metadata extraction from file system

## What Was Built

Added document browsing capabilities to SearchEngine:
- `list_all_documents()` returns all 21 documents with complete metadata (id, title, file_type, topic, size_bytes, modified_date, relative_path)
- `list_documents_by_topic()` groups documents by auto-detected topics (TikTok, AI工具, 财务, 收款, 流量, 广告投放, Facebook, Google, 其他)
- `get_document_stats()` provides aggregate statistics (total count, file type breakdown, topic distribution)
- Topic extraction from filenames using keyword pattern matching
- ISO date formatting for timestamps

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Missing datetime import**
- **Found during:** Task 1 implementation
- **Issue:** NameError in `_format_timestamp()` - datetime module not imported
- **Fix:** Added `from datetime import datetime` to imports
- **Files modified:** src/search/search_engine.py
- **Commit:** 2abb43a

**2. [Rule 1 - Bug] Test fixture incompatibility**
- **Found during:** Task 1 testing
- **Issue:** Document browsing tests tried to initialize full SearchEngine with vector store and LLM, causing OpenAI API key errors and Qdrant lock conflicts
- **Fix:** Created separate `doc_browser` fixture that instantiates SearchEngine methods without vector store dependencies
- **Files modified:** tests/test_search_engine.py
- **Commit:** d3dd814

**3. [Rule 1 - Bug] File truncation during edit**
- **Found during:** Import fix commit
- **Issue:** Git commit accidentally removed document browsing methods from search_engine.py
- **Fix:** Restored methods from previous commit and re-committed
- **Files modified:** src/search/search_engine.py, tests/test_search_engine.py
- **Commit:** 61a8910

## Test Coverage

All 6 document browsing tests passing:

1. `test_list_all_documents` - Returns 21 documents
2. `test_document_metadata_structure` - Each document has required fields (id, title, file_type, topic, size_bytes, modified_date, relative_path)
3. `test_list_documents_by_topic` - Documents grouped by topic
4. `test_topic_extraction` - Filenames with "tiktok" → topic="TikTok", "ai"/"gpt" → topic="AI工具"
5. `test_document_stats` - Returns total/markdown/excel counts and topic distribution
6. `test_documents_sorted_by_name` - Documents sorted alphabetically by filename

## Integration Points

**Upstream dependencies:**
- `DocumentStore.list_documents()` - file system access
- `DocumentStore.get_document_metadata()` - file metadata extraction
- `DocumentStore.get_document_count()` - aggregate counts

**Downstream consumers:**
- Future API endpoints for document browsing
- Frontend document management UI (Phase 8)

## Known Limitations

- Topic extraction uses simple keyword matching - may misclassify documents with ambiguous names
- Topics are hardcoded in `_extract_topic_from_filename()` - adding new topics requires code changes
- No support for custom topic taxonomies or user-defined categories
- Documents with no matching keywords default to "其他" (Other)

## Verification

```bash
# Run document browsing tests
pytest tests/test_search_engine.py::TestDocumentBrowsing -v

# Manual verification
python3 -c "
from src.search.search_engine import SearchEngine
from src.storage.document_store import DocumentStore

class DocBrowser:
    def __init__(self):
        self.document_store = DocumentStore()
    
    def list_all_documents(self):
        engine = SearchEngine.__new__(SearchEngine)
        engine.document_store = self.document_store
        return engine.list_all_documents()
    
    def list_documents_by_topic(self):
        engine = SearchEngine.__new__(SearchEngine)
        engine.document_store = self.document_store
        return engine.list_documents_by_topic()
    
    def get_document_stats(self):
        engine = SearchEngine.__new__(SearchEngine)
        engine.document_store = self.document_store
        return engine.get_document_stats()

browser = DocBrowser()
docs = browser.list_all_documents()
print(f'Total: {len(docs)} documents')

by_topic = browser.list_documents_by_topic()
print(f'Topics: {list(by_topic.keys())}')

stats = browser.get_document_stats()
print(f'Stats: {stats}')
"
```

## Success Criteria Met

- ✅ SearchEngine.list_all_documents() returns 21 documents
- ✅ Each document contains complete metadata (id, title, file_type, topic, size_bytes, modified_date, relative_path)
- ✅ SearchEngine.list_documents_by_topic() returns documents grouped by topic
- ✅ Topics automatically extracted from filenames (TikTok, AI工具, 财务, 收款, 流量, 广告投放, 其他)
- ✅ SearchEngine.get_document_stats() returns statistics
- ✅ Documents sorted by filename
- ✅ All 6 document browsing tests passing

## Requirements Completed

- **DOC-01**: 用户可以浏览所有文章列表 ✓
- **DOC-02**: 用户可以按主题分类查看文章 ✓

## Next Steps

- Plan 03-03 (if exists): Continue semantic search implementation
- Phase 4: RAG Engine Core - integrate document browsing with retrieval and generation
- Phase 8: Frontend UI - build document management interface using these APIs

## Self-Check: PASSED

**Files:**
- ✓ src/search/search_engine.py exists
- ✓ tests/test_search_engine.py exists

**Commits:**
- ✓ ffddd80: test(03-02): add failing tests for document browsing
- ✓ d3dd814: feat(03-02): implement document browsing and topic categorization
- ✓ 2abb43a: fix(03-02): add missing datetime import
- ✓ 61a8910: fix(03-02): restore document browsing methods and tests
