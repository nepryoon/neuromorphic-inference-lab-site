from pydantic import BaseModel
from typing import List, Optional

# Ingest schemas
class IngestResponse(BaseModel):
    message: str
    session_id: str
    word_count: int
    chunk_count: int

# Chat schemas
class ChatRequest(BaseModel):
    session_id: str
    question: str

class Citation(BaseModel):
    chunk_id: str
    text: str
    page: int
    score: float

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    retrieval_latency_ms: int

# Evaluation schemas
class EvalRequest(BaseModel):
    session_id: str

class EvalResponse(BaseModel):
    precision: float
    relevance: float
    coverage: float
    total_queries: int
    passed_queries: int
    message: str
