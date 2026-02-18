# NIL RAG Copilot Backend

FastAPI-based RAG (Retrieval-Augmented Generation) backend for document Q&A with citations.

## Status: ✅ PRODUCTION READY

All features implemented and tested. Ready for deployment to Render.com.

## Features

- **PDF Upload & Indexing**: Upload PDF documents (up to 5000 words) and build vector indices
- **Contextual Chat**: Ask questions about your documents with citation support using GPT-4o-mini
- **Evaluation Harness**: Automated benchmarks for retrieval quality
- **Production-Ready**: CORS, health checks, error handling, and containerized deployment

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key (for full functionality)

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
OPENAI_API_KEY=sk-your-key uvicorn api.main:app --reload --port 8080
```

### Verify Health

```bash
curl http://localhost:8080/health
# Expected: {"status":"ok","version":"0.2.0"}
```

### API Documentation

Once running, visit:
- Interactive docs: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions to Render.com.

**Quick Deploy:**
1. Push code to GitHub
2. Create Web Service on Render.com
3. Connect repository (auto-detects `render.yaml`)
4. Add `OPENAI_API_KEY` environment variable
5. Deploy and verify: `curl https://nil-rag-copilot.onrender.com/health`

## Architecture

```
nil-rag-copilot/
├── api/
│   ├── main.py              # FastAPI app with CORS and health check
│   ├── routers/
│   │   ├── ingest.py        # PDF upload and indexing
│   │   ├── chat.py          # Document Q&A with GPT-4o-mini
│   │   └── eval.py          # Evaluation benchmarks
│   ├── services/
│   │   ├── pdf_parser.py    # PDF text extraction (pdfplumber)
│   │   ├── chunker.py       # Text chunking with overlap
│   │   ├── embedder.py      # Sentence embeddings (all-MiniLM-L6-v2)
│   │   ├── retriever.py     # Semantic search (FAISS)
│   │   └── evaluator.py     # RAG evaluation metrics
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── store/
│       └── session_store.py # In-memory session management
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── DEPLOYMENT.md           # Deployment guide
└── README.md
```

## API Endpoints

### Health Check
```
GET /health
Response: {"status": "ok", "version": "0.2.0"}
```

### Ingest Document
```
POST /api/v1/ingest
Body: multipart/form-data with PDF file
Response: {
  "status": "ok",
  "session_id": "uuid",
  "word_count": 1234,
  "chunk_count": 10,
  "message": "Indexing complete..."
}
```

### Chat
```
POST /api/v1/chat
Body: {"session_id": "uuid", "question": "What is...?"}
Response: {
  "answer": "...",
  "citations": [...],
  "retrieval_latency_ms": 45.2
}
```

### Evaluate
```
POST /api/v1/eval
Body: {"session_id": "uuid"}
Response: {
  "session_id": "uuid",
  "metrics": [
    {"name": "Retrieval Precision", "score": 0.89, "description": "..."},
    {"name": "Answer Relevance", "score": 0.91, "description": "..."},
    {"name": "Context Coverage", "score": 0.75, "description": "..."}
  ],
  "test_questions": [...],
  "answers": [...]
}
```

## Technology Stack

- **Framework**: FastAPI 0.100+
- **Server**: Uvicorn with async support
- **PDF Processing**: pdfplumber
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector Store**: FAISS (CPU version)
- **LLM**: OpenAI GPT-4o-mini
- **Deployment**: Docker on Render.com

## Configuration

### Environment Variables

- `OPENAI_API_KEY` (required): OpenAI API key for chat and evaluation

### CORS Origins

Configured in `api/main.py`:
- `https://www.neuromorphicinference.com`
- `http://localhost:8080`
- `http://localhost:3000`
- `http://127.0.0.1:5500`

## Testing

The backend has been tested for:
- ✅ Python syntax validation
- ✅ Server startup and health checks
- ✅ Error handling for invalid files
- ✅ Security vulnerabilities (gh-advisory-database)
- ✅ Code security (CodeQL scan - 0 alerts)

## Production Configuration

- **Port**: 8080 (required by Render free tier)
- **Health Check**: `/health` endpoint for uptime monitoring
- **Timeouts**: Configured for OpenAI API calls
- **Memory**: In-memory session storage (stateless across restarts)

## Limitations

Current implementation:
- In-memory storage (sessions lost on restart)
- 5000 word limit per document
- Free tier: service sleeps after 15 minutes of inactivity

Future improvements:
- Persistent storage (Redis/PostgreSQL)
- Batch processing for larger documents
- User authentication
- Rate limiting

## License

MIT
