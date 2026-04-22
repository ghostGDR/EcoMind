import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

@dataclass
class Message:
    """Message data structure"""
    id: Optional[int]
    conversation_id: int
    role: str  # 'user' or 'assistant'
    content: str
    created_at: str
    sources: Optional[List[Dict[str, Any]]] = None

@dataclass
class Conversation:
    """Conversation data structure"""
    id: Optional[int]
    title: str
    created_at: str
    messages: List[Message] = field(default_factory=list)

class ConversationStore:
    """SQLite-based conversation storage"""
    
    def __init__(self, db_path: str = "./data/conversations.db"):
        """Initialize database connection and create schema"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_schema()
    
    def _create_schema(self):
        """Create database schema"""
        cursor = self.conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Conversations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
        ''')
        
        # Message sources table (for citation tracking)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS message_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            document_path TEXT NOT NULL,
            chunk_text TEXT,
            relevance_score REAL,
            FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
        )
        ''')
        
        self.conn.commit()
    
    def create_conversation(self, title: str = "New Conversation") -> int:
        """Create a new conversation"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (title) VALUES (?)",
            (title,)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def add_message(
        self, 
        conversation_id: int, 
        role: str, 
        content: str,
        sources: Optional[List[Dict[str, Any]]] = None
    ) -> int:
        """Add a message to a conversation"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content)
        )
        message_id = cursor.lastrowid
        
        # Add sources if provided
        if sources:
            for source in sources:
                cursor.execute(
                    """INSERT INTO message_sources 
                       (message_id, document_path, chunk_text, relevance_score) 
                       VALUES (?, ?, ?, ?)""",
                    (
                        message_id,
                        source.get("document_path"),
                        source.get("chunk_text"),
                        source.get("relevance_score")
                    )
                )
        
        self.conn.commit()
        return message_id
    
    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Retrieve a conversation with all messages"""
        cursor = self.conn.cursor()
        
        # Get conversation
        cursor.execute(
            "SELECT * FROM conversations WHERE id = ?",
            (conversation_id,)
        )
        conv_row = cursor.fetchone()
        if not conv_row:
            return None
        
        # Get messages
        cursor.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at",
            (conversation_id,)
        )
        message_rows = cursor.fetchall()
        
        messages = []
        for msg_row in message_rows:
            # Get sources for this message
            cursor.execute(
                "SELECT * FROM message_sources WHERE message_id = ?",
                (msg_row["id"],)
            )
            source_rows = cursor.fetchall()
            sources = [dict(row) for row in source_rows] if source_rows else None
            
            messages.append(Message(
                id=msg_row["id"],
                conversation_id=msg_row["conversation_id"],
                role=msg_row["role"],
                content=msg_row["content"],
                created_at=msg_row["created_at"],
                sources=sources
            ))
        
        return Conversation(
            id=conv_row["id"],
            title=conv_row["title"],
            created_at=conv_row["created_at"],
            messages=messages
        )
    
    def list_conversations(self) -> List[Conversation]:
        """List all conversations (without messages)"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM conversations ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        return [
            Conversation(
                id=row["id"],
                title=row["title"],
                created_at=row["created_at"],
                messages=[]
            )
            for row in rows
        ]
    
    def close(self):
        """Close database connection"""
        self.conn.close()
