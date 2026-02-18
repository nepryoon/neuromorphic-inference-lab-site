from typing import List

MAX_WORDS = 5000
CHUNK_SIZE = 200
OVERLAP = 40

def validate_word_limit(text: str) -> int:
    """
    Validate that the document doesn't exceed the word limit.
    
    Args:
        text: Document text to validate
        
    Returns:
        Word count
        
    Raises:
        ValueError: If word count exceeds MAX_WORDS
    """
    wc = len(text.split())
    if wc > MAX_WORDS:
        raise ValueError(
            f"The document contains {wc} words. "
            f"This demo accepts a maximum of {MAX_WORDS} words."
        )
    return wc

def chunk_text(text: str) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Document text to chunk
        
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    start = 0
    
    while start < len(words):
        end = min(start + CHUNK_SIZE, len(words))
        chunks.append(" ".join(words[start:end]))
        
        if end == len(words):
            break
            
        start += CHUNK_SIZE - OVERLAP
    
    return chunks
