"""Dependency injection for FastAPI endpoints"""
from typing import Optional
import threading

from src.rag.conversation_manager import ConversationManager
from src.search.search_engine import SearchEngine
from src.storage.document_store import DocumentStore
from src.storage.conversation_store import ConversationStore
from src.rag.query_engine import QueryEngine
from src.storage.vector_store import EcoMindVectorStore

from src.api.config import load_settings, Settings
from src.llm.llm_client import LLMClient

# Module-level cache for singleton instances
_vector_store: Optional[EcoMindVectorStore] = None
_search_engine: Optional[SearchEngine] = None
_query_engine: Optional[QueryEngine] = None
_conversation_store: Optional[ConversationStore] = None
_conversation_manager: Optional[ConversationManager] = None
_document_store: Optional[DocumentStore] = None

# Lock for thread-safe singleton initialization
_init_lock = threading.RLock()


def reset_dependencies():
    """Clear all singleton instances to force re-initialization with new config"""
    global _vector_store, _search_engine, _query_engine, _conversation_store, _conversation_manager, _document_store
    with _init_lock:
        _vector_store = None
        _search_engine = None
        _query_engine = None
        _conversation_store = None
        _conversation_manager = None
        _document_store = None


def get_vector_store() -> EcoMindVectorStore:
    """Get or create EcoMindVectorStore singleton"""
    global _vector_store
    if _vector_store is None:
        with _init_lock:
            if _vector_store is None:
                _vector_store = EcoMindVectorStore()
    return _vector_store


def get_search_engine() -> SearchEngine:
    """Get or create SearchEngine singleton instance"""
    global _search_engine
    if _search_engine is None:
        with _init_lock:
            if _search_engine is None:
                vector_store = get_vector_store()
                _search_engine = SearchEngine(vector_store=vector_store)
    return _search_engine


def get_query_engine() -> QueryEngine:
    """Get or create QueryEngine singleton"""
    global _query_engine
    if _query_engine is None:
        with _init_lock:
            if _query_engine is None:
                settings = load_settings()
                search_engine = get_search_engine()
                
                # Initialize LLM client with current settings
                llm_client = LLMClient(
                    provider=settings.llm_provider,
                    model=settings.llm_model,
                    api_key=settings.llm_api_key,
                    base_url=settings.llm_base_url
                )
                
                _query_engine = QueryEngine(
                    search_engine=search_engine,
                    llm_client=llm_client
                )
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
    """Get or create ConversationManager singleton instance"""
    global _conversation_manager
    if _conversation_manager is None:
        with _init_lock:
            if _conversation_manager is None:
                query_engine = get_query_engine()
                conversation_store = get_conversation_store()
                
                _conversation_manager = ConversationManager(
                    query_engine=query_engine,
                    conversation_store=conversation_store,
                    max_history_messages=10
                )
    return _conversation_manager


def get_document_store() -> DocumentStore:
    """Get or create DocumentStore singleton instance"""
    global _document_store
    if _document_store is None:
        with _init_lock:
            if _document_store is None:
                settings = load_settings()
                _document_store = DocumentStore(base_path=settings.wiki_path)
    return _document_store
