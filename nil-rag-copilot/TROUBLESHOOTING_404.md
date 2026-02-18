# Troubleshooting 404 Error for RAG Copilot

## Problem
When clicking "Start indexing" in the RAG Copilot demo, you receive a **404 Not Found** error.

## Root Cause Analysis

The 404 error occurs when the frontend tries to call an API endpoint that doesn't exist on the backend. This can happen for several reasons:

### 1. Backend Not Deployed
**Symptom**: Health check also fails with connection error  
**Cause**: The Render service hasn't been created or deployed yet  
**Solution**: Deploy the backend to Render (see DEPLOYMENT.md)

### 2. Wrong Backend Code Deployed
**Symptom**: Health check works (`/health` returns 200) but `/api/v1/ingest` returns 404  
**Cause**: An older version of the backend is deployed that uses different route paths  
**Solution**: Redeploy the latest code from the repository

### 3. Incorrect Frontend URL
**Symptom**: Consistent 404 on all endpoints  
**Cause**: The `API_BASE` URL in the frontend doesn't match the actual deployed service  
**Solution**: Update the frontend configuration

## Diagnostic Steps

### Step 1: Verify Backend Deployment

Check if the backend service exists and is running:

```bash
# Test health endpoint
curl https://nil-rag-copilot.onrender.com/health

# Expected response:
# {"status":"ok","version":"0.2.0"}

# If this fails with connection error: Backend not deployed
# If this fails with 404: Health endpoint path is wrong (very unlikely)
# If this succeeds: Proceed to Step 2
```

### Step 2: Test API Endpoints

Test each API endpoint to see which ones exist:

```bash
# Test ingest endpoint (should return 400 or 422 without a file, NOT 404)
curl -X POST https://nil-rag-copilot.onrender.com/api/v1/ingest

# Test chat endpoint (should return 422 validation error, NOT 404)
curl -X POST https://nil-rag-copilot.onrender.com/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{}'

# Test eval endpoint (should return 422 validation error, NOT 404)
curl -X POST https://nil-rag-copilot.onrender.com/api/v1/eval \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Results**:
- ✅ **400/422 Error**: Endpoint exists, just missing required data → Backend is correctly configured
- ❌ **404 Error**: Endpoint doesn't exist → Backend has wrong routes

### Step 3: Check API Documentation

Visit the auto-generated API docs:

```
https://nil-rag-copilot.onrender.com/docs
```

This will show all available endpoints. Compare with expected endpoints:
- `GET /health`
- `POST /api/v1/ingest`
- `POST /api/v1/chat`
- `POST /api/v1/eval`

## Solutions

### Solution A: Backend Routes Missing `/api/v1/` Prefix

**If the API docs show**:
- `POST /ingest`
- `POST /chat`
- `POST /eval`

**Then the backend needs to be fixed**:

The routes in `nil-rag-copilot/api/main.py` should have the `/api/v1/` prefix:

```python
@app.post("/api/v1/ingest", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)):
    ...

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    ...

@app.post("/api/v1/eval", response_model=EvalResponse)
async def run_eval(req: EvalRequest):
    ...
```

**Verify** the code in the repository matches this, then redeploy.

### Solution B: Frontend URL Incorrect

**If the API docs show the correct routes** but the frontend still gets 404, check:

1. Open `demos/rag-copilot/index.html`
2. Find the configuration section (around line 505)
3. Verify `PROD_API_BASE` matches your deployed service:

```javascript
const PROD_API_BASE = "https://nil-rag-copilot.onrender.com/api/v1";
const PROD_API_ROOT = "https://nil-rag-copilot.onrender.com";
```

4. If your Render service has a different URL, update these values
5. Commit and push changes

### Solution C: Service Not Deployed

If `curl https://nil-rag-copilot.onrender.com/health` fails with connection error:

1. Go to https://dashboard.render.com
2. Check if the `nil-rag-copilot` service exists
3. If not, create it following `DEPLOYMENT.md`
4. If yes, check the service status and logs

## Current Repository State (Feb 2026)

As of the latest commit, the repository code is correct:

✅ **Backend** (`nil-rag-copilot/api/main.py`):
- `POST /api/v1/ingest` ✓
- `POST /api/v1/chat` ✓
- `POST /api/v1/eval` ✓

✅ **Frontend** (`demos/rag-copilot/index.html`):
- Calls `${API_BASE}/ingest` where `API_BASE = "https://nil-rag-copilot.onrender.com/api/v1"` ✓
- Auto-detects local vs production environment ✓
- Enhanced error messages for 404 debugging ✓

**If both match and you still get 404**: The deployed version on Render is out of date.

## Forcing a Redeploy

To ensure Render is running the latest code:

1. Go to https://dashboard.render.com
2. Find your `nil-rag-copilot` service
3. Click "Manual Deploy" → "Deploy latest commit"
4. Wait for deployment to complete (~3-5 minutes)
5. Verify with health check: `curl https://nil-rag-copilot.onrender.com/health`
6. Test frontend at https://www.neuromorphicinference.com/demos/rag-copilot/

## Quick Reference

| Component | Expected Value |
|-----------|---------------|
| Health endpoint | `GET /health` |
| Ingest endpoint | `POST /api/v1/ingest` |
| Chat endpoint | `POST /api/v1/chat` |
| Eval endpoint | `POST /api/v1/eval` |
| Frontend API_BASE | `https://nil-rag-copilot.onrender.com/api/v1` |
| Backend port | 8080 |

## Still Having Issues?

1. Check Render service logs for errors
2. Verify `OPENAI_API_KEY` environment variable is set
3. Test with the API docs UI at `/docs`
4. Check browser console for detailed error messages
5. Look for enhanced error messages in the UI (added in this PR)
