"""
Phase 1: PDF Document Upload, Chunking, and Embedding Storage - OpenAI Version
FastAPI application with OpenAI embeddings support.
"""

import logging
import os
import time
import uuid
from typing import List

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from db import get_db, create_tables
from models import Document, Chunk
from schemas import (
    DocumentCreate, DocumentResponse, DocumentCreateResponse,
    UploadResponse, HealthResponse
)
from pdf_processor import PDFProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Phase 1: PDF Document Processing API - OpenAI Version",
    description="Upload PDFs, extract text, create chunks, and generate OpenAI embeddings",
    version="1.0.0-openai"
)

# Initialize PDF processor with OpenAI configuration
use_openai = os.getenv("USE_OPENAI_EMBEDDINGS", "true").lower() == "true"
openai_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
openai_api_key = os.getenv("OPENAI_API_KEY")

if use_openai and not openai_api_key:
    logger.error("OPENAI_API_KEY environment variable is required when USE_OPENAI_EMBEDDINGS=true")
    raise ValueError("OPENAI_API_KEY environment variable is required")

pdf_processor = PDFProcessor(
    chunk_size=600,
    overlap=80,
    embedding_model=openai_model,
    use_openai=use_openai,
    openai_api_key=openai_api_key
)

# Ensure upload directory exists
os.makedirs("./data/uploads", exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Initializing OpenAI-powered PDF processing API...")
    create_tables()
    logger.info(f"Phase 1 OpenAI API ready! Using {'OpenAI' if use_openai else 'local'} embeddings")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()


@app.post("/documents", response_model=DocumentCreateResponse)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):
    """Create a new document entry with unique ID."""
    try:
        document_id = str(uuid.uuid4())
        
        db_document = Document(
            id=document_id,
            name=document.name,
            file_path="",  # Will be set during upload
            status="pending"
        )
        
        db.add(db_document)
        db.commit()
        
        logger.info(f"Created document {document_id}: {document.name}")
        return DocumentCreateResponse(document_id=document_id)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents", response_model=List[DocumentResponse])
async def list_documents(db: Session = Depends(get_db)):
    """List all documents."""
    try:
        documents = db.query(Document).order_by(Document.created_at.desc()).all()
        return [DocumentResponse.model_validate(doc) for doc in documents]
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/{document_id}/upload", response_model=UploadResponse)
async def upload_pdf(
    document_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a PDF file with OpenAI embeddings:
    1. Save the PDF file
    2. Extract text and create chunks
    3. Generate OpenAI embeddings
    4. Store everything in SQLite
    """
    start_time = time.time()
    
    try:
        # Check if document exists
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Update document status
        document.status = "processing"
        db.commit()
        
        # Save uploaded file
        file_path = f"./data/uploads/{document_id}.pdf"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        document.file_path = file_path
        db.commit()
        logger.info(f"Saved PDF: {file.filename} -> {file_path}")
        
        # Process PDF: extract text, create chunks, generate embeddings
        logger.info(f"Processing PDF for document {document_id} with OpenAI embeddings")
        result = pdf_processor.process_pdf(file_path, document_id)
        
        if not result["chunks"]:
            document.status = "error"
            db.commit()
            raise HTTPException(status_code=400, detail="No text could be extracted from PDF")
        
        # Update document info
        document.num_pages = result["num_pages"]
        
        # Clear existing chunks for this document (in case of re-upload)
        db.query(Chunk).filter(Chunk.document_id == document_id).delete()
        
        # Save chunks with embeddings to database
        chunks_created = 0
        embeddings_generated = 0
        
        for chunk_data in result["chunks"]:
            # Create deterministic chunk ID
            chunk_id = f"{document_id}_{chunk_data['page']}_{chunk_data['order']}"
            
            # Create database record
            db_chunk = Chunk(
                id=chunk_id,
                document_id=document_id,
                page_number=chunk_data["page"],
                chunk_order=chunk_data["order"],
                text=chunk_data["text"],
                token_count=chunk_data["token_count"],
                embedding=chunk_data["embedding"],  # Store as JSON
                embedding_model=result["embedding_model"]
            )
            db.add(db_chunk)
            chunks_created += 1
            
            if chunk_data["embedding"]:
                embeddings_generated += 1
        
        # Mark as ready
        document.status = "ready"
        db.commit()
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(f"OpenAI processing complete for {document_id}: "
                   f"{result['num_pages']} pages, {chunks_created} chunks, "
                   f"{embeddings_generated} embeddings, {processing_time_ms}ms")
        
        return UploadResponse(
            document_id=document_id,
            filename=file.filename,
            pages=result["num_pages"],
            chunks_created=chunks_created,
            embeddings_generated=embeddings_generated,
            status="ready",
            processing_time_ms=processing_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        
        # Update document status to error
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = "error"
                db.commit()
        except:
            pass
        
        logger.error(f"Error during OpenAI PDF processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents/{document_id}")
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get document details including chunk count."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Count chunks
    chunk_count = db.query(Chunk).filter(Chunk.document_id == document_id).count()
    
    response = DocumentResponse.model_validate(document)
    return {
        **response.model_dump(),
        "chunk_count": chunk_count
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
