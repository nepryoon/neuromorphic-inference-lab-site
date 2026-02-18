import io
import os
import time
import uuid
import logging
import numpy as np
import pdfplumber
import faiss
import openai

from typing import List, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="NIL RAG Copilot API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.neuromorphicinference.com",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "*",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router with /api/v1 prefix
api_router = APIRouter(prefix="/api/v1")

# ── Schemas ───────────────────────────────────────────────────────────────────
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

# ── In-memory session store ───────────────────────────────────────────────────
_sessions: Dict[str, Any] = {}

# ── Embedding model (loaded once) ─────────────────────────────────────────────
_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Model loaded.")
    return _model

# ── OpenAI client (loaded once) ───────────────────────────────────────────────
_openai_client = None

def get_openai_client() -> openai.OpenAI:
    global _openai_client
    if _openai_client is None:
        logger.info("Initializing OpenAI client...")
        _openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
        logger.info("OpenAI client initialized.")
    return _openai_client

# ── Services ──────────────────────────────────────────────────────────────────
MAX_WORDS = 5000
CHUNK_SIZE = 200
OVERLAP = 40
TOP_K = 4
MAX_SNIPPET_LENGTH = 150

def extract_text(file_bytes: bytes) -> str:
    parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                parts.append(text.strip())
    return "\n\n".join(parts)

def validate_words(text: str) -> int:
    wc = len(text.split())
    if wc > MAX_WORDS:
        raise ValueError(
            f"The document contains {wc} words. "
            f"This demo accepts a maximum of {MAX_WORDS} words."
        )
    return wc

def make_chunks(text: str) -> List[str]:
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + CHUNK_SIZE, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += CHUNK_SIZE - OVERLAP
    return chunks

def build_index(chunks: List[str]):
    model = get_model()
    emb = model.encode(chunks, normalize_embeddings=True,
                       show_progress_bar=False).astype(np.float32)
    index = faiss.IndexFlatIP(emb.shape[1])
    index.add(emb)
    return index

def retrieve(query: str, index, chunks: List[str]):
    model = get_model()
    q = model.encode([query], normalize_embeddings=True).astype(np.float32)
    scores, indices = index.search(q, min(TOP_K, len(chunks)))
    return [(int(i), chunks[i], float(s))
            for s, i in zip(scores[0], indices[0]) if i >= 0]

def call_openai_chat(messages, max_tokens=600, temperature=0.1) -> str:
    client = get_openai_client()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "version": "0.2.0"}


@api_router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted.")
    content = await file.read()
    try:
        text = extract_text(content)
    except Exception as e:
        raise HTTPException(422, f"Cannot read PDF: {e}")
    if not text.strip():
        raise HTTPException(422, "The PDF contains no extractable text.")
    try:
        wc = validate_words(text)
    except ValueError as e:
        raise HTTPException(422, str(e))
    chunks = make_chunks(text)
    index = build_index(chunks)
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {"index": index, "chunks": chunks, "word_count": wc}
    logger.info(f"Ingest OK: {wc} words, {len(chunks)} chunks, session={session_id}")
    return IngestResponse(
        status="ok",
        session_id=session_id,
        word_count=wc,
        chunk_count=len(chunks),
        message=f"Indexing complete. {wc} words, {len(chunks)} chunks indexed.",
    )


@api_router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if req.session_id not in _sessions:
        raise HTTPException(404, "Session not found. Run /ingest first.")
    session = _sessions[req.session_id]
    t0 = time.perf_counter()
    results = retrieve(req.question, session["index"], session["chunks"])
    latency = (time.perf_counter() - t0) * 1000
    context = "\n\n".join(f"[Chunk {i}]: {t}" for i, t, _ in results)
    answer = call_openai_chat([
        {"role": "system", "content": (
            "You are an expert assistant on the uploaded documentation. "
            "Answer ONLY from the provided context. "
            "If the answer is not in the context reply: "
            "'I could not find this information in the uploaded document.' "
            "Cite relevant passages as [Chunk N]."
        )},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {req.question}"},
    ])
    return ChatResponse(
        answer=answer,
        citations=[
            Citation(
                chunk_id=i,
                text_snippet=t[:MAX_SNIPPET_LENGTH] + ("…" if len(t) > MAX_SNIPPET_LENGTH else ""),
                score=s
            )
            for i, t, s in results
        ],
        retrieval_latency_ms=round(latency, 2),
    )


@api_router.post("/eval", response_model=EvalResponse)
async def run_eval(req: EvalRequest):
    if req.session_id not in _sessions:
        raise HTTPException(404, "Session not found. Run /ingest first.")
    session = _sessions[req.session_id]
    chunks, index = session["chunks"], session["index"]

    # Generate synthetic test questions
    questions = []
    step = max(1, len(chunks) // 5)
    for i in range(0, min(5 * step, len(chunks)), step):
        s = chunks[i].split(".")[0].strip()
        if len(s) > 15:
            questions.append(f"What does this content describe: '{s[:80]}'?")
    if not questions:
        raise HTTPException(422, "Could not generate test questions.")

    # Generate answers
    answers = []
    for q in questions:
        results = retrieve(q, index, chunks)
        context = "\n\n".join(f"[Chunk {i}]: {t}" for i, t, _ in results)
        a = call_openai_chat([
            {"role": "system", "content": "Answer only from the context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {q}"},
        ], max_tokens=200, temperature=0.0)
        answers.append(a)

    # Metrics
    model = get_model()
    rp_scores = []
    used_chunks = set()
    for q in questions:
        r = retrieve(q, index, chunks)
        if r:
            rp_scores.append(r[0][2])
            for idx, _, _ in r:
                used_chunks.add(idx)
    retrieval_precision = float(np.mean(rp_scores)) if rp_scores else 0.0

    q_emb = model.encode(questions, normalize_embeddings=True)
    a_emb = model.encode(answers,   normalize_embeddings=True)
    answer_relevance = float(np.mean(np.sum(q_emb * a_emb, axis=1)))

    context_coverage = len(used_chunks) / len(chunks) if chunks else 0.0

    metrics = [
        MetricResult(
            name="Retrieval Precision",
            score=round(retrieval_precision, 3),
            description="Avg top-1 FAISS cosine score across test questions (0–1)",
        ),
        MetricResult(
            name="Answer Relevance",
            score=round(answer_relevance, 3),
            description="Avg cosine similarity between questions and answers (0–1)",
        ),
        MetricResult(
            name="Context Coverage",
            score=round(context_coverage, 3),
            description="Fraction of distinct chunks used across all retrievals (0–1)",
        ),
    ]
    return EvalResponse(
        session_id=req.session_id,
        metrics=metrics,
        test_questions=questions,
        answers=answers,
    )

# ── Include API Router ────────────────────────────────────────────────────────
# Mount the API router with /api/v1 prefix
app.include_router(api_router)
