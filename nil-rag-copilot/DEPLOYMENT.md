# Deployment Guide for NIL RAG Copilot Backend

## Overview

This guide walks through deploying the NIL RAG Copilot backend to Render.com's free tier.

## Prerequisites

- GitHub repository with the code pushed
- Render.com account (sign up at https://dashboard.render.com)
- OpenAI API key (get one at https://platform.openai.com/api-keys)

## Deployment Steps

### 1. Push Code to GitHub

Ensure all changes are committed and pushed:

```bash
git add .
git commit -m "Complete RAG Copilot backend"
git push origin main
```

### 2. Create Render Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `neuromorphic-inference-lab-site`
4. Render will auto-detect the `render.yaml` configuration

### 3. Configure Environment Variables

In the Render dashboard for your service:

1. Go to **"Environment"** tab
2. Add the following environment variable:
   - **Key**: `OPENAI_API_KEY`
   - **Value**: Your OpenAI API key (e.g., `sk-proj-...`)
   - Keep **"Secret"** checked

### 4. Deploy

1. Click **"Create Web Service"** or **"Manual Deploy"**
2. Wait for the build to complete (~3-5 minutes for first deployment)
3. Monitor logs for any errors

### 5. Verify Deployment

Once deployed, verify the service is running:

```bash
# Test health endpoint
curl https://nil-rag-copilot.onrender.com/health
# Expected: {"status":"ok","version":"0.2.0"}

# Test API documentation
curl https://nil-rag-copilot.onrender.com/
# Expected: {"service":"NIL RAG Copilot API",...}
```

Visit the interactive API docs at:
- https://nil-rag-copilot.onrender.com/docs

### 6. Update Frontend

In the main repository, update the frontend to point to the deployed backend:

1. Edit `demos/rag-copilot/index.html`
2. Find the line with `const API_BASE =`
3. Update it to:
   ```javascript
   const API_BASE = "https://nil-rag-copilot.onrender.com/api/v1";
   ```
4. Commit and push the change
5. Cloudflare Pages will automatically redeploy

## Service Configuration

### render.yaml

The service is configured via `render.yaml` in the repository root:

```yaml
services:
  - type: web
    name: nil-rag-copilot
    runtime: docker
    dockerfilePath: ./nil-rag-copilot/Dockerfile
    dockerContext: ./nil-rag-copilot
    plan: free
    envVars:
      - key: OPENAI_API_KEY
        sync: false
    healthCheckPath: /health
    autoDeploy: true
```

### Dockerfile

The Docker container configuration in `nil-rag-copilot/Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Free Tier Limitations

Render's free tier has the following limitations:

- **Sleep after inactivity**: Service sleeps after 15 minutes of inactivity
- **Startup time**: First request after sleep takes 30-60 seconds
- **Memory**: 512 MB RAM
- **Build minutes**: 500 minutes/month

### Handling Sleep Mode

The frontend shows an offline indicator when the service is sleeping. Users will see:
- ⚠️ "Backend service is starting up..." during cold start
- ● "System online" once connected

## Monitoring

### View Logs

In Render dashboard:
1. Go to your service
2. Click **"Logs"** tab
3. Monitor for errors or warnings

### Health Checks

Render automatically monitors `/health` endpoint:
- If it returns non-200, service is marked as unhealthy
- Automatic restarts on repeated failures

## Troubleshooting

### Service won't start

Check logs for:
- Missing environment variables: `OPENAI_API_KEY`
- Python dependency installation errors
- Port binding issues (should use 8080)

### 500 errors on requests

Common causes:
- Invalid OpenAI API key
- Rate limiting from OpenAI
- Out of memory (large PDFs)

### Long cold starts

First request after sleep takes ~30-60 seconds because:
- Render spins up container
- Python dependencies load
- Sentence transformer model downloads (~80MB)

Consider upgrading to paid tier for:
- No sleep mode
- Faster cold starts
- More memory

## Cost Estimates

### Free Tier (Current Setup)
- **Cost**: $0/month
- **Limitations**: Sleep mode, slower cold starts
- **Best for**: Demo purposes, light usage

### Starter Tier (If Needed)
- **Cost**: ~$7/month
- **Benefits**: No sleep, faster responses, 1GB RAM
- **Best for**: Production use with moderate traffic

## Security Notes

### Environment Variables
- Never commit `OPENAI_API_KEY` to git
- Use Render's environment variable management
- Rotate keys regularly

### Rate Limiting
Consider adding rate limiting middleware if traffic increases:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### CORS Configuration
Current CORS settings allow:
- `https://www.neuromorphicinference.com`
- `http://localhost:*` (for local development)

Update in `api/main.py` if deploying to additional domains.

## Maintenance

### Updates
1. Push changes to GitHub
2. Render auto-deploys (if `autoDeploy: true`)
3. Monitor logs during deployment

### Rollback
In Render dashboard:
1. Go to **"Events"** tab
2. Find previous successful deploy
3. Click **"Rollback to this version"**

## Support

For issues:
- Backend: Check Render logs and server errors
- Frontend: Check browser console for API errors
- OpenAI: Verify API key and quota at https://platform.openai.com

## Next Steps

After deployment:
1. ✅ Verify health endpoint responds
2. ✅ Test PDF upload via `/docs` interface
3. ✅ Update frontend API_BASE URL
4. ✅ Test end-to-end from https://www.neuromorphicinference.com/demos/rag-copilot/
5. Monitor logs for first 24 hours
