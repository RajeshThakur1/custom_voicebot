## API Integration Guide (Frontend ↔ Backend)

This document explains exactly which backend endpoints the UI needs and how to call them. It covers three services (as per your architecture):

- API‑1: Document ingestion (upload → chunking → embeddings → storage)
- API‑2: Question answering over selected documents (embeddings + semantic similarity + LLM answer)
- API‑3: Document catalog/listing (per user) and document management

Use this as the single source of truth for wiring frontend components to the backend.

---

### Base URLs and Environment

Expose these in a `.env` (or your hosting env) and read them in the frontend build:

```
VITE_API1_BASE_URL=https://api1.example.com
VITE_API2_BASE_URL=https://api2.example.com
VITE_API3_BASE_URL=https://api3.example.com
```

- All endpoints below are shown relative to their base URL.
- Frontend should send `Content-Type` and `Authorization` if your backend requires it.
- CORS: Make sure all APIs allow the Vite dev origin and your production origin.

Common headers
```
Authorization: Bearer <token>          # if applicable
X-User-Id: <userId>                    # if you identify users on the backend
```

---

## API‑1: Document Ingestion

Purpose: Accept raw PDFs (or other types), trigger chunking and embedding, and store vectors/metadata for later retrieval.

1) Upload document
```
POST /documents/upload
Content-Type: multipart/form-data
Form fields:
  file: <PDF|DOCX|TXT>
  userId: string
  docName?: string
```
Response 201
```
{
  "docId": "string",
  "docName": "string",
  "status": "uploaded"
}
```

2) Start ingestion (if not auto‑ingested on upload)
```
POST /documents/{docId}/ingest
Body: { userId: string }
```
Response 202
```
{ "docId": "string", "status": "processing" }
```

3) Check ingestion status
```
GET /documents/{docId}/status?userId=<id>
```
Response 200
```
{ "docId": "string", "status": "processing|ready|failed", "errorMessage"?: "string" }
```

4) Optional: signed URL/preview bytes
```
GET /documents/{docId}/preview?userId=<id>
```
Response 200: `{ url: string }` or file bytes

Frontend touchpoints
- `DocumentUploadModal.tsx`: calls (1), optionally polls (3), shows progress, then closes when `status=ready`.
- `DocumentPreviewModal.tsx`: calls (4) to preview.

---

## API‑3: Document Catalog / Management

Purpose: Provide list of documents per user and allow deletes. (Your diagram labels vary between API‑2/API‑3 for listing; align the base URL to whichever service actually serves it.)

1) List documents
```
GET /documents?userId=<id>
```
Response 200
```
{
  "documents": [
    { "docId": "string", "docName": "string", "pages": 12, "updatedAt": "ISO" , "status": "ready|processing|failed" }
  ]
}
```

2) Delete a document
```
DELETE /documents/{docId}?userId=<id>
```
Response 204 (no body)

Frontend touchpoints
- `Dashboard.tsx`: fetches list on mount using (1). Uses (2) from `DeleteConfirmationDialog.tsx`.
- `AgentCreationPage.tsx`: also needs (1) to show selectable docs when creating an agent.

---

## API‑2: Question Answering (RAG)

Purpose: Given a user input and selected documents, compute the question embedding, retrieve top‑K chunks by semantic similarity, and generate an answer via LLM. Return answer plus citations.

Endpoint (non‑streaming)
```
POST /query
Content-Type: application/json
Body:
{
  "userId": "string",
  "question": "string",
  "docIds": ["docId1", "docId2"],
  "topK": 8,
  "model": "gpt-4o-mini",
  "temperature": 0.2
}
```
Response 200
```
{
  "answer": "string",
  "citations": [
    {
      "docId": "string",
      "page": 3,
      "score": 0.87,
      "snippet": "text chunk..."
    }
  ],
  "usage": { "promptTokens": 123, "completionTokens": 45 }
}
```

Optional: streaming SSE
```
POST /query/stream
Accept: text/event-stream
```

Frontend touchpoints
- `Dashboard.tsx` (or your chat widget) sends the user’s question and selected `docIds` to `/query` then renders `answer` and `citations`.
- `AgentCreationPage.tsx` stores the chosen `docIds` and `model` to use for subsequent queries.

---

## Error Model (all APIs)

```
4xx/5xx
{
  "error": {
    "code": "string",
    "message": "human readable message",
    "details"?: any
  }
}
```

Frontend should show a toast with `message` and, when useful, surface `details` for troubleshooting.

---

## Minimal Wiring Map (per component)

- `LoginPage.tsx`: If you have auth, obtain token; store to `localStorage` and add `Authorization` header on all calls.
- `Dashboard.tsx`:
  - On mount: `GET {API3}/documents?userId=<id>` to populate the list
  - On delete: `DELETE {API3}/documents/{docId}?userId=<id>`
  - On ask: `POST {API2}/query` with `{ question, docIds, userId, topK, model }`
- `DocumentUploadModal.tsx`:
  - On submit: `POST {API1}/documents/upload` (multipart)
  - If needed: `POST {API1}/documents/{docId}/ingest`
  - Poll: `GET {API1}/documents/{docId}/status`
- `DocumentPreviewModal.tsx`:
  - `GET {API1}/documents/{docId}/preview`
- `AgentCreationPage.tsx`:
  - `GET {API3}/documents?userId=<id>` to show selectable docs
  - Persist agent locally or to your own endpoint if/when introduced

---

## Example cURLs

Upload
```
curl -X POST "$VITE_API1_BASE_URL/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/file.pdf" \
  -F "userId=USER_123" \
  -F "docName=Policy.pdf"
```

List documents
```
curl "$VITE_API3_BASE_URL/documents?userId=USER_123" \
  -H "Authorization: Bearer $TOKEN"
```

Ask question
```
curl -X POST "$VITE_API2_BASE_URL/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "userId": "USER_123",
        "question": "What is the refund policy?",
        "docIds": ["DOC_A", "DOC_B"],
        "topK": 8,
        "model": "gpt-4o-mini",
        "temperature": 0.2
      }'
```

---

## Notes & Gotchas

- Ensure CSP/CORS allow requests from your Vite dev URL and production origin.
- Large files: set upload limits accordingly; the UI should show progress and handle `413 Payload Too Large` errors gracefully.
- Consistency: Use the same embedding model for API‑1 (doc vectors) and API‑2 (query vectors) to keep cosine similarity meaningful.
- If your team decided that the “list documents” lives in API‑2 instead of API‑3, keep the same paths; just point `VITE_API3_BASE_URL` to that service for the frontend.


