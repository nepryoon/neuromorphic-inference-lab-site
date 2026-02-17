#!/bin/bash
#
# Test script for MLOps Monitoring Infrastructure
# This script verifies that all components are working correctly
#

set -e

echo "======================================"
echo "MLOps Monitoring Infrastructure Tests"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check if all services are running
echo "Test 1: Checking service health..."
if docker compose -f docker-compose.monitoring.yml ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Services are running${NC}"
else
    echo -e "${RED}✗ Services are not running${NC}"
    exit 1
fi
echo ""

# Test 2: Check inference service health
echo "Test 2: Testing inference service health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Inference service is healthy${NC}"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}✗ Inference service health check failed${NC}"
    exit 1
fi
echo ""

# Test 3: Make a prediction
echo "Test 3: Making a test prediction..."
PREDICTION=$(curl -s -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"features": [1.5, 2.3, 3.1, 4.2, 5.0]}')
if echo "$PREDICTION" | grep -q "predicted_class"; then
    echo -e "${GREEN}✓ Prediction successful${NC}"
    echo "   Response: $PREDICTION"
else
    echo -e "${RED}✗ Prediction failed${NC}"
    exit 1
fi
echo ""

# Test 4: Check Prometheus metrics
echo "Test 4: Verifying Prometheus metrics..."
METRICS=$(curl -s http://localhost:8000/metrics)
if echo "$METRICS" | grep -q "model_f1_score"; then
    echo -e "${GREEN}✓ Prometheus metrics are exposed${NC}"
    MODEL_F1=$(echo "$METRICS" | grep "^model_f1_score" | awk '{print $2}')
    echo "   Model F1 Score: $MODEL_F1"
else
    echo -e "${RED}✗ Prometheus metrics not found${NC}"
    exit 1
fi
echo ""

# Test 5: Check Prometheus scraping
echo "Test 5: Checking if Prometheus is scraping metrics..."
sleep 2  # Wait for scrape
PROM_TARGETS=$(curl -s http://localhost:9090/api/v1/targets)
if echo "$PROM_TARGETS" | grep -q '"job":"inference"'; then
    HEALTH=$(echo "$PROM_TARGETS" | grep -o '"health":"[^"]*"' | head -1 | cut -d'"' -f4)
    if [ "$HEALTH" == "up" ]; then
        echo -e "${GREEN}✓ Prometheus is scraping inference service${NC}"
        echo "   Target health: $HEALTH"
    else
        echo -e "${YELLOW}⚠ Prometheus target is not healthy: $HEALTH${NC}"
    fi
else
    echo -e "${RED}✗ Prometheus not scraping inference service${NC}"
    exit 1
fi
echo ""

# Test 6: Check database logging
echo "Test 6: Verifying database logging..."
DB_COUNT=$(docker compose -f docker-compose.monitoring.yml exec -T db \
    psql -U user -d mlops -t -c "SELECT COUNT(*) FROM prediction_log;" | xargs)
if [ "$DB_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Predictions are being logged to database${NC}"
    echo "   Total predictions in DB: $DB_COUNT"
else
    echo -e "${YELLOW}⚠ No predictions in database yet${NC}"
fi
echo ""

# Test 7: Check Grafana
echo "Test 7: Checking Grafana..."
GRAFANA_HEALTH=$(curl -s http://localhost:3000/api/health)
if echo "$GRAFANA_HEALTH" | grep -q "ok"; then
    echo -e "${GREEN}✓ Grafana is running${NC}"
    
    # Check if dashboard exists
    DASHBOARD=$(curl -s -u admin:admin http://localhost:3000/api/search?type=dash-db)
    if echo "$DASHBOARD" | grep -q "ml-predictions"; then
        echo -e "${GREEN}✓ ML Predictions dashboard is provisioned${NC}"
    else
        echo -e "${YELLOW}⚠ Dashboard not found${NC}"
    fi
else
    echo -e "${RED}✗ Grafana is not healthy${NC}"
    exit 1
fi
echo ""

# Test 8: Query metrics from Prometheus
echo "Test 8: Querying metrics from Prometheus..."
F1_QUERY=$(curl -s 'http://localhost:9090/api/v1/query?query=model_f1_score')
if echo "$F1_QUERY" | grep -q "\"value\""; then
    F1_VALUE=$(echo "$F1_QUERY" | grep -o '"value":\[[^]]*\]' | grep -o '[0-9.]*"$' | tr -d '"')
    echo -e "${GREEN}✓ Can query metrics from Prometheus${NC}"
    echo "   Model F1 Score from Prometheus: $F1_VALUE"
else
    echo -e "${RED}✗ Cannot query metrics from Prometheus${NC}"
    exit 1
fi
echo ""

# Summary
echo "======================================"
echo -e "${GREEN}All tests passed!${NC}"
echo "======================================"
echo ""
echo "Services are accessible at:"
echo "  - Grafana: http://localhost:3000 (admin/admin)"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Prometheus: http://localhost:9090"
echo "  - Metrics: http://localhost:8000/metrics"
echo ""
echo "To view the ML Predictions dashboard:"
echo "  1. Open http://localhost:3000"
echo "  2. Login with admin/admin"
echo "  3. Go to Dashboards → MLOps → ML Predictions Dashboard"
echo ""
