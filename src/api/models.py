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
