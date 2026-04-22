"""Conversation management REST API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from src.api.dependencies import get_conversation_manager
from src.api.models import (
    CreateConversationRequest,
    CreateConversationResponse,
    ConversationListResponse,
    ConversationListItem,
    ConversationResponse,
    MessageResponse
)
from src.rag.conversation_manager import ConversationManager
import logging

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/conversations",
    tags=["conversations"]
)


@router.post("", response_model=CreateConversationResponse, status_code=201)
async def create_conversation(
    request: CreateConversationRequest,
    manager: ConversationManager = Depends(get_conversation_manager)
):
    """
    Create a new conversation
    
    Args:
        request: CreateConversationRequest with optional title
        manager: ConversationManager dependency
    
    Returns:
        CreateConversationResponse with conversation id, title, and created_at
    
    Raises:
        HTTPException 500: If conversation creation fails
    """
    try:
        # Create new conversation
        conversation_id = manager.start_conversation(title=request.title)
        
        # Retrieve conversation metadata
        conversation = manager.get_conversation(conversation_id)
        
        if conversation is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve created conversation"
            )
        
        # Return conversation metadata
        return CreateConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at
        )
    
    except Exception as e:
        logger.error(f"Failed to create conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create conversation: {str(e)}"
        )


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    manager: ConversationManager = Depends(get_conversation_manager)
):
    """
    List all conversations
    
    Args:
        manager: ConversationManager dependency
    
    Returns:
        ConversationListResponse with list of conversations and total count
        Conversations are ordered by created_at DESC (newest first)
    """
    try:
        # Get all conversations from manager
        conversations = manager.list_conversations()
        
        # Transform to response format
        conversation_items = [
            ConversationListItem(
                id=conv['id'],
                title=conv['title'],
                created_at=conv['created_at'],
                message_count=conv['message_count']
            )
            for conv in conversations
        ]
        
        return ConversationListResponse(
            conversations=conversation_items,
            total=len(conversation_items)
        )
    
    except Exception as e:
        logger.error(f"Failed to list conversations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list conversations: {str(e)}"
        )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    manager: ConversationManager = Depends(get_conversation_manager)
):
    """
    Get conversation details with all messages
    
    Args:
        conversation_id: ID of the conversation to retrieve
        manager: ConversationManager dependency
    
    Returns:
        ConversationResponse with full conversation including all messages
    
    Raises:
        HTTPException 404: If conversation not found
        HTTPException 500: If retrieval fails
    """
    try:
        # Retrieve conversation from manager
        conversation = manager.get_conversation(conversation_id)
        
        # Check if conversation exists
        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Transform Conversation dataclass to ConversationResponse
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            messages=[
                MessageResponse(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at,
                    sources=msg.sources
                )
                for msg in conversation.messages
            ]
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (404)
        raise
    
    except Exception as e:
        logger.error(f"Failed to get conversation {conversation_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve conversation: {str(e)}"
        )
