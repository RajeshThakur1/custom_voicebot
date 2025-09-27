"""
Phase 1: PDF Processing - Extract text, chunk, and generate embeddings - OpenAI Version
Supports both local sentence-transformers and OpenAI API embeddings.
"""

import logging
import re
import os
from typing import List, Dict, Any, Optional
import pypdf
from pdfminer.high_level import extract_text as pdfminer_extract_text
import tiktoken
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles all PDF processing: text extraction, chunking, and embedding generation."""
    
    def __init__(self, 
                 chunk_size: int = 600, 
                 overlap: int = 80, 
                 embedding_model: str = "text-embedding-3-small",
                 use_openai: bool = True,
                 openai_api_key: Optional[str] = None):
        
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.embedding_model_name = embedding_model
        self.use_openai = use_openai
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize tokenizer for chunking
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Initialize embedding model (lazy loading)
        self._embedding_model = None
        self._openai_client = None
    
    @property
    def embedding_model(self):
        """Lazy load the embedding model."""
        if self.use_openai:
            if self._openai_client is None:
                logger.info("Initializing OpenAI client...")
                try:
                    from openai import OpenAI
                    self._openai_client = OpenAI(api_key=self.openai_api_key)
                    logger.info("OpenAI client initialized successfully")
                except ImportError:
                    raise ImportError("OpenAI package not installed. Run: pip install openai")
                except Exception as e:
                    raise ValueError(f"Failed to initialize OpenAI client: {e}")
            return self._openai_client
        else:
            if self._embedding_model is None:
                logger.info(f"Loading local embedding model: {self.embedding_model_name}")
                try:
                    from sentence_transformers import SentenceTransformer
                    self._embedding_model = SentenceTransformer(self.embedding_model_name)
                    logger.info("Local embedding model loaded successfully")
                except ImportError:
                    raise ImportError("sentence-transformers package not installed. Run: pip install sentence-transformers")
            return self._embedding_model
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[tuple]:
        """
        Extract text from PDF, returning list of (page_number, text) tuples.
        Uses pypdf with pdfminer fallback.
        """
        pages_text = []
        
        try:
            # First try pypdf
            logger.info(f"Extracting text from {pdf_path} using pypdf...")
            with open(pdf_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                
                for page_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    if text.strip():
                        pages_text.append((page_num, text))
                    else:
                        logger.warning(f"Empty text from page {page_num}")
                
                # If no text extracted, try pdfminer
                if not pages_text:
                    logger.info("No text with pypdf, trying pdfminer...")
                    return self._extract_with_pdfminer(pdf_path)
                
        except Exception as e:
            logger.warning(f"pypdf failed: {e}. Trying pdfminer...")
            return self._extract_with_pdfminer(pdf_path)
        
        logger.info(f"Extracted text from {len(pages_text)} pages")
        return pages_text
    
    def _extract_with_pdfminer(self, pdf_path: str) -> List[tuple]:
        """Fallback extraction using pdfminer."""
        try:
            full_text = pdfminer_extract_text(pdf_path)
            if not full_text.strip():
                logger.error("No text extracted with pdfminer")
                return []
            
            # Simple heuristic: split on form feeds or multiple newlines
            pages = re.split(r'\f|\n\s*\n\s*\n', full_text)
            pages_text = [(i + 1, page.strip()) for i, page in enumerate(pages) if page.strip()]
            
            logger.info(f"Extracted text using pdfminer, {len(pages_text)} page sections")
            return pages_text
            
        except Exception as e:
            logger.error(f"pdfminer failed: {e}")
            return []
    
    def normalize_text(self, text: str) -> str:
        """Normalize whitespace while preserving paragraph breaks."""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        # Preserve paragraph breaks but normalize other whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # Replace single newlines with spaces
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        return text.strip()
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        return len(self.tokenizer.encode(text))
    
    def create_chunks(self, pages_text: List[tuple]) -> List[Dict[str, Any]]:
        """
        Create overlapping chunks from page texts.
        Returns list of chunk dictionaries with metadata.
        """
        chunks = []
        global_order = 0
        
        for page_num, page_text in pages_text:
            normalized_text = self.normalize_text(page_text)
            
            # Split into sentences for better chunk boundaries
            sentences = re.split(r'(?<=[.!?])\s+', normalized_text)
            
            current_chunk = ""
            current_tokens = 0
            
            for sentence in sentences:
                sentence_tokens = self.count_tokens(sentence)
                
                # If adding this sentence would exceed chunk size, finalize current chunk
                if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "page": page_num,
                        "order": global_order,
                        "token_count": current_tokens
                    })
                    global_order += 1
                    
                    # Start new chunk with overlap
                    if self.overlap > 0:
                        overlap_text = self._get_overlap_text(current_chunk, self.overlap)
                        current_chunk = overlap_text + " " + sentence
                        current_tokens = self.count_tokens(current_chunk)
                    else:
                        current_chunk = sentence
                        current_tokens = sentence_tokens
                else:
                    # Add sentence to current chunk
                    if current_chunk:
                        current_chunk += " " + sentence
                    else:
                        current_chunk = sentence
                    current_tokens += sentence_tokens
            
            # Don't forget the last chunk of the page
            if current_chunk.strip():
                chunks.append({
                    "text": current_chunk.strip(),
                    "page": page_num,
                    "order": global_order,
                    "token_count": current_tokens
                })
                global_order += 1
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def _get_overlap_text(self, text: str, overlap_tokens: int) -> str:
        """Get the last N tokens from text for overlap."""
        tokens = self.tokenizer.encode(text)
        if len(tokens) <= overlap_tokens:
            return text
        
        overlap_token_ids = tokens[-overlap_tokens:]
        return self.tokenizer.decode(overlap_token_ids)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using either local or OpenAI models."""
        if not texts:
            return []
        
        logger.info(f"Generating embeddings for {len(texts)} chunks using {'OpenAI' if self.use_openai else 'local'} model")
        
        if self.use_openai:
            return self._generate_openai_embeddings(texts)
        else:
            return self._generate_local_embeddings(texts)
    
    def _generate_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for OpenAI embeddings")
        
        embeddings = []
        
        # Process in batches (OpenAI has rate limits)
        batch_size = 100  # OpenAI allows up to 2048 inputs per request, but let's be conservative
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(texts) + batch_size - 1) // batch_size
            
            logger.info(f"Processing OpenAI batch {batch_num}/{total_batches} ({len(batch_texts)} chunks)")
            
            try:
                response = self.embedding_model.embeddings.create(
                    model=self.embedding_model_name,
                    input=batch_texts,
                    encoding_format="float"
                )
                
                # Extract embeddings from response
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)
                
                logger.info(f"✅ Batch {batch_num} complete: {len(batch_embeddings)} embeddings generated")
                
            except Exception as e:
                logger.error(f"❌ OpenAI embedding API error in batch {batch_num}: {e}")
                raise
        
        logger.info(f"🎉 Generated {len(embeddings)} OpenAI embeddings total")
        return embeddings
    
    def _generate_local_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local sentence-transformers model."""
        # Generate embeddings in batch
        embeddings = self.embedding_model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 10
        )
        
        # Convert to lists for JSON storage
        embedding_lists = [embedding.tolist() for embedding in embeddings]
        
        logger.info(f"Generated {len(embedding_lists)} local embeddings")
        return embedding_lists
    
    def process_pdf(self, pdf_path: str, document_id: str) -> Dict[str, Any]:
        """
        Main processing method: extract text, create chunks, generate embeddings.
        Returns all processed data for storage.
        """
        logger.info(f"Processing PDF: {pdf_path}")
        
        # Step 1: Extract text from PDF
        pages_text = self.extract_text_from_pdf(pdf_path)
        if not pages_text:
            logger.error("No text could be extracted from PDF")
            return {"chunks": [], "num_pages": 0, "embedding_model": self.embedding_model_name}
        
        # Step 2: Create chunks
        chunks = self.create_chunks(pages_text)
        if not chunks:
            logger.error("No chunks created from PDF")
            return {"chunks": [], "num_pages": len(pages_text), "embedding_model": self.embedding_model_name}
        
        # Step 3: Generate embeddings
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = self.generate_embeddings(chunk_texts)
        
        # Step 4: Combine chunks with embeddings
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i] if i < len(embeddings) else None
        
        model_info = f"{'OpenAI:' if self.use_openai else ''}{self.embedding_model_name}"
        logger.info(f"PDF processing complete: {len(pages_text)} pages, {len(chunks)} chunks")
        
        return {
            "chunks": chunks,
            "num_pages": len(pages_text),
            "embedding_model": model_info
        }
