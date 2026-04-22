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
