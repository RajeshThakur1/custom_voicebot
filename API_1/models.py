"""Simplified SQLAlchemy models for Phase 1: Documents and Chunks with Embeddings."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Document(Base):
    """Document metadata - tracks uploaded PDFs."""
    
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)  # UUID
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # Path to uploaded PDF
    num_pages = Column(Integer, default=0)
    status = Column(String, default="pending")  # pending, processing, ready, error
    created_at = Column(DateTime, default=datetime.utcnow)


class Chunk(Base):
    """Text chunks with embeddings - the core storage for Phase 1."""
    
    __tablename__ = "chunks"
    
    id = Column(String, primary_key=True)  # Format: {document_id}_{page}_{chunk_order}
    document_id = Column(String, nullable=False)
    page_number = Column(Integer, nullable=False)
    chunk_order = Column(Integer, nullable=False)  # Order within the document
    text = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    
    # Embedding storage - this is key for Phase 1
    embedding = Column(JSON, nullable=True)  # Store as JSON array
    embedding_model = Column(String, default="text-embedding-3-small")  # Track which model was used
    
    created_at = Column(DateTime, default=datetime.utcnow)
