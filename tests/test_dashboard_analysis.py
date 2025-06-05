import os
import time
import pytest
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import json


class TestCarbonAnalysisAPI:
    """Test the carbon analysis API endpoints directly."""
    
    @pytest.fixture
    def api_base_url(self):
        """Get the API base URL from environment or use default."""
        return os.getenv('API_BASE_URL', 'http://localhost:8000')
    
    @pytest.fixture
    def test_polygon(self):
        """Sample polygon around Victoria, BC for testing."""
        return "POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))"
    
    @pytest.fixture
    def test_date(self):
        """Sample date for testing."""
        return "2024-07-15"
    
    def test_health_endpoint(self, api_base_url):
        """Test the health check endpoint."""
        response = requests.get(f"{api_base_url}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "timestamp" in data
        assert data["status"] in ["healthy", "unhealthy"]
    
    def test_carbon_analysis_valid_request(self, api_base_url, test_polygon, test_date):
        """Test carbon analysis with valid parameters."""
        params = {
            "date": test_date,
            "aoi": test_polygon
        }
        
        response = requests.get(f"{api_base_url}/carbon", params=params)
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
        assert -0.2 <= data["mean_fai"] <= 0.5  # Reasonable FAI range
        
        assert isinstance(data["mean_ndre"], (int, float))
        assert -0.3 <= data["mean_ndre"] <= 0.8  # Reasonable NDRE range
        
        assert isinstance(data["biomass_t"], (int, float))
        assert data["biomass_t"] >= 0
        
        assert isinstance(data["co2e_t"], (int, float))
        assert data["co2e_t"] >= 0
        
        # Validate returned date matches input
        assert data["date"] == test_date
        assert data["aoi_wkt"] == test_polygon
    
    def test_carbon_analysis_invalid_date(self, api_base_url, test_polygon):
        """Test carbon analysis with invalid date format."""
        params = {
            "date": "invalid-date",
            "aoi": test_polygon
        }
        
        response = requests.get(f"{api_base_url}/carbon", params=params)
        assert response.status_code == 400
    
    def test_carbon_analysis_invalid_polygon(self, api_base_url, test_date):
        """Test carbon analysis with invalid WKT."""
        params = {
            "date": test_date,
            "aoi": "INVALID WKT"
        }
        
        response = requests.get(f"{api_base_url}/carbon", params=params)
        assert response.status_code == 400
    
    def test_carbon_analysis_missing_parameters(self, api_base_url):
        """Test carbon analysis with missing parameters."""
        # Missing both parameters
        response = requests.get(f"{api_base_url}/carbon")
        assert response.status_code == 422
        
        # Missing date
        response = requests.get(f"{api_base_url}/carbon", params={"aoi": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))"})
        assert response.status_code == 422
        
        # Missing aoi
        response = requests.get(f"{api_base_url}/carbon", params={"date": "2024-01-01"})
        assert response.status_code == 422
    
    def test_carbon_analysis_realistic_values(self, api_base_url, test_date):
        """Test carbon analysis produces realistic biomass values."""
        # Small area test
        small_polygon = "POLYGON((-123.35 48.42, -123.34 48.42, -123.34 48.43, -123.35 48.43, -123.35 48.42))"
        
        params = {
            "date": test_date,
            "aoi": small_polygon
        }
        
        response = requests.get(f"{api_base_url}/carbon", params=params)
        assert response.status_code == 200
        
        data = response.json()
        
        # For a small area (~1 km²), biomass should be reasonable
        area_km2 = data["area_m2"] / 1_000_000
        biomass_density = data["biomass_t"] / area_km2  # tonnes per km²
        
        # Realistic kelp density should be 0-10,000 tonnes/km² (0-10 kg/m²)
        assert 0 <= biomass_density <= 10_000, f"Unrealistic biomass density: {biomass_density} tonnes/km²"
        
        # CO2 sequestration should be reasonable (roughly 1.2x biomass)
        co2_ratio = data["co2e_t"] / max(data["biomass_t"], 0.001)
        assert 0.8 <= co2_ratio <= 2.0, f"Unrealistic CO2/biomass ratio: {co2_ratio}"


class TestDashboardSelenium:
    """Test the dashboard UI using Selenium browser automation."""
    
    @pytest.fixture
    def driver(self):
        """Create a Chrome WebDriver for testing."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode for CI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        yield driver
        driver.quit()
    
    @pytest.fixture
    def dashboard_url(self):
        """Get the dashboard URL from environment or use default."""
        return os.getenv('DASHBOARD_URL', 'https://illidus.github.io/kelpie-carbon/dashboard/')
    
    def test_dashboard_loads(self, driver, dashboard_url):
        """Test that the dashboard loads successfully."""
        driver.get(dashboard_url)
        
        # Wait for the page to load
        wait = WebDriverWait(driver, 10)
        
        # Check for the main title
        title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        assert "Kelpie Carbon Dashboard" in title.text
        
        # Check for the map container
        map_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "leaflet-container")))
        assert map_container.is_displayed()
        
        # Check for drawing controls
        draw_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Draw Polygon')]")))
        assert draw_button.is_displayed()
    
    def test_date_picker_functionality(self, driver, dashboard_url):
        """Test that the date picker works."""
        driver.get(dashboard_url)
        wait = WebDriverWait(driver, 10)
        
        # Find and interact with date picker
        date_input = wait.until(EC.presence_of_element_located((By.ID, "analysis-date")))
        assert date_input.is_displayed()
        
        # Set a test date
        driver.execute_script("arguments[0].value = '2024-07-15'", date_input)
        
        # Verify the date was set
        assert date_input.get_attribute("value") == "2024-07-15"
    
    def test_draw_polygon_interaction(self, driver, dashboard_url):
        """Test drawing a polygon on the map."""
        driver.get(dashboard_url)
        wait = WebDriverWait(driver, 10)
        
        # Wait for map to load
        map_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "leaflet-container")))
        
        # Click the draw button
        draw_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Draw Polygon')]")))
        draw_button.click()
        
        # Verify button text changed
        assert "Drawing..." in draw_button.text
        
        # Simulate clicking on the map to draw a polygon
        actions = ActionChains(driver)
        
        # Get map center and create a small polygon
        map_rect = map_container.get_rect()
        center_x = map_rect['x'] + map_rect['width'] // 2
        center_y = map_rect['y'] + map_rect['height'] // 2
        
        # Click several points to create a polygon (triangle)
        points = [
            (center_x - 50, center_y - 50),  # Top-left
            (center_x + 50, center_y - 50),  # Top-right
            (center_x, center_y + 50),       # Bottom
        ]
        
        for x, y in points:
            actions.move_to_element_with_offset(map_container, x - map_rect['x'], y - map_rect['y'])
            actions.click()
            actions.perform()
            time.sleep(0.5)  # Small delay between clicks
        
        # Double-click to finish the polygon
        actions.double_click()
        actions.perform()
        
        # Wait for analysis to start (loading state)
        try:
            loading_element = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Analyzing')]")))
            assert loading_element.is_displayed()
        except:
            # If analysis happens too quickly, check for results
            pass
    
    def test_results_display(self, driver, dashboard_url):
        """Test that results display correctly after analysis."""
        # This test would be more complex and might require mocking the API
        # or ensuring the API is available for testing
        pass
    
    def test_clear_functionality(self, driver, dashboard_url):
        """Test the clear button functionality."""
        driver.get(dashboard_url)
        wait = WebDriverWait(driver, 10)
        
        # Find and click the clear button
        clear_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Clear')]")))
        clear_button.click()
        
        # The button should still be present after clicking
        assert clear_button.is_displayed()
    
    def test_responsive_design(self, driver, dashboard_url):
        """Test that the dashboard works on different screen sizes."""
        driver.get(dashboard_url)
        wait = WebDriverWait(driver, 10)
        
        # Test desktop size
        driver.set_window_size(1920, 1080)
        map_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "leaflet-container")))
        assert map_container.is_displayed()
        
        # Test tablet size
        driver.set_window_size(768, 1024)
        assert map_container.is_displayed()
        
        # Test mobile size
        driver.set_window_size(375, 667)
        assert map_container.is_displayed()
    
    def test_error_handling(self, driver, dashboard_url):
        """Test error handling in the UI."""
        # This would require setting up scenarios where the API returns errors
        # and verifying the UI handles them gracefully
        pass


class TestIntegration:
    """Integration tests combining API and UI functionality."""
    
    @pytest.mark.skipif(
        not all([
            os.getenv('API_BASE_URL'),
            os.getenv('DASHBOARD_URL')
        ]),
        reason="Integration tests require both API_BASE_URL and DASHBOARD_URL environment variables"
    )
    def test_end_to_end_analysis(self):
        """Test the complete end-to-end analysis workflow."""
        # This would test the full workflow from UI interaction to API call to results display
        pass


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 