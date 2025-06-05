# Kelpie Carbon Dashboard Testing Guide

## 🎉 What's Working

✅ **Dashboard UI**: The React dashboard is now successfully deployed on GitHub Pages at:
   - https://illidus.github.io/kelpie-carbon/dashboard/

✅ **UI Components**: All user interface elements are functional:
   - Interactive map (Leaflet.js)
   - Polygon drawing tools
   - Date picker for analysis
   - Results display panel

✅ **API Implementation**: Complete FastAPI backend with:
   - Carbon analysis endpoints
   - WKT polygon parsing
   - Spectral index calculations
   - Biomass estimation
   - CO₂ sequestration calculations

## ⚠️ Current Limitation

**API Hosting**: The analysis functionality doesn't work on the live site because:
- GitHub Pages only serves static files
- The API endpoints require a backend server
- The dashboard tries to call `https://illidus.github.io/kelpie-carbon/carbon` but this endpoint doesn't exist

## 🧪 Testing Options

### 1. Test the Live Dashboard UI
Visit: https://illidus.github.io/kelpie-carbon/dashboard/

**What to test:**
- ✅ Page loads correctly
- ✅ Map displays (centered on Victoria, BC)
- ✅ Drawing controls are visible
- ✅ Date picker works
- ❌ Analysis will show "fetch error" (expected)

### 2. Test API Functionality Locally

#### Prerequisites
```bash
pip install fastapi uvicorn numpy joblib requests pytest
```

#### Option A: Quick Test
```bash
python run_local_test.py
```
This will:
- Start the API server on `localhost:8000`
- Run comprehensive tests
- Show detailed results
- Stop the server automatically

#### Option B: Manual Testing
```bash
# Terminal 1: Start the API server
python -m uvicorn api.main:app --host localhost --port 8000

# Terminal 2: Test endpoints
curl "http://localhost:8000/health"
curl "http://localhost:8000/carbon?date=2024-07-15&aoi=POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))"

# Or visit http://localhost:8000 for the dashboard with working analysis
```

### 3. Selenium UI Testing

```bash
pip install selenium
python tests/test_dashboard_analysis.py
```

Note: Requires Chrome/ChromeDriver for browser automation.

### 4. Direct Function Testing

```bash
python tests/test_api_endpoints.py
```

Tests the core API functions without starting a server.

## 📊 Expected Test Results

### Carbon Analysis Response
```json
{
  "date": "2024-07-15",
  "aoi_wkt": "POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))",
  "area_m2": 12345678.0,
  "mean_fai": 0.123,
  "mean_ndre": 0.456,
  "biomass_t": 789.12,
  "co2e_t": 939.45
}
```

### Validation Ranges
- `area_m2`: > 0
- `mean_fai`: -0.2 to 0.5
- `mean_ndre`: -0.3 to 0.8
- `biomass_t`: ≥ 0
- `co2e_t`: ≥ 0
- `co2e_t/biomass_t` ratio: ~1.19 (acceptable: 0.8 to 2.0)

## 🚀 Next Steps for Full Deployment

### Option 1: Deploy API to Cloud Service
1. **Railway.app** (Recommended):
   ```bash
   # Create railway.json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
     }
   }
   ```

2. **Heroku**:
   ```bash
   # Create Procfile
   web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Render.com**:
   - Deploy from GitHub
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Option 2: Update Dashboard for Production
Once you have a deployed API URL, update:

```javascript
// dashboard/src/App.jsx
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-api-domain.com'  // Replace with actual API URL
  : 'http://localhost:8000'
```

Then rebuild and redeploy:
```bash
cd dashboard
npm run build
# Copy dist/* to GitHub Pages
```

## 🔧 Development Workflow

### Making Changes
1. **API Changes**: Edit files in `api/` directory
2. **Dashboard Changes**: Edit files in `dashboard/src/`
3. **Test Locally**: Use `python run_local_test.py`
4. **Deploy**: 
   - API: Push to cloud service
   - Dashboard: Build and push to `gh-pages` branch

### Testing Strategy
1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test API endpoints
3. **UI Tests**: Test dashboard interactions
4. **End-to-End Tests**: Test complete workflow

## 📁 File Structure

```
kelpie-carbon/
├── api/                     # FastAPI backend
│   └── main.py             # API endpoints
├── dashboard/              # React frontend
│   ├── src/
│   │   └── App.jsx        # Main dashboard component
│   └── dist/              # Built files (for deployment)
├── tests/                  # Test files
│   ├── test_dashboard_analysis.py    # Selenium tests
│   └── test_api_endpoints.py         # API tests
├── run_local_test.py      # Local testing script
├── test_dashboard_api.py   # GitHub Pages test
└── TESTING_GUIDE.md       # This file
```

## 🎯 Test Summary

**What Works Now:**
- ✅ Dashboard UI loads and displays correctly
- ✅ All UI components are functional
- ✅ API backend is fully implemented
- ✅ Local testing works perfectly
- ✅ Comprehensive test suite available

**What Needs Deployment:**
- 🚀 API backend to cloud service
- 🔧 Update dashboard API URL
- 📊 Set up CI/CD for automated testing

The dashboard is ready for production use once the API is deployed to a cloud service! 