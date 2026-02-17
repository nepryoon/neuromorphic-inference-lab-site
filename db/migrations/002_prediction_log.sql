-- Migration: Create prediction_log table for tracking ML predictions
-- Version: 002
-- Description: Stores prediction logs with input data, outputs, and performance metrics

CREATE TABLE IF NOT EXISTS prediction_log (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMPTZ DEFAULT now(),
    input_json JSONB NOT NULL,
    predicted_class INTEGER NOT NULL,
    probability FLOAT NOT NULL,
    model_version TEXT NOT NULL,
    latency_ms FLOAT
);

-- Index for efficient time-based queries (most recent first)
CREATE INDEX idx_prediction_log_ts ON prediction_log(ts DESC);

-- Index for querying by model version
CREATE INDEX idx_prediction_log_model_version ON prediction_log(model_version);

-- Index for querying by predicted class
CREATE INDEX idx_prediction_log_predicted_class ON prediction_log(predicted_class);

-- Comments for documentation
COMMENT ON TABLE prediction_log IS 'Logs all ML model predictions with metadata and performance metrics';
COMMENT ON COLUMN prediction_log.ts IS 'Timestamp when prediction was made';
COMMENT ON COLUMN prediction_log.input_json IS 'Input features as JSONB for flexibility';
COMMENT ON COLUMN prediction_log.predicted_class IS 'Model output class/label';
COMMENT ON COLUMN prediction_log.probability IS 'Prediction confidence/probability';
COMMENT ON COLUMN prediction_log.model_version IS 'Version of model used for prediction';
COMMENT ON COLUMN prediction_log.latency_ms IS 'Inference latency in milliseconds';
