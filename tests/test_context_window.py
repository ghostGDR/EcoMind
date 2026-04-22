"""Tests for context window management in ConversationManager"""
import pytest
from unittest.mock import Mock, MagicMock
from src.rag.conversation_manager import ConversationManager
from src.rag.query_engine import QueryEngine
from src.storage.conversation_store import ConversationStore, Conversation, Message
from datetime import datetime


@pytest.fixture
def mock_query_engine():
    """Mock QueryEngine to avoid LLM API calls"""
    engine = Mock(spec=QueryEngine)
    engine.query.return_value = {
        'answer': 'Test answer',
        'sources': [],
        'has_sources': False
    }
    return engine


@pytest.fixture
def conversation_store():
    """Real ConversationStore with in-memory database"""
    store = ConversationStore(db_path=':memory:')
    yield store
    store.close()


def test_conversation_manager_accepts_max_history_messages_parameter(mock_query_engine, conversation_store):
    """Test 1: ConversationManager.__init__() accepts max_history_messages parameter (default 10)"""
    # Test with default value
    manager = ConversationManager(
        query_engine=mock_query_engine,
        conversation_store=conversation_store
    )
    assert hasattr(manager, 'max_history_messages')
    assert manager.max_history_messages == 10
    
    # Test with custom value
    manager_custom = ConversationManager(
        query_engine=mock_query_engine,
        conversation_store=conversation_store,
        max_history_messages=5
    )
    assert manager_custom.max_history_messages == 5


def test_send_message_with_few_messages_includes_all_history(mock_query_engine, conversation_store):
    """Test 2: send_message() with <= max_history_messages includes all history"""
    manager = ConversationManager(
        query_engine=mock_query_engine,
        conversation_store=conversation_store,
        max_history_messages=10
    )
    
    # Create conversation and add 4 messages (2 Q&A pairs)
    conv_id = manager.start_conversation("Test conversation")
    
    # First exchange
    manager.send_message(conv_id, "Question 1")
    # Second exchange
    manager.send_message(conv_id, "Question 2")
    
    # Third exchange - should include all previous history
    manager.send_message(conv_id, "Question 3")
    
    # Verify QueryEngine was called with formatted history including all messages
    last_call_query = mock_query_engine.query.call_args[0][0]
    
    # Should contain all previous messages (4 messages: 2 user + 2 assistant)
    assert "Question 1" in last_call_query
    assert "Question 2" in last_call_query
    assert "Question 3" in last_call_query


def test_send_message_with_many_messages_truncates_to_last_n(mock_query_engine, conversation_store):
    """Test 3: send_message() with > max_history_messages truncates to last N messages"""
    manager = ConversationManager(
        query_engine=mock_query_engine,
        conversation_store=conversation_store,
        max_history_messages=4  # Only keep last 4 messages (2 Q&A pairs)
    )
    
    # Create conversation and add 8 messages (4 Q&A pairs)
    conv_id = manager.start_conversation("Long conversation")
    
    for i in range(1, 5):
        manager.send_message(conv_id, f"Question {i}")
    
    # Reset mock to track next call
    mock_query_engine.query.reset_mock()
    
    # Fifth exchange - should only include last 4 messages (Q3, A3, Q4, A4)
    manager.send_message(conv_id, "Question 5")
    
    # Verify QueryEngine was called with truncated history
    last_call_query = mock_query_engine.query.call_args[0][0]
    
    # Should NOT contain old messages
    assert "Question 1" not in last_call_query
    assert "Question 2" not in last_call_query
    
    # Should contain recent messages
    assert "Question 3" in last_call_query
    assert "Question 4" in last_call_query
    assert "Question 5" in last_call_query


def test_truncation_preserves_most_recent_exchanges(mock_query_engine, conversation_store):
    """Test 4: Truncation preserves most recent exchanges (last 10 messages = 5 Q&A pairs)"""
    manager = ConversationManager(
        query_engine=mock_query_engine,
        conversation_store=conversation_store,
        max_history_messages=10
    )
    
    # Create conversation with 15 messages (7 Q&A pairs + 1 user message)
    conv_id = manager.start_conversation("Very long conversation")
    
    for i in range(1, 8):
        manager.send_message(conv_id, f"Question {i}")
    
    # Reset mock to track next call
    mock_query_engine.query.reset_mock()
    
    # 8th exchange - should only include last 10 messages
    manager.send_message(conv_id, "Question 8")
    
    last_call_query = mock_query_engine.query.call_args[0][0]
    
    # Should NOT contain very old messages (Q1, A1, Q2, A2, Q3, A3)
    assert "Question 1" not in last_call_query
    assert "Question 2" not in last_call_query
    assert "Question 3" not in last_call_query
    
    # Should contain last 5 Q&A pairs (Q4-Q7 and their answers)
    assert "Question 4" in last_call_query
    assert "Question 5" in last_call_query
    assert "Question 6" in last_call_query
    assert "Question 7" in last_call_query
    assert "Question 8" in last_call_query


def test_database_contains_full_history_after_truncation(mock_query_engine, conversation_store):
    """Test 5: Database still contains full history (truncation only affects context injection, not persistence)"""
    manager = ConversationManager(
        query_engine=mock_query_engine,
        conversation_store=conversation_store,
        max_history_messages=4
    )
    
    # Create conversation with 10 messages (5 Q&A pairs)
    conv_id = manager.start_conversation("Test persistence")
    
    for i in range(1, 6):
        manager.send_message(conv_id, f"Question {i}")
    
    # Retrieve full conversation from database
    conversation = manager.get_history(conv_id)
    
    # Database should contain ALL 10 messages (5 user + 5 assistant)
    assert len(conversation.messages) == 10
    
    # Verify all messages are present in database
    user_messages = [m for m in conversation.messages if m.role == 'user']
    assert len(user_messages) == 5
    assert user_messages[0].content == "Question 1"
    assert user_messages[4].content == "Question 5"
