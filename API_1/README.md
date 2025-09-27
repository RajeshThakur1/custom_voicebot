# Phase 1: PDF Processing with OpenAI Embeddings

This is the OpenAI-powered version of the Phase 1 PDF processing system. It uses OpenAI's embedding API instead of local sentence-transformers.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure .env file:**
   Create a `.env` file in this directory with:
   ```bash
   OPENAI_API_KEY=your-actual-openai-api-key-here
   USE_OPENAI_EMBEDDINGS=true
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small
   ```

3. **Verify setup:**
   ```bash
   python setup_env.py
   ```

4. **Run the server:**
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8001
   ```

## Key Differences from Base Version

- **Port 8001** (to avoid conflict with base version)
- **OpenAI embeddings** (1536 dimensions vs 384)
- **API-based processing** (requires internet + API key)
- **Different database** (./data/rag_poc_openai.db)

## API Endpoints

- **Swagger UI**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **Create Document**: POST /documents
- **Upload PDF**: POST /documents/{id}/upload
- **List Documents**: GET /documents
- **Get Document**: GET /documents/{id}

## Cost Considerations

- OpenAI text-embedding-3-small: ~$0.02 per 1M tokens
- Typical document costs ~$0.001-0.01 depending on size

## Models Supported

- `text-embedding-3-small` (1536 dimensions) - Recommended
- `text-embedding-3-large` (3072 dimensions) - Higher quality
- `text-embedding-ada-002` (1536 dimensions) - Legacy

## Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `USE_OPENAI_EMBEDDINGS` - Set to "true" for OpenAI, "false" for local
- `OPENAI_EMBEDDING_MODEL` - Which OpenAI model to use

## Testing

Use the same PDFs as the base version and compare results:
- Base version uses 384-dimensional local embeddings
- OpenAI version uses 1536-dimensional OpenAI embeddings
