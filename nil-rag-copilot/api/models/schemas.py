from pydantic import BaseModel
from typing import List

class IngestResponse(BaseModel):
    status: str
    session_id: str
    word_count: int
    chunk_count: int
    message: str

class ChatRequest(BaseModel):
    session_id: str
    question: str

class Citation(BaseModel):
    chunk_id: int
    text_snippet: str
    score: float

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    retrieval_latency_ms: float

class EvalRequest(BaseModel):
    session_id: str

class MetricResult(BaseModel):
    name: str
    score: float
    description: str

class EvalResponse(BaseModel):
    session_id: str
    metrics: List[MetricResult]
    test_questions: List[str]
    answers: List[str]
