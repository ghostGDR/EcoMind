"""Pydantic models for API request/response validation"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str


class MessageResponse(BaseModel):
    """Message response model for conversation messages"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    role: str
    content: str
    created_at: str
    sources: Optional[List[Dict[str, Any]]] = None


class ConversationResponse(BaseModel):
    """Conversation response model with all messages"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    created_at: str
    messages: List[MessageResponse]


class ChatRequest(BaseModel):
    """Chat request model for SSE streaming endpoint"""
    conversation_id: int
    message: str


class SourceResponse(BaseModel):
    """Source response model for document citations"""
    document_path: str
    chunk_text: str
    relevance_score: float


class DocumentResponse(BaseModel):
    """Document metadata response model"""
    filename: str
    file_path: str
    topic: str
    modified_at: str
    size_kb: float


class DocumentListResponse(BaseModel):
    """Document list response with total count"""
    documents: List[DocumentResponse]
    total: int


class TopicDocumentsResponse(BaseModel):
    """Documents grouped by topic"""
    topics: Dict[str, List[DocumentResponse]]


class SearchRequest(BaseModel):
    """Search request parameters"""
    query: str
    top_k: int = 5
    min_score: float = 0.5


class SearchResultItem(BaseModel):
    """Single search result item"""
    content: str
    score: float
    document_path: str
    chunk_id: str


class SearchResponse(BaseModel):
    """Search response with results and metadata"""
    results: List[SearchResultItem]
    query: str
    total: int


class CreateConversationRequest(BaseModel):
    """Request model for creating a new conversation"""
    title: str = "新对话"


class CreateConversationResponse(BaseModel):
    """Response model for created conversation"""
    id: int
    title: str
    created_at: str


class ConversationListItem(BaseModel):
    """Single conversation item in list response"""
    id: int
    title: str
    created_at: str
    message_count: int


class ConversationListResponse(BaseModel):
    """Response model for conversation list"""
    conversations: List[ConversationListItem]
    total: int


class ChatRequest(BaseModel):
    """Chat request model for SSE streaming endpoint"""
    conversation_id: int
    message: str


class SourceResponse(BaseModel):
    """Source response model for document citations"""
    document_path: str
    chunk_text: str
    relevance_score: float
