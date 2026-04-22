---
phase: 06-backend-api-layer
plan: 02
subsystem: api
tags: [rest-api, conversations, crud, fastapi, integration-tests]
dependency_graph:
  requires:
    - src.api.dependencies.get_conversation_manager
    - src.rag.conversation_manager.ConversationManager
    - src.api.models (MessageResponse, ConversationResponse)
  provides:
    - POST /api/conversations (create conversation)
    - GET /api/conversations (list conversations)
    - GET /api/conversations/{id} (get conversation details)
  affects:
    - Future chat endpoints will use these conversation management endpoints
tech_stack:
  added: []
  patterns:
    - RESTful API design with proper HTTP status codes
    - Pydantic models for request/response validation
    - Dependency injection for service layer access
    - Integration tests with TestClient
key_files:
  created:
    - src/api/routes/__init__.py
    - src/api/routes/conversations.py
    - tests/test_conversation_routes.py
  modified:
    - src/api/models.py
    - src/api/main.py
    - src/storage/conversation_store.py
decisions:
  - "Use check_same_thread=False in SQLite connection for FastAPI async compatibility - allows singleton ConversationStore to work across async request threads"
  - "Return 201 Created for POST /api/conversations - follows REST conventions for resource creation"
  - "Include message_count in conversation list response - provides useful metadata without loading full messages"
  - "Use empty string path for POST endpoint (@router.post('')) - creates clean /api/conversations URL"
metrics:
  duration_minutes: 5
  completed_date: "2026-04-22"
  tasks_completed: 1
  tests_added: 6
  files_modified: 6
---

# Phase 06 Plan 02: Conversation Management API Summary

**One-liner:** REST API endpoints for conversation CRUD operations with create, list, and detail endpoints returning JSON responses validated by Pydantic models

## What Was Built

Implemented three REST API endpoints for conversation management, enabling frontend to create conversations, list all conversations, and retrieve conversation details with full message history.

### Key Components

1. **Conversation Router (src/api/routes/conversations.py)**
   - APIRouter with prefix="/api/conversations", tags=["conversations"]
   - POST "" - Create new conversation with optional title
     - Request: CreateConversationRequest (title: str = "新对话")
     - Response: CreateConversationResponse (201 Created)
     - Returns: id, title, created_at
   - GET "" - List all conversations
     - Response: ConversationListResponse (200 OK)
     - Returns: conversations array with id, title, created_at, message_count
     - Ordered by created_at DESC (newest first)
   - GET "/{conversation_id}" - Get conversation details
     - Path param: conversation_id (int)
     - Response: ConversationResponse (200 OK) or 404 Not Found
     - Returns: full conversation with all messages and sources
   - All endpoints use Depends(get_conversation_manager) for dependency injection
   - Comprehensive error handling with try/except and HTTPException

2. **Request/Response Models (src/api/models.py)**
   - CreateConversationRequest: title field with default "新对话"
   - CreateConversationResponse: id, title, created_at
   - ConversationListItem: id, title, created_at, message_count
   - ConversationListResponse: conversations array, total count
   - All models use Pydantic BaseModel for validation

3. **Router Integration (src/api/main.py)**
   - Import conversations router: `from src.api.routes import conversations`
   - Include router: `app.include_router(conversations.router)`
   - Router registered at application startup

4. **SQLite Threading Fix (src/storage/conversation_store.py)**
   - Added check_same_thread=False to sqlite3.connect()
   - Enables singleton ConversationStore to work across FastAPI async threads
   - Prevents "SQLite objects created in a thread can only be used in that same thread" error

5. **Integration Tests (tests/test_conversation_routes.py)**
   - test_create_conversation_success: POST returns 201 with conversation metadata
   - test_create_conversation_with_custom_title: Custom title persists correctly
   - test_list_conversations: GET returns proper structure with conversations array
   - test_get_conversation_success: GET /{id} returns full conversation details
   - test_get_conversation_not_found: GET /99999 returns 404
   - test_conversation_response_structure: Response includes messages array
   - All tests use TestClient for integration testing
   - Tests verify HTTP status codes, response structure, and data integrity

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking Issue] Fixed SQLite threading error in ConversationStore**
- **Found during:** Task 1 - First test execution
- **Issue:** SQLite connection created in one thread cannot be used in FastAPI async request threads. Error: "SQLite objects created in a thread can only be used in that same thread"
- **Fix:** Added `check_same_thread=False` parameter to `sqlite3.connect()` in ConversationStore.__init__()
- **Files modified:** src/storage/conversation_store.py
- **Commit:** Included in main task commit (11570ae)
- **Rationale:** FastAPI runs async endpoints in thread pool. Singleton ConversationStore must allow cross-thread access. This is safe because SQLite operations are serialized by Python's GIL and ConversationStore doesn't share cursors across threads.

## Threat Mitigations Implemented

| Threat ID | Mitigation | Implementation |
|-----------|------------|----------------|
| T-06-05 | conversation_id validation | FastAPI validates conversation_id as int, invalid values return 422 Unprocessable Entity |
| T-06-08 | Conversation title injection | Pydantic validates title as str, SQLite parameterized queries prevent SQL injection |

Threats T-06-06 (Information Disclosure) and T-06-07 (DoS) accepted per plan - single-user local deployment.

## Test Results

All 6 tests pass:

1. ✅ test_create_conversation_success - POST /api/conversations returns 201 with id, title, created_at
2. ✅ test_create_conversation_with_custom_title - Custom title "TikTok 广告投放策略" persists correctly
3. ✅ test_list_conversations - GET /api/conversations returns proper structure with conversations array and total count
4. ✅ test_get_conversation_success - GET /api/conversations/{id} returns full conversation with messages array
5. ✅ test_get_conversation_not_found - GET /api/conversations/99999 returns 404 with error detail
6. ✅ test_conversation_response_structure - Response includes empty messages array for new conversations

```bash
$ python3 -m pytest tests/test_conversation_routes.py -v
6 passed, 5 warnings in 11.94s
```

## Integration Points

- **Phase 07 (Chat UI):** Frontend will use POST /api/conversations to create new chat sessions
- **Phase 07 (Chat UI):** Frontend will use GET /api/conversations to display conversation history sidebar
- **Phase 07 (Chat UI):** Frontend will use GET /api/conversations/{id} to load conversation details and messages
- **Future plans:** Message sending endpoint will add messages to conversations created here

## Known Stubs

None - all functionality fully implemented and wired. Conversations can be created, listed, and retrieved with full message history.

## Threat Flags

None - no new security-relevant surface introduced beyond plan's threat model.

## Self-Check: PASSED

**Files created:**
- ✅ src/api/routes/__init__.py (exists)
- ✅ src/api/routes/conversations.py (exists)
- ✅ tests/test_conversation_routes.py (exists)

**Files modified:**
- ✅ src/api/models.py (request/response models added)
- ✅ src/api/main.py (router included)
- ✅ src/storage/conversation_store.py (check_same_thread=False added)

**Commits verified:**
- ✅ 11570ae: feat(06-02): implement conversation management REST API

**Tests verified:**
```bash
$ python3 -m pytest tests/test_conversation_routes.py -v
6 passed, 5 warnings in 11.94s
```

All files exist, commit present, all tests pass.
