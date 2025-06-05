# 🚀 Kelpie Carbon API Deployment Guide

## Overview
This guide helps you deploy the Kelpie Carbon Analysis API to the cloud for external internet access.

## 🌟 Recommended: Railway.app

### Step 1: Setup Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (free tier available)
3. Connect your GitHub repository

### Step 2: Deploy
1. **Create New Project** in Railway dashboard
2. **Connect GitHub Repository**: Select your `kelpie-carbon` repo
3. **Auto-Deploy**: Railway will detect the `railway.json` and deploy automatically
4. **Environment Variables**: None needed for basic setup
5. **Domain**: Railway provides a free `.up.railway.app` domain

### Step 3: Get Your API URL
After deployment (5-10 minutes), you'll get a URL like:
```
https://your-app-name.up.railway.app
```

## 🔄 Alternative: Render.com

### Step 1: Setup Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (free tier available)
3. Connect your GitHub repository

### Step 2: Deploy
1. **Create New Web Service**
2. **Connect Repository**: Select your `kelpie-carbon` repo
3. **Configuration**:
   - **Name**: `kelpie-carbon-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
4. **Deploy**: Click "Create Web Service"

### Step 3: Get Your API URL
After deployment, you'll get a URL like:
```
https://kelpie-carbon-api.onrender.com
```

## 🔧 Alternative: Heroku

### Step 1: Create Procfile
```bash
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### Step 2: Deploy
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Commands:
```bash
heroku create kelpie-carbon-api
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## 📱 Update Frontend for Production

Once your API is deployed, update the dashboard to use the production API:

### Option A: Environment-based Configuration
Create `dashboard/src/config.js`:
```javascript
const config = {
  API_BASE_URL: process.env.NODE_ENV === 'production' 
    ? 'https://your-api-domain.up.railway.app'  // Replace with your actual API URL
    : 'http://localhost:8000'
};

export default config;
```

### Option B: Direct Update
Update `dashboard/src/App.jsx`:
```javascript
// Change this line:
const API_BASE_URL = 'http://localhost:8000'

// To this (replace with your actual API URL):
const API_BASE_URL = 'https://your-api-domain.up.railway.app'
```

### Rebuild and Deploy Dashboard
```bash
cd dashboard
npm run build
# Copy dist/* contents to GitHub Pages
```

## 🧪 Testing Your Deployed API

### Test Endpoints
```bash
# Health check
curl https://your-api-domain.up.railway.app/health

# Carbon analysis
curl "https://your-api-domain.up.railway.app/carbon?date=2024-07-15&aoi=POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))"
```

### API Documentation
Visit: `https://your-api-domain.up.railway.app/docs`

## 🔒 Production Considerations

### Environment Variables (if needed)
- `DATABASE_URL`: If you add a database later
- `SECRET_KEY`: For authentication features
- `CORS_ORIGINS`: Restrict allowed domains

### Monitoring
- Railway: Built-in metrics and logs
- Render: Application logs and metrics
- Heroku: Heroku metrics and logging

### Scaling
- **Railway**: Automatic scaling available
- **Render**: Upgrade to paid plans for auto-scaling
- **Heroku**: Dyno scaling options

## 📊 Cost Comparison

| Platform | Free Tier | Paid Plans Start |
|----------|-----------|------------------|
| Railway  | $5/month worth of usage | $5/month |
| Render   | 750 hours/month | $7/month |
| Heroku   | 550-1000 dyno hours | $7/month |

## 🎯 Quick Start Commands

Choose your platform and run:

### Railway (Recommended)
```bash
# Files already created: railway.json
# Just connect GitHub repo in Railway dashboard
```

### Render
```bash
# Files already created: render.yaml
# Just connect GitHub repo in Render dashboard
```

## 🔧 Troubleshooting

### Docker Build Issues
If you encounter Docker build errors like "context canceled" or "exit code: 1":

**Option 1: Use Nixpacks (Default)**
- Railway is configured to use Nixpacks instead of Docker
- This avoids Docker build complexity

**Option 2: Use Simple Dockerfile**
If you need Docker, rename `Dockerfile.simple` to `Dockerfile`:
```bash
mv Dockerfile.simple Dockerfile
git add Dockerfile
git commit -m "Use simple Dockerfile"
git push
```

**Option 3: Skip Docker Health Checks**
Some platforms don't support Docker health checks. The simple Dockerfile removes them.

### Manual Testing
```bash
# Test locally first
(.venv) PS> uvicorn api.main:app --host 0.0.0.0 --port 8000
# Visit http://localhost:8000/docs
```

## ✅ Success Checklist

- [ ] Cloud platform account created
- [ ] Repository connected
- [ ] API deployed successfully
- [ ] Health endpoint responding
- [ ] Carbon analysis endpoint working
- [ ] API documentation accessible
- [ ] Frontend updated with production API URL
- [ ] Dashboard redeployed to GitHub Pages

Your API will be accessible worldwide at your deployment URL! 🌍 