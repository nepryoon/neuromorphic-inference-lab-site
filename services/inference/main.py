"""
FastAPI Inference Service with Prometheus Metrics
"""
import json
import os
import time
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import asyncpg


# Initialize FastAPI app
app = FastAPI(title="ML Inference Service", version="1.0.0")

# Prometheus metrics
prediction_score = Histogram(
    "prediction_score_distribution",
    "Distribution of prediction probabilities",
    buckets=[0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]
)

predictions_total = Counter(
    "predictions_total",
    "Total predictions by class and model version",
    ["predicted_class", "model_version"]
)

model_f1 = Gauge("model_f1_score", "Current model F1 score")

prediction_latency = Histogram(
    "prediction_latency_seconds",
    "Inference latency in seconds",
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["handler", "method", "status"]
)

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None

# Model metadata
MODEL_VERSION = "1.0.0"
MODEL_METADATA = {}


class PredictionRequest(BaseModel):
    features: List[float]


class PredictionResponse(BaseModel):
    predicted_class: int
    probability: float
    model_version: str


@app.on_event("startup")
async def startup_event():
    """Load model metadata and initialize database connection"""
    global MODEL_VERSION, MODEL_METADATA, db_pool
    
    # Load metadata.json if it exists
    metadata_path = Path("metadata.json")
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            MODEL_METADATA = json.load(f)
            
        # Set F1 score metric
        if "f1_score" in MODEL_METADATA:
            f1_value = MODEL_METADATA["f1_score"]
            model_f1.set(f1_value)
            print(f"Loaded model F1 score: {f1_value}")
        
        # Update model version if available
        if "version" in MODEL_METADATA:
            MODEL_VERSION = MODEL_METADATA["version"]
            print(f"Model version: {MODEL_VERSION}")
    
    # Initialize database connection pool
    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/mlops")
    try:
        db_pool = await asyncpg.create_pool(database_url, min_size=1, max_size=10)
        print(f"Database connection pool created")
    except Exception as e:
        print(f"Warning: Failed to initialize database pool: {e}")
        db_pool = None


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection pool"""
    global db_pool
    if db_pool:
        await db_pool.close()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "ML Inference API",
        "version": MODEL_VERSION,
        "status": "healthy"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "model_version": MODEL_VERSION}


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make predictions and record metrics
    """
    start_time = time.time()
    
    try:
        # Simulate prediction (replace with actual model inference)
        # For demonstration, we'll create a simple prediction based on input features
        features = request.features
        if not features:
            raise HTTPException(status_code=400, detail="Features list cannot be empty")
        
        # Simple prediction logic (replace with actual model)
        # Using sum of features to determine class and probability
        feature_sum = sum(features) % 10
        predicted_class = int(feature_sum % 3)  # 3 classes: 0, 1, 2
        probability = (feature_sum / 10.0 + 0.5) % 1.0  # Probability between 0 and 1
        if probability < 0.1:
            probability += 0.5
        
        # Calculate latency
        latency_seconds = time.time() - start_time
        latency_ms = latency_seconds * 1000
        
        # Record Prometheus metrics
        prediction_score.observe(probability)
        predictions_total.labels(
            predicted_class=str(predicted_class),
            model_version=MODEL_VERSION
        ).inc()
        prediction_latency.observe(latency_seconds)
        
        # Log prediction to database
        if db_pool:
            try:
                async with db_pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO prediction_log 
                        (input_json, predicted_class, probability, model_version, latency_ms)
                        VALUES ($1, $2, $3, $4, $5)
                        """,
                        json.dumps({"features": features}),
                        predicted_class,
                        probability,
                        MODEL_VERSION,
                        latency_ms
                    )
            except Exception as e:
                # Don't block response if DB is down
                print(f"Warning: Failed to log prediction to database: {e}")
        
        # Record HTTP request metric
        http_requests_total.labels(
            handler="/predict",
            method="POST",
            status="200"
        ).inc()
        
        return PredictionResponse(
            predicted_class=predicted_class,
            probability=probability,
            model_version=MODEL_VERSION
        )
    
    except HTTPException:
        http_requests_total.labels(
            handler="/predict",
            method="POST",
            status="400"
        ).inc()
        raise
    except Exception as e:
        http_requests_total.labels(
            handler="/predict",
            method="POST",
            status="500"
        ).inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
