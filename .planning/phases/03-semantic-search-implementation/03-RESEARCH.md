# Phase 3: Semantic Search Implementation - Research

**Phase:** 3 - Semantic Search Implementation
**Researched:** 2026-04-22
**Confidence:** High (established patterns with LlamaIndex + Qdrant)

## Executive Summary

Phase 3 implements semantic search over the indexed knowledge base (551 vectors from 21 documents). The system needs to support:
1. **Semantic search** - Chinese language queries finding relevant documents by meaning
2. **Hybrid retrieval** - Combining semantic + keyword search for technical terms
3. **Relevance scoring** - Filtering low-quality results
4. **Document browsing** - List all articles with topic categorization
5. **Content search** - Find documents by text content

**Key insight:** LlamaIndex already provides the query engine infrastructure. Phase 3 focuses on exposing search APIs and implementing hybrid retrieval strategies.

## Standard Stack

### Core Libraries (Already Installed)

```python
# Vector search (Phase 1)
llama-index-core==0.10.68
llama-index-vector-stores-qdrant==0.2.16
qdrant-client==1.7.0

# Embeddings (Phase 1)
llama-index-embeddings-huggingface==0.2.3
sentence-transformers>=2.0.0  # all-MiniLM-L6-v2 model
```

### Additional Dependencies Needed

```python
# None - all required libraries already installed in Phase 1
```

## Architecture Patterns

### 1. Query Engine Pattern (LlamaIndex Standard)

```python
from llama_index.core import VectorStoreIndex

# Load existing index from Qdrant
index = VectorStoreIndex.from_vector_store(vector_store)

# Create query engine with retrieval parameters
query_engine = index.as_query_engine(
    similarity_top_k=5,           # Return top 5 results
    response_mode="compact",       # Compact response format
)

# Execute query
response = query_engine.query("TikTok 广告投放最佳时间")
```

**Why this pattern:**
- LlamaIndex handles embedding generation automatically
- Qdrant performs vector similarity search
- Results include source nodes with metadata
- No need to manually manage embeddings or similarity calculations

### 2. Hybrid Retrieval Pattern (Semantic + Keyword)

LlamaIndex 0.10.x supports hybrid search through custom retrievers:

```python
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

# Semantic retriever
vector_retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=10,
)

# For keyword search, use metadata filtering
# Qdrant supports filtering by metadata fields
from qdrant_client.models import Filter, FieldCondition, MatchText

# Combine semantic + keyword via custom retriever
class HybridRetriever:
    def retrieve(self, query_str: str):
        # 1. Semantic search (vector similarity)
        semantic_results = vector_retriever.retrieve(query_str)
        
        # 2. Keyword search (metadata filtering)
        # Extract keywords from query
        keywords = extract_keywords(query_str)
        
        # 3. Merge and re-rank results
        return merge_results(semantic_results, keyword_results)
```

**Why hybrid:**
- Semantic search handles "TikTok 广告投放最佳时间" → finds time-related content
- Keyword search handles exact terms like "ROI", "CPC", "conversion rate"
- Chinese text benefits from both approaches

### 3. Document Browsing Pattern

```python
from src.storage.document_store import DocumentStore

# List all documents with metadata
doc_store = DocumentStore(wiki_path)
documents = doc_store.list_documents()

# Group by topic (from metadata)
by_topic = {}
for doc in documents:
    topic = doc.metadata.get('topic', 'uncategorized')
    by_topic.setdefault(topic, []).append(doc)
```

**Topic extraction strategies:**
1. **From filename** - `tiktok_ads.md` → topic: "TikTok"
2. **From frontmatter** - YAML metadata in Markdown files
3. **From directory structure** - `/articles/tiktok/` → topic: "TikTok"

### 4. Relevance Filtering Pattern

```python
# LlamaIndex returns scores with each node
response = query_engine.query("query")

# Filter by score threshold
MIN_SCORE = 0.7  # Adjust based on testing
filtered_nodes = [
    node for node in response.source_nodes
    if node.score >= MIN_SCORE
]
```

**Score interpretation:**
- 0.9-1.0: Highly relevant (exact match)
- 0.7-0.9: Relevant (semantic match)
- 0.5-0.7: Possibly relevant (weak match)
- <0.5: Not relevant (filter out)

## Implementation Approach

### Phase 3 Deliverables

1. **SearchEngine class** - Wrapper around LlamaIndex query engine
   - `semantic_search(query: str, top_k: int) -> List[SearchResult]`
   - `hybrid_search(query: str, top_k: int) -> List[SearchResult]`
   - `get_document_list() -> List[DocumentMetadata]`
   - `get_documents_by_topic(topic: str) -> List[DocumentMetadata]`

2. **SearchResult dataclass** - Structured search results
   - `content: str` - Matched text chunk
   - `document_id: str` - Source document ID
   - `document_title: str` - Document title
   - `score: float` - Relevance score
   - `metadata: dict` - Additional metadata

3. **Topic extraction** - Categorize documents
   - Parse filenames for topic keywords
   - Map to predefined categories: TikTok, AI, 财务, 收款, 流量, 广告

4. **Integration tests** - Verify search quality
   - Test Chinese query → relevant results
   - Test technical terms → exact matches
   - Test score filtering → low scores excluded

### File Structure

```
src/search/
  __init__.py
  search_engine.py      # SearchEngine class
  hybrid_retriever.py   # Custom hybrid retriever (optional)
  
tests/
  test_search_engine.py # Integration tests
```

## Don't Hand-Roll

### ❌ Don't Build Custom

1. **Vector similarity calculation** - Use Qdrant's built-in cosine similarity
2. **Embedding generation** - Use LlamaIndex's automatic embedding via Settings.embed_model
3. **Query parsing** - Use LlamaIndex's query engine (handles tokenization, embedding, retrieval)
4. **Result ranking** - Use Qdrant's similarity scores (already optimized)

### ✅ Use Existing

1. **LlamaIndex VectorStoreIndex** - Already configured in Phase 1
2. **Qdrant vector search** - Already storing 551 vectors
3. **HuggingFace embeddings** - Already configured (sentence-transformers/all-MiniLM-L6-v2)
4. **DocumentStore** - Already provides document listing (Phase 1)

## Common Pitfalls

### 1. Index Loading Performance

**Problem:** Creating a new index from scratch on every query is slow.

**Solution:** Load index once and reuse:
```python
# ❌ Bad - recreates index every time
def search(query):
    index = VectorStoreIndex.from_vector_store(vector_store)
    return index.query(query)

# ✅ Good - load once, reuse
class SearchEngine:
    def __init__(self):
        self.index = VectorStoreIndex.from_vector_store(vector_store)
        self.query_engine = self.index.as_query_engine()
    
    def search(self, query):
        return self.query_engine.query(query)
```

### 2. Chinese Text Tokenization

**Problem:** Default tokenizers may not handle Chinese text well.

**Solution:** sentence-transformers/all-MiniLM-L6-v2 already handles Chinese (configured in Phase 1). No additional tokenization needed.

### 3. Empty Query Results

**Problem:** Query returns no results even when relevant documents exist.

**Causes:**
- Query too specific (no semantic match)
- Score threshold too high
- Index not loaded correctly

**Solution:**
```python
# Check index status first
info = vector_store.get_collection_info()
assert info['points_count'] > 0, "Index is empty"

# Lower score threshold for testing
MIN_SCORE = 0.5  # Start permissive, tighten based on results

# Log scores for debugging
for node in response.source_nodes:
    print(f"Score: {node.score}, Text: {node.text[:100]}")
```

### 4. Metadata Loss

**Problem:** Search results don't include document metadata (title, topic, file_type).

**Solution:** Metadata is preserved in Qdrant during indexing (Phase 2). Access via:
```python
for node in response.source_nodes:
    metadata = node.metadata  # Contains file_type, source, etc.
    title = metadata.get('file_name', 'Unknown')
```

### 5. Hybrid Search Complexity

**Problem:** Implementing true hybrid search (semantic + BM25) is complex.

**Solution for v1:** Start with semantic-only search. Add keyword filtering via metadata:
```python
# Simple hybrid: semantic search + metadata filter
results = query_engine.query(
    query_str,
    filters={"file_type": "markdown"}  # Filter by document type
)
```

**Future enhancement:** Use Qdrant's hybrid search feature (requires Qdrant 1.7+):
```python
# Qdrant native hybrid search (future)
from qdrant_client.models import SearchRequest, Prefetch

search_request = SearchRequest(
    query=query_vector,
    prefetch=[
        Prefetch(query=query_vector, using="dense"),
        Prefetch(query=query_text, using="sparse")
    ],
    using="hybrid"
)
```

## Code Examples

### Example 1: Basic Semantic Search

```python
from llama_index.core import VectorStoreIndex
from src.storage.vector_store import HenryVectorStore

class SearchEngine:
    def __init__(self):
        self.vector_store = HenryVectorStore()
        self.index = VectorStoreIndex.from_vector_store(
            self.vector_store.vector_store
        )
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=5,
            response_mode="no_text"  # Return nodes only, no LLM synthesis
        )
    
    def search(self, query: str, top_k: int = 5) -> List[dict]:
        """Semantic search returning top_k results"""
        response = self.query_engine.query(query)
        
        results = []
        for node in response.source_nodes[:top_k]:
            results.append({
                'content': node.text,
                'score': node.score,
                'metadata': node.metadata,
                'document_id': node.node_id
            })
        
        return results
```

### Example 2: Document Listing with Topics

```python
from src.storage.document_store import DocumentStore
from collections import defaultdict

class SearchEngine:
    def __init__(self):
        self.doc_store = DocumentStore("/Users/a1234/wiki/raw/articles")
    
    def list_documents_by_topic(self) -> dict:
        """Group documents by topic"""
        documents = self.doc_store.list_documents()
        
        by_topic = defaultdict(list)
        for doc in documents:
            # Extract topic from filename
            filename = doc.metadata.get('file_name', '')
            topic = self._extract_topic(filename)
            
            by_topic[topic].append({
                'id': doc.doc_id,
                'title': filename,
                'file_type': doc.metadata.get('file_type', 'unknown')
            })
        
        return dict(by_topic)
    
    def _extract_topic(self, filename: str) -> str:
        """Extract topic from filename"""
        filename_lower = filename.lower()
        
        if 'tiktok' in filename_lower:
            return 'TikTok'
        elif 'ai' in filename_lower or 'chatgpt' in filename_lower:
            return 'AI工具'
        elif '财务' in filename_lower or 'finance' in filename_lower:
            return '财务'
        elif '收款' in filename_lower or 'payment' in filename_lower:
            return '收款'
        elif '流量' in filename_lower or 'traffic' in filename_lower:
            return '流量'
        elif '广告' in filename_lower or 'ads' in filename_lower:
            return '广告投放'
        else:
            return '其他'
```

### Example 3: Relevance Filtering

```python
def search_with_filtering(self, query: str, min_score: float = 0.7) -> List[dict]:
    """Search with relevance score filtering"""
    response = self.query_engine.query(query)
    
    # Filter by score threshold
    filtered_results = []
    for node in response.source_nodes:
        if node.score >= min_score:
            filtered_results.append({
                'content': node.text,
                'score': node.score,
                'metadata': node.metadata
            })
    
    # If no results above threshold, return top 3 with warning
    if not filtered_results and response.source_nodes:
        filtered_results = [
            {
                'content': node.text,
                'score': node.score,
                'metadata': node.metadata,
                'warning': 'Low confidence result'
            }
            for node in response.source_nodes[:3]
        ]
    
    return filtered_results
```

## Validation Architecture

### Test Strategy

1. **Unit tests** - SearchEngine class methods
   - `test_search_engine_initialization()`
   - `test_semantic_search_returns_results()`
   - `test_search_with_chinese_query()`
   - `test_relevance_score_filtering()`
   - `test_document_listing()`
   - `test_topic_categorization()`

2. **Integration tests** - End-to-end search quality
   - Query: "TikTok 广告投放最佳时间" → Should return time-related TikTok content
   - Query: "ROI 计算方法" → Should return financial/ROI content
   - Query: "AI 工具推荐" → Should return AI tools content

3. **Quality metrics**
   - Precision@5: Are top 5 results relevant?
   - Score distribution: Are scores meaningful?
   - Chinese text handling: Do Chinese queries work?

### Acceptance Criteria

- [ ] Chinese query "TikTok 广告投放" returns relevant TikTok documents
- [ ] Technical term "ROI" returns exact matches (hybrid search)
- [ ] Results include relevance scores (0.0-1.0 range)
- [ ] Low-score results (<0.7) are filtered or flagged
- [ ] Document list shows all 21 articles
- [ ] Documents grouped by topic (TikTok, AI, 财务, etc.)
- [ ] Search returns results in <2 seconds (performance requirement)

## Security Considerations

### Trust Boundaries

| Boundary | Description | Threat |
|----------|-------------|--------|
| User → SearchEngine | User provides query string | Injection attacks (low risk - no SQL/code execution) |
| SearchEngine → Qdrant | Query vector sent to database | None (local-only) |

### STRIDE Analysis

| Threat ID | Category | Component | Disposition | Mitigation |
|-----------|----------|-----------|-------------|------------|
| T-03-01 | Spoofing | N/A | accept | Single-user system, no authentication needed |
| T-03-02 | Tampering | Query input | accept | No code execution, vector search is read-only |
| T-03-03 | Repudiation | N/A | accept | No audit requirements for v1 |
| T-03-04 | Info Disclosure | Search results | accept | User's own data, local-only access |
| T-03-05 | Denial of Service | Query processing | mitigate | Limit top_k to reasonable value (max 20) |
| T-03-06 | Elevation | N/A | accept | No privilege levels in single-user system |

**Mitigation for T-03-05:**
```python
MAX_TOP_K = 20

def search(self, query: str, top_k: int = 5):
    # Prevent excessive result retrieval
    top_k = min(top_k, MAX_TOP_K)
    # ... rest of search logic
```

## Performance Considerations

### Expected Performance

- **Query latency:** <500ms for semantic search (embedding + vector search)
- **Index loading:** ~1-2 seconds on first load (551 vectors)
- **Memory usage:** ~100MB (embedding model + index)

### Optimization Strategies

1. **Lazy loading** - Load index on first query, not on initialization
2. **Result caching** - Cache frequent queries (future enhancement)
3. **Batch queries** - Process multiple queries in parallel (future enhancement)

### Performance Testing

```python
import time

def test_search_performance():
    engine = SearchEngine()
    
    queries = [
        "TikTok 广告投放",
        "AI 工具推荐",
        "财务规划"
    ]
    
    for query in queries:
        start = time.time()
        results = engine.search(query)
        elapsed = time.time() - start
        
        assert elapsed < 2.0, f"Query too slow: {elapsed}s"
        assert len(results) > 0, "No results returned"
```

## Dependencies

### Upstream (Must Complete First)

- Phase 1 Plan 01: Qdrant vector database ✅
- Phase 2 Plan 01: Document indexing (551 vectors) ✅

### Downstream (Enabled by This Phase)

- Phase 4: RAG Engine Core (uses search results for context)
- Phase 7: Frontend UI - Chat Interface (calls search API)
- Phase 8: Frontend UI - Document Management (uses document listing)

## Open Questions

None - all technical approaches validated against existing infrastructure.

## Research Confidence

**Overall: High (95%)**

- ✅ LlamaIndex query engine pattern is well-documented
- ✅ Qdrant vector search is already working (Phase 1)
- ✅ Chinese text embeddings validated (Phase 2)
- ✅ Document metadata preserved during indexing
- ⚠️ Hybrid search complexity (start with semantic-only, add keyword filtering later)

## References

- LlamaIndex 0.10.x Query Engine: https://docs.llamaindex.ai/en/v0.10.68/module_guides/deploying/query_engine/
- Qdrant Python Client: https://qdrant.tech/documentation/frameworks/llama-index/
- sentence-transformers Chinese support: https://www.sbert.net/docs/pretrained_models.html

---

*Research completed: 2026-04-22*
*Ready for planning: Yes*
