#!/bin/bash
# Quick verification script for RAG Copilot backend

set -e

cd "$(dirname "$0")"

echo "=== RAG Copilot Backend Verification ==="
echo ""

echo "✓ Step 1: Verify Python syntax"
python3 -m py_compile api/main.py
python3 -m py_compile api/routers/*.py
python3 -m py_compile api/models/*.py
echo "  All Python files compile successfully"
echo ""

echo "✓ Step 2: Verify route definitions"
echo "  Checking for route decorators..."
grep -E "@app\.(get|post|put|delete)\(\"" api/main.py | while read -r line; do
    echo "  Found: $line"
done
echo ""

echo "✓ Step 3: Verify CORS configuration"
grep -A 10 "CORSMiddleware" api/main.py | grep "allow_origins" -A 6
echo ""

echo "✓ Step 4: Check for expected routes"
expected_routes=(
    "GET /health"
    "POST /api/v1/ingest"
    "POST /api/v1/chat"
    "POST /api/v1/eval"
)

for route in "${expected_routes[@]}"; do
    method=$(awk '{print tolower($1)}' <<< "$route")
    path=$(awk '{print $2}' <<< "$route")
    if grep -q "@app.$method(\"$path\"" api/main.py; then
        echo "  ✓ Found: $route"
    else
        echo "  ✗ Missing: $route"
        exit 1
    fi
done
echo ""

echo "=== All checks passed! ==="
echo ""
echo "Next steps:"
echo "1. Install dependencies: pip install -r requirements.txt"
echo "2. Set environment variable: export OPENAI_API_KEY=your-key"
echo "3. Start server: uvicorn api.main:app --reload --port 8080"
echo "4. Test health: curl http://localhost:8080/health"
echo "5. View API docs: http://localhost:8080/docs"

exit 0
exit 0
