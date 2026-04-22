// ============================================================================
// State Management
// ============================================================================

const state = {
  conversations: [],           // Array of conversation objects
  currentConversationId: null, // Currently selected conversation ID
  currentMessages: [],         // Messages in current conversation
  isStreaming: false          // Whether chat is currently streaming
};

function updateState(updates) {
  Object.assign(state, updates);
  render();
}

// ============================================================================
// Markdown Configuration
// ============================================================================

if (typeof marked !== 'undefined') {
  marked.setOptions({
    highlight: function(code, lang) {
      if (lang && hljs.getLanguage(lang)) {
        return hljs.highlight(code, { language: lang }).value;
      }
      return hljs.highlightAuto(code).value;
    },
    breaks: true,
    gfm: true
  });
}

// ============================================================================
// API Client Functions
// ============================================================================

// POST /api/conversations - Create new conversation
async function createConversation(title = "新对话") {
  const response = await fetch('/api/conversations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  });
  if (!response.ok) throw new Error('Failed to create conversation');
  return await response.json(); // Returns {id, title, created_at}
}

// GET /api/conversations - List all conversations
async function listConversations() {
  const response = await fetch('/api/conversations');
  if (!response.ok) throw new Error('Failed to list conversations');
  const data = await response.json();
  return data.conversations; // Array of conversation objects
}

// GET /api/conversations/{id} - Get conversation with messages
async function getConversation(conversationId) {
  const response = await fetch(`/api/conversations/${conversationId}`);
  if (!response.ok) throw new Error('Failed to get conversation');
  return await response.json(); // Returns {id, title, created_at, messages}
}

// DELETE /api/conversations/{id} - Delete conversation
async function deleteConversation(conversationId) {
  const response = await fetch(`/api/conversations/${conversationId}`, {
    method: 'DELETE'
  });
  if (!response.ok) throw new Error('Failed to delete conversation');
  return await response.json();
}

// POST /api/chat - Send message and handle SSE streaming response
async function sendMessage(conversationId, message) {
  if (!message.trim()) return;
  
  // Add user message to UI immediately
  const userMessage = {
    id: Date.now(), // Temporary ID
    role: 'user',
    content: message,
    created_at: new Date().toISOString(),
    sources: null
  };
  
  state.currentMessages.push(userMessage);
  updateState({ isStreaming: true });
  
  // Create placeholder for Henry's response
  const henryMessage = {
    id: Date.now() + 1,
    role: 'assistant',
    content: '',
    created_at: new Date().toISOString(),
    sources: []
  };
  state.currentMessages.push(henryMessage);
  render();
  
  try {
    // Send POST request to /api/chat/
    const response = await fetch('/api/chat/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conversation_id: conversationId,
        message: message
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    // Read SSE stream using ReadableStream
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      // Decode chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });
      
      // Process complete lines (SSE events end with \n\n)
      const lines = buffer.split('\n');
      buffer = lines.pop(); // Keep incomplete line in buffer
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const eventData = JSON.parse(line.slice(6));
          handleSSEEvent(eventData, henryMessage);
        }
      }
    }
    
    // Reload conversation to get persisted messages with correct IDs
    await loadConversation(conversationId);
    
  } catch (error) {
    console.error('Error sending message:', error);
    henryMessage.content = '抱歉，发送消息时出错了。请重试。';
    render();
  } finally {
    updateState({ isStreaming: false });
  }
}

// Handle individual SSE events
function handleSSEEvent(event, henryMessage) {
  switch (event.type) {
    case 'answer':
      // Append answer chunk to Henry's message
      henryMessage.content += event.content;
      render();
      break;
      
    case 'sources':
      // Add sources to Henry's message
      henryMessage.sources = event.content;
      render();
      break;
      
    case 'done':
      // Stream complete - no action needed
      console.log('Stream complete');
      break;
      
    case 'error':
      // Display error message
      henryMessage.content = `错误: ${event.content}`;
      render();
      break;
      
    default:
      console.warn('Unknown SSE event type:', event.type);
  }
}

// ============================================================================
// Event Handlers
// ============================================================================

// Handle "新对话" button click
async function handleNewConversation() {
  try {
    const conversation = await createConversation();
    await loadConversations(); // Refresh list
    await loadConversation(conversation.id); // Load new conversation
  } catch (error) {
    console.error('Error creating conversation:', error);
    alert('创建对话失败，请重试');
  }
}

// Handle conversation item click
async function handleConversationClick(conversationId) {
  await loadConversation(conversationId);
}

// Handle send button click
async function handleSendMessage() {
  const input = document.getElementById('message-input');
  const message = input.value.trim();
  
  if (!message) return;
  if (state.isStreaming) return; // Prevent sending while streaming
  if (!state.currentConversationId) {
    alert('请先创建或选择一个对话');
    return;
  }
  
  // Clear input immediately
  input.value = '';
  
  // Send message
  await sendMessage(state.currentConversationId, message);
}

// Handle Enter key in textarea (Shift+Enter for new line)
function handleMessageInputKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    handleSendMessage();
  }
}

// Load conversation and display messages
async function loadConversation(conversationId) {
  try {
    const conversation = await getConversation(conversationId);
    console.log('Successfully loaded conversation:', conversation);
    updateState({
      currentConversationId: conversation.id,
      currentMessages: conversation.messages
    });
  } catch (error) {
    console.error(`Error loading conversation ${conversationId}:`, error);
    alert(`加载对话失败: ${error.message}`);
  }
}

// Load and display conversation list
async function loadConversations() {
  try {
    const conversations = await listConversations();
    updateState({ conversations });
  } catch (error) {
    console.error('Error loading conversations:', error);
  }
}

// ============================================================================
// Render Functions
// ============================================================================

function render() {
  renderConversationList();
  renderMessages();
  updateInputState();
}

function renderConversationList() {
  const listContainer = document.getElementById('conversation-list');
  listContainer.innerHTML = ''; // Clear existing
  
  if (state.conversations.length === 0) {
    listContainer.innerHTML = '<div class="empty-state">暂无对话</div>';
    return;
  }
  
  state.conversations.forEach(conv => {
    const item = document.createElement('div');
    item.className = `conversation-item ${conv.id === state.currentConversationId ? 'active' : ''}`;
    
    // Create a wrapper for the title to allow flex grow
    const titleSpan = document.createElement('span');
    titleSpan.className = 'conversation-title';
    titleSpan.textContent = conv.title || `对话 ${conv.id}`;
    
    // Create the delete button
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-conv-btn';
    deleteBtn.title = '删除对话';
    deleteBtn.setAttribute('aria-label', '删除对话');
    
    // Use a simpler SVG path for better compatibility
    deleteBtn.innerHTML = `
      <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="pointer-events: none; display: block;">
        <polyline points="3 6 5 6 21 6"></polyline>
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        <line x1="10" y1="11" x2="10" y2="17"></line>
        <line x1="14" y1="11" x2="14" y2="17"></line>
      </svg>
    `;
    
    // Event handlers
    deleteBtn.onclick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      handleDeleteConversation(e, conv.id);
    };
    
    item.onclick = () => loadConversation(conv.id);
    
    // Append in correct order
    item.appendChild(titleSpan);
    item.appendChild(deleteBtn);
    listContainer.appendChild(item);
  });
}

async function handleDeleteConversation(event, conversationId) {
  event.stopPropagation(); // Prevent selection
  
  if (!confirm('确定要删除这条对话吗？此操作不可恢复。')) {
    return;
  }
  
  try {
    await deleteConversation(conversationId);
    
    // If deleted the current conversation, clear view or switch to newest
    if (state.currentConversationId === conversationId) {
      updateState({ 
        currentConversationId: null, 
        currentMessages: [] 
      });
    }
    
    // Refresh list
    await loadConversations();
  } catch (error) {
    console.error('Error deleting conversation:', error);
    alert('删除失败: ' + error.message);
  }
}

function renderMessages() {
  const messagesContainer = document.getElementById('messages');
  const wasAtBottom = messagesContainer.scrollHeight - messagesContainer.scrollTop <= messagesContainer.clientHeight + 100;
  
  // To avoid flickering, we only rebuild the entire list if the message count changed
  // or if we're not in a streaming state.
  const currentMessageCount = messagesContainer.querySelectorAll('.message').length;
  
  if (currentMessageCount !== state.currentMessages.length || !state.isStreaming) {
    messagesContainer.innerHTML = '';
    
    if (state.currentMessages.length === 0) {
      messagesContainer.innerHTML = '<div class="empty-state">开始新对话吧！</div>';
      return;
    }
    
    state.currentMessages.forEach((msg, index) => {
      const isLast = index === state.currentMessages.length - 1;
      const messageDiv = createMessageElement(msg, isLast && state.isStreaming);
      messagesContainer.appendChild(messageDiv);
    });
  } else {
    // We are streaming and the message count matches. 
    // Just update the content of the last message.
    const lastMsg = state.currentMessages[state.currentMessages.length - 1];
    const messageElements = messagesContainer.querySelectorAll('.message');
    const lastElement = messageElements[messageElements.length - 1];
    
    if (lastElement && lastMsg.role === 'assistant') {
      const contentDiv = lastElement.querySelector('.message-content');
      if (contentDiv) {
        const rendered = typeof marked !== 'undefined' ? marked.parse(lastMsg.content) : escapeHtml(lastMsg.content);
        if (contentDiv.innerHTML !== rendered) {
          contentDiv.innerHTML = rendered;
          // Apply syntax highlighting to new code blocks
          contentDiv.querySelectorAll('pre code').forEach((block) => {
            if (typeof hljs !== 'undefined') hljs.highlightElement(block);
          });
        }
      }
    }
  }
  
  // Sticky scroll to bottom
  if (wasAtBottom || !state.isStreaming) {
    requestAnimationFrame(() => {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });
  }
}

function createMessageElement(msg, isStreaming) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${msg.role === 'user' ? 'user' : 'henry'}`;
  
  if (isStreaming && msg.role === 'assistant') {
    messageDiv.classList.add('message-streaming');
  }
  
  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';
  
  if (typeof marked !== 'undefined') {
    contentDiv.innerHTML = marked.parse(msg.content);
    // Apply syntax highlighting
    contentDiv.querySelectorAll('pre code').forEach((block) => {
      if (typeof hljs !== 'undefined') hljs.highlightElement(block);
    });
  } else {
    contentDiv.textContent = msg.content;
  }
  
  messageDiv.appendChild(contentDiv);
  
  // Add sources if present
  if (msg.role === 'assistant' && msg.sources && msg.sources.length > 0) {
    const sourcesDiv = document.createElement('div');
    sourcesDiv.className = 'message-sources';
    
    const title = document.createElement('strong');
    title.textContent = '参考资料：';
    sourcesDiv.appendChild(title);
    
    const list = document.createElement('div');
    const getPath = (s) => s.metadata?.relative_path || s.metadata?.file_path || s.document_path || '未知文件';
    const uniquePaths = Array.from(new Set(msg.sources.map(getPath)));
    const uniqueSources = uniquePaths.map(path => msg.sources.find(s => getPath(s) === path));
      
    list.textContent = uniqueSources.map(s => {
      const path = getPath(s);
      const parts = path.split('/');
      return parts[parts.length - 1];
    }).join('、');
    
    sourcesDiv.appendChild(list);
    messageDiv.appendChild(sourcesDiv);
  }
  
  return messageDiv;
}

function updateInputState() {
  const input = document.getElementById('message-input');
  const sendBtn = document.getElementById('send-btn');
  
  if (state.isStreaming) {
    input.disabled = true;
    sendBtn.disabled = true;
    sendBtn.style.opacity = '0.5';
  } else {
    input.disabled = false;
    sendBtn.disabled = false;
    sendBtn.style.opacity = '1';
  }
}

// Auto-expand textarea
function initAutoExpand() {
  const input = document.getElementById('message-input');
  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = (input.scrollHeight) + 'px';
  });
}

// ============================================================================
// Utility Functions
// ============================================================================

// Escape HTML to prevent XSS (T-07-09 mitigation)
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Check if the backend is ready (model loaded)
async function checkSystemReadiness() {
  const overlay = document.getElementById('loading-overlay');
  const maxAttempts = 60; // 60 seconds max
  let attempts = 0;
  
  while (attempts < maxAttempts) {
    try {
      const response = await fetch('/health');
      const data = await response.json();
      
      if (data.status === 'ok') {
        console.log('System is ready!');
        overlay.classList.add('hidden');
        return;
      }
    } catch (e) {
      console.warn('Waiting for backend...', e);
    }
    
    attempts++;
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  // If timeout, show error in overlay
  const loaderH3 = overlay.querySelector('h3');
  loaderH3.textContent = '系统初始化超时';
  loaderH3.style.color = '#ef4444';
}

// ============================================================================
// Initialization
// ============================================================================

// Initialize app on page load
document.addEventListener('DOMContentLoaded', async () => {
  // Start readiness check
  checkSystemReadiness();

  // Attach event listeners
  document.getElementById('new-conversation-btn').addEventListener('click', handleNewConversation);
  document.getElementById('send-btn').addEventListener('click', handleSendMessage);
  document.getElementById('message-input').addEventListener('keydown', handleMessageInputKeydown);
  
  initAutoExpand();
  
  // Load initial data
  await loadConversations();
  
  // If no conversations exist, create first one
  if (state.conversations.length === 0) {
    await handleNewConversation();
  } else {
    // Load most recent conversation
    await loadConversation(state.conversations[0].id);
  }
});
