---
phase: 04-rag-engine-core
plan: 02
subsystem: rag
tags: [rag, query-engine, retrieval, generation, llm-integration]
completed: 2026-04-22T06:58:26Z
duration_seconds: 162

dependency_graph:
  requires:
    - Phase 03 semantic search (SearchEngine with hybrid_search)
    - Phase 04 Plan 01 (LLMClient and prompts)
  provides:
    - QueryEngine class integrating search + LLM
    - RAG pipeline: retrieve → format → generate
    - Source metadata preservation for citation extraction
  affects:
    - Phase 04 Plan 03 (chat API will use QueryEngine)
    - Phase 05 (conversation management will wrap QueryEngine)

tech_stack:
  added: []
  patterns:
    - RAG pipeline pattern (retrieval-augmented generation)
    - Context formatting with source labels
    - Graceful degradation (no results → explicit message)
    - Error isolation (search vs LLM failures)

key_files:
  created:
    - src/rag/__init__.py (module exports)
    - src/rag/query_engine.py (QueryEngine class - 149 lines)
    - tests/test_query_engine.py (6 test cases - 160 lines)
  modified: []

decisions:
  - decision: Use hybrid_search instead of semantic_search
    rationale: Hybrid search combines semantic understanding with keyword boosting for technical terms (ROI, CPC, TikTok), improving accuracy for e-commerce domain queries
    alternatives_considered: semantic_search only (misses exact term matches)
  
  - decision: Return structured response with answer, sources, and has_sources flag
    rationale: Enables downstream citation extraction (Plan 03), provides transparency about knowledge base coverage
    alternatives_considered: Return string only (loses source metadata)
  
  - decision: Format context with numbered source labels [来源 N: filename]
    rationale: Makes citation extraction easier, provides clear attribution in LLM prompt
    alternatives_considered: Unlabeled context (harder to extract citations)
  
  - decision: Skip LLM call when no documents retrieved
    rationale: No point generating without context, saves API costs, prevents hallucination
    alternatives_considered: Always call LLM (wastes API calls, may hallucinate)

metrics:
  lines_of_code: 313
  test_coverage: 6 tests (all passing)
  files_created: 3
  files_modified: 0
  commits: 2 (RED + GREEN for TDD)
---

# Phase 04 Plan 02: RAG Query Engine Summary

**One-liner:** RAG query engine integrating hybrid search retrieval with LLM generation for knowledge-grounded answers with source tracking

## What Was Built

Implemented complete RAG (Retrieval-Augmented Generation) pipeline that combines semantic search with LLM generation:

1. **QueryEngine class** - Orchestrates retrieval → formatting → generation workflow
2. **Hybrid search integration** - Uses SearchEngine.hybrid_search for semantic + keyword matching
3. **Context formatting** - Structures retrieved documents with source labels for LLM prompt
4. **LLM generation** - Sends formatted context to LLMClient with RAG prompt template
5. **Source preservation** - Returns answer with full source metadata for citation extraction
6. **Empty results handling** - Returns explicit "no information" message when no relevant docs found
7. **Error handling** - Gracefully handles search and LLM failures with user-friendly messages

## Implementation Details

### RAG Pipeline Architecture

```python
class QueryEngine:
    def __init__(search_engine, llm_client, top_k=5, min_score=0.5)
    def query(user_query: str) -> Dict[str, Any]
```

**Pipeline flow:**
1. **Retrieve**: `search_engine.hybrid_search(query, top_k=5, min_score=0.5)`
2. **Check empty**: If no results → return "抱歉，我的知识库中暂时没有关于这个问题的信息。"
3. **Format context**: Concatenate documents with source labels
4. **Build prompt**: `RAG_PROMPT_TEMPLATE.format(context=..., query=...)`
5. **Generate**: `llm_client.generate(prompt, temperature=0.7)`
6. **Return**: `{answer: str, sources: List[Dict], has_sources: bool}`

### Context Formatting

Retrieved documents are formatted with numbered source labels:

```
[来源 1: tiktok_ads.md]
TikTok 广告投放的关键是精准定位受众

[来源 2: roi_optimization.md]
ROI 优化需要持续测试和调整
```

**Design rationale:**
- Clear attribution for each content chunk
- Enables citation extraction in downstream plans
- Helps LLM understand source boundaries
- Chinese language matches user's wiki content

### Response Structure

```python
{
    'answer': str,           # LLM-generated response
    'sources': List[Dict],   # Retrieved documents with metadata
    'has_sources': bool      # True if sources found, False if no relevant docs
}
```

**Source metadata preserved:**
- `content`: Document chunk text
- `score`: Similarity score (0.0-1.0)
- `metadata`: File name, topic, etc.
- `node_id`: Unique node identifier

### Error Handling

**Search errors:**
- Catch vector store failures → "搜索知识库时出错，请稍后重试。"

**LLM errors:**
- Catch API failures → "生成回答时出错，请稍后重试。"

**Empty results:**
- No documents above min_score → "抱歉，我的知识库中暂时没有关于这个问题的信息。"
- Skip LLM call (no context = no generation needed)

## Test Coverage

All 6 tests passing:

1. ✓ QueryEngine initializes with SearchEngine and LLMClient
2. ✓ query() retrieves documents using hybrid_search with correct parameters
3. ✓ query() formats context from retrieved documents with source labels
4. ✓ query() sends formatted prompt to LLM and returns response
5. ✓ query() returns "no information" message when no documents retrieved
6. ✓ query() includes source metadata in response for citation extraction

**Test strategy:** Mock SearchEngine and LLMClient to verify integration logic without real API calls or vector store access.

## Deviations from Plan

None - plan executed exactly as written. All tasks completed with TDD cycle (RED → GREEN).

## Security & Privacy

**Threat mitigations implemented:**

- **T-04-05 (Query manipulation):** Query passed through SearchEngine's existing validation, no SQL/code injection risk (vector search only)
- **T-04-07 (Context overflow):** top_k=5 limits retrieved documents, prevents context window overflow (5 docs * ~500 tokens = ~2500 tokens, well under limits)
- **T-04-08 (LLM hallucination):** System prompt enforces "只基于提供的知识库内容回答", empty results return explicit "no information" message

**Accepted risks:**

- **T-04-06 (Knowledge base content to LLM):** User's PROJECT.md explicitly requires cloud LLM API, user controls their own wiki content, no PII in articles

## Integration Points

**Dependencies satisfied:**

- Phase 03 semantic search: SearchEngine.hybrid_search provides retrieval
- Phase 04 Plan 01: LLMClient.generate provides generation, RAG_PROMPT_TEMPLATE structures prompt

**Provides to downstream plans:**

- Phase 04 Plan 03: Chat API will use QueryEngine.query() for answer generation
- Phase 05: Conversation management will wrap QueryEngine with multi-turn context

## Known Limitations

1. **No streaming support:** query() returns complete response (not token-by-token streaming)
2. **No conversation history:** QueryEngine is stateless, caller must manage multi-turn context
3. **Fixed top_k and min_score:** Hardcoded to 5 and 0.5 (sufficient for v1, configurable via constructor)

These are intentional simplifications for v1. Streaming and conversation management will be handled at the chat API layer (Plan 03).

## Next Steps

Ready for Phase 04 Plan 03: Chat API with Conversation Management

**What's needed:**
1. Wrap QueryEngine with conversation history tracking
2. Implement multi-turn context management (previous Q&A pairs)
3. Add conversation persistence (save/load from database)
4. Build REST API endpoints for chat interface

## Self-Check: PASSED

✓ All created files exist:
  - src/rag/__init__.py
  - src/rag/query_engine.py
  - tests/test_query_engine.py

✓ All commits exist:
  - cb73fda: test(04-02): add failing tests for RAG query engine (RED)
  - ffcbc25: feat(04-02): implement RAG query engine with search and LLM integration (GREEN)

✓ All tests pass: 6/6
✓ Success criteria met: QueryEngine integrates SearchEngine + LLMClient, returns answers with sources, handles empty results gracefully
