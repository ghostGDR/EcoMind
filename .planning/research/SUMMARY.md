# Project Research Summary

**Project:** Henry - AI 电商专家对话系统
**Domain:** AI Dialogue System with Knowledge Base Management (RAG)
**Researched:** 2026-04-22
**Confidence:** HIGH

## Executive Summary

Henry is a local AI dialogue system that enables natural conversations with an AI expert grounded in a personal knowledge base of e-commerce articles. The system uses Retrieval-Augmented Generation (RAG) to combine semantic search over documents with LLM-powered answer generation, ensuring responses are factual and verifiable.

The recommended approach centers on a **Python backend with FastAPI and LlamaIndex** for RAG orchestration, **Qdrant for vector storage**, and **React + Vite for the frontend**. This stack prioritizes local deployment (all data stays on the user's machine), multilingual support (Chinese/English mixed content), and production-ready performance. The architecture follows a layered pattern: Presentation Layer (Chat/Document UI) → Application Layer (Conversation/Document Management) → RAG Engine Layer (Query Processing/Retrieval/LLM) → Data Layer (Vector Store/Database/File System).

The key risks are **naive chunking strategies that break semantic units** (causing retrieval failures and hallucinations), **unmanaged conversation context windows** (leading to API failures or cost explosions), and **lack of retrieval quality validation** (resulting in confident but incorrect answers). These are mitigated by implementing semantic chunking with overlap, conversation memory management from day one, and a retrieval validation pipeline that scores document relevance before generating answers.

## Key Findings

### Recommended Stack

The stack is optimized for local AI applications with strong privacy guarantees and multilingual support.

**Core technologies:**
- **Python 3.11+ with FastAPI** — Industry standard for AI/ML with 25% performance improvement over 3.10; FastAPI provides async support and automatic API documentation
- **LlamaIndex 0.14.6+** — Purpose-built RAG framework with superior document management compared to LangChain's general-purpose agent approach
- **Qdrant 1.12+** — Highest-performing vector database in benchmarks (2-4x RPS advantage over ChromaDB), excellent filtered search, local deployment support
- **sentence-transformers 3.3+** — Local multilingual embeddings (paraphrase-multilingual-mpnet-base-v2) for Chinese/English text, no API costs, data stays local
- **React 19 + Vite 8** — Modern frontend with blazing-fast HMR and optimized builds
- **SQLite 3.45+** — Lightweight, serverless database for conversation history and metadata
- **Anthropic/OpenAI SDKs** — LLM API clients for Claude (primary) and OpenAI (fallback)

**Critical version requirements:**
- FastAPI 0.115+ requires Pydantic 2.7+ (not compatible with Pydantic v1)
- Vite 8 requires Node.js 20.19+/22.12+ (dropped Node 18 support)
- Python 3.11+ recommended for performance (25% faster than 3.10)

**What NOT to use:**
- FAISS (library, not a database; no CRUD or persistence)
- Pinecone (SaaS-only, violates privacy requirement)
- ChromaDB for production (10x slower filtered search, memory inefficient)
- LangChain for RAG-only use cases (over-engineered, steeper learning curve)

### Expected Features

**Must have (table stakes) — Launch with v1:**
- 对话界面 (Chat Interface) — Core interaction method, users expect natural dialogue
- 语义搜索 (Semantic Search) — AI system standard, keyword search is outdated
- 对话历史 (Conversation History) — Users expect system to "remember" context
- 文档浏览 (Document Browsing) — Knowledge base management foundation
- 来源引用 (Source Citation) — AI answers must be verifiable to avoid hallucinations
- 多轮对话 (Multi-turn Conversation) — Basic dialogue system capability
- 文档上传 (Document Upload) — Users need to add new knowledge
- Markdown 支持 — Standard format for technical documentation

**Should have (competitive) — Add after validation (v1.x):**
- 用户反馈学习 (Feedback Learning) — Continuous optimization, personalized experience
- 对话中教学 (In-conversation Teaching) — Seamlessly supplement knowledge without switching interfaces (unique differentiator)
- 混合检索 (Hybrid Retrieval) — Combine semantic + keyword search for robustness
- 智能分块 (Smart Chunking) — Improve retrieval accuracy with semantic boundaries
- 实时文件监控 (Real-time File Watching) — Auto-sync external knowledge base changes
- Excel 文件支持 — Handle structured data (financial tables, etc.)
- 上下文窗口管理 (Context Window Management) — Optimize long conversation performance

**Defer (v2+):**
- 多模态检索 (Multi-modal Retrieval) — Image/chart support (high complexity)
- 个性化回答风格 (Personalized Response Style) — Requires significant user data
- 多用户协作 (Multi-user Collaboration) — Single-user value not yet validated
- 语音对话 (Voice Chat) — Text dialogue is sufficient, voice is nice-to-have

**Competitive advantages:**
1. 对话中教学 — Unique feature, seamless knowledge supplementation
2. 强制来源引用 — Ensures verifiable answers, builds trust
3. 本地运行 + 完全隐私 — Business knowledge is sensitive, data never leaves local machine
4. 实时文件监控 — Auto-sync with external knowledge base changes

### Architecture Approach

The system follows a **four-layer RAG architecture** with clear separation of concerns:

**Major components:**
1. **Presentation Layer** — Chat UI, Document UI, History UI (React components with WebSocket/SSE for streaming)
2. **Application Layer** — Conversation Manager (session + context), Document Manager (CRUD + file watching), Feedback Manager (collection + storage)
3. **RAG Engine Layer** — Query Processor (enhancement), Retriever (semantic search), LLM Interface (API client with streaming)
4. **Data Layer** — Vector Store (embeddings), Conversation Database (history), File System Watcher (real-time sync)

**Key architectural patterns:**
- **RAG Pipeline:** Query → Retrieve relevant docs → Build context → Generate answer with LLM → Return with source citations
- **Conversational Memory:** Manage multi-turn context with sliding window or summarization to stay within token limits
- **Document Chunking with Overlap:** Split documents into 500-1500 character chunks with 100-300 character overlap to preserve context
- **File System Watcher:** Monitor `/Users/a1234/wiki/raw/articles` for changes, trigger incremental re-indexing

**Data flows:**
- **Query flow:** User question → Load conversation history → Enhance query with context → Vector search → Rerank results → Build prompt → Stream LLM response → Save to history
- **Indexing flow:** File change detected → Read content → Parse (Markdown/Excel) → Chunk with overlap → Generate embeddings → Store in vector DB → Update metadata
- **Feedback flow:** User feedback → Store with conversation_id + message_id → Link to source documents → Analyze for improvement opportunities

### Critical Pitfalls

**Top 5 pitfalls that cause rewrites or major issues:**

1. **Naive Chunking Strategy Leading to Context Loss** — Fixed-size chunking breaks semantic units mid-sentence, causing retrieval to return incomplete context and LLM to hallucinate. **Prevention:** Use semantic chunking that respects document structure (paragraphs, sections), test that each chunk can stand alone, add contextual headers (document title, section name).

2. **Ignoring Conversation Context Window Limits** — Storing full conversation history without management causes context overflow, API failures, or silent truncation after 10-20 turns. **Prevention:** Implement sliding window (keep last N turns) or summarization (compress old turns) from day one, monitor token usage, store full history in DB but send only relevant context to LLM.

3. **No Retrieval Quality Validation (Blind Trust in Vector Search)** — Assuming vector similarity always returns relevant documents leads to confident but incorrect answers when retrieval fails. **Prevention:** Implement Corrective RAG pattern with relevance scoring (>0.7 = use docs, <0.3 = fallback, 0.3-0.7 = combine sources), add faithfulness evaluation, log retrieval scores.

4. **Single Retrieval Strategy (No Hybrid Search)** — Relying solely on semantic search misses exact keyword matches for domain-specific terms (TikTok Shop, 跨境电商, product names). **Prevention:** Implement fusion retrieval (vector + BM25 keyword search) from the start, weight keyword search higher for quoted phrases and technical terms.

5. **Ignoring Chinese Text Segmentation Issues** — Chinese has no spaces between words; naive tokenization breaks semantic units like "跨境电商" into meaningless fragments, degrading embedding quality. **Prevention:** Use Chinese-aware tokenization (jieba), choose embedding models trained on Chinese text (paraphrase-multilingual-mpnet-base-v2), test with Chinese queries during development.

**Additional critical concerns:**
- **No Answer Source Attribution** — Users can't verify answers or trace errors back to source documents. Always return document citations with confidence scores.
- **Static Knowledge Base** — Without incremental indexing, knowledge base becomes stale. Implement file system watching for real-time updates.
- **Poor Error Handling for Missing Information** — Distinguish between "retrieval found nothing" vs "information missing from knowledge base" with confidence thresholds.

## Implications for Roadmap

Based on research, suggested phase structure follows dependency order and risk mitigation:

### Phase 1: Data Layer Foundation
**Rationale:** All upper layers depend on data storage; must establish persistence before building features
**Delivers:** Vector store setup (Qdrant), conversation database (SQLite), document storage interface
**Addresses:** Infrastructure for semantic search, conversation history, document management
**Avoids:** Building features without persistence layer (Pitfall: no conversation history persistence)
**Research flag:** Standard patterns, skip research-phase

### Phase 2: Knowledge Base Indexing
**Rationale:** Need to load and process documents before retrieval can work; critical to get chunking right early
**Delivers:** Document parsing (Markdown/Excel), semantic chunking with overlap, embedding generation, initial indexing pipeline
**Addresses:** Document upload, Markdown support (table stakes features)
**Avoids:** Naive chunking (Pitfall #1), Chinese text segmentation issues (Pitfall #5), Markdown/Excel parsing issues (Pitfall #14)
**Research flag:** Needs research for Chinese text handling and Excel parsing strategies

### Phase 3: Semantic Search Implementation
**Rationale:** Core RAG capability; must validate retrieval quality before building conversation layer
**Delivers:** Vector similarity search, hybrid retrieval (vector + BM25), retrieval validation with confidence scoring, reranking
**Addresses:** Semantic search (table stakes), hybrid retrieval (differentiator)
**Avoids:** Single retrieval strategy (Pitfall #4), no retrieval quality validation (Pitfall #3), inadequate reranking (Pitfall #7)
**Research flag:** Needs research for hybrid search implementation and reranking strategies

### Phase 4: RAG Engine Core
**Rationale:** Integrate retrieval with LLM to generate answers; validate end-to-end RAG pipeline
**Delivers:** Query processor, LLM interface (Claude/OpenAI), prompt engineering, answer generation with source attribution
**Addresses:** Source citation (table stakes), answer quality
**Avoids:** No answer source attribution (Pitfall #6), poor error handling for missing information (Pitfall #9)
**Research flag:** Standard RAG patterns, skip research-phase

### Phase 5: Conversation Management
**Rationale:** Add multi-turn capability once single-turn RAG works; critical to implement context management early
**Delivers:** Conversation session management, context window management (sliding window/summarization), conversation history persistence
**Addresses:** Conversation history, multi-turn conversation (table stakes)
**Avoids:** Context window overflow (Pitfall #2), no conversation history persistence (Pitfall #12)
**Research flag:** Needs research for context compression strategies

### Phase 6: Backend API Layer
**Rationale:** Expose RAG engine and conversation management via API for frontend integration
**Delivers:** FastAPI endpoints (REST + WebSocket/SSE), request validation, error handling, streaming responses
**Addresses:** API infrastructure for frontend
**Avoids:** Synchronous blocking (use async FastAPI)
**Research flag:** Standard patterns, skip research-phase

### Phase 7: Frontend UI - Chat Interface
**Rationale:** Build primary user interface once backend API is stable
**Delivers:** Chat UI with message history, input box, streaming response display, source citation display
**Addresses:** Chat interface (table stakes), source citation display
**Avoids:** Poor UX for streaming responses
**Research flag:** Standard patterns, skip research-phase

### Phase 8: Frontend UI - Document Management
**Rationale:** Add document browsing and upload after core chat functionality works
**Delivers:** Document browser, upload interface, search/filter, topic classification
**Addresses:** Document browsing, document upload (table stakes), topic classification
**Avoids:** Synchronous blocking during upload (use async indexing)
**Research flag:** Standard patterns, skip research-phase

### Phase 9: Real-time Knowledge Base Updates
**Rationale:** Automate document sync once manual upload works; prevents knowledge base staleness
**Delivers:** File system watcher for `/Users/a1234/wiki/raw/articles`, incremental indexing, change detection
**Addresses:** Real-time file watching (differentiator)
**Avoids:** Static knowledge base (Pitfall #8), synchronous blocking during indexing (Pitfall #5 from PITFALLS.md)
**Research flag:** Needs research for file watching patterns and incremental indexing

### Phase 10: User Feedback & Learning
**Rationale:** Collect feedback to improve system over time; enables continuous optimization
**Delivers:** Feedback UI (thumbs up/down, comments), feedback storage, feedback analysis
**Addresses:** User feedback learning (differentiator)
**Avoids:** Inadequate feedback loop (Pitfall #13)
**Research flag:** Standard patterns, skip research-phase

### Phase 11: Performance Optimization
**Rationale:** Optimize after core features work; address bottlenecks identified during usage
**Delivers:** Performance monitoring, query caching, batch embedding generation, response time optimization
**Addresses:** Performance requirements (<2s response time)
**Avoids:** No performance monitoring (Pitfall #15), inefficient embedding generation (Pitfall #11)
**Research flag:** Standard patterns, skip research-phase

### Phase Ordering Rationale

- **Data layer first** because all features depend on persistence (vector store, database, file system)
- **Indexing before retrieval** because you can't search documents that haven't been processed
- **Retrieval before conversation** because single-turn RAG must work before adding multi-turn complexity
- **Backend API before frontend** because UI needs stable API endpoints
- **Core features before optimization** because premature optimization wastes effort
- **Feedback system last** because it requires working chat functionality to collect meaningful data

**Dependency chain:**
```
Phase 1 (Data Layer) 
  → Phase 2 (Indexing) 
    → Phase 3 (Search) 
      → Phase 4 (RAG Engine) 
        → Phase 5 (Conversation) 
          → Phase 6 (API) 
            → Phase 7 (Chat UI) 
            → Phase 8 (Document UI)
              → Phase 9 (Real-time Updates)
              → Phase 10 (Feedback)
                → Phase 11 (Optimization)
```

### Research Flags

**Phases needing deeper research during planning:**
- **Phase 2 (Knowledge Base Indexing):** Chinese text segmentation strategies, Excel parsing for structured data, optimal chunk sizes for mixed Chinese/English content
- **Phase 3 (Semantic Search):** Hybrid search implementation (vector + BM25 fusion), reranking algorithms, confidence scoring thresholds
- **Phase 5 (Conversation Management):** Context compression strategies (sliding window vs summarization), token counting for mixed Chinese/English text
- **Phase 9 (Real-time Updates):** File system watching patterns (watchdog library), incremental indexing strategies, handling concurrent file changes

**Phases with standard patterns (skip research-phase):**
- **Phase 1 (Data Layer):** Well-documented Qdrant and SQLite setup
- **Phase 4 (RAG Engine):** Standard LlamaIndex patterns for query engines
- **Phase 6 (Backend API):** Standard FastAPI patterns for REST + WebSocket
- **Phase 7-8 (Frontend UI):** Standard React patterns for chat and document interfaces
- **Phase 10 (Feedback):** Standard CRUD patterns for feedback collection
- **Phase 11 (Optimization):** Standard profiling and caching patterns

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All core technologies verified via Context7 official documentation with version numbers; performance benchmarks from official sources |
| Features | HIGH | Feature landscape based on authoritative RAG sources (Context7 rag_techniques, LangChain docs) and competitor analysis |
| Architecture | HIGH | Architecture patterns from LangChain official tutorials, ChromaDB cookbook, and high-reputation RAG implementations (haiku.rag) |
| Pitfalls | HIGH | Critical pitfalls (1-6) well-documented in authoritative sources; moderate/minor pitfalls based on standard RAG best practices |

**Overall confidence:** HIGH

### Gaps to Address

**During planning/execution:**
- **Chinese-English mixed text handling:** Limited specific guidance in RAG literature; will need experimentation with tokenization and embedding models during Phase 2
- **Excel file handling in RAG:** Less documented than Markdown; will need to test table preservation strategies during Phase 2
- **Optimal chunk sizes for domain:** Research suggests 500-1500 characters with 100-300 overlap, but optimal values depend on document structure; validate with actual 22 articles during Phase 2
- **Context window management strategy:** Multiple approaches (sliding window, summarization, semantic compression); choose based on conversation length patterns observed during Phase 5
- **Retrieval confidence thresholds:** Research suggests 0.7 (high), 0.3 (low) as thresholds, but optimal values are dataset-dependent; calibrate during Phase 3 testing

**Validation strategy:**
- Test chunking strategies with actual 22 articles during Phase 2 (don't rely on generic recommendations)
- Validate Chinese text handling with real queries during Phase 3 (ensure semantic search works for Chinese synonyms)
- Monitor conversation context usage in Phase 5 to validate memory management approach (measure token usage patterns)
- Collect user feedback in Phase 10 to identify domain-specific pitfalls not covered in research

## Sources

### Primary (HIGH confidence)
- **LlamaIndex:** Context7 `/websites/developers_llamaindex_ai_python` — RAG framework, v0.14.6, query engines, document management
- **LangChain:** Context7 `/websites/langchain` — RAG tutorials, conversation memory patterns, retrieval chains
- **Qdrant:** Context7 `/qdrant/qdrant-client` — Vector database client, local mode, performance benchmarks
- **FastAPI:** Context7 `/fastapi/fastapi` — Web framework, v0.115+, async patterns
- **RAG Techniques:** Context7 `/nirdiamant/rag_techniques` — Chunking strategies, evaluation, retrieval patterns, pitfalls
- **ChromaDB Cookbook:** Context7 `/websites/cookbook_chromadb_dev` — Vector store patterns, embedding strategies
- **Haiku RAG:** Context7 `/ggozad/haiku.rag` — High-reputation RAG architecture (82.57 benchmark score)
- **Anthropic SDK:** Context7 `/anthropics/anthropic-sdk-python` — Claude API client
- **React:** Context7 `/facebook/react` — v19.2.0, frontend framework
- **Vite:** Context7 `/vitejs/vite` — v8.0.7, build tool
- **sentence-transformers:** Context7 `/huggingface/sentence-transformers` — v3.3+, multilingual embeddings

### Secondary (MEDIUM confidence)
- **Qdrant vs ChromaDB performance:** Qdrant official benchmarks (https://qdrant.tech/benchmarks/) — 2-4x RPS advantage, better filtered search
- **Conversation Memory:** Context7 `/ofershap/conversation-memory` — Conversation history management patterns
- **RAG anti-patterns:** RAG Techniques GitHub repository (26.9k stars) — Common failure modes and prevention strategies

### Tertiary (LOW confidence)
- **Chinese text processing in RAG:** Inferred from general NLP best practices; limited specific guidance in English-centric RAG tutorials
- **Excel handling in RAG:** Implementation patterns vary; less documented than Markdown processing

---
*Research completed: 2026-04-22*
*Ready for roadmap: yes*
