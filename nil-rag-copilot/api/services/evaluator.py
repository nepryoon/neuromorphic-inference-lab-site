import numpy as np
from typing import List
from .retriever import retrieve
from .embedder import get_model

def generate_test_questions(chunks: List[str], n: int = 5) -> List[str]:
    """
    Generate test questions from document chunks.
    
    Args:
        chunks: List of text chunks
        n: Number of questions to generate
        
    Returns:
        List of test questions
    """
    questions = []
    step = max(1, len(chunks) // n)
    
    for i in range(0, min(n * step, len(chunks)), step):
        # Take first sentence from chunk
        sentence = chunks[i].split(".")[0].strip()
        if len(sentence) > 15:
            questions.append(f"What does this content describe: '{sentence[:80]}'?")
    
    return questions[:n]

def compute_retrieval_precision(questions: List[str], index, chunks: List[str]) -> float:
    """
    Compute average retrieval precision across test questions.
    
    Args:
        questions: List of test questions
        index: FAISS index
        chunks: List of text chunks
        
    Returns:
        Average top-1 similarity score (0-1)
    """
    scores = []
    for question in questions:
        results = retrieve(question, index, chunks)
        if results:
            scores.append(results[0][2])  # Top-1 score
    
    return float(np.mean(scores)) if scores else 0.0

def compute_answer_relevance(questions: List[str], answers: List[str]) -> float:
    """
    Compute semantic similarity between questions and answers.
    
    Args:
        questions: List of questions
        answers: List of answers
        
    Returns:
        Average cosine similarity (0-1)
    """
    model = get_model()
    
    q_embeddings = model.encode(questions, normalize_embeddings=True)
    a_embeddings = model.encode(answers, normalize_embeddings=True)
    
    # Compute cosine similarity (dot product of normalized vectors)
    similarities = np.sum(q_embeddings * a_embeddings, axis=1)
    
    return float(np.mean(similarities))

def compute_context_coverage(questions: List[str], index, chunks: List[str]) -> float:
    """
    Compute what fraction of chunks are used across all retrievals.
    
    Args:
        questions: List of test questions
        index: FAISS index
        chunks: List of text chunks
        
    Returns:
        Fraction of chunks used (0-1)
    """
    used_chunks = set()
    
    for question in questions:
        results = retrieve(question, index, chunks)
        for chunk_idx, _, _ in results:
            used_chunks.add(chunk_idx)
    
    return len(used_chunks) / len(chunks) if chunks else 0.0
