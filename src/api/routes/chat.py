"""SSE streaming chat endpoint"""
import asyncio
import json
import logging
from typing import AsyncGenerator
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from src.api.dependencies import get_conversation_manager
from src.api.models import ChatRequest
from src.rag.conversation_manager import ConversationManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


async def stream_chat_response(
    conversation_id: int,
    message: str,
    manager: ConversationManager
) -> AsyncGenerator[str, None]:
    """
    Generate SSE stream for chat response
    
    Yields SSE-formatted events:
    - Multiple "data: {type: answer, content: chunk}" events for answer chunks
    - One "data: {type: sources, content: [...]}" event for sources
    - One "data: {type: done, content: ''}" event to signal completion
    - On error: "data: {type: error, content: error_message}" event
    
    Args:
        conversation_id: ID of the conversation
        message: User's message
        manager: ConversationManager instance
    
    Yields:
        SSE-formatted event strings
    """
    try:
        # Get full response from ConversationManager
        response = manager.send_message(conversation_id, message)
        answer = response["answer"]
        sources = response["sources"]
        
        # Stream answer in chunks (simulate token-by-token streaming)
        # Split by characters for smooth progressive display
        chunk_size = 20  # characters per chunk
        for i in range(0, len(answer), chunk_size):
            chunk = answer[i:i+chunk_size]
            event_data = json.dumps({"type": "answer", "content": chunk}, ensure_ascii=False)
            yield f"data: {event_data}\n\n"
            await asyncio.sleep(0.05)  # Small delay for visual effect
        
        # Send sources after answer completes
        sources_data = json.dumps({"type": "sources", "content": sources}, ensure_ascii=False)
        yield f"data: {sources_data}\n\n"
        
        # Send completion event
        done_data = json.dumps({"type": "done", "content": ""}, ensure_ascii=False)
        yield f"data: {done_data}\n\n"
        
    except ValueError as e:
        # Invalid conversation_id or other validation error
        logger.warning(f"Chat stream error: {str(e)}")
        error_data = json.dumps({"type": "error", "content": str(e)}, ensure_ascii=False)
        yield f"data: {error_data}\n\n"
    except Exception as e:
        # Unexpected error - log details but send generic message
        logger.error(f"Unexpected error in chat stream: {str(e)}", exc_info=True)
        error_data = json.dumps({"type": "error", "content": "Internal server error"}, ensure_ascii=False)
        yield f"data: {error_data}\n\n"


@router.post("/")
async def chat(
    request: ChatRequest,
    manager: ConversationManager = Depends(get_conversation_manager)
):
    """
    Send message and stream response via SSE
    
    POST /api/chat
    
    Request body:
        {
            "conversation_id": 1,
            "message": "TikTok 广告投放有什么技巧？"
        }
    
    Response: text/event-stream with SSE events:
        data: {"type": "answer", "content": "chunk1"}
        
        data: {"type": "answer", "content": "chunk2"}
        
        data: {"type": "sources", "content": [...]}
        
        data: {"type": "done", "content": ""}
        
    Error handling:
        - Invalid conversation_id: sends error event in stream
        - Empty message: FastAPI validation error (422)
    
    Args:
        request: ChatRequest with conversation_id and message
        manager: ConversationManager dependency
    
    Returns:
        StreamingResponse with text/event-stream content type
    """
    return StreamingResponse(
        stream_chat_response(
            request.conversation_id,
            request.message,
            manager
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
