"""Dependency injection for FastAPI endpoints"""
from typing import Optional
import threading

from src.rag.conversation_manager import ConversationManager
from src.search.search_engine import SearchEngine
from src.storage.document_store import DocumentStore
from src.storage.conversation_store import ConversationStore
from src.rag.query_engine import QueryEngine
from src.storage.vector_store import HenryVectorStore

# Module-level cache for singleton instances
_vector_store: Optional[HenryVectorStore] = None
_search_engine: Optional[SearchEngine] = None
_query_engine: Optional[QueryEngine] = None
_conversation_store: Optional[ConversationStore] = None
_conversation_manager: Optional[ConversationManager] = None
_document_store: Optional[DocumentStore] = None

# Lock for thread-safe singleton initialization
_init_lock = threading.RLock()


def get_vector_store() -> HenryVectorStore:
    """Get or create HenryVectorStore singleton"""
    global _vector_store
    if _vector_store is None:
        with _init_lock:
            if _vector_store is None:
                _vector_store = HenryVectorStore()
    return _vector_store


def get_search_engine() -> SearchEngine:
    """
    Get or create SearchEngine singleton instance
    
    Returns:
        SearchEngine instance with shared vector store
    """
    global _search_engine
    
    if _search_engine is None:
        with _init_lock:
            if _search_engine is None:
                # Use shared vector store singleton
                vector_store = get_vector_store()
                _search_engine = SearchEngine(vector_store=vector_store)
    
    return _search_engine


def get_query_engine() -> QueryEngine:
    """Get or create QueryEngine singleton"""
    global _query_engine
    if _query_engine is None:
        with _init_lock:
            if _query_engine is None:
                # Use shared search engine singleton
                search_engine = get_search_engine()
                _query_engine = QueryEngine(search_engine=search_engine)
    return _query_engine


def get_conversation_store() -> ConversationStore:
    """Get or create ConversationStore singleton"""
    global _conversation_store
    if _conversation_store is None:
        with _init_lock:
            if _conversation_store is None:
                _conversation_store = ConversationStore()
    return _conversation_store


def get_conversation_manager() -> ConversationManager:
    """
    Get or create ConversationManager singleton instance
    
    Returns:
        ConversationManager instance with shared QueryEngine and ConversationStore
    """
    global _conversation_manager
    
    if _conversation_manager is None:
        with _init_lock:
            if _conversation_manager is None:
                # Use shared singletons
                query_engine = get_query_engine()
                conversation_store = get_conversation_store()
                
                # Create ConversationManager
                _conversation_manager = ConversationManager(
                    query_engine=query_engine,
                    conversation_store=conversation_store,
                    max_history_messages=10
                )
    
    return _conversation_manager


def get_document_store() -> DocumentStore:
    """
    Get or create DocumentStore singleton instance
    
    Returns:
        DocumentStore instance from environment configuration
    """
    global _document_store
    
    if _document_store is None:
        with _init_lock:
            if _document_store is None:
                _document_store = DocumentStore.from_env()
    
    return _document_store
