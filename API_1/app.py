"""
Phase 1: PDF Document Upload, Chunking, and Embedding Storage - OpenAI Version
FastAPI application with OpenAI embeddings support.
"""

import logging
import os
import time
import uuid
from typing import List
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from dotenv import load_dotenv
import json
import numpy as np
from openai import OpenAI
# Load environment variables from .env file
load_dotenv()

from db import get_db, create_tables, Base
from models import Document, Chunk
from schemas import (
    DocumentCreate, DocumentResponse, DocumentCreateResponse,
    UploadResponse, HealthResponse,ErrorResponse, QueryRequest, 
    QueryResponse, RetrievedChunk, UserQueryHistoryItem,UserQueryHistoryResponse
)
from pdf_processor import PDFProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserQuery(Base):
    """Store user queries for tracking"""
    __tablename__ = "user_queries"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    selected_documents = Column(Text)  # JSON array of document IDs
    embedding = Column(Text)  # JSON array
    created_at = Column(DateTime, default=datetime.utcnow)


class QueryResponseModel(Base):
    """Store query responses"""
    __tablename__ = "query_responses"
    
    id = Column(String, primary_key=True)
    query_id = Column(String, ForeignKey("user_queries.id"))
    response_text = Column(Text)
    retrieved_chunks = Column(Text)  # JSON array of chunk IDs
    created_at = Column(DateTime, default=datetime.utcnow)

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

# ---------------------------API 3-----------------------------------

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))

@app.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Complete RAG pipeline:
    1. Record user ID and query
    2. Generate query embedding
    3. Perform semantic similarity search
    4. Retrieve relevant chunks
    5. Generate answer using OpenAI
    6. Return formatted response
    """
    start_time = time.time()
    
    try:
        query_id = str(uuid.uuid4())
        logger.info(f"Processing query {query_id} from user {request.user_id}")
        
        # Step 1: Generate query embedding
        embedding_response = openai_client.embeddings.create(
            model=openai_model,
            input=request.query
        )
        query_embedding = embedding_response.data[0].embedding
        
        # Step 2: Filter documents (if specified)
        chunks_query = db.query(Chunk).join(Document)
        
        if request.document_ids:
            chunks_query = chunks_query.filter(
                Chunk.document_id.in_(request.document_ids)
            )
            logger.info(f"Filtering to {len(request.document_ids)} selected documents")
        
        # Get all eligible chunks with embeddings
        chunks = chunks_query.filter(
            Chunk.embedding.isnot(None),
            Document.status == "ready"
        ).all()
        
        if not chunks:
            raise HTTPException(
                status_code=404, 
                detail="No documents with embeddings found"
            )
        
        # Step 3: Calculate semantic similarity
        similarities = []
        for chunk in chunks:
            chunk_embedding = json.loads(chunk.embedding)
            similarity = cosine_similarity(query_embedding, chunk_embedding)
            
            similarities.append({
                "chunk": chunk,
                "similarity": similarity
            })
        
        # Sort by similarity and get top K
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        top_chunks = similarities[:request.top_k]
        
        logger.info(f"Retrieved {len(top_chunks)} relevant chunks")
        
        # Step 4: Build context for OpenAI
        context_parts = []
        retrieved_chunks = []
        
        for item in top_chunks:
            chunk = item["chunk"]
            document = db.query(Document).filter(
                Document.id == chunk.document_id
            ).first()
            
            context_parts.append(
                f"[Document: {document.name}, Page {chunk.page_number}]\n{chunk.text}"
            )
            
            retrieved_chunks.append(RetrievedChunk(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                document_name=document.name,
                page_number=chunk.page_number,
                text=chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
                similarity_score=round(item["similarity"], 4)
            ))
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Step 5: Generate answer using OpenAI
        chat_response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on the provided document context. Always cite which document and page your information comes from."
                },
                {
                    "role": "user",
                    "content": f"Context from documents:\n\n{context}\n\nQuestion: {request.query}\n\nPlease provide a detailed answer based on the context above."
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        answer = chat_response.choices[0].message.content
        
        # Step 6: Store query and response in database
        db_query = UserQuery(
            id=query_id,
            user_id=request.user_id,
            query_text=request.query,
            selected_documents=json.dumps(request.document_ids) if request.document_ids else None,
            embedding=json.dumps(query_embedding)
        )
        db.add(db_query)
        
        db_response = QueryResponseModel(
            id=str(uuid.uuid4()),
            query_id=query_id,
            response_text=answer,
            retrieved_chunks=json.dumps([chunk.chunk_id for chunk in retrieved_chunks])
        )
        db.add(db_response)
        db.commit()
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(f"Query {query_id} completed in {processing_time_ms}ms")
        
        return QueryResponse(
            query_id=query_id,
            query=request.query,
            answer=answer,
            retrieved_chunks=retrieved_chunks,
            processing_time_ms=processing_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{user_id}/queries", response_model=UserQueryHistoryResponse)
async def get_user_queries(
    user_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Retrieve query history for a user."""
    queries = db.query(UserQuery).filter(
        UserQuery.user_id == user_id
    ).order_by(
        UserQuery.created_at.desc()
    ).limit(limit).all()
    
    return UserQueryHistoryResponse(
        user_id=user_id,
        query_count=len(queries),
        queries=[
            UserQueryHistoryItem(
                query_id=q.id,
                query=q.query_text,
                timestamp=q.created_at.isoformat()
            )
            for q in queries
        ]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
