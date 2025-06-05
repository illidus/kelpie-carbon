# Kelpie Carbon - Kelp Biomass & Carbon Sequestration Analysis

A comprehensive platform for analyzing kelp biomass and carbon sequestration using satellite imagery and machine learning.

## 🌊 Overview

This project provides:
- **API Backend**: FastAPI server for kelp biomass estimation
- **Interactive Dashboard**: React-based web interface with map visualization  
- **Satellite Processing**: Spectral indices calculation (FAI, NDRE)
- **ML Model**: Random Forest model for biomass prediction
- **GitHub Pages Deployment**: Live dashboard at your GitHub Pages URL

## 📁 Project Structure

```
kelpie-carbon/
├── api/                    # FastAPI backend
│   └── main.py            # Main API server
├── dashboard/             # React frontend  
│   ├── src/
│   │   └── App.jsx       # Main React component
│   └── dist/             # Built dashboard (deployed)
├── models/                # ML models
│   └── biomass_rf.pkl    # Random Forest biomass model
├── sentinel_pipeline/     # Satellite data processing
│   ├── __init__.py
│   └── indices.py        # Spectral indices (FAI, NDRE)
├── tests/                 # Test suites
├── notebooks/             # Jupyter analysis notebooks
├── tiles/                 # Map tile cache
├── requirements.txt       # Python dependencies
└── index.html            # GitHub Pages landing page
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `numpy` - Numerical computing
- `scikit-learn` - Machine learning
- `joblib` - Model serialization

### 2. Run API Locally

```powershell
# Windows PowerShell
cd api
python main.py
```

```bash
# Linux/Mac
cd api && python main.py
```

The API will start on `http://localhost:8000`

### 3. Test API Endpoints

**Health Check:**
```
GET http://localhost:8000/health
```

**Carbon Analysis:**
```
GET http://localhost:8000/carbon?date=2023-06-15&aoi=POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))
```

### 4. View Dashboard

- **Local Development**: Open `dashboard/dist/index.html` in browser
- **Live Dashboard**: Visit your GitHub Pages URL

## 🔬 How It Works

### Spectral Indices
- **FAI (Floating Algae Index)**: Detects algae/kelp in water
- **NDRE (Normalized Difference Red Edge)**: Measures vegetation health

### Carbon Calculation
1. Satellite imagery → Spectral indices (FAI, NDRE)
2. ML model predicts biomass from indices  
3. Biomass → Carbon content (32.5%)
4. Carbon → CO₂ equivalent (3.67x ratio)

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health check |
| `/carbon` | GET | Analyze carbon sequestration |
| `/docs` | GET | Interactive API documentation |

## 🌐 Deployment

### GitHub Pages (Dashboard Only)
The dashboard is automatically deployed to GitHub Pages. The API needs separate cloud hosting.

### Cloud API Deployment Options
- **Railway**: `railway up` (free tier)
- **Render**: Connect GitHub repo (free tier)
- **Fly.io**: `fly deploy` (free allowance)
- **Heroku**: `git push heroku main` (paid)

## 🧪 Testing

### Manual Testing
```bash
python test_api_simple.py
```

### Full Test Suite
```bash
python run_local_test.py
```

## 📊 Data Flow

```
Satellite Data → Spectral Indices → ML Model → Biomass → Carbon → CO₂e
     ↓               ↓                ↓          ↓         ↓        ↓
  Sentinel-2        FAI/NDRE    Random Forest   kg/m²    32.5%   3.67x
```

## 🛠️ Development

### API Development
```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Dashboard Development  
```bash
cd dashboard
npm install
npm run dev
```

## 📝 API Response Format

```json
{
  "date": "2023-06-15",
  "aoi_wkt": "POLYGON(...)",
  "area_m2": 1000000.0,
  "mean_fai": 0.15,
  "mean_ndre": 0.35,
  "biomass_t": 2.5,
  "co2e_t": 3.0
}
```

## 🔧 Troubleshooting

### API Won't Start
- Check Python version (3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Verify model file exists: `models/biomass_rf.pkl`

### Dashboard Shows Error
- Check API is running on localhost:8000
- For production, update API URL in `App.jsx`

### Import Errors
- Ensure `sentinel_pipeline` module is in Python path
- Check all dependencies are installed

## 📚 References

- [Sentinel-2 Bands](https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi/resolutions/radiometric)
- [FAI Algorithm](https://doi.org/10.1016/j.rse.2009.01.026)
- [Kelp Carbon Content](https://doi.org/10.1038/ncomms3837)

## 📄 License

Open source - see repository for details. 