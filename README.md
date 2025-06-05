# Kelpie Carbon

**Kelp biomass estimation and carbon sequestration analysis using satellite spectral indices**

## Description

Kelpie Carbon is a machine learning pipeline that analyzes satellite imagery to estimate kelp biomass and calculate carbon sequestration potential. The system uses spectral indices (FAI - Floating Algae Index, NDRE - Normalized Difference Red Edge) from Sentinel-2 imagery to predict kelp dry biomass and estimate CO₂ equivalent sequestration.

### Features

- 🛰️ **Spectral Analysis**: FAI and NDRE index calculation for kelp detection
- 🤖 **ML Prediction**: Random Forest model for biomass estimation  
- 🌊 **Carbon Calculation**: CO₂ equivalent sequestration estimates
- 🚀 **FastAPI Service**: Production-ready REST API
- 🧪 **Comprehensive Testing**: 62+ tests with 94% coverage
- 📊 **Jupyter Notebooks**: Interactive analysis and visualization

## Getting Started

### Prerequisites

- Python 3.9+ 
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/illidus/kelpie-carbon.git
cd kelpie-carbon

# Install dependencies
poetry install

# Run tests to verify setup
poetry run pytest -q

# Start the API server
poetry run uvicorn api.main:app --reload
```

The API will be available at http://localhost:8000 with interactive docs at http://localhost:8000/docs

### 🐳 Docker Deployment (Recommended for Production)

1. **Clone and setup environment**:
   ```bash
   git clone https://github.com/illidus/kelpie-carbon.git
   cd kelpie-carbon
   cp .env.example .env  # Configure your environment variables
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **Verify deployment**:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status": "healthy", "model_loaded": true}
   ```

**Services Included:**
- 🌊 **FastAPI Application** (`localhost:8000`) - Carbon analysis API and dashboard
- 🗄️ **PostGIS Database** (`localhost:5432`) - Spatial data storage  
- 📦 **Redis Cache** (`localhost:6379`) - Results caching

### API Usage

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Carbon Analysis
```bash
curl "http://localhost:8000/carbon?date=2024-06-15&aoi=POLYGON((-123.5 48.4, -123.4 48.4, -123.4 48.5, -123.5 48.5, -123.5 48.4))"
```

**Response:**
```json
{
  "date": "2024-06-15",
  "aoi_wkt": "POLYGON((-123.5 48.4, -123.4 48.4, -123.4 48.5, -123.5 48.5, -123.5 48.4))",
  "area_m2": 123210000.0,
  "mean_fai": 0.3,
  "mean_ndre": 0.78,
  "biomass_t": 2222461.98,
  "co2e_t": 2650841.53
}
```

### Environment Variables

For production deployment, configure these environment variables:

```bash
# Model Configuration
MODEL_PATH=models/biomass_rf.pkl  # Path to trained ML model

# Sentinel Hub API (for real satellite data)
SENTINELHUB_CLIENT_ID=your_client_id
SENTINELHUB_CLIENT_SECRET=your_client_secret
SENTINELHUB_INSTANCE_ID=your_instance_id

# API Configuration  
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
```

### Development

#### Project Structure
```
kelpie-carbon/
├── api/                    # FastAPI application
│   └── main.py            # API endpoints and models
├── data/                  # Sample datasets
├── models/                # Trained ML models (Git LFS)
├── notebooks/             # Jupyter analysis notebooks
├── sentinel_pipeline/     # Core Python package
│   ├── indices.py        # Spectral index calculations
│   ├── mask.py           # Cloud masking utilities
│   └── fetch.py          # Data fetching utilities
└── tests/                 # Test suite (62+ tests)
```

#### Running Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=sentinel_pipeline --cov=api

# Run specific test file
poetry run pytest tests/test_api.py -v

# Type checking
poetry run mypy sentinel_pipeline/ api/
```

#### Code Quality
```bash
# Format code
poetry run black sentinel_pipeline/ api/

# Sort imports  
poetry run isort sentinel_pipeline/ api/

# Lint code
poetry run flake8 sentinel_pipeline/ api/
```

### Notebooks

- `notebooks/biomass_regression.ipynb` - Complete ML pipeline with model training and evaluation
- Interactive analysis with mock data and visualizations

### Model Details

- **Algorithm**: Random Forest Regression
- **Features**: FAI (Floating Algae Index), NDRE (Normalized Difference Red Edge)  
- **Training Data**: 20 sample points around Victoria, BC
- **Performance**: R² = 0.730, MSE = 1.41
- **Carbon Conversion**: 32.5% carbon content, 3.67 CO₂/C ratio

## API Reference

### Endpoints

#### `GET /health`
Health check endpoint returning API status and model state.

#### `GET /carbon`
Carbon analysis endpoint for biomass and CO₂ estimation.

**Parameters:**
- `date` (string): Analysis date in YYYY-MM-DD format
- `aoi` (string): Area of Interest as WKT POLYGON geometry

**Returns:** Carbon analysis results with area, spectral indices, biomass, and CO₂ estimates.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run the test suite (`poetry run pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Sentinel-2 imagery provided by ESA Copernicus program
- Spectral indices research from kelp remote sensing literature
- Carbon sequestration estimates based on kelp biology research 


   ```

4. **Test carbon analysis**:
   ```bash
   curl "http://localhost:8000/carbon?date=2024-06-15&aoi=POLYGON((-123.5%2048.4,%20-123.4%2048.4,%20-123.4%2048.5,%20-123.5%2048.5,%20-123.5%2048.4))"
   ```

### Services Included

- **🌊 FastAPI Application** (`localhost:8000`) - Carbon analysis API and dashboard
- **🗄️ PostGIS Database** (`localhost:5432`) - Spatial data storage
- **📦 Redis Cache** (`localhost:6379`) - Results caching
- **📊 Dashboard** (`localhost:8000/`) - Interactive kelp carbon analysis

### Environment Variables

```bash
# Database Configuration
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://kelpie:password@localhost:5432/kelpie_carbon

# Optional: AWS S3 for result storage
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_RESULTS_BUCKET=kelpie-carbon-results

# Optional: Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/your/webhook
```

### Production Considerations

1. **Security**: Change default passwords in `.env`
2. **SSL**: Add nginx reverse proxy with SSL certificates
3. **Monitoring**: Enable health checks and logging
4. **Backup**: Configure automatic PostGIS backups
5. **Scaling**: Use Docker Swarm or Kubernetes for multi-node deployment 