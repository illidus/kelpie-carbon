"""
Kelp Carbon Analysis API

FastAPI microservice for kelp biomass and carbon sequestration estimation.
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, Optional

import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from joblib import load

# Initialize FastAPI app
app = FastAPI(
    title="Kelp Carbon Analysis API",
    description="Microservice for kelp biomass estimation and carbon sequestration analysis using satellite spectral indices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global model variable
model = None

# Response models
class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="API status")
    model_loaded: bool = Field(..., description="Whether the ML model is loaded")
    timestamp: str = Field(..., description="Current timestamp")

class CarbonAnalysisResponse(BaseModel):
    """Carbon analysis response model."""
    date: str = Field(..., description="Analysis date")
    aoi_wkt: str = Field(..., description="Area of interest as WKT")
    area_m2: float = Field(..., description="Area in square meters")
    mean_fai: float = Field(..., description="Mean Floating Algae Index")
    mean_ndre: float = Field(..., description="Mean Normalized Difference Red Edge")
    biomass_t: float = Field(..., description="Estimated biomass in tonnes")
    co2e_t: float = Field(..., description="CO2 equivalent in tonnes")

def load_model():
    """Load the biomass regression model at startup."""
    global model
    model_path = "models/biomass_rf.pkl"
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    try:
        model = load(model_path)
        print(f"✅ Model loaded successfully from {model_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to load model: {e}")

def parse_simple_polygon_wkt(wkt: str) -> float:
    """
    Simple WKT parser for POLYGON geometries to calculate approximate area.
    
    This is a basic implementation that extracts coordinates and calculates
    area using the shoelace formula. For production, use shapely.
    """
    # Extract coordinates from WKT POLYGON
    pattern = r'POLYGON\s*\(\s*\(\s*([\d\s\.\-,]+)\s*\)\s*\)'
    match = re.search(pattern, wkt.upper())
    
    if not match:
        raise ValueError("Invalid WKT format. Expected POLYGON((x1 y1, x2 y2, ...))")
    
    coords_str = match.group(1)
    coord_pairs = []
    
    # Parse coordinate pairs
    for coord in coords_str.split(','):
        coord = coord.strip()
        if coord:
            parts = coord.split()
            if len(parts) >= 2:
                try:
                    x, y = float(parts[0]), float(parts[1])
                    coord_pairs.append((x, y))
                except ValueError:
                    continue
    
    if len(coord_pairs) < 3:
        raise ValueError("Polygon must have at least 3 coordinate pairs")
    
    # Calculate area using shoelace formula (approximate for lat/lon)
    # Note: This is a simplified calculation. For accurate geodesic area,
    # use proper projection and geodesic libraries like GeoPy or Shapely
    n = len(coord_pairs)
    area = 0.0
    
    for i in range(n):
        j = (i + 1) % n
        area += coord_pairs[i][0] * coord_pairs[j][1]
        area -= coord_pairs[j][0] * coord_pairs[i][1]
    
    area = abs(area) / 2.0
    
    # Convert from degrees to approximate meters squared
    # Very rough approximation: 1 degree ≈ 111,000 meters at equator
    # This is simplified and not geodesically accurate
    area_m2 = area * (111000 ** 2)
    
    return area_m2

def generate_mock_spectral_data(area_m2: float, date: str) -> tuple[float, float]:
    """
    Generate realistic mock spectral indices based on area and date.
    
    In production, this would extract actual satellite data for the AOI and date.
    """
    # Use area and date to create deterministic but varied values
    date_hash = hash(date) % 1000000
    area_factor = np.log10(max(area_m2, 1.0))
    
    # Generate FAI and NDRE with some seasonal variation
    month = int(date.split('-')[1]) if len(date.split('-')) > 1 else 6
    seasonal_factor = np.sin(2 * np.pi * month / 12) * 0.1
    
    # Mock FAI: -0.05 to 0.3 range
    fai = 0.05 + (date_hash % 100) / 1000.0 + area_factor * 0.02 + seasonal_factor
    fai = np.clip(fai, -0.05, 0.3)
    
    # Mock NDRE: -0.2 to 0.8 range
    ndre = 0.2 + (date_hash % 200) / 500.0 + area_factor * 0.05 + seasonal_factor * 1.5
    ndre = np.clip(ndre, -0.2, 0.8)
    
    return float(fai), float(ndre)

def estimate_carbon_sequestration(biomass_kg: float) -> float:
    """
    Estimate CO2 equivalent sequestration from kelp biomass.
    
    Based on research:
    - Kelp carbon content: ~30-35% dry weight
    - CO2 equivalent: 3.67 (molecular weight ratio CO2/C)
    """
    carbon_content_ratio = 0.325  # 32.5% carbon content
    co2_equivalent_ratio = 3.67   # CO2/C molecular weight ratio
    
    carbon_kg = biomass_kg * carbon_content_ratio
    co2e_kg = carbon_kg * co2_equivalent_ratio
    
    return co2e_kg / 1000.0  # Convert to tonnes

@app.on_event("startup")
async def startup_event():
    """Load model on application startup."""
    load_model()

@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns the API status and model loading state.
    """
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        timestamp=datetime.now().isoformat()
    )

@app.get("/carbon", response_model=CarbonAnalysisResponse)
async def carbon_analysis(
    date: str = Query(..., description="Analysis date in YYYY-MM-DD format", pattern=r'^\d{4}-\d{2}-\d{2}$'),
    aoi: str = Query(..., description="Area of Interest as WKT POLYGON")
) -> CarbonAnalysisResponse:
    """
    Kelp carbon analysis endpoint.
    
    Analyzes kelp biomass and carbon sequestration for a given area and date.
    
    Parameters:
    - date: Analysis date in YYYY-MM-DD format
    - aoi: Area of Interest as WKT POLYGON geometry
    
    Returns:
    - Carbon analysis results including biomass and CO2 estimates
    """
    # Validate model is loaded
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available")
    
    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Parse WKT and calculate area
    try:
        area_m2 = parse_simple_polygon_wkt(aoi)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid WKT geometry: {e}")
    
    # Generate mock spectral data (in production, this would extract from satellite imagery)
    mean_fai, mean_ndre = generate_mock_spectral_data(area_m2, date)
    
    # Predict biomass using the loaded model
    try:
        # Model expects FAI, NDRE as features
        features = np.array([[mean_fai, mean_ndre]])
        biomass_kg_per_m2 = model.predict(features)[0]
        
        # Ensure non-negative prediction
        biomass_kg_per_m2 = max(biomass_kg_per_m2, 0.0)
        
        # Calculate total biomass for the area
        total_biomass_kg = biomass_kg_per_m2 * area_m2
        biomass_tonnes = total_biomass_kg / 1000.0
        
        # Estimate carbon sequestration
        co2e_tonnes = estimate_carbon_sequestration(total_biomass_kg)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")
    
    return CarbonAnalysisResponse(
        date=date,
        aoi_wkt=aoi,
        area_m2=area_m2,
        mean_fai=mean_fai,
        mean_ndre=mean_ndre,
        biomass_t=biomass_tonnes,
        co2e_t=co2e_tonnes
    )

@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "message": "Kelp Carbon Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "carbon": "/carbon?date=YYYY-MM-DD&aoi=WKT_POLYGON"
        }
    }

# Serve static files for the dashboard
dashboard_path = "dashboard/dist"
if os.path.exists(dashboard_path):
    # Mount the assets directory for CSS/JS files
    app.mount("/assets", StaticFiles(directory=f"{dashboard_path}/assets"), name="assets")
    
    @app.get("/")
    async def dashboard():
        """Serve the React dashboard."""
        return FileResponse(f"{dashboard_path}/index.html")
    
    @app.get("/vite.svg")
    async def vite_svg():
        """Serve the Vite logo."""
        return FileResponse(f"{dashboard_path}/vite.svg")
else:
    @app.get("/")
    async def root():
        """Root endpoint when dashboard is not available."""
        return {
            "message": "Kelp Carbon Analysis API",
            "version": "1.0.0", 
            "dashboard": "Dashboard not built. Run 'cd dashboard && npm run build' to build the frontend.",
            "docs": "/docs",
            "health": "/health"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 