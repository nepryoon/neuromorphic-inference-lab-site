import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

try:
    from .routers import ingest
    logger.info("ingest router imported OK")
except Exception as e:
    logger.error(f"Failed to import ingest router: {e}")
    raise

try:
    from .routers import chat
    logger.info("chat router imported OK")
except Exception as e:
    logger.error(f"Failed to import chat router: {e}")
    raise

try:
    from .routers import eval as eval_router
    logger.info("eval router imported OK")
except Exception as e:
    logger.error(f"Failed to import eval router: {e}")
    raise

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

# List registered routes at startup
for route in app.routes:
    logger.info(f"Route: {getattr(route, 'methods', '-')} {route.path}")

@app.get("/")
def root():
    return {
        "service": "NIL RAG Copilot API",
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/health"
    }
