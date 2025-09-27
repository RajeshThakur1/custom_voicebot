"""Simplified Pydantic schemas for Phase 1 API."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DocumentCreate(BaseModel):
    """Request to create a new document."""
    name: str


class DocumentResponse(BaseModel):
    """Document information response."""
    id: str
    name: str
    status: str
    num_pages: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentCreateResponse(BaseModel):
    """Response after creating a document."""
    document_id: str
    message: str = "Document created successfully. Upload PDF using /documents/{document_id}/upload endpoint."


class UploadResponse(BaseModel):
    """Response after PDF upload and processing."""
    document_id: str
    filename: str
    pages: int
    chunks_created: int
    embeddings_generated: int
    status: str
    processing_time_ms: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    timestamp: datetime = datetime.utcnow()


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
