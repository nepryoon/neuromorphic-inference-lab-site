from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Tuple

MODEL_NAME = "all-MiniLM-L6-v2"
_model = None

def get_model() -> SentenceTransformer:
    """
    Get or initialize the sentence transformer model.
    Uses lazy loading to avoid loading model on import.
    
    Returns:
        Initialized SentenceTransformer model
    """
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def build_index(chunks: List[str]) -> Tuple[faiss.IndexFlatIP, np.ndarray]:
    """
    Build FAISS index from text chunks.
    
    Args:
        chunks: List of text chunks to index
        
    Returns:
        Tuple of (FAISS index, embeddings array)
    """
    model = get_model()
    embeddings = model.encode(
        chunks,
        normalize_embeddings=True,
        show_progress_bar=False
    ).astype(np.float32)
    
    # Create FAISS index using inner product (cosine similarity with normalized vectors)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    
    return index, embeddings
