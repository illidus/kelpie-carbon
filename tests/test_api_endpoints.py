import pytest
import requests
import subprocess
import time
import os
import signal
from contextlib import contextmanager


class TestLocalAPI:
    """Test the API endpoints by running the server locally."""
    
    @pytest.fixture(scope="class")
    def api_server(self):
        """Start the FastAPI server for testing."""
        # Start the server process
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        
        process = subprocess.Popen(
            ["python", "-m", "uvicorn", "api.main:app", "--host", "localhost", "--port", "8001"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        for _ in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get("http://localhost:8001/health", timeout=1)
                if response.status_code == 200:
                    break
            except:
                time.sleep(1)
        else:
            process.terminate()
            pytest.fail("Server failed to start")
        
        yield "http://localhost:8001"
        
        # Clean up
        process.terminate()
        process.wait()
    
    @pytest.fixture
    def test_polygon(self):
        """Sample polygon around Victoria, BC for testing."""
        return "POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))"
    
    @pytest.fixture
    def test_date(self):
        """Sample date for testing."""
        return "2024-07-15"
    
    def test_health_endpoint(self, api_server):
        """Test the health check endpoint."""
        response = requests.get(f"{api_server}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "timestamp" in data
        assert data["status"] in ["healthy", "unhealthy"]
    
    def test_api_info_endpoint(self, api_server):
        """Test the API info endpoint."""
        response = requests.get(f"{api_server}/api")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_carbon_analysis_valid_request(self, api_server, test_polygon, test_date):
        """Test carbon analysis with valid parameters."""
        params = {
            "date": test_date,
            "aoi": test_polygon
        }
        
        response = requests.get(f"{api_server}/carbon", params=params)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check all required fields are present
        required_fields = [
            "date", "aoi_wkt", "area_m2", "mean_fai", "mean_ndre", 
            "biomass_t", "co2e_t"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Validate data types and ranges
        assert isinstance(data["area_m2"], (int, float))
        assert data["area_m2"] > 0
        
        assert isinstance(data["mean_fai"], (int, float))
        assert -0.2 <= data["mean_fai"] <= 0.5
        
        assert isinstance(data["mean_ndre"], (int, float))
        assert -0.3 <= data["mean_ndre"] <= 0.8
        
        assert isinstance(data["biomass_t"], (int, float))
        assert data["biomass_t"] >= 0
        
        assert isinstance(data["co2e_t"], (int, float))
        assert data["co2e_t"] >= 0
        
        # Validate returned values match input
        assert data["date"] == test_date
        assert data["aoi_wkt"] == test_polygon
        
        print(f"✅ Analysis Results:")
        print(f"   Area: {data['area_m2']:,.0f} m²")
        print(f"   FAI: {data['mean_fai']:.3f}")
        print(f"   NDRE: {data['mean_ndre']:.3f}")
        print(f"   Biomass: {data['biomass_t']:.2f} tonnes")
        print(f"   CO₂ Sequestered: {data['co2e_t']:.2f} tonnes CO₂e")
    
    def test_carbon_analysis_invalid_date(self, api_server, test_polygon):
        """Test carbon analysis with invalid date format."""
        params = {
            "date": "invalid-date",
            "aoi": test_polygon
        }
        
        response = requests.get(f"{api_server}/carbon", params=params)
        assert response.status_code == 400
    
    def test_carbon_analysis_invalid_polygon(self, api_server, test_date):
        """Test carbon analysis with invalid WKT."""
        params = {
            "date": test_date,
            "aoi": "INVALID WKT"
        }
        
        response = requests.get(f"{api_server}/carbon", params=params)
        assert response.status_code == 400
    
    def test_carbon_analysis_missing_parameters(self, api_server):
        """Test carbon analysis with missing parameters."""
        # Missing both parameters
        response = requests.get(f"{api_server}/carbon")
        assert response.status_code == 422
        
        # Missing date
        response = requests.get(f"{api_server}/carbon", params={"aoi": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))"})
        assert response.status_code == 422
        
        # Missing aoi
        response = requests.get(f"{api_server}/carbon", params={"date": "2024-01-01"})
        assert response.status_code == 422
    
    def test_carbon_analysis_different_areas(self, api_server, test_date):
        """Test carbon analysis with different area sizes."""
        test_cases = [
            {
                "name": "Small coastal area",
                "polygon": "POLYGON((-123.35 48.42, -123.34 48.42, -123.34 48.43, -123.35 48.43, -123.35 48.42))",
                "expected_area_range": (1e6, 2e9)  # 1 km² to 2000 km²
            },
            {
                "name": "Tiny test area", 
                "polygon": "POLYGON((-123.350 48.420, -123.349 48.420, -123.349 48.421, -123.350 48.421, -123.350 48.420))",
                "expected_area_range": (1e4, 1e7)  # 0.01 km² to 10 km²
            }
        ]
        
        for case in test_cases:
            params = {
                "date": test_date,
                "aoi": case["polygon"]
            }
            
            response = requests.get(f"{api_server}/carbon", params=params)
            assert response.status_code == 200
            
            data = response.json()
            area_m2 = data["area_m2"]
            min_area, max_area = case["expected_area_range"]
            
            assert min_area <= area_m2 <= max_area, f"{case['name']}: Area {area_m2} not in expected range {case['expected_area_range']}"
            
            print(f"✅ {case['name']}: {area_m2:,.0f} m² -> {data['biomass_t']:.2f} tonnes biomass")
    
    def test_carbon_analysis_seasonal_variation(self, api_server, test_polygon):
        """Test that different dates produce different results (seasonal variation)."""
        dates = ["2024-01-15", "2024-04-15", "2024-07-15", "2024-10-15"]
        results = []
        
        for date in dates:
            params = {
                "date": date,
                "aoi": test_polygon
            }
            
            response = requests.get(f"{api_server}/carbon", params=params)
            assert response.status_code == 200
            
            data = response.json()
            results.append({
                "date": date,
                "fai": data["mean_fai"],
                "ndre": data["mean_ndre"],
                "biomass": data["biomass_t"]
            })
        
        # Check that not all results are identical (seasonal variation should occur)
        fai_values = [r["fai"] for r in results]
        ndre_values = [r["ndre"] for r in results]
        
        assert len(set(fai_values)) > 1, "FAI values should vary with season"
        assert len(set(ndre_values)) > 1, "NDRE values should vary with season"
        
        print("✅ Seasonal variation detected:")
        for result in results:
            print(f"   {result['date']}: FAI={result['fai']:.3f}, NDRE={result['ndre']:.3f}, Biomass={result['biomass']:.2f}t")
    
    def test_carbon_sequestration_calculation(self, api_server, test_polygon, test_date):
        """Test that carbon sequestration calculations are reasonable."""
        params = {
            "date": test_date,
            "aoi": test_polygon
        }
        
        response = requests.get(f"{api_server}/carbon", params=params)
        assert response.status_code == 200
        
        data = response.json()
        
        # CO2 sequestration should be approximately 1.2x biomass
        # (based on ~32.5% carbon content and 3.67 CO2/C ratio)
        biomass_t = data["biomass_t"]
        co2e_t = data["co2e_t"]
        
        if biomass_t > 0:
            ratio = co2e_t / biomass_t
            expected_ratio = 0.325 * 3.67  # ~1.19
            
            # Allow some tolerance around the expected ratio
            assert 0.8 <= ratio <= 2.0, f"CO2/biomass ratio {ratio:.2f} seems unrealistic"
            assert abs(ratio - expected_ratio) < 0.5, f"CO2/biomass ratio {ratio:.2f} differs significantly from expected {expected_ratio:.2f}"
            
            print(f"✅ Carbon sequestration: {biomass_t:.2f}t biomass -> {co2e_t:.2f}t CO₂e (ratio: {ratio:.2f})")


def test_simple_api_request():
    """Simple test that can run without starting a server (for quick testing)."""
    # This test assumes the API might be running elsewhere or we want to test
    # the functions directly
    from api.main import parse_simple_polygon_wkt, estimate_carbon_sequestration
    
    # Test WKT parsing
    test_polygon = "POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))"
    area = parse_simple_polygon_wkt(test_polygon)
    assert area > 0
    print(f"✅ WKT parsing: {area:,.0f} m²")
    
    # Test carbon calculation
    biomass_kg = 1000  # 1 tonne
    co2e_kg = estimate_carbon_sequestration(biomass_kg)
    assert co2e_kg > 0
    expected = biomass_kg * 0.325 * 3.67 / 1000  # tonnes
    assert abs(co2e_kg - expected) < 0.01
    print(f"✅ Carbon calculation: {biomass_kg}kg biomass -> {co2e_kg:.3f}t CO₂e")


if __name__ == "__main__":
    # Run the simple test first
    test_simple_api_request()
    
    # Run pytest for the full test suite
    pytest.main([__file__, "-v", "-s"]) 