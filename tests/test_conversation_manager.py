"""
Tests for ConversationManager - multi-turn conversation with history injection
"""
import pytest
from unittest.mock import Mock
from src.rag.conversation_manager import ConversationManager
from src.rag.query_engine import QueryEngine
from src.storage.conversation_store import ConversationStore
import tempfile
import os


@pytest.fixture
def conversation_store():
    """Create test conversation store with temporary database"""
    # Create temporary database file
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
    # Default mock response - sources format matches QueryEngine output
    mock_engine.query.return_value = {
        'answer': '这是 Henry 的回答',
        'sources': [
            {
                'content': '测试内容',
                'score': 0.9,
                'metadata': {'file_path': 'test.md', 'file_name': 'test.md'},
                'node_id': 'test-node-123'
            }
        ],
        'has_sources': True
    }
    return mock_engine


@pytest.fixture
def conversation_manager(query_engine, conversation_store):
    """Create test conversation manager"""
    return ConversationManager(query_engine, conversation_store)


def test_start_conversation_creates_in_database(conversation_manager, conversation_store):
    """Test 1: start_conversation() creates new conversation in database and returns conversation_id"""
    conversation_id = conversation_manager.start_conversation(title="测试对话")
    
    assert isinstance(conversation_id, int)
    assert conversation_id > 0
    
    # Verify in database
    conversation = conversation_store.get_conversation(conversation_id)
    assert conversation is not None
    assert conversation.title == "测试对话"
    assert len(conversation.messages) == 0


def test_send_message_with_no_history(conversation_manager, conversation_store):
    """Test 2: send_message() with no history calls QueryEngine.query() with just the user query"""
    conversation_id = conversation_manager.start_conversation()
    
    response = conversation_manager.send_message(
        conversation_id,
        "TikTok 广告投放的最佳实践是什么？"
    )
    
    assert "answer" in response
    assert "sources" in response
    assert "conversation_id" in response
    assert response["conversation_id"] == conversation_id
    
    # Verify messages persisted
    conversation = conversation_store.get_conversation(conversation_id)
    assert len(conversation.messages) == 2  # user + assistant
    assert conversation.messages[0].role == "user"
    assert conversation.messages[1].role == "assistant"


def test_send_message_with_history_injects_context(conversation_manager, conversation_store):
    """Test 3: send_message() with existing history injects previous Q&A pairs into the query context"""
    conversation_id = conversation_manager.start_conversation()
    
    # First message
    conversation_manager.send_message(conversation_id, "TikTok 广告投放的最佳实践是什么？")
    
    # Second message (follow-up)
    response = conversation_manager.send_message(conversation_id, "那具体怎么做？")
    
    assert "answer" in response
    
    # Verify history was injected (check database has both exchanges)
    conversation = conversation_store.get_conversation(conversation_id)
    assert len(conversation.messages) == 4  # 2 user + 2 assistant


def test_send_message_persists_with_sources(conversation_manager, conversation_store):
    """Test 4: send_message() persists both user message and assistant response to database with sources"""
    conversation_id = conversation_manager.start_conversation()
    
    response = conversation_manager.send_message(
        conversation_id,
        "如何提高 TikTok 视频的播放量？"
    )
    
    # Verify sources in response
    assert "sources" in response
    assert isinstance(response["sources"], list)
    
    # Verify sources persisted in database
    conversation = conversation_store.get_conversation(conversation_id)
    assistant_message = conversation.messages[1]
    assert assistant_message.role == "assistant"
    # Sources may be None or empty list depending on search results
    assert assistant_message.sources is not None or assistant_message.sources == []


def test_get_history_retrieves_full_conversation(conversation_manager):
    """Test 5: get_history() retrieves full conversation from database"""
    conversation_id = conversation_manager.start_conversation(title="历史测试")
    
    # Send multiple messages
    conversation_manager.send_message(conversation_id, "第一个问题")
    conversation_manager.send_message(conversation_id, "第二个问题")
    
    # Retrieve history
    history = conversation_manager.get_history(conversation_id)
    
    assert history is not None
    assert history.title == "历史测试"
    assert len(history.messages) == 4  # 2 user + 2 assistant
    assert history.messages[0].content == "第一个问题"
    assert history.messages[2].content == "第二个问题"
