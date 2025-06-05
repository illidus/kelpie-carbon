# Render.com Deployment Guide

## Quick Deploy Steps:

1. **Go to [render.com](https://render.com)** and sign up/login with GitHub
2. **Connect your GitHub repository**: `illidus/kelpie-carbon`
3. **Create New Web Service**:
   - Repository: `illidus/kelpie-carbon` 
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - Plan: Free tier

## Configuration:
- **Environment**: Python 3
- **Health Check Path**: `/health`
- **Auto-deploy**: Yes (deploys on git push)

## Files Ready:
- ✅ `render.yaml` - Auto-detected configuration
- ✅ `requirements.txt` - All dependencies listed
- ✅ `/health` endpoint - Working health check
- ✅ API code in `api/main.py`

## Expected Result:
- Build time: ~2-3 minutes
- Your API will be available at: `https://kelpie-carbon-api.onrender.com`
- Health check: `https://kelpie-carbon-api.onrender.com/health`

## If Issues:
- Check build logs in Render dashboard
- Ensure main branch is selected
- Verify all files committed to git 