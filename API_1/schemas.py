"""Simplified Pydantic schemas for Phase 1 API."""

from datetime import datetime
from typing import Optional,List
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


class QueryRequest(BaseModel):
    """Request to query documents with RAG."""
    user_id: str
    query: str
    document_ids: Optional[List[str]] = None  
    top_k: int = 5  
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "query": "What is machine learning?",
                "document_ids": ["doc-abc-123", "doc-def-456"],
                "top_k": 5
            }
        }


class RetrievedChunk(BaseModel):
    """Information about a retrieved document chunk."""
    chunk_id: str
    document_id: str
    document_name: str
    page_number: int
    text: str
    similarity_score: float


class QueryResponse(BaseModel):
    """Response after processing a query with RAG."""
    query_id: str
    query: str
    answer: str
    retrieved_chunks: List[RetrievedChunk]
    processing_time_ms: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "query-xyz-789",
                "query": "What is machine learning?",
                "answer": "Machine learning is a subset of artificial intelligence...",
                "retrieved_chunks": [
                    {
                        "chunk_id": "doc-abc-123_1_0",
                        "document_id": "doc-abc-123",
                        "document_name": "AI Textbook.pdf",
                        "page_number": 1,
                        "text": "Machine learning involves...",
                        "similarity_score": 0.8765
                    }
                ],
                "processing_time_ms": 1234
            }
        }


class UserQueryHistoryItem(BaseModel):
    """Single query from user history."""
    query_id: str
    query: str
    timestamp: str


class UserQueryHistoryResponse(BaseModel):
    """Response with user's query history."""
    user_id: str
    query_count: int
    queries: List[UserQueryHistoryItem]