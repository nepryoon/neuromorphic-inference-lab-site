import numpy as np
from typing import List, Tuple
from .embedder import get_model

TOP_K = 4

def retrieve(query: str, index, chunks: List[str]) -> List[Tuple[int, str, float]]:
    """
    Retrieve most relevant chunks for a query.
    
    Args:
        query: User question
        index: FAISS index
        chunks: List of text chunks
        
    Returns:
        List of tuples (chunk_index, chunk_text, similarity_score)
    """
    # Encode query
    query_embedding = get_model().encode(
        [query],
        normalize_embeddings=True
    ).astype(np.float32)
    
    # Search index
    scores, indices = index.search(query_embedding, min(TOP_K, len(chunks)))
    
    # Return results
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx >= 0:  # FAISS returns -1 for empty slots
            results.append((int(idx), chunks[idx], float(score)))
    
    return results
