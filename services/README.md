# MLOps Monitoring Infrastructure

This directory contains the complete MLOps monitoring stack for the ML inference service.

## Architecture Overview

The monitoring infrastructure consists of:

1. **Inference Service** (FastAPI) - ML model serving with Prometheus metrics
2. **PostgreSQL** - Prediction log storage
3. **Prometheus** - Metrics collection and storage
4. **Grafana** - Visualization and dashboards

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Port 3000 (Grafana), 8000 (API), 9090 (Prometheus), 5432 (PostgreSQL) available

### Running the Stack

```bash
# Start all services
docker-compose -f docker-compose.monitoring.yml up -d

# Check services status
docker-compose -f docker-compose.monitoring.yml ps

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f
```

### Accessing Services

- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Inference API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Metrics Endpoint**: http://localhost:8000/metrics

## Components

### 1. Inference Service

FastAPI service located in `services/inference/` that:
- Serves ML predictions via `/predict` endpoint
- Exposes Prometheus metrics at `/metrics`
- Logs predictions to PostgreSQL
- Tracks model F1 score, prediction distribution, and request rates

**Key Metrics:**
- `model_f1_score` - Current model F1 score (Gauge)
- `prediction_score_distribution` - Distribution of prediction probabilities (Histogram)
- `predictions_total` - Total predictions by class and model version (Counter)
- `http_requests_total` - HTTP request counter (Counter)

### 2. Database

PostgreSQL database with migration in `db/migrations/002_prediction_log.sql`:
- `prediction_log` table stores all predictions with metadata
- Indexed for efficient time-series queries

### 3. Prometheus

Configuration in `monitoring/prometheus/prometheus.yml`:
- Scrapes inference service every 15 seconds
- Stores metrics for querying and alerting

### 4. Grafana

Dashboard configuration in `monitoring/grafana/`:
- **Provisioning**: Auto-loads datasources and dashboards
- **Dashboard**: `ml-predictions.json` with 5 panels:
  1. Model F1 Score (stat panel)
  2. Predictions per Minute (stat panel)
  3. Request Rate & Latency (time series)
  4. Prediction Score Distribution (heatmap)
  5. Predictions by Class (time series)

## Testing the Inference Service

### Health Check

```bash
curl http://localhost:8000/health
```

### Make a Prediction

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [1.5, 2.3, 3.1, 4.2, 5.0]}'
```

### View Metrics

```bash
curl http://localhost:8000/metrics
```

## Development

### Local Development Without Docker

```bash
# Install dependencies
cd services/inference
pip install -r requirements.txt

# Set database URL
export DATABASE_URL="postgresql://user:password@localhost:5432/mlops"

# Run the service
python main.py
```

### Database Migration

The migration runs automatically on first startup. To run manually:

```bash
docker-compose -f docker-compose.monitoring.yml exec db \
  psql -U user -d mlops -f /docker-entrypoint-initdb.d/002_prediction_log.sql
```

## Monitoring

### Grafana Dashboard

1. Open http://localhost:3000
2. Login with admin/admin
3. Navigate to "Dashboards" → "MLOps" → "ML Predictions Dashboard"

The dashboard auto-refreshes every 10 seconds and shows the last 6 hours of data.

### Prometheus Queries

Access Prometheus at http://localhost:9090 and try these queries:

```promql
# Current F1 score
model_f1_score

# Predictions per second
rate(predictions_total[5m])

# Request rate by status
rate(http_requests_total[5m])

# 95th percentile prediction score
histogram_quantile(0.95, rate(prediction_score_distribution_bucket[5m]))
```

## Troubleshooting

### Services not starting

```bash
# Check logs
docker-compose -f docker-compose.monitoring.yml logs

# Restart services
docker-compose -f docker-compose.monitoring.yml restart
```

### Database connection issues

```bash
# Verify database is running
docker-compose -f docker-compose.monitoring.yml exec db pg_isready -U user

# Check database logs
docker-compose -f docker-compose.monitoring.yml logs db
```

### Metrics not appearing in Grafana

1. Check Prometheus is scraping: http://localhost:9090/targets
2. Verify metrics endpoint: http://localhost:8000/metrics
3. Check Grafana datasource: Configuration → Data Sources → Prometheus

## Cleanup

```bash
# Stop all services
docker-compose -f docker-compose.monitoring.yml down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose -f docker-compose.monitoring.yml down -v
```

## Production Considerations

For production deployment:

1. **Security**:
   - Change default Grafana password
   - Use secrets management for database credentials
   - Enable TLS/SSL for all services
   - Implement authentication for inference API

2. **Scalability**:
   - Use external PostgreSQL with replication
   - Add load balancer for inference service
   - Configure Prometheus remote storage
   - Set up Grafana in HA mode

3. **Monitoring**:
   - Configure alerting rules in Prometheus
   - Set up notification channels in Grafana
   - Add request tracing with Jaeger/Zipkin
   - Implement log aggregation (ELK/Loki)

4. **Performance**:
   - Adjust Prometheus retention and scrape intervals
   - Optimize database indexes
   - Configure proper resource limits
   - Enable connection pooling

## License

Part of the Neuromorphic Inference Lab MLOps infrastructure.
