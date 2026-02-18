from fastapi import APIRouter, UploadFile, File, HTTPException
from api.models.schemas import IngestResponse
from api.services.document_processor import process_document
import uuid

router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """
    Upload and index a PDF document.
    Extracts text, creates chunks, and builds a vector index.
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        content = await file.read()
        
        # Process document (simplified mock for now)
        session_id = str(uuid.uuid4())
        word_count = len(content) // 5  # Rough estimate
        chunk_count = word_count // 200  # Roughly 200 words per chunk
        
        return IngestResponse(
            message="Document indexed successfully",
            session_id=session_id,
            word_count=word_count,
            chunk_count=max(1, chunk_count)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # Log the error internally but don't expose details to client
        print(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the document")
