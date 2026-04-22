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
    updateState({
      currentConversationId: conversation.id,
      currentMessages: conversation.messages
    });
  } catch (error) {
    console.error('Error loading conversation:', error);
    alert('加载对话失败，请重试');
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
    item.className = 'conversation-item';
    if (conv.id === state.currentConversationId) {
      item.classList.add('active');
    }
    
    item.innerHTML = `
      <div class="conversation-title">${escapeHtml(conv.title)}</div>
      <div class="conversation-meta">${conv.message_count} 条消息</div>
    `;
    
    item.addEventListener('click', () => handleConversationClick(conv.id));
    listContainer.appendChild(item);
  });
}

function renderMessages() {
  const messagesContainer = document.getElementById('messages');
  messagesContainer.innerHTML = ''; // Clear existing
  
  if (state.currentMessages.length === 0) {
    messagesContainer.innerHTML = '<div class="empty-state">开始新对话吧！</div>';
    return;
  }
  
  state.currentMessages.forEach(msg => {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${msg.role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = msg.content;
    messageDiv.appendChild(contentDiv);
    
    // Add sources if present (for Henry's messages)
    if (msg.sources && msg.sources.length > 0) {
      const sourcesDiv = document.createElement('div');
      sourcesDiv.className = 'message-sources';
      const sourceFiles = msg.sources.map(s => {
        const filename = s.document_path.split('/').pop();
        return filename;
      }).join(', ');
      sourcesDiv.textContent = `来源: ${sourceFiles}`;
      messageDiv.appendChild(sourcesDiv);
    }
    
    messagesContainer.appendChild(messageDiv);
  });
  
  // Auto-scroll to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function updateInputState() {
  const input = document.getElementById('message-input');
  const sendBtn = document.getElementById('send-btn');
  
  if (state.isStreaming) {
    input.disabled = true;
    sendBtn.disabled = true;
    sendBtn.textContent = '发送中...';
  } else {
    input.disabled = false;
    sendBtn.disabled = false;
    sendBtn.textContent = '发送';
  }
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

// ============================================================================
// Initialization
// ============================================================================

// Initialize app on page load
document.addEventListener('DOMContentLoaded', async () => {
  // Attach event listeners
  document.getElementById('new-conversation-btn').addEventListener('click', handleNewConversation);
  document.getElementById('send-btn').addEventListener('click', handleSendMessage);
  document.getElementById('message-input').addEventListener('keydown', handleMessageInputKeydown);
  
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
