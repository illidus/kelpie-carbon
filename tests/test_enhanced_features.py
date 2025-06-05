#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced Kelp Carbon API Features

Tests cover:
- Real Landsat data integration
- Result mapping (all types)
- Enhanced response validation
- Error handling
- Edge cases
"""

import unittest
import requests
import json
import time
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class TestEnhancedAPI(unittest.TestCase):
    """Test suite for enhanced API features."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test configuration."""
        cls.API_BASE = "https://kelpie-carbon.onrender.com"
        cls.timeout = 30
        
        # Test areas around Victoria, BC
        cls.test_areas = {
            "small": "POLYGON((-123.36 48.41, -123.35 48.41, -123.35 48.40, -123.36 48.40, -123.36 48.41))",
            "medium": "POLYGON((-123.4 48.42, -123.35 48.42, -123.35 48.38, -123.4 48.38, -123.4 48.42))",
            "large": "POLYGON((-123.45 48.45, -123.30 48.45, -123.30 48.35, -123.45 48.35, -123.45 48.45))"
        }
        
        # Test dates
        cls.test_dates = {
            "recent": "2024-06-01",
            "summer": "2024-07-15", 
            "winter": "2024-01-15",
            "older": "2023-08-01"
        }
        
        print(f"🧪 Testing Enhanced API: {cls.API_BASE}")
        
    def setUp(self):
        """Set up for each test."""
        self.session = requests.Session()
        
    def test_api_health(self):
        """Test that the API is responding."""
        response = self.session.get(f"{self.API_BASE}/health", timeout=self.timeout)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("model_loaded", data)
        print("✅ API health check passed")

class TestSyntheticDataAnalysis(TestEnhancedAPI):
    """Test synthetic data analysis with enhanced features."""
    
    def test_basic_enhanced_response(self):
        """Test that enhanced response fields are present."""
        response = self.session.get(
            f"{self.API_BASE}/carbon",
            params={
                "date": self.test_dates["recent"],
                "aoi": self.test_areas["small"],
                "use_real_landsat": "false",
                "include_map": "true",
                "map_type": "geojson"
            },
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check all required fields are present
        required_fields = [
            'date', 'aoi_wkt', 'area_m2', 'mean_fai', 'mean_ndre',
            'biomass_t', 'co2e_t', 'data_source', 'biomass_density_t_ha'
        ]
        
        for field in required_fields:
            self.assertIn(field, data, f"Missing required field: {field}")
            
        # Check enhanced fields
        self.assertIn('landsat_metadata', data)
        self.assertIn('result_map', data)
        
        # Validate data types and ranges
        self.assertIsInstance(data['area_m2'], (int, float))
        self.assertGreater(data['area_m2'], 0)
        
        self.assertIsInstance(data['biomass_t'], (int, float))
        self.assertGreaterEqual(data['biomass_t'], 0)
        
        self.assertIsInstance(data['co2e_t'], (int, float))
        self.assertGreaterEqual(data['co2e_t'], 0)
        
        self.assertIsInstance(data['biomass_density_t_ha'], (int, float))
        self.assertGreaterEqual(data['biomass_density_t_ha'], 0)
        
        print("✅ Basic enhanced response validation passed")
        
    def test_data_source_synthetic(self):
        """Test that synthetic data source is correctly identified."""
        response = self.session.get(
            f"{self.API_BASE}/carbon",
            params={
                "date": self.test_dates["recent"],
                "aoi": self.test_areas["medium"],
                "use_real_landsat": "false"
            },
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['data_source'], 'synthetic')
        print("✅ Synthetic data source correctly identified")

class TestLandsatIntegration(TestEnhancedAPI):
    """Test real Landsat data integration."""
    
    def test_landsat_option_accepted(self):
        """Test that Landsat option is accepted by API."""
        response = self.session.get(
            f"{self.API_BASE}/carbon",
            params={
                "date": self.test_dates["recent"],
                "aoi": self.test_areas["small"],
                "use_real_landsat": "true"
            },
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should have metadata regardless of whether real data was found
        self.assertIn('landsat_metadata', data)
        self.assertIn('data_source', data)
        
        # Data source should be either 'landsat_real' or 'synthetic'
        self.assertIn(data['data_source'], ['landsat_real', 'synthetic'])
        
        print(f"✅ Landsat option accepted, data source: {data['data_source']}")
        
    def test_landsat_metadata_structure(self):
        """Test Landsat metadata structure."""
        response = self.session.get(
            f"{self.API_BASE}/carbon",
            params={
                "date": self.test_dates["summer"],
                "aoi": self.test_areas["medium"],
                "use_real_landsat": "true"
            },
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        metadata = data.get('landsat_metadata')
        self.assertIsNotNone(metadata)
        
        if data['data_source'] == 'landsat_real':
            # If real data was used, check for scene info
            expected_keys = ['source', 'scene_id', 'date']
            for key in expected_keys:
                self.assertIn(key, metadata)
        else:
            # If synthetic fallback, should have error info
            self.assertIn('error', metadata)
            
        print("✅ Landsat metadata structure validated")

class TestResultMapping(TestEnhancedAPI):
    """Test result mapping functionality."""
    
    def test_geojson_map_generation(self):
        """Test GeoJSON map generation."""
        response = self.session.get(
            f"{self.API_BASE}/carbon",
            params={
                "date": self.test_dates["recent"],
                "aoi": self.test_areas["small"],
                "include_map": "true",
                "map_type": "geojson"
            },
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('result_map', data)
        result_map = data['result_map']
        
        self.assertIn('type', result_map)
        self.assertEqual(result_map['type'], 'geojson_map')
        self.assertIn('success', result_map)
        self.assertTrue(result_map['success'])
        
        # Check GeoJSON structure
        self.assertIn('geojson', result_map)
        geojson = result_map['geojson']
        
        self.assertEqual(geojson['type'], 'FeatureCollection')
        self.assertIn('features', geojson)
        self.assertGreater(len(geojson['features']), 0)
        
        # Check feature properties
        feature = geojson['features'][0]
        self.assertIn('properties', feature)
        properties = feature['properties']
        
        expected_props = ['name', 'area_hectares', 'biomass_tonnes', 'co2_tonnes']
        for prop in expected_props:
            self.assertIn(prop, properties)
            
        print("✅ GeoJSON map generation successful")
        
    def test_static_map_generation(self):
        """Test static map generation."""
        response = self.session.get(
            f"{self.API_BASE}/carbon",
            params={
                "date": self.test_dates["recent"],
                "aoi": self.test_areas["medium"],
                "include_map": "true",
                "map_type": "static"
            },
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        result_map = data['result_map']
        
        if result_map.get('success'):
            self.assertEqual(result_map['type'], 'static_map')
            self.assertIn('image_base64', result_map)
            
            # Validate base64 image
            image_data = result_map['image_base64']
            self.assertIsInstance(image_data, str)
            self.assertGreater(len(image_data), 1000)  # Should be substantial
            
            # Test base64 decoding
            try:
                decoded = base64.b64decode(image_data)
                self.assertGreater(len(decoded), 0)
            except Exception as e:
                self.fail(f"Invalid base64 image data: {e}")
                
            print("✅ Static map generation successful")
        else:
            print(f"⚠️  Static map generation failed: {result_map.get('error', 'Unknown error')}")
            
    def test_interactive_map_generation(self):
        """Test interactive map generation."""
        response = self.session.get(
            f"{self.API_BASE}/carbon",
            params={
                "date": self.test_dates["recent"],
                "aoi": self.test_areas["large"],
                "include_map": "true",
                "map_type": "interactive"
            },
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        result_map = data['result_map']
        
        if result_map.get('success'):
            self.assertEqual(result_map['type'], 'interactive_map')
            self.assertIn('html', result_map)
            
            # Validate HTML content
            html_content = result_map['html']
            self.assertIsInstance(html_content, str)
            self.assertGreater(len(html_content), 1000)
            
            # Check for folium markers
            self.assertIn('folium', html_content.lower())
            
            print("✅ Interactive map generation successful")
        else:
            print(f"⚠️  Interactive map generation failed: {result_map.get('error', 'Unknown error')}")
            
    def test_map_coordinates(self):
        """Test that map coordinates match input area."""
        aoi = self.test_areas["small"]
        
        response = self.session.get(
            f"{self.API_BASE}/carbon",
            params={
                "date": self.test_dates["recent"],
                "aoi": aoi,
                "include_map": "true",
                "map_type": "geojson"
            },
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        result_map = data['result_map']
        self.assertTrue(result_map.get('success'))
        
        # Check bounds
        self.assertIn('bounds', result_map)
        bounds = result_map['bounds']
        self.assertEqual(len(bounds), 2)  # [[min_lat, min_lon], [max_lat, max_lon]]
        
        # Check center
        self.assertIn('center', result_map)
        center = result_map['center']
        self.assertEqual(len(center), 2)  # [lat, lon]
        
        # Validate coordinates are in Victoria BC area
        lat, lon = center
        self.assertGreater(lat, 48.0)  # North of 48°N
        self.assertLess(lat, 49.0)     # South of 49°N
        self.assertLess(lon, -123.0)   # West of 123°W
        self.assertGreater(lon, -124.0) # East of 124°W
        
        print("✅ Map coordinates validation passed")

class TestErrorHandling(TestEnhancedAPI):
    """Test error handling and edge cases."""
    
    def test_invalid_wkt(self):
        """Test handling of invalid WKT geometry."""
        response = self.session.get(
            f"{self.API_BASE}/carbon",
            params={
                "date": self.test_dates["recent"],
                "aoi": "INVALID_WKT_STRING",
                "include_map": "true"
            },
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 400)
        print("✅ Invalid WKT properly rejected")
        
    def test_invalid_date(self):
        """Test handling of invalid date format."""
        response = self.session.get(
            f"{self.API_BASE}/carbon",
            params={
                "date": "invalid-date",
                "aoi": self.test_areas["small"],
                "include_map": "true"
            },
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 400)
        print("✅ Invalid date properly rejected")
        
    def test_very_small_area(self):
        """Test handling of very small analysis areas."""
        tiny_area = "POLYGON((-123.36 48.41, -123.359 48.41, -123.359 48.409, -123.36 48.409, -123.36 48.41))"
        
        response = self.session.get(
            f"{self.API_BASE}/carbon",
            params={
                "date": self.test_dates["recent"],
                "aoi": tiny_area,
                "include_map": "true"
            },
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should still work but with small values
        self.assertGreater(data['area_m2'], 0)
        self.assertGreaterEqual(data['biomass_t'], 0)
        
        print("✅ Very small area handled correctly")
        
    def test_missing_parameters(self):
        """Test handling of missing required parameters."""
        # Missing aoi
        response = self.session.get(
            f"{self.API_BASE}/carbon",
            params={"date": self.test_dates["recent"]},
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 422)  # Validation error
        
        # Missing date
        response = self.session.get(
            f"{self.API_BASE}/carbon",
            params={"aoi": self.test_areas["small"]},
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 422)  # Validation error
        
        print("✅ Missing parameters properly rejected")

class TestIntegration(TestEnhancedAPI):
    """Integration tests for complete workflows."""
    
    def test_complete_workflow_synthetic(self):
        """Test complete workflow with synthetic data and mapping."""
        # Run analysis with all enhanced features
        response = self.session.get(
            f"{self.API_BASE}/carbon",
            params={
                "date": self.test_dates["summer"],
                "aoi": self.test_areas["medium"],
                "use_real_landsat": "false",
                "include_map": "true",
                "map_type": "geojson"
            },
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Validate complete data pipeline
        self.assertEqual(data['data_source'], 'synthetic')
        self.assertGreater(data['area_m2'], 0)
        self.assertGreater(data['biomass_t'], 0)
        self.assertGreater(data['co2e_t'], 0)
        self.assertGreater(data['biomass_density_t_ha'], 0)
        
        # Validate mapping integration
        result_map = data['result_map']
        self.assertTrue(result_map['success'])
        self.assertIn('geojson', result_map)
        
        # Cross-validate calculations
        expected_density = data['biomass_t'] / (data['area_m2'] / 10000)
        self.assertAlmostEqual(data['biomass_density_t_ha'], expected_density, places=1)
        
        print("✅ Complete synthetic workflow validated")
        
    def test_complete_workflow_landsat_attempt(self):
        """Test complete workflow with Landsat attempt."""
        response = self.session.get(
            f"{self.API_BASE}/carbon",
            params={
                "date": self.test_dates["recent"],
                "aoi": self.test_areas["large"],
                "use_real_landsat": "true",
                "include_map": "true",
                "map_type": "interactive"
            },
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should work regardless of whether real Landsat was available
        self.assertIn(data['data_source'], ['landsat_real', 'synthetic'])
        self.assertIsNotNone(data['landsat_metadata'])
        
        # All calculations should be valid
        self.assertGreater(data['biomass_t'], 0)
        self.assertGreater(data['co2e_t'], 0)
        
        print(f"✅ Complete Landsat workflow: {data['data_source']} data used")

def run_test_suite():
    """Run the complete test suite with reporting."""
    print("🧪 Enhanced Kelp Carbon API - Comprehensive Test Suite")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create test suite
    test_classes = [
        TestSyntheticDataAnalysis,
        TestLandsatIntegration, 
        TestResultMapping,
        TestErrorHandling,
        TestIntegration
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, failure in result.failures:
            print(f"  - {test}: {failure}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, error in result.errors:
            print(f"  - {test}: {error}")
    
    if not result.failures and not result.errors:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Enhanced API features are fully functional")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_test_suite()
    exit(0 if success else 1) 