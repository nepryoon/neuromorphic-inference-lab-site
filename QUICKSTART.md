# Quick Start Guide - MLOps Monitoring Stack

## 🚀 Getting Started in 2 Minutes

### Start the Stack

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

### Wait for Services (30 seconds)

```bash
# Check status
docker compose -f docker-compose.monitoring.yml ps
```

### Test the API

```bash
# Make a prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [1.5, 2.3, 3.1, 4.2, 5.0]}'
```

### View the Dashboard

1. Open http://localhost:3000 in your browser
2. Login: **admin** / **admin**
3. Navigate to: **Dashboards** → **MLOps** → **ML Predictions Dashboard**

## 📊 What You'll See

The dashboard displays 5 real-time panels:

1. **Model F1 Score** - Current model performance (0.87)
2. **Predictions/Minute** - Request rate
3. **Request Rate & Latency** - API performance over time
4. **Prediction Score Distribution** - Heatmap of confidence scores
5. **Predictions by Class** - Breakdown by predicted class (0, 1, 2)

## 🧪 Run Tests

```bash
./test-monitoring.sh
```

This validates all components are working correctly.

## 🔍 Access Points

- **Grafana Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Raw Metrics**: http://localhost:8000/metrics

## 📈 Generate Sample Data

```bash
# Send 50 predictions
for i in {1..50}; do
  curl -s -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"features": ['$RANDOM', '$RANDOM', '$RANDOM', '$RANDOM', '$RANDOM']}' > /dev/null
  echo "Sent prediction $i"
done
```

## 🛑 Stop the Stack

```bash
docker compose -f docker-compose.monitoring.yml down
```

## 📚 Full Documentation

See [services/README.md](services/README.md) for complete documentation including:
- Architecture details
- Development setup
- Production considerations
- Troubleshooting guide

## 🎯 Key Features Implemented

✅ FastAPI inference service with Prometheus metrics  
✅ PostgreSQL prediction logging with async DB operations  
✅ Prometheus scraping and metric storage  
✅ Grafana auto-provisioned dashboards  
✅ 5-panel ML monitoring dashboard  
✅ Docker Compose orchestration  
✅ Health checks and graceful degradation  
✅ Comprehensive test suite  

## 🔐 Security Note

This is a **development setup**. For production:
- Change default passwords
- Use secrets management
- Enable TLS/SSL
- Implement authentication
- Configure firewall rules

See the full README for production deployment guidance.
