from fastapi import APIRouter, HTTPException
from api.models.schemas import ChatRequest, ChatResponse
from pydantic import BaseModel

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Ask a question about the indexed document.
    Returns an answer with citations and retrieval metrics.
    """
    try:
        # Mock response for now
        return ChatResponse(
            answer="This is a mock response. The full RAG functionality requires OpenAI API integration and document indexing.",
            citations=[
                {
                    "chunk_id": "chunk_0",
                    "text": "Sample citation text...",
                    "page": 1,
                    "score": 0.95
                }
            ],
            retrieval_latency_ms=150
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # Log the error internally but don't expose details to client
        print(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your question")
