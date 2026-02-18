from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.pdf_parser import extract_text_from_pdf
from ..services.chunker import validate_word_limit, chunk_text
from ..services.embedder import build_index
from ..store.session_store import create_session
from ..models.schemas import IngestResponse

router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)):
    """
    Upload and index a PDF document.
    Extracts text, creates chunks, and builds a vector index.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted.")
    
    content = await file.read()
    
    try:
        text = extract_text_from_pdf(content)
    except Exception as e:
        raise HTTPException(422, f"Cannot read PDF: {e}")
    
    if not text.strip():
        raise HTTPException(422, "The PDF contains no extractable text.")
    
    try:
        wc = validate_word_limit(text)
    except ValueError as e:
        raise HTTPException(422, str(e))
    
    chunks = chunk_text(text)
    index, _ = build_index(chunks)
    session_id = create_session(index, chunks, wc)
    
    return IngestResponse(
        status="ok",
        session_id=session_id,
        word_count=wc,
        chunk_count=len(chunks),
        message=f"Indexing complete. {wc} words, {len(chunks)} chunks indexed."
    )
