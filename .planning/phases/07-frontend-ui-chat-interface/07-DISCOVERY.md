# Discovery: Phase 7 - Frontend UI - Chat Interface

**Phase:** 07-frontend-ui-chat-interface
**Discovery Level:** 2 (Standard Research)
**Started:** 2026-04-22
**Status:** In Progress

## Discovery Scope

**What we're deciding:**
1. Frontend framework/approach (React, Vue, vanilla JS, etc.)
2. SSE (Server-Sent Events) integration pattern for streaming chat
3. UI component structure for chat interface
4. Conversation history display pattern

**Why discovery is needed:**
- New frontend layer (no existing frontend in codebase)
- Multiple framework options with different tradeoffs
- SSE integration patterns vary by framework
- Need to balance simplicity vs maintainability for single-user app

## Context from Prior Phases

**Backend API available (Phase 6):**
- POST /api/conversations - Create new conversation
- GET /api/conversations - List all conversations
- GET /api/conversations/{id} - Get conversation with messages
- POST /api/chat - SSE streaming endpoint for chat responses

**SSE Event Format:**
```json
data: {"type": "answer", "content": "chunk"}
data: {"type": "sources", "content": [...]}
data: {"type": "done", "content": ""}
data: {"type": "error", "content": "error message"}
```

**Project Constraints:**
- Single-user local deployment
- Chinese language UI (用户界面使用中文)
- No authentication needed (v1)
- Privacy-focused (local-only)

## Research Questions

### Q1: Framework Selection

**Options:**

**A. Vanilla HTML/CSS/JS**
- Pros: Zero dependencies, fast load, simple deployment, no build step
- Cons: Manual DOM manipulation, no reactive state management, more boilerplate
- Best for: Simple UIs, minimal maintenance overhead

**B. React (with Vite)**
- Pros: Component reusability, rich ecosystem, good SSE libraries, familiar patterns
- Cons: Build step required, heavier bundle, overkill for single-user app
- Best for: Complex UIs, team projects, long-term maintenance

**C. Vue 3 (with Vite)**
- Pros: Simpler than React, good reactivity, progressive framework, smaller bundle
- Cons: Build step required, less familiar to some developers
- Best for: Medium complexity UIs, balance between simplicity and features

**D. Alpine.js + Tailwind CSS**
- Pros: Minimal JS, declarative, no build step, reactive, easy to learn
- Cons: Limited for very complex UIs, smaller ecosystem
- Best for: Simple-to-medium UIs with reactive needs

**Recommendation: Vanilla HTML/CSS/JS**

**Rationale:**
1. **Simplicity**: Single-user app doesn't need framework complexity
2. **Zero dependencies**: No npm, no build step, no version conflicts
3. **Fast deployment**: Just serve static files alongside FastAPI
4. **Maintainability**: Fewer moving parts, easier to debug
5. **SSE support**: Native EventSource API works perfectly
6. **Project fit**: Aligns with "local deployment, privacy-focused" philosophy

### Q2: SSE Integration Pattern

**Native EventSource API (Vanilla JS):**
```javascript
const eventSource = new EventSource('/api/chat', {
  method: 'POST',  // Note: EventSource only supports GET
  // Workaround: Use fetch for POST, then EventSource for stream
});

// Better pattern: POST to initiate, then stream
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ conversation_id, message })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      handleEvent(data);
    }
  }
}
```

**Recommendation: Fetch API with ReadableStream**

**Rationale:**
- EventSource only supports GET, but our endpoint is POST
- Fetch API with ReadableStream gives full control
- Can handle SSE format manually (simple parsing)
- No additional libraries needed

### Q3: UI Component Structure

**Recommended Structure:**

```
frontend/
├── index.html              # Main chat interface
├── styles.css              # Global styles
├── app.js                  # Main application logic
└── components/
    ├── chat.js             # Chat message display and input
    ├── conversation-list.js # Conversation history sidebar
    └── api.js              # API client wrapper
```

**Key Components:**

1. **Conversation List (Sidebar)**
   - Display all conversations (GET /api/conversations)
   - Show title, message count, created date
   - Click to load conversation
   - "New Conversation" button

2. **Chat Interface (Main)**
   - Message display area (scrollable)
   - User messages (right-aligned)
   - Henry messages (left-aligned, with sources)
   - Input box with send button
   - Loading indicator during streaming

3. **Message Display**
   - User message: Simple text bubble
   - Henry message: Text + source citations
   - Progressive display during streaming
   - Markdown rendering for Henry's responses (optional v1)

### Q4: State Management

**Recommended: Simple Object State**

```javascript
const state = {
  conversations: [],
  currentConversationId: null,
  currentMessages: [],
  isStreaming: false
};

function updateState(updates) {
  Object.assign(state, updates);
  render();
}
```

**Rationale:**
- No framework = manual state management
- Single state object is simple and predictable
- Explicit render() calls after state changes
- Sufficient for chat UI complexity

### Q5: Styling Approach

**Options:**

**A. Tailwind CSS (CDN)**
- Pros: Utility-first, fast prototyping, no build step with CDN
- Cons: Large CDN bundle, verbose HTML

**B. Custom CSS**
- Pros: Full control, minimal size, no dependencies
- Cons: More CSS to write

**C. CSS Framework (Bootstrap, Bulma)**
- Pros: Pre-built components, consistent design
- Cons: Heavier bundle, opinionated styles

**Recommendation: Custom CSS with CSS Variables**

**Rationale:**
- Full control over design
- Minimal bundle size
- CSS variables for theming (light/dark mode future)
- Chat UI is simple enough to not need framework
- Can use Flexbox/Grid for layout

## Technical Decisions

### Decision 1: Vanilla HTML/CSS/JS (No Framework)

**Chosen:** Vanilla HTML/CSS/JS

**Alternatives considered:**
- React: Too heavy for single-user app
- Vue: Still requires build step
- Alpine.js: Good option, but vanilla is simpler

**Rationale:**
- Zero dependencies, no build step
- Native SSE support via Fetch API
- Sufficient for chat UI complexity
- Aligns with project's simplicity goals

### Decision 2: Fetch API with ReadableStream for SSE

**Chosen:** Fetch API with manual SSE parsing

**Alternatives considered:**
- EventSource API: Doesn't support POST
- SSE libraries: Unnecessary for simple format

**Rationale:**
- Full control over POST request
- Native browser API, no dependencies
- SSE format is simple to parse manually

### Decision 3: FastAPI Static File Serving

**Chosen:** Serve frontend via FastAPI's StaticFiles

**Implementation:**
```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
```

**Rationale:**
- Single server for API + frontend
- No CORS issues (same origin)
- Simple deployment (one process)

### Decision 4: Progressive Enhancement

**Chosen:** Build working UI first, enhance later

**v1 Features:**
- Plain text messages (no Markdown rendering)
- Basic CSS styling
- Essential functionality only

**v2 Enhancements (Phase 8 or later):**
- Markdown rendering for Henry's responses
- Syntax highlighting for code blocks
- Dark mode toggle
- Message timestamps

## Implementation Guidance

### File Structure

```
frontend/
├── index.html          # Main page
├── styles.css          # Styles
└── app.js              # Application logic
```

### Key Implementation Patterns

**1. SSE Streaming Handler:**
```javascript
async function sendMessage(conversationId, message) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conversation_id: conversationId, message })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop(); // Keep incomplete line in buffer

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const event = JSON.parse(line.slice(6));
        handleSSEEvent(event);
      }
    }
  }
}
```

**2. Message Display:**
```javascript
function renderMessage(message) {
  const div = document.createElement('div');
  div.className = `message message-${message.role}`;
  
  const content = document.createElement('div');
  content.className = 'message-content';
  content.textContent = message.content;
  
  div.appendChild(content);
  
  if (message.sources && message.sources.length > 0) {
    const sources = document.createElement('div');
    sources.className = 'message-sources';
    sources.textContent = `来源: ${message.sources.map(s => s.document_path).join(', ')}`;
    div.appendChild(sources);
  }
  
  return div;
}
```

**3. Conversation Loading:**
```javascript
async function loadConversation(conversationId) {
  const response = await fetch(`/api/conversations/${conversationId}`);
  const conversation = await response.json();
  
  state.currentConversationId = conversationId;
  state.currentMessages = conversation.messages;
  render();
}
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| SSE parsing bugs | Chat breaks | Comprehensive error handling, fallback to full response |
| Browser compatibility | Users can't use app | Test on Chrome/Firefox/Safari, use standard APIs |
| State management complexity | Hard to maintain | Keep state simple, explicit render calls |
| CSS layout issues | Poor UX | Use Flexbox/Grid, test responsive design |

## Open Questions

1. **Markdown rendering in v1?**
   - Recommendation: No, defer to Phase 8 or later
   - Rationale: Adds dependency (marked.js), not essential for v1

2. **Message timestamps?**
   - Recommendation: Yes, show relative time ("2 minutes ago")
   - Rationale: Helps user understand conversation flow

3. **Auto-scroll to bottom?**
   - Recommendation: Yes, during streaming and on new messages
   - Rationale: Standard chat UX pattern

## Next Steps

1. Create frontend directory structure
2. Implement index.html with basic layout
3. Implement app.js with API client and state management
4. Implement styles.css with chat UI styling
5. Test SSE streaming integration
6. Test conversation loading and history display

## References

- MDN: Fetch API - https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
- MDN: ReadableStream - https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream
- SSE Format Spec - https://html.spec.whatwg.org/multipage/server-sent-events.html
- FastAPI StaticFiles - https://fastapi.tiangolo.com/tutorial/static-files/

---
**Discovery Complete:** 2026-04-22
**Ready for Planning:** Yes
