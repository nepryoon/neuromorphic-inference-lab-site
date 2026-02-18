import os
import time
import openai
from fastapi import APIRouter, HTTPException
from ..models.schemas import ChatRequest, ChatResponse, Citation
from ..store.session_store import get_session
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

SYSTEM_PROMPT = (
    "You are an expert assistant on the uploaded documentation. "
    "Answer ONLY from the provided context. "
    "If the answer is not in the context, say: "
    "'I could not find this information in the uploaded document.' "
    "Always cite relevant passages as [Chunk N]."
)

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Ask a question about the indexed document.
    Returns an answer with citations and retrieval metrics.
    """
    try:
        session = get_session(req.session_id)
    except KeyError as e:
        raise HTTPException(404, str(e))
    
    # Retrieve relevant chunks
    t0 = time.perf_counter()
    results = retrieve(req.question, session["index"], session["chunks"])
    latency = (time.perf_counter() - t0) * 1000
    
    # Build context from retrieved chunks
    context = "\n\n".join(f"[Chunk {i}]: {t}" for i, t, _ in results)
    
    # Generate answer using OpenAI
    client = get_openai_client()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {req.question}"}
        ],
        temperature=0.1,
        max_tokens=600
    )
    
    # Safely truncate text snippets at word boundaries
    citations = []
    for i, t, s in results:
        snippet = t[:150]
        if len(t) > 150:
            # Find last space to avoid cutting words
            last_space = snippet.rfind(' ')
            if last_space > 0:
                snippet = snippet[:last_space]
            snippet += "…"
        citations.append(Citation(chunk_id=i, text_snippet=snippet, score=s))
    
    return ChatResponse(
        answer=resp.choices[0].message.content,
        citations=citations,
        retrieval_latency_ms=round(latency, 2)
    )
