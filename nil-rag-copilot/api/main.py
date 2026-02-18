from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import ingest, chat, eval as eval_router

app = FastAPI(
    title="NIL RAG Copilot API",
    version="0.2.0",
    description="RAG-based document Q&A with citations and evaluation"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.neuromorphicinference.com",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok", "version": "0.2.0"}

# Include API routers
app.include_router(ingest.router, prefix="/api/v1", tags=["ingest"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(eval_router.router, prefix="/api/v1", tags=["eval"])

@app.get("/")
def root():
    return {
        "service": "NIL RAG Copilot API",
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/health"
    }
