from fastapi import APIRouter, HTTPException
from api.models.schemas import EvalRequest, EvalResponse

router = APIRouter()

@router.post("/eval", response_model=EvalResponse)
async def evaluate(request: EvalRequest):
    """
    Run automated evaluation benchmarks on the indexed document.
    Returns metrics for retrieval precision, answer relevance, and context coverage.
    """
    try:
        # Mock response for now
        return EvalResponse(
            precision=0.85,
            relevance=0.90,
            coverage=0.88,
            total_queries=10,
            passed_queries=9,
            message="Evaluation complete (mock data)"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # Log the error internally but don't expose details to client
        print(f"Error running evaluation: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while running evaluation")
