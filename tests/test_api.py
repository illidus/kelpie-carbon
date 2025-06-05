"""
Tests for the Kelp Carbon Analysis API.
"""

import json
import os
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from api.main import app


class TestKelpCarbonAPI:
    """Test suite for the Kelp Carbon Analysis API."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock model for testing."""
        mock = MagicMock()
        mock.predict.return_value = [12.5]  # Mock biomass prediction
        return mock
        
    def test_health_endpoint_with_model(self, client, mock_model):
        """Test health endpoint when model is loaded."""
        # Mock the global model variable
        with patch('api.main.model', mock_model):
            response = client.get("/health")
            
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True
        assert "timestamp" in data
        
    def test_health_endpoint_without_model(self, client):
        """Test health endpoint when model is not loaded."""
        with patch('api.main.model', None):
            response = client.get("/health")
            
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "unhealthy"
        assert data["model_loaded"] is False
        assert "timestamp" in data
        
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Kelp Carbon Analysis API"
        assert data["version"] == "1.0.0"
        assert "docs" in data
        assert "endpoints" in data
        
    def test_carbon_endpoint_success(self, client, mock_model):
        """Test successful carbon analysis request."""
        test_date = "2024-06-15"
        test_wkt = "POLYGON((-123.5 48.4, -123.4 48.4, -123.4 48.5, -123.5 48.5, -123.5 48.4))"
        
        with patch('api.main.model', mock_model):
            response = client.get(f"/carbon?date={test_date}&aoi={test_wkt}")
            
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        required_fields = [
            "date", "aoi_wkt", "area_m2", "mean_fai", 
            "mean_ndre", "biomass_t", "co2e_t"
        ]
        for field in required_fields:
            assert field in data
            
        # Verify data types and ranges
        assert data["date"] == test_date
        assert data["aoi_wkt"] == test_wkt
        assert isinstance(data["area_m2"], float)
        assert data["area_m2"] > 0
        assert isinstance(data["mean_fai"], float)
        assert isinstance(data["mean_ndre"], float)
        assert isinstance(data["biomass_t"], float)
        assert data["biomass_t"] >= 0
        assert isinstance(data["co2e_t"], float)
        assert data["co2e_t"] >= 0
        
        # Verify model was called
        mock_model.predict.assert_called_once()
        
    def test_carbon_endpoint_no_model(self, client):
        """Test carbon endpoint when model is not loaded."""
        test_date = "2024-06-15"
        test_wkt = "POLYGON((-123.5 48.4, -123.4 48.4, -123.4 48.5, -123.5 48.5, -123.5 48.4))"
        
        with patch('api.main.model', None):
            response = client.get(f"/carbon?date={test_date}&aoi={test_wkt}")
            
        assert response.status_code == 503
        assert "Model not available" in response.json()["detail"]
        
    def test_carbon_endpoint_invalid_date_format(self, client, mock_model):
        """Test carbon endpoint with invalid date format."""
        test_wkt = "POLYGON((-123.5 48.4, -123.4 48.4, -123.4 48.5, -123.5 48.5, -123.5 48.4))"
        
        with patch('api.main.model', mock_model):
            # Test regex validation failures (422)
            regex_invalid_dates = ["24-06-15", "2024/06/15", "invalid-date"]
            for invalid_date in regex_invalid_dates:
                response = client.get(f"/carbon?date={invalid_date}&aoi={test_wkt}")
                assert response.status_code == 422
                
            # Test datetime parsing failures (400) - valid regex but invalid date
            parsing_invalid_dates = ["2024-13-01", "2024-02-30"]
            for invalid_date in parsing_invalid_dates:
                response = client.get(f"/carbon?date={invalid_date}&aoi={test_wkt}")
                assert response.status_code == 400
                
    def test_carbon_endpoint_invalid_wkt(self, client, mock_model):
        """Test carbon endpoint with invalid WKT geometry."""
        test_date = "2024-06-15"
        invalid_wkts = [
            "INVALID_WKT",
            "POLYGON((invalid))",
            "POINT(1 2)",  # Not a polygon
            "POLYGON((1))",  # Too few coordinates
        ]
        
        with patch('api.main.model', mock_model):
            for invalid_wkt in invalid_wkts:
                response = client.get(f"/carbon?date={test_date}&aoi={invalid_wkt}")
                assert response.status_code == 400
                assert "Invalid WKT" in response.json()["detail"]
                
    def test_carbon_endpoint_missing_parameters(self, client, mock_model):
        """Test carbon endpoint with missing required parameters."""
        with patch('api.main.model', mock_model):
            # Missing date
            response = client.get("/carbon?aoi=POLYGON((1 1, 2 2, 3 3, 1 1))")
            assert response.status_code == 422
            
            # Missing aoi
            response = client.get("/carbon?date=2024-06-15")
            assert response.status_code == 422
            
            # Missing both
            response = client.get("/carbon")
            assert response.status_code == 422
            
    def test_carbon_endpoint_model_prediction_error(self, client):
        """Test carbon endpoint when model prediction fails."""
        test_date = "2024-06-15"
        test_wkt = "POLYGON((-123.5 48.4, -123.4 48.4, -123.4 48.5, -123.5 48.5, -123.5 48.4))"
        
        # Mock model that raises an exception
        mock_model = MagicMock()
        mock_model.predict.side_effect = Exception("Prediction failed")
        
        with patch('api.main.model', mock_model):
            response = client.get(f"/carbon?date={test_date}&aoi={test_wkt}")
            
        assert response.status_code == 500
        assert "Prediction error" in response.json()["detail"]
        
    def test_parse_simple_polygon_wkt(self):
        """Test the WKT polygon parser function."""
        from api.main import parse_simple_polygon_wkt
        
        # Valid polygon
        wkt = "POLYGON((-123.5 48.4, -123.4 48.4, -123.4 48.5, -123.5 48.5, -123.5 48.4))"
        area = parse_simple_polygon_wkt(wkt)
        assert isinstance(area, float)
        assert area > 0
        
        # Test case insensitive
        wkt_lower = "polygon((-123.5 48.4, -123.4 48.4, -123.4 48.5, -123.5 48.5, -123.5 48.4))"
        area_lower = parse_simple_polygon_wkt(wkt_lower)
        assert area == area_lower
        
        # Invalid WKT should raise ValueError
        with pytest.raises(ValueError):
            parse_simple_polygon_wkt("INVALID_WKT")
            
        with pytest.raises(ValueError):
            parse_simple_polygon_wkt("POLYGON((1 1))")  # Too few points
            
    def test_generate_mock_spectral_data(self):
        """Test mock spectral data generation."""
        from api.main import generate_mock_spectral_data
        
        area = 1000000.0  # 1 km²
        date = "2024-06-15"
        
        fai, ndre = generate_mock_spectral_data(area, date)
        
        # Check data types
        assert isinstance(fai, float)
        assert isinstance(ndre, float)
        
        # Check reasonable ranges
        assert -0.05 <= fai <= 0.3
        assert -0.2 <= ndre <= 0.8
        
        # Check deterministic behavior
        fai2, ndre2 = generate_mock_spectral_data(area, date)
        assert fai == fai2
        assert ndre == ndre2
        
    def test_estimate_carbon_sequestration(self):
        """Test carbon sequestration estimation."""
        from api.main import estimate_carbon_sequestration
        
        # Test with known biomass
        biomass_kg = 1000.0  # 1000 kg biomass
        co2e_tonnes = estimate_carbon_sequestration(biomass_kg)
        
        assert isinstance(co2e_tonnes, float)
        assert co2e_tonnes > 0
        
        # Rough calculation check (1000 kg * 0.325 * 3.67 / 1000 ≈ 1.19 tonnes)
        expected = 1000 * 0.325 * 3.67 / 1000
        assert abs(co2e_tonnes - expected) < 0.01
        
        # Zero biomass should give zero CO2
        assert estimate_carbon_sequestration(0.0) == 0.0
        
    @patch('api.main.load')
    @patch('os.path.exists')
    def test_load_model_success(self, mock_exists, mock_load):
        """Test successful model loading."""
        from api.main import load_model
        
        mock_exists.return_value = True
        mock_model = MagicMock()
        mock_load.return_value = mock_model
        
        load_model()
        
        mock_exists.assert_called_once_with("models/biomass_rf.pkl")
        mock_load.assert_called_once_with("models/biomass_rf.pkl")
        
    @patch('os.path.exists')
    def test_load_model_file_not_found(self, mock_exists):
        """Test model loading when file doesn't exist."""
        from api.main import load_model
        
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            load_model()
            
    @patch('api.main.load')
    @patch('os.path.exists')
    def test_load_model_load_error(self, mock_exists, mock_load):
        """Test model loading when load fails."""
        from api.main import load_model
        
        mock_exists.return_value = True
        mock_load.side_effect = Exception("Load failed")
        
        with pytest.raises(RuntimeError):
            load_model()
            
    def test_carbon_analysis_with_different_geometries(self, client, mock_model):
        """Test carbon analysis with different polygon geometries."""
        test_date = "2024-06-15"
        
        # Different polygon sizes
        geometries = [
            # Small polygon
            "POLYGON((-123.45 48.45, -123.44 48.45, -123.44 48.46, -123.45 48.46, -123.45 48.45))",
            # Larger polygon
            "POLYGON((-124.0 48.0, -123.0 48.0, -123.0 49.0, -124.0 49.0, -124.0 48.0))",
            # Triangle
            "POLYGON((-123.5 48.4, -123.4 48.4, -123.45 48.5, -123.5 48.4))",
        ]
        
        with patch('api.main.model', mock_model):
            for wkt in geometries:
                response = client.get(f"/carbon?date={test_date}&aoi={wkt}")
                assert response.status_code == 200
                
                data = response.json()
                assert data["area_m2"] > 0
                assert data["biomass_t"] >= 0
                assert data["co2e_t"] >= 0
                
    def test_seasonal_variation_in_spectral_data(self):
        """Test that spectral data shows seasonal variation."""
        from api.main import generate_mock_spectral_data
        
        area = 1000000.0
        
        # Get data for different months
        summer_date = "2024-06-15"  # June
        winter_date = "2024-12-15"  # December
        
        summer_fai, summer_ndre = generate_mock_spectral_data(area, summer_date)
        winter_fai, winter_ndre = generate_mock_spectral_data(area, winter_date)
        
        # Values should be different due to seasonal factor
        assert summer_fai != winter_fai or summer_ndre != winter_ndre 