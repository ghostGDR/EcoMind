"""
Tests for conversation listing and retrieval functionality
"""
import pytest
from unittest.mock import Mock
from src.rag.conversation_manager import ConversationManager
from src.rag.query_engine import QueryEngine
from src.storage.conversation_store import ConversationStore
import tempfile
import os
import time


@pytest.fixture
def conversation_store():
    """Create test conversation store with temporary database"""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    store = ConversationStore(db_path=temp_db.name)
    yield store
    store.close()
    
    # Clean up
    try:
        os.unlink(temp_db.name)
    except:
        pass


@pytest.fixture
def query_engine():
    """Create mock query engine"""
    mock_engine = Mock(spec=QueryEngine)
    mock_engine.query.return_value = {
        'answer': '这是 Henry 的回答',
        'sources': [
            {'content': '测试内容', 'score': 0.9, 'metadata': {'file_path': 'test.md'}}
        ],
        'has_sources': True
    }
    return mock_engine


@pytest.fixture
def conversation_manager(query_engine, conversation_store):
    """Create test conversation manager"""
    return ConversationManager(query_engine, conversation_store)


def test_list_conversations_returns_empty_when_no_conversations(conversation_manager):
    """Test 1: list_conversations() returns empty list when no conversations exist"""
    conversations = conversation_manager.list_conversations()
    
    assert isinstance(conversations, list)
    assert len(conversations) == 0


def test_list_conversations_returns_all_with_metadata(conversation_manager):
    """Test 2: list_conversations() returns all conversations with metadata"""
    # Create 3 conversations
    conv1_id = conversation_manager.start_conversation(title="TikTok 广告咨询")
    time.sleep(0.01)  # Ensure different timestamps
    conv2_id = conversation_manager.start_conversation(title="财务规划讨论")
    time.sleep(0.01)
    conv3_id = conversation_manager.start_conversation(title="AI 工具应用")
    
    # Add messages to conversations
    conversation_manager.send_message(conv1_id, "第一个问题")
    conversation_manager.send_message(conv2_id, "问题1")
    conversation_manager.send_message(conv2_id, "问题2")
    
    # List conversations
    conversations = conversation_manager.list_conversations()
    
    # Debug
    print(f"\nConversations: {conversations}")
    
    assert len(conversations) == 3
    
    # Verify each conversation has required metadata
    for conv in conversations:
        assert 'id' in conv
        assert 'title' in conv
        assert 'created_at' in conv
        assert 'message_count' in conv
        assert isinstance(conv['id'], int)
        assert isinstance(conv['title'], str)
        assert isinstance(conv['message_count'], int)
    
    # Verify message counts
    conv_by_id = {c['id']: c for c in conversations}
    assert conv_by_id[conv1_id]['message_count'] == 2  # 1 user + 1 assistant
    assert conv_by_id[conv2_id]['message_count'] == 4  # 2 user + 2 assistant
    assert conv_by_id[conv3_id]['message_count'] == 0  # No messages yet


def test_list_conversations_orders_by_created_at_desc(conversation_manager):
    """Test 3: list_conversations() orders by created_at DESC (newest first)"""
    # Create conversations with delays to ensure different timestamps
    conv1_id = conversation_manager.start_conversation(title="第一个对话")
    time.sleep(1.1)  # Use full second delay for SQLite timestamp precision
    conv2_id = conversation_manager.start_conversation(title="第二个对话")
    time.sleep(1.1)
    conv3_id = conversation_manager.start_conversation(title="第三个对话")
    
    conversations = conversation_manager.list_conversations()
    
    # Verify we have 3 conversations
    assert len(conversations) == 3
    
    # Verify order: newest first (conv3, conv2, conv1)
    assert conversations[0]['id'] == conv3_id
    assert conversations[1]['id'] == conv2_id
    assert conversations[2]['id'] == conv1_id
    
    # Verify titles match expected order
    assert conversations[0]['title'] == "第三个对话"
    assert conversations[1]['title'] == "第二个对话"
    assert conversations[2]['title'] == "第一个对话"


def test_get_conversation_returns_full_conversation_with_messages(conversation_manager):
    """Test 4: get_conversation() returns full conversation with all messages"""
    # Create conversation and add messages
    conv_id = conversation_manager.start_conversation(title="完整对话测试")
    conversation_manager.send_message(conv_id, "第一个问题")
    conversation_manager.send_message(conv_id, "第二个问题")
    
    # Get full conversation
    conversation = conversation_manager.get_conversation(conv_id)
    
    assert conversation is not None
    assert conversation.id == conv_id
    assert conversation.title == "完整对话测试"
    assert len(conversation.messages) == 4  # 2 user + 2 assistant
    
    # Verify message order and content
    assert conversation.messages[0].role == 'user'
    assert conversation.messages[0].content == "第一个问题"
    assert conversation.messages[1].role == 'assistant'
    assert conversation.messages[2].role == 'user'
    assert conversation.messages[2].content == "第二个问题"
    assert conversation.messages[3].role == 'assistant'


def test_get_conversation_returns_none_for_nonexistent_id(conversation_manager):
    """Test 5: get_conversation() returns None for non-existent conversation_id"""
    conversation = conversation_manager.get_conversation(999)
    
    assert conversation is None
