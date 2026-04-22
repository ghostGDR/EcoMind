import pytest
import tempfile
import os
from pathlib import Path
from src.storage.conversation_store import ConversationStore, Conversation, Message

@pytest.fixture
def temp_db():
    """Create temporary database"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    store = ConversationStore(db_path=path)
    yield store
    store.close()
    os.unlink(path)

def test_database_initialization(temp_db):
    """Test database initializes with correct schema"""
    cursor = temp_db.conn.cursor()
    
    # Check tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    assert "conversations" in tables
    assert "messages" in tables
    assert "message_sources" in tables

def test_create_conversation(temp_db):
    """Test create conversation returns conversation ID"""
    conv_id = temp_db.create_conversation(title="Test Conversation")
    assert conv_id > 0
    
    # Verify conversation exists
    conv = temp_db.get_conversation(conv_id)
    assert conv is not None
    assert conv.title == "Test Conversation"

def test_add_message(temp_db):
    """Test add message to conversation succeeds"""
    conv_id = temp_db.create_conversation()
    
    msg_id = temp_db.add_message(
        conversation_id=conv_id,
        role="user",
        content="你好，Henry"
    )
    assert msg_id > 0
    
    # Verify message exists
    conv = temp_db.get_conversation(conv_id)
    assert len(conv.messages) == 1
    assert conv.messages[0].content == "你好，Henry"
    assert conv.messages[0].role == "user"

def test_retrieve_conversation_with_messages(temp_db):
    """Test retrieve conversation with messages returns correct data"""
    conv_id = temp_db.create_conversation(title="Multi-turn Chat")
    
    temp_db.add_message(conv_id, "user", "TikTok 广告怎么投放？")
    temp_db.add_message(conv_id, "assistant", "根据我的知识库...")
    temp_db.add_message(conv_id, "user", "具体步骤是什么？")
    
    conv = temp_db.get_conversation(conv_id)
    assert conv.title == "Multi-turn Chat"
    assert len(conv.messages) == 3
    assert conv.messages[0].role == "user"
    assert conv.messages[1].role == "assistant"
    assert conv.messages[2].role == "user"

def test_foreign_key_constraints(temp_db):
    """Test foreign key constraints prevent orphaned messages"""
    # Try to add message to non-existent conversation
    with pytest.raises(Exception):
        temp_db.add_message(
            conversation_id=99999,
            role="user",
            content="This should fail"
        )

def test_message_sources(temp_db):
    """Test message sources can be attached to messages"""
    conv_id = temp_db.create_conversation()
    
    sources = [
        {
            "document_path": "/wiki/tiktok-ads.md",
            "chunk_text": "TikTok 广告投放最佳时间...",
            "relevance_score": 0.95
        }
    ]
    
    msg_id = temp_db.add_message(
        conversation_id=conv_id,
        role="assistant",
        content="根据文档，TikTok 广告...",
        sources=sources
    )
    
    # Verify sources attached
    conv = temp_db.get_conversation(conv_id)
    assert len(conv.messages) == 1
    assert conv.messages[0].sources is not None
    assert len(conv.messages[0].sources) == 1
    assert conv.messages[0].sources[0]["document_path"] == "/wiki/tiktok-ads.md"

def test_list_conversations(temp_db):
    """Test list all conversations"""
    temp_db.create_conversation(title="Chat 1")
    temp_db.create_conversation(title="Chat 2")
    temp_db.create_conversation(title="Chat 3")
    
    conversations = temp_db.list_conversations()
    assert len(conversations) == 3
    assert all(isinstance(c, Conversation) for c in conversations)
