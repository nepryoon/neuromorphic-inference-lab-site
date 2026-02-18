# NIL RAG Copilot Backend

FastAPI-based RAG (Retrieval-Augmented Generation) backend for document Q&A with citations.

## Features

- **PDF Upload & Indexing**: Upload PDF documents and build vector indices
- **Contextual Chat**: Ask questions about your documents with citation support
- **Evaluation Harness**: Automated benchmarks for retrieval quality
- **Production-Ready**: CORS, health checks, and containerized deployment

## Local Development

### Prerequisites

- Python 3.11+
- OpenAI API key (for full functionality)

### Start the API

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server (without OpenAI integration for testing)
uvicorn api.main:app --reload --port 8080

# Or with OpenAI API key for full functionality
OPENAI_API_KEY=sk-... uvicorn api.main:app --reload --port 8080
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

### Serve the Frontend

From the repository root:

```bash
# Using wrangler (Cloudflare Pages)
npx wrangler pages dev .

# Or use any static file server
python -m http.server 8000
```

### Switch API_BASE for Local Dev

In `demos/rag-copilot/index.html`, temporarily change:

```javascript
const API_BASE = "http://localhost:8080/api/v1";
```

**Important**: Revert to the Render URL before committing.

## Deployment

This backend is configured for deployment on Render.com (free tier).

### Deploy Steps

1. Push code to GitHub
2. Render auto-deploys via `render.yaml`
3. In Render dashboard: Set `OPENAI_API_KEY` environment variable
4. Verify deployment: `curl https://nil-rag-copilot.onrender.com/health`

### Production Configuration

- **CORS**: Configured for `https://www.neuromorphicinference.com`
- **Port**: 8080 (required by Render free tier)
- **Health Check**: `/health` endpoint for uptime monitoring

## Architecture

```
nil-rag-copilot/
├── api/
│   ├── main.py              # FastAPI app with CORS and health check
│   ├── routers/
│   │   ├── ingest.py        # PDF upload and indexing
│   │   ├── chat.py          # Document Q&A
│   │   └── eval.py          # Evaluation benchmarks
│   ├── services/
│   │   └── document_processor.py  # Text extraction and chunking
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── store/               # Session and vector storage
├── requirements.txt
├── Dockerfile
└── README.md
```

## Current Status

This is a **minimal deployable version** with mock responses. Full RAG functionality requires:

- OpenAI API integration for embeddings and chat
- PDF text extraction (PyPDF2 or similar)
- FAISS vector store implementation
- Session state management

## License

MIT
