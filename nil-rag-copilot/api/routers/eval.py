import os
import openai
from fastapi import APIRouter, HTTPException
from ..models.schemas import EvalRequest, EvalResponse, MetricResult
from ..store.session_store import get_session
from ..services.evaluator import (
    generate_test_questions,
    compute_retrieval_precision,
    compute_answer_relevance,
    compute_context_coverage
)
from ..services.retriever import retrieve

router = APIRouter()

# Initialize OpenAI client once at module level
_openai_client = None

def get_openai_client() -> openai.OpenAI:
    """Get or create OpenAI client instance."""
    global _openai_client
    if _openai_client is None:
        _openai_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _openai_client

@router.post("/eval", response_model=EvalResponse)
async def run_eval(req: EvalRequest):
    """
    Run automated evaluation benchmarks on the indexed document.
    Returns metrics for retrieval precision, answer relevance, and context coverage.
    """
    try:
        session = get_session(req.session_id)
    except KeyError as e:
        raise HTTPException(404, str(e))
    
    chunks = session["chunks"]
    index = session["index"]
    
    # Generate test questions
    questions = generate_test_questions(chunks)
    if not questions:
        raise HTTPException(422, "Could not generate test questions from chunks.")
    
    # Generate answers for each question
    client = get_openai_client()
    answers = []
    
    for q in questions:
        results = retrieve(q, index, chunks)
        context = "\n\n".join(f"[Chunk {i}]: {t}" for i, t, _ in results)
        
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Answer only from the context."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {q}"}
            ],
            temperature=0.0,
            max_tokens=200
        )
        answers.append(r.choices[0].message.content)
    
    # Compute metrics
    metrics = [
        MetricResult(
            name="Retrieval Precision",
            score=round(compute_retrieval_precision(questions, index, chunks), 3),
            description="Avg top-1 FAISS cosine score across test questions (0–1)"
        ),
        MetricResult(
            name="Answer Relevance",
            score=round(compute_answer_relevance(questions, answers), 3),
            description="Avg cosine similarity between questions and generated answers (0–1)"
        ),
        MetricResult(
            name="Context Coverage",
            score=round(compute_context_coverage(questions, index, chunks), 3),
            description="Fraction of distinct chunks used at least once across all retrievals (0–1)"
        ),
    ]
    
    return EvalResponse(
        session_id=req.session_id,
        metrics=metrics,
        test_questions=questions,
        answers=answers
    )
