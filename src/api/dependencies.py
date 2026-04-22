"""Dependency injection for FastAPI endpoints"""
from typing import Optional
from src.rag.conversation_manager import ConversationManager
from src.search.search_engine import SearchEngine
from src.storage.document_store import DocumentStore
from src.storage.conversation_store import ConversationStore
from src.rag.query_engine import QueryEngine

# Module-level cache for singleton instances
_conversation_manager: Optional[ConversationManager] = None
_search_engine: Optional[SearchEngine] = None
_document_store: Optional[DocumentStore] = None


def get_conversation_manager() -> ConversationManager:
    """
    Get or create ConversationManager singleton instance
    
    Returns:
        ConversationManager instance with QueryEngine and ConversationStore
    """
    global _conversation_manager
    
    if _conversation_manager is None:
        # Initialize dependencies
        # QueryEngine creates its own SearchEngine internally
        query_engine = QueryEngine()
        conversation_store = ConversationStore()
        
        # Create ConversationManager
        _conversation_manager = ConversationManager(
            query_engine=query_engine,
            conversation_store=conversation_store,
            max_history_messages=10
        )
    
    return _conversation_manager


def get_search_engine() -> SearchEngine:
    """
    Get or create SearchEngine singleton instance
    
    Returns:
        SearchEngine instance with existing vector store
    """
    global _search_engine
    
    if _search_engine is None:
        # SearchEngine creates its own vector store
        _search_engine = SearchEngine()
    
    return _search_engine


def get_document_store() -> DocumentStore:
    """
    Get or create DocumentStore singleton instance
    
    Returns:
        DocumentStore instance from environment configuration
    """
    global _document_store
    
    if _document_store is None:
        _document_store = DocumentStore.from_env()
    
    return _document_store
