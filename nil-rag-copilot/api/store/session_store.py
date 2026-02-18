import uuid
from typing import Dict, Any

# In-memory session storage
_sessions: Dict[str, Any] = {}

def create_session(index, chunks: list, word_count: int) -> str:
    """
    Create a new session with document index and metadata.
    
    Args:
        index: FAISS index
        chunks: List of text chunks
        word_count: Total word count in document
        
    Returns:
        Session ID (UUID)
    """
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "index": index,
        "chunks": chunks,
        "word_count": word_count
    }
    return session_id

def get_session(session_id: str) -> dict:
    """
    Retrieve a session by ID.
    
    Args:
        session_id: Session ID to retrieve
        
    Returns:
        Session data dictionary
        
    Raises:
        KeyError: If session not found
    """
    if session_id not in _sessions:
        raise KeyError(f"Session '{session_id}' not found. Run /ingest first.")
    return _sessions[session_id]
