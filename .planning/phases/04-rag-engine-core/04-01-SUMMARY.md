---
phase: 04-rag-engine-core
plan: 01
subsystem: llm
tags: [llm, openai, anthropic, persona, prompts]
completed: 2026-04-22T06:54:09Z
duration_seconds: 185

dependency_graph:
  requires:
    - Phase 03 semantic search (SearchEngine with hybrid search)
  provides:
    - LLMClient abstraction for OpenAI/Anthropic
    - Henry's e-commerce expert persona prompts
    - RAG prompt template with context/query placeholders
  affects:
    - Phase 04 Plan 02 (RAG query engine will use LLMClient)
    - Phase 04 Plan 03 (chat API will use Henry's persona)

tech_stack:
  added:
    - openai>=1.0.0 (LLM API client)
    - anthropic>=0.18.0 (LLM API client)
  patterns:
    - Provider abstraction pattern for multi-LLM support
    - Environment-based configuration for API keys
    - Graceful error handling for external API failures

key_files:
  created:
    - src/llm/__init__.py (module exports)
    - src/llm/llm_client.py (LLMClient class - 80 lines)
    - src/llm/prompts.py (Henry persona and RAG template - 30 lines)
    - tests/test_llm_client.py (5 test cases - 77 lines)
    - .env.example (API key configuration template)
  modified:
    - requirements.txt (added openai and anthropic dependencies)

decisions:
  - decision: Use OpenAI gpt-4o-mini as default model
    rationale: Cost-effective ($0.15/1M tokens vs GPT-4 $30/1M), sufficient quality for RAG synthesis, fast response (<2s)
    alternatives_considered: GPT-4 (too expensive), local models (user requires cloud API per PROJECT.md)
  
  - decision: Support both OpenAI and Anthropic providers
    rationale: Flexibility for user to choose provider, PROJECT.md mentions "Claude/OpenAI"
    alternatives_considered: OpenAI-only (simpler but less flexible)
  
  - decision: Chinese language for Henry's system prompt
    rationale: User's wiki is 22 Chinese articles, target users are Chinese-speaking e-commerce professionals
    alternatives_considered: English (doesn't match user's content language)
  
  - decision: Explicit citation requirement in system prompt
    rationale: SEARCH-02 requirement "引用具体的来源文章和段落", prevents hallucination
    alternatives_considered: Implicit citation (less reliable)

metrics:
  lines_of_code: 187
  test_coverage: 5 tests (all passing)
  files_created: 5
  files_modified: 1
  commits: 2 (RED + GREEN for TDD)
---

# Phase 04 Plan 01: LLM Integration and Henry's Persona Summary

**One-liner:** OpenAI/Anthropic LLM client with Chinese e-commerce expert persona and citation-enforced RAG prompts

## What Was Built

Established LLM integration foundation for RAG-based answer generation:

1. **LLMClient abstraction** - Unified interface for OpenAI and Anthropic APIs with provider switching, temperature control, and graceful error handling
2. **Henry's persona** - Chinese-language system prompt defining professional e-commerce expert tone with explicit citation requirements
3. **RAG prompt template** - Structured template with {context} and {query} placeholders for knowledge-grounded responses
4. **Test coverage** - 5 comprehensive tests with mocked API calls (no real API usage during tests)
5. **Configuration** - Environment-based API key management with .env.example template

## Implementation Details

### LLMClient Architecture

```python
class LLMClient:
    def __init__(provider='openai', model='gpt-4o-mini', api_key=None)
    def generate(prompt: str, temperature: float = 0.7) -> str
```

**Key features:**
- Provider abstraction: Switch between OpenAI/Anthropic with single parameter
- Environment-based auth: API keys from OPENAI_API_KEY or ANTHROPIC_API_KEY
- Error handling: Rate limits, auth failures, network errors → user-friendly messages
- Temperature control: 0.0-1.0 range for response creativity tuning

### Henry's Persona Design

**Professional tone characteristics:**
- 专业但易懂 (Professional but accessible)
- 基于数据和经验 (Data and experience-driven)
- 实用导向 (Practical, actionable advice)
- 诚实透明 (Honest about knowledge limitations)

**Hallucination prevention rules:**
- "只基于提供的知识库内容回答问题" (Only answer from knowledge base)
- "每个回答都必须引用具体的来源文章" (Must cite source articles)
- "如果知识库中没有相关信息，明确告知用户" (Explicitly state when info is missing)

### RAG Prompt Template

```
基于以下知识库内容回答用户的问题。

知识库内容：
{context}

用户问题：
{query}

请基于上述知识库内容回答问题。如果知识库中没有相关信息，明确告知用户。在回答中引用具体的来源文章。
```

**Design rationale:**
- Separates context from query (prevents prompt injection)
- Reinforces citation requirement at prompt level
- Chinese language matches user's wiki content

## Test Coverage

All 5 tests passing:

1. ✓ LLMClient initializes with API key from environment
2. ✓ generate() sends prompt and returns text response
3. ✓ generate() handles API errors gracefully (no crashes)
4. ✓ generate() supports temperature parameter (0.0-1.0)
5. ✓ Mock API calls in tests (no real API usage)

**Test strategy:** unittest.mock for API calls, verify prompt formatting, error handling, and response parsing without real API costs.

## Deviations from Plan

None - plan executed exactly as written. All tasks completed with TDD cycle (RED → GREEN).

## Security & Privacy

**Threat mitigations implemented:**

- **T-04-01 (Information Disclosure):** API keys stored in environment variables, .env.example provided (no secrets in git)
- **T-04-03 (Prompt Injection):** System prompt enforces "只基于知识库内容" rule, RAG template separates context from user query

**Accepted risks:**

- **T-04-02 (DoS via rate limits):** Single-user system with low query volume, errors handled gracefully
- **T-04-04 (User queries to external API):** User's PROJECT.md explicitly requires cloud LLM API, no PII in e-commerce wiki

## Integration Points

**Provides to downstream plans:**

- Phase 04 Plan 02: RAG query engine will use `LLMClient.generate()` with `RAG_PROMPT_TEMPLATE`
- Phase 04 Plan 03: Chat API will use `HENRY_SYSTEM_PROMPT` for conversation context

**Dependencies satisfied:**

- Phase 03 semantic search: SearchEngine provides context chunks for RAG template

## Known Limitations

1. **No streaming support:** generate() returns complete response (not token-by-token streaming)
2. **No conversation history:** LLMClient is stateless, caller must manage multi-turn context
3. **Fixed max_tokens:** Anthropic uses hardcoded 4096 max_tokens (sufficient for RAG synthesis)

These are intentional simplifications for v1. Streaming and conversation management will be handled at the chat API layer (Plan 03).

## Next Steps

Ready for Phase 04 Plan 02: RAG Query Engine Integration

**What's needed:**
1. Combine SearchEngine (semantic search) + LLMClient (generation) into RAG pipeline
2. Implement context formatting from search results to RAG template
3. Add source citation extraction from LLM responses
4. Test end-to-end RAG flow: query → search → format → generate → cite

## Self-Check: PASSED

✓ All created files exist:
  - src/llm/llm_client.py
  - src/llm/prompts.py
  - tests/test_llm_client.py
  - .env.example

✓ All commits exist:
  - 1daef16: test(04-01): add failing tests for LLM client (RED)
  - ccd3ac1: feat(04-01): implement LLM client with OpenAI/Anthropic support (GREEN)

✓ All tests pass: 5/5
✓ Success criteria met: LLMClient can generate responses, Henry's persona configured, API keys protected
