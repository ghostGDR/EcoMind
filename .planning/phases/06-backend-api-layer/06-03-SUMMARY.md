---
phase: 06-backend-api-layer
plan: 03
subsystem: api
tags: [sse, streaming, chat, real-time, fastapi]
dependency_graph:
  requires:
    - src.api.dependencies.get_conversation_manager
    - src.rag.conversation_manager.ConversationManager
    - src.api.routes.conversations (for test setup)
  provides:
    - POST /api/chat SSE streaming endpoint
    - SSE event stream with answer chunks, sources, and done events
  affects:
    - Frontend chat UI (Phase 07) will consume this SSE stream
tech_stack:
  added:
    - FastAPI StreamingResponse for SSE
    - asyncio for async streaming
  patterns:
    - Server-Sent Events (SSE) for unidirectional streaming
    - Chunked response streaming for progressive display
    - Error events in stream instead of HTTP errors
key_files:
  created:
    - src/api/routes/chat.py
    - tests/test_chat_routes.py
  modified:
    - src/api/models.py
    - src/api/main.py
    - src/api/routes/__init__.py
decisions:
  - "Use SSE over WebSocket - simpler protocol, automatic browser reconnection, unidirectional sufficient for chat"
  - "Chunk answer text into 20-char segments with 50ms delay - provides progressive display UX like ChatGPT"
  - "Send error events in stream instead of HTTP errors - connection already established, maintains SSE protocol"
  - "Simulate streaming by chunking full response - ConversationManager returns complete response, true token-by-token streaming deferred to Phase 11"
metrics:
  duration_minutes: 7
  completed_date: "2026-04-22"
  tasks_completed: 1
  tests_added: 6
  files_modified: 5
---

# Phase 06 Plan 03: SSE Streaming Chat API Summary

**One-liner:** SSE streaming chat endpoint with progressive answer display, sources, and done events for real-time conversation experience

## What Was Built

Implemented Server-Sent Events (SSE) streaming endpoint for chat responses, enabling real-time progressive display of AI answers in the frontend.

### Key Components

1. **SSE Streaming Endpoint (src/api/routes/chat.py)**
   - POST /api/chat - Accepts conversation_id and message, streams response
   - Response type: text/event-stream with SSE format
   - Headers: Cache-Control: no-cache, Connection: keep-alive, X-Accel-Buffering: no
   - Dependency: ConversationManager via get_conversation_manager()

2. **Streaming Logic**
   - Calls ConversationManager.send_message() to get full response
   - Chunks answer text into 20-character segments
   - Yields each chunk as SSE event with 50ms delay (progressive display effect)
   - Sends sources event after answer completes
   - Sends done event to signal stream completion
   - Error handling: sends error events in stream (not HTTP errors)

3. **SSE Event Types**
   - `data: {"type": "answer", "content": "chunk"}` - Answer text chunks
   - `data: {"type": "sources", "content": [...]}` - Document sources with citations
   - `data: {"type": "done", "content": ""}` - Stream completion signal
   - `data: {"type": "error", "content": "message"}` - Error events (invalid conversation_id, etc.)

4. **Pydantic Models (src/api/models.py)**
   - ChatRequest: conversation_id (int), message (str)
   - SourceResponse: document_path, chunk_text, relevance_score (for type hints)

5. **Router Integration (src/api/main.py)**
   - Imported chat router: `from src.api.routes import chat`
   - Included router: `app.include_router(chat.router)`
   - Also included conversations router (needed for tests)

6. **Comprehensive Tests (tests/test_chat_routes.py)**
   - test_chat_stream_success: Verifies answer chunks, sources, and done events
   - test_chat_stream_includes_sources: Confirms sources sent after answer
   - test_chat_stream_includes_done_event: Validates done event is last
   - test_chat_invalid_conversation_id: Error event for invalid conversation_id
   - test_chat_empty_message: Validates empty message handling
   - test_chat_stream_headers: Verifies SSE headers (content-type, cache-control, etc.)
   - All tests use fixtures to avoid SQLite threading issues with TestClient

## Deviations from Plan

None - plan executed exactly as written.

## Threat Mitigations Implemented

| Threat ID | Mitigation | Implementation |
|-----------|------------|----------------|
| T-06-09 | Injection via user message | Message passed to ConversationManager which uses parameterized queries and LLM API (no code execution risk) |
| T-06-10 | DoS via long-running SSE | Accepted - single-user local deployment, no connection limits needed in v1 |
| T-06-11 | Information disclosure in errors | Generic error events sent to client, detailed errors logged server-side only |
| T-06-12 | Tampering via conversation_id | ConversationManager validates conversation_id exists, raises ValueError for invalid IDs |

## Test Results

All 6 tests pass:

1. ✅ test_chat_stream_success - Creates conversation, sends message, verifies answer chunks, sources, and done events in SSE stream
2. ✅ test_chat_stream_includes_sources - Confirms sources event sent after answer chunks
3. ✅ test_chat_stream_includes_done_event - Validates done event is last in stream
4. ✅ test_chat_invalid_conversation_id - Invalid conversation_id sends error event (not HTTP error)
5. ✅ test_chat_empty_message - Empty message handling (validation or acceptance)
6. ✅ test_chat_stream_headers - Verifies SSE headers: text/event-stream, no-cache, keep-alive, no buffering

## Integration Points

- **Phase 05 (Conversation Management):** Uses ConversationManager.send_message() to get responses
- **Phase 06-02 (Conversation REST API):** Tests use POST /api/conversations to create test conversations
- **Phase 07 (Chat UI):** Frontend will use EventSource API to consume this SSE stream
- **Phase 11 (Performance Optimization):** Can upgrade to true token-by-token streaming by modifying QueryEngine

## Known Stubs

None - all functionality fully implemented and wired. Answer streaming is simulated by chunking the full response, but this is intentional v1 design (not a stub).

## Threat Flags

None - no new security-relevant surface introduced beyond plan's threat model.

## Self-Check: PASSED

**Files created:**
- ✅ src/api/routes/chat.py (exists, 122 lines)
- ✅ src/api/routes/__init__.py (exists)
- ✅ tests/test_chat_routes.py (exists, 207 lines)

**Files modified:**
- ✅ src/api/models.py (ChatRequest and SourceResponse added)
- ✅ src/api/main.py (chat and conversations routers included)

**Commits verified:**
- ✅ df6cf3f: feat(06-04): implement document management REST API (includes chat.py, conversations.py, models.py, main.py)
- ✅ 2ee734e: feat(06-03): implement SSE streaming chat endpoint (tests)

**Tests verified:**
```bash
$ python3 -m pytest tests/test_chat_routes.py -v
6 passed, 10 warnings in 36.81s
```

All files exist, all commits present, all tests pass.

## Notes

**Why SSE over WebSocket:**
- Simpler protocol - no handshake, just HTTP GET
- Automatic browser reconnection built-in
- Unidirectional communication sufficient for chat (server → client)
- No need for bidirectional messaging in v1

**Why chunk the response:**
Even though ConversationManager returns the full response (not streaming), chunking provides better UX by showing progressive output like ChatGPT. This is v1 implementation with simulated streaming. Phase 11 (Performance Optimization) can add true streaming by modifying QueryEngine to stream LLM tokens directly.

**Implementation note:**
The source files (chat.py, models.py updates, main.py updates) were created in commit df6cf3f during phase 06-04 execution, which ran before 06-03. The test file was added in commit 2ee734e. All functionality matches the plan specification exactly.
