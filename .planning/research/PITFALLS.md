# Domain Pitfalls

**Domain:** AI 对话系统和知识库管理 (AI Dialogue Systems and Knowledge Base Management)
**Researched:** 2026-04-22

## Critical Pitfalls

Mistakes that cause rewrites or major issues.

### Pitfall 1: Naive Chunking Strategy Leading to Context Loss
**What goes wrong:** Using fixed-size chunking (e.g., every 500 characters) without considering semantic boundaries breaks logical units mid-sentence or mid-concept. This causes the retrieval system to return incomplete or misleading context, leading to hallucinations and incorrect answers.

**Why it happens:** Developers default to simple character-based or token-based splitting because it's easy to implement. They underestimate how much semantic coherence matters for retrieval quality.

**Consequences:** 
- Retrieved chunks lack necessary context to answer questions accurately
- LLM generates answers based on incomplete information (hallucinations)
- User trust erodes when answers contradict the source material
- Requires complete re-indexing and re-chunking of entire knowledge base

**Prevention:** 
- Use semantic chunking that respects document structure (paragraphs, sections, logical units)
- Implement proposition-based chunking where each chunk represents a complete, self-contained idea
- Test chunk quality: can each chunk stand alone and be understood without surrounding context?
- Add contextual headers to chunks (document title, section name) to preserve hierarchy
- Experiment with chunk sizes (256, 512, 1024 tokens) and measure retrieval quality metrics (faithfulness, relevancy)

**Detection:** 
- User feedback indicates answers are "incomplete" or "missing context"
- Manual inspection shows chunks ending mid-sentence or mid-concept
- Evaluation metrics show low faithfulness scores (answer doesn't match retrieved context)
- Retrieved chunks require reading 3+ neighboring chunks to understand meaning

**Phase mapping:** Address in Phase 2-3 (Knowledge Base Indexing/Semantic Search Implementation)

---

### Pitfall 2: Ignoring Conversation Context Window Limits
**What goes wrong:** Storing full conversation history without management causes context window overflow. The system either crashes, truncates critical context silently, or becomes prohibitively expensive as conversations grow beyond 10-20 turns.

**Why it happens:** Developers focus on "remembering everything" without considering token limits (Claude: 200K tokens, but practical limits are lower for cost/latency). They don't implement conversation summarization or context pruning strategies.

**Consequences:**
- API calls fail with context length errors after extended conversations
- Silent truncation drops early conversation turns, causing the AI to "forget" user preferences or earlier instructions
- Costs spiral as every message includes full history (10-turn conversation = 10x token usage)
- Response latency increases dramatically with conversation length

**Prevention:**
- Implement conversation memory management from day one:
  - Sliding window: keep last N turns + system prompt
  - Summarization: compress old turns into summary, keep recent turns verbatim
  - Semantic compression: extract key facts/decisions, discard conversational filler
- Monitor token usage per request and set alerts at 80% of context limit
- Store full history in database but send only relevant context to LLM
- Use conversation memory patterns: extract decisions, code changes, conclusions rather than raw transcripts

**Detection:**
- API errors mentioning "context_length_exceeded" or "maximum context length"
- Response quality degrades in longer conversations (AI "forgets" earlier context)
- Token usage grows linearly with conversation length
- Users report "the AI forgot what we discussed earlier"

**Phase mapping:** Address in Phase 4-5 (Conversation Management/Multi-turn Dialogue)

---

### Pitfall 3: No Retrieval Quality Validation (Blind Trust in Vector Search)
**What goes wrong:** Assuming vector similarity search always returns relevant documents. In reality, semantically similar embeddings don't guarantee factual relevance. The system retrieves plausible-sounding but incorrect documents, and the LLM confidently generates wrong answers.

**Why it happens:** Developers treat vector search as a "black box" that magically works. They skip the validation layer that checks whether retrieved documents actually answer the query.

**Consequences:**
- System returns confident but incorrect answers (worst failure mode for user trust)
- No way to detect when retrieval fails until users complain
- LLM hallucinates based on irrelevant retrieved context
- Cannot distinguish between "no relevant information" vs "wrong information retrieved"

**Prevention:**
- Implement retrieval validation pipeline (Corrective RAG pattern):
  - Score each retrieved document for relevance (0-1 scale)
  - If max score > 0.7: use retrieved docs
  - If max score < 0.3: trigger fallback (web search, or "I don't have information on this")
  - If 0.3-0.7: combine retrieval + web search or ask clarifying questions
- Add faithfulness evaluation: does the generated answer derive from retrieved context?
- Implement explainable retrieval: highlight which document segments were used
- Log retrieval scores and review low-confidence cases

**Detection:**
- User feedback: "This answer doesn't match my documents"
- Manual spot-checks reveal retrieved documents don't match query intent
- Faithfulness evaluation scores below 0.5
- High variance in answer quality for similar questions

**Phase mapping:** Address in Phase 3 (Semantic Search Implementation) and Phase 6 (Answer Quality Validation)

---

### Pitfall 4: Single Retrieval Strategy (No Hybrid Search)
**What goes wrong:** Relying solely on semantic (vector) search misses exact keyword matches. For domain-specific terms (e.g., "TikTok Shop", "跨境电商", product names, technical jargon), semantic search may fail while keyword search succeeds. Users ask about specific terms and get generic answers.

**Why it happens:** Developers implement vector search first (it's trendy) and assume it handles all cases. They don't realize semantic embeddings struggle with rare terms, acronyms, and exact phrases.

**Consequences:**
- Queries with specific terminology return irrelevant results
- Cannot find documents containing exact product names, technical terms, or domain jargon
- User frustration: "I know this is in my documents, why can't you find it?"
- Particularly severe for Chinese text with mixed English terms (common in e-commerce domain)

**Prevention:**
- Implement fusion retrieval (hybrid search) from the start:
  - Vector search for semantic similarity
  - BM25/keyword search for exact term matching
  - Combine results using Reciprocal Rank Fusion (RRF)
- Weight keyword search higher for queries containing:
  - Quoted phrases ("TikTok Shop")
  - Technical terms, product names, acronyms
  - Mixed Chinese-English text
- Test with domain-specific terminology during development

**Detection:**
- Queries with specific terms (product names, technical jargon) return poor results
- Users resort to exact phrase matching in their queries
- Keyword search alone outperforms vector search on certain query types
- Low recall on queries containing rare or domain-specific terms

**Phase mapping:** Address in Phase 3 (Semantic Search Implementation)

---

### Pitfall 5: Ignoring Chinese Text Segmentation Issues
**What goes wrong:** Chinese text has no spaces between words. Using character-level or naive tokenization breaks semantic units. Embeddings and search quality suffer because "跨境电商" (cross-border e-commerce) gets split into meaningless character fragments.

**Why it happens:** Developers use English-centric NLP tools without considering Chinese linguistic properties. They assume tokenization "just works" across languages.

**Consequences:**
- Poor embedding quality for Chinese text (semantic meaning lost)
- Search fails to match synonyms or related concepts
- Mixed Chinese-English text (common in e-commerce) causes additional problems
- Chunking breaks in the middle of Chinese words/phrases

**Prevention:**
- Use Chinese-aware tokenization (jieba, pkuseg, or LLM-based tokenizers)
- Choose embedding models trained on Chinese text:
  - OpenAI text-embedding-3 (multilingual, good for mixed content)
  - Chinese-specific models if monolingual
- Test with Chinese queries during development
- Handle mixed Chinese-English text explicitly (common in your domain: "TikTok", "AI", "ROI")
- Validate that semantic search works for Chinese synonyms and related terms

**Detection:**
- Chinese queries return worse results than English queries
- Manual inspection shows embeddings don't capture Chinese semantic meaning
- Search fails to match obvious synonyms in Chinese
- Chunking splits Chinese phrases awkwardly

**Phase mapping:** Address in Phase 2 (Knowledge Base Indexing) and Phase 3 (Semantic Search)

---

### Pitfall 6: No Answer Source Attribution
**What goes wrong:** System generates answers without citing which documents were used. Users cannot verify accuracy, and when answers are wrong, there's no way to trace the problem back to source documents or retrieval failures.

**Why it happens:** Developers focus on answer generation and treat retrieval as an internal implementation detail. They don't surface source attribution to users.

**Consequences:**
- Zero transparency: users can't verify answers against source material
- Cannot debug why wrong answers were generated
- Users don't trust the system (black box problem)
- No way to identify which documents need updating when answers are outdated
- Liability issues if system gives wrong business advice

**Prevention:**
- Always return source citations with answers:
  - Document title/filename
  - Relevant excerpt/chunk that was used
  - Confidence score for each source
- Implement explainable retrieval: highlight exact text segments used
- Show retrieval scores to indicate confidence
- Allow users to click through to full source documents
- Log which documents were retrieved for each query (debugging)

**Detection:**
- Users ask "where did this information come from?"
- Cannot trace wrong answers back to source
- Debugging requires re-running queries manually
- Users don't trust answers without verification

**Phase mapping:** Address in Phase 6 (Answer Quality & Source Attribution)

---

## Moderate Pitfalls

### Pitfall 7: Inadequate Reranking After Retrieval
**What goes wrong:** Vector search returns top-K documents by similarity, but similarity ≠ relevance. The most similar document might not be the most useful for answering the query. Without reranking, lower-quality documents get sent to the LLM.

**Why it happens:** Developers stop after vector search, assuming top-K results are good enough. They don't add a reranking layer to refine results.

**Prevention:**
- Implement two-stage retrieval:
  - Stage 1: Vector search retrieves top-20 candidates (high recall)
  - Stage 2: Reranker scores candidates for query relevance, returns top-5 (high precision)
- Use cross-encoder rerankers (more accurate than bi-encoders for ranking)
- Consider LLM-based reranking for complex queries
- Measure improvement: compare answer quality with/without reranking

**Detection:**
- Top-1 retrieved document is often not the most relevant
- Manual review shows better documents ranked lower
- Answer quality improves when you manually reorder retrieved documents

**Phase mapping:** Address in Phase 3 (Semantic Search) or Phase 7 (Optimization)

---

### Pitfall 8: Static Knowledge Base (No Update Strategy)
**What goes wrong:** Knowledge base becomes stale as documents are added, updated, or deleted. The system continues to reference outdated information or misses new content. Users lose trust when answers don't reflect recent changes.

**Why it happens:** Developers build initial indexing but don't implement incremental updates. Re-indexing the entire knowledge base on every change is too slow/expensive.

**Prevention:**
- Implement file system watching for document changes (requirement: monitor `/Users/a1234/wiki/raw/articles`)
- Incremental indexing: only re-process changed documents
- Version control for documents: track when each document was last indexed
- Periodic full re-indexing (weekly/monthly) to catch missed changes
- Show users when knowledge base was last updated
- Handle document deletion: remove from vector store and metadata

**Detection:**
- Users report answers don't reflect recent document updates
- System references deleted documents
- New documents don't appear in search results
- Timestamp checks show indexed content is outdated

**Phase mapping:** Address in Phase 8 (Real-time Knowledge Base Updates)

---

### Pitfall 9: Poor Error Handling for Missing Information
**What goes wrong:** When the knowledge base doesn't contain information to answer a query, the system either hallucinates an answer or returns a generic "I don't know" without guidance. Users don't know if the information is missing or if the search failed.

**Why it happens:** Developers don't distinguish between "retrieval found nothing" vs "retrieval found irrelevant results" vs "information genuinely missing from knowledge base."

**Prevention:**
- Implement confidence thresholds:
  - High confidence (>0.7): answer directly
  - Medium confidence (0.3-0.7): answer with caveats, show sources
  - Low confidence (<0.3): "I don't have information on this in your knowledge base"
- Suggest related topics when information is missing
- Allow users to add missing information directly (requirement: teach Henry new knowledge)
- Log unanswerable queries to identify knowledge gaps

**Detection:**
- Users report hallucinated answers for out-of-scope questions
- Generic "I don't know" responses frustrate users
- No way to distinguish search failure from missing information

**Phase mapping:** Address in Phase 6 (Answer Quality Validation)

---

### Pitfall 10: Ignoring Query Intent Classification
**What goes wrong:** Treating all queries the same way. Some queries need factual retrieval ("What is TikTok Shop?"), others need reasoning ("Should I invest in TikTok ads?"), and others need clarification ("Tell me about AI"). Without intent classification, the system uses the wrong strategy.

**Why it happens:** Developers build one-size-fits-all retrieval pipeline without considering query diversity.

**Prevention:**
- Classify query intent before retrieval:
  - Factual: direct retrieval + extraction
  - Analytical: retrieval + reasoning + synthesis
  - Clarification needed: ask follow-up questions
  - Out of scope: politely decline
- Use different retrieval strategies per intent type
- Implement query transformation (rewriting, decomposition) for complex queries

**Detection:**
- Simple factual queries get over-complicated answers
- Complex analytical queries get shallow factual responses
- Users need to rephrase questions multiple times

**Phase mapping:** Address in Phase 5 (Multi-turn Dialogue) or Phase 7 (Optimization)

---

## Minor Pitfalls

### Pitfall 11: Inefficient Embedding Generation
**What goes wrong:** Generating embeddings synchronously for every query causes latency spikes. Batch embedding generation during indexing is not optimized, making knowledge base updates slow.

**Why it happens:** Developers use naive API calls without batching or caching.

**Prevention:**
- Batch embed documents during indexing (process 100+ at once)
- Cache query embeddings for common questions
- Use async embedding generation to avoid blocking
- Consider local embedding models for lower latency (trade-off: accuracy)

**Detection:**
- Query response time dominated by embedding generation
- Indexing new documents takes excessively long
- API rate limits hit during batch operations

**Phase mapping:** Address in Phase 7 (Performance Optimization)

---

### Pitfall 12: No Conversation History Persistence
**What goes wrong:** Conversation history is lost when the user closes the browser or restarts the application. Users cannot review past conversations or continue previous discussions.

**Why it happens:** Developers store conversation state in memory only, without database persistence.

**Prevention:**
- Persist conversation history to database from the start
- Implement conversation threading (group related conversations)
- Allow users to search and resume past conversations
- Store conversation metadata (date, topic, summary)

**Detection:**
- Users complain about losing conversation history
- Cannot review past interactions
- No way to continue previous conversations

**Phase mapping:** Address in Phase 4 (Conversation Management)

---

### Pitfall 13: Inadequate Feedback Loop
**What goes wrong:** Users cannot provide feedback on answer quality. The system has no mechanism to learn from mistakes or improve over time based on user corrections.

**Why it happens:** Developers focus on initial functionality without building feedback and learning mechanisms.

**Prevention:**
- Implement feedback UI: thumbs up/down, detailed comments
- Store feedback with query-answer pairs for analysis
- Use feedback to identify problematic documents or retrieval failures
- Implement active learning: prioritize improving answers with negative feedback
- Show users how their feedback improves the system

**Detection:**
- No data on answer quality from user perspective
- Cannot identify systematic problems
- Users have no way to correct wrong answers

**Phase mapping:** Address in Phase 9 (User Feedback & Learning)

---

### Pitfall 14: Markdown and Excel Parsing Issues
**What goes wrong:** Naive parsing loses document structure. Tables in Markdown become unreadable text. Excel files are treated as plain text, losing cell relationships and formulas.

**Why it happens:** Developers use generic text extraction without format-specific parsing.

**Prevention:**
- Use format-specific parsers:
  - Markdown: preserve headers, lists, tables, code blocks
  - Excel: extract tables with cell relationships, handle multiple sheets
- Maintain document structure in chunks (don't break tables mid-row)
- Test with actual documents from knowledge base (22 articles including Excel)

**Detection:**
- Tables are unreadable in retrieved chunks
- Excel data loses meaning when converted to text
- Document structure is lost in search results

**Phase mapping:** Address in Phase 2 (Knowledge Base Indexing)

---

### Pitfall 15: No Performance Monitoring
**What goes wrong:** System performance degrades over time as knowledge base grows, but there's no visibility into bottlenecks. Response times increase, but developers don't know if it's retrieval, embedding, or LLM generation.

**Why it happens:** Developers don't instrument the system with performance metrics.

**Prevention:**
- Log timing for each pipeline stage:
  - Query embedding generation
  - Vector search
  - Reranking
  - LLM generation
- Monitor token usage and costs
- Track knowledge base size and query volume
- Set performance budgets (e.g., <2s response time requirement)
- Alert on performance degradation

**Detection:**
- Users complain about slow responses
- Cannot identify performance bottlenecks
- No data to guide optimization efforts

**Phase mapping:** Address in Phase 7 (Performance Optimization)

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Knowledge Base Indexing | Naive chunking breaks semantic units | Use semantic chunking, test with actual documents |
| Semantic Search | Vector search alone misses exact matches | Implement hybrid search (vector + keyword) |
| Semantic Search | Chinese text segmentation issues | Use Chinese-aware tokenization and embeddings |
| Conversation Management | Context window overflow in long conversations | Implement conversation memory management early |
| Multi-turn Dialogue | Losing conversation context between turns | Persist conversation history, implement context compression |
| Answer Quality | No retrieval validation | Implement Corrective RAG pattern with confidence scoring |
| Answer Quality | Missing source attribution | Always return document citations with answers |
| User Feedback | No feedback mechanism | Build feedback UI and storage from the start |
| Real-time Updates | Static knowledge base becomes stale | Implement file system watching and incremental indexing |
| Performance | No visibility into bottlenecks | Instrument all pipeline stages with timing metrics |

---

## Sources

**HIGH Confidence:**
- Context7 RAG Techniques: /nirdiamant/rag_techniques (chunking strategies, evaluation, retrieval patterns)
- Context7 LangChain: /websites/langchain (conversation memory, context management)
- Context7 Conversation Memory: /ofershap/conversation-memory (conversation history management patterns)

**MEDIUM Confidence:**
- RAG Techniques GitHub repository (comprehensive RAG patterns and anti-patterns)
- LangChain documentation (memory management best practices)

**Domain-Specific Insights:**
- Chinese text processing requires language-aware tokenization (not covered in most English-centric RAG tutorials)
- E-commerce domain (TikTok, 跨境电商) has mixed Chinese-English terminology requiring special handling
- Local deployment requirement (privacy) rules out cloud-based solutions
- Single-user system simplifies some concerns (no multi-tenancy) but doesn't eliminate core RAG pitfalls

**Research Gaps:**
- Limited specific guidance on Chinese-English mixed text handling in RAG systems (LOW confidence on optimal approaches)
- Excel file handling in RAG pipelines less documented than Markdown (MEDIUM confidence)
- Real-time file system monitoring for knowledge base updates (implementation patterns vary)

---

## Validation Notes

This research is based on:
1. **Authoritative sources**: Context7 documentation for RAG techniques, LangChain, conversation memory
2. **Domain analysis**: Project requirements (Chinese e-commerce knowledge base, local deployment, 22 articles)
3. **Common RAG failure modes**: Documented in RAG Techniques repository (26.9k stars, actively maintained)

**Confidence Assessment:**
- Critical pitfalls (1-6): HIGH confidence - well-documented in authoritative sources
- Moderate pitfalls (7-10): HIGH confidence - standard RAG best practices
- Minor pitfalls (11-15): MEDIUM confidence - implementation-dependent

**Recommended Validation:**
- Test chunking strategies with actual 22 articles during Phase 2
- Validate Chinese text handling with real queries during Phase 3
- Monitor conversation context usage in Phase 4-5 to validate memory management approach
- Collect user feedback in Phase 9 to identify domain-specific pitfalls not covered here
