"""Multi-turn conversation manager with history injection"""
from typing import Dict, Any, Optional
from src.rag.query_engine import QueryEngine
from src.storage.conversation_store import ConversationStore, Conversation
import logging

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages multi-turn conversations with context injection and persistence.
    
    Wraps QueryEngine to inject conversation history into queries, enabling
    follow-up questions like "那具体怎么做？" to reference prior exchanges.
    """
    
    def __init__(
        self,
        query_engine: QueryEngine,
        conversation_store: ConversationStore,
        max_history_messages: int = 10
    ):
        """
        Initialize ConversationManager
        
        Args:
            query_engine: QueryEngine instance for RAG queries
            conversation_store: ConversationStore instance for persistence
            max_history_messages: Maximum number of messages to include in context (default: 10)
                                  Prevents context window overflow in long conversations
        """
        self.query_engine = query_engine
        self.conversation_store = conversation_store
        self.max_history_messages = max_history_messages
    
    def start_conversation(self, title: str = "新对话") -> int:
        """
        Start a new conversation
        
        Args:
            title: Conversation title (default: "新对话")
        
        Returns:
            conversation_id: ID of the newly created conversation
        """
        conversation_id = self.conversation_store.create_conversation(title)
        logger.info(f"Started new conversation: {conversation_id} - {title}")
        return conversation_id
    
    def send_message(
        self,
        conversation_id: int,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Send a message in a conversation with history context injection
        
        Args:
            conversation_id: ID of the conversation
            user_message: User's message/question
        
        Returns:
            Dictionary with:
                - answer: str (Henry's response)
                - sources: List[Dict] (Retrieved documents)
                - conversation_id: int (Conversation ID)
                - has_sources: bool (Whether sources were found)
        """
        # Step 1: Validate conversation exists (T-05-01 mitigation)
        conversation = self.conversation_store.get_conversation(conversation_id)
        if conversation is None:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Step 2: Retrieve conversation history
        history = conversation.messages
        
        # Step 3: Truncate history to last N messages (context window management)
        if len(history) > self.max_history_messages:
            recent_history = history[-self.max_history_messages:]
        else:
            recent_history = history
        
        # Step 4: Format query with history context
        if recent_history:
            # Inject previous Q&A pairs as context
            formatted_query = self._format_query_with_history(recent_history, user_message)
        else:
            # First message - no history to inject
            formatted_query = user_message
        
        # Step 5: Call QueryEngine with formatted query
        response = self.query_engine.query(formatted_query)
        
        # Step 6: Persist user message to database
        self.conversation_store.add_message(
            conversation_id=conversation_id,
            role='user',
            content=user_message,
            sources=None
        )
        
        # Step 7: Transform sources to match ConversationStore format
        transformed_sources = self._transform_sources(response.get('sources', []))
        
        # Step 8: Persist assistant response to database with sources
        self.conversation_store.add_message(
            conversation_id=conversation_id,
            role='assistant',
            content=response['answer'],
            sources=transformed_sources
        )
        
        # Step 9: Return response with conversation_id
        return {
            'answer': response['answer'],
            'sources': response.get('sources', []),
            'conversation_id': conversation_id,
            'has_sources': response.get('has_sources', False)
        }
    
    def get_history(self, conversation_id: int) -> Optional[Conversation]:
        """
        Retrieve full conversation history
        
        Args:
            conversation_id: ID of the conversation
        
        Returns:
            Conversation object with all messages, or None if not found
        """
        return self.conversation_store.get_conversation(conversation_id)
    
    def list_conversations(self) -> list:
        """
        List all conversations with metadata
        
        Returns:
            List of dicts with: {id, title, created_at, message_count}
            Ordered by created_at DESC (newest first)
        """
        conversations = self.conversation_store.list_conversations()
        
        # Transform to frontend-friendly format with message counts
        return [
            {
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at,
                'message_count': len(conv.messages)
            }
            for conv in conversations
        ]
    
    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """
        Retrieve full conversation with all messages
        
        Args:
            conversation_id: ID of the conversation
        
        Returns:
            Conversation object with all messages, or None if not found
        """
        return self.conversation_store.get_conversation(conversation_id)
    
    def _format_query_with_history(
        self,
        history: list,
        current_message: str
    ) -> str:
        """
        Format query with conversation history as context
        
        Args:
            history: List of Message objects from conversation
            current_message: Current user message
        
        Returns:
            Formatted query string with history context
        """
        # Build history context
        history_parts = ["之前的对话："]
        
        for message in history:
            if message.role == 'user':
                history_parts.append(f"用户：{message.content}")
            elif message.role == 'assistant':
                history_parts.append(f"Henry：{message.content}")
        
        # Combine history with current question
        formatted_query = "\n".join(history_parts)
        formatted_query += f"\n\n当前问题：{current_message}"
        
        return formatted_query
    
    def _transform_sources(self, sources: list) -> list:
        """
        Transform QueryEngine sources to ConversationStore format
        
        Args:
            sources: List of source dicts from QueryEngine with structure:
                     {content: str, score: float, metadata: dict, node_id: str}
        
        Returns:
            List of source dicts for ConversationStore with structure:
            {document_path: str, chunk_text: str, relevance_score: float}
        """
        transformed = []
        for source in sources:
            transformed.append({
                'document_path': source.get('metadata', {}).get('file_path', 'unknown'),
                'chunk_text': source.get('content', ''),
                'relevance_score': source.get('score', 0.0)
            })
        return transformed
