#!/usr/bin/env python3
"""
Test suite to debug the mapping functionality error:
"Map generation failed: Mapping features not available"
"""

import requests
import json
from datetime import datetime

class MappingErrorTests:
    def __init__(self):
        self.api_base = 'https://kelpie-carbon.onrender.com'
        # Test polygon around Victoria, BC
        self.test_polygon = "POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))"
        
    def test_1_basic_api_without_mapping(self):
        """Test 1: Basic API call without mapping features"""
        print("🔍 TEST 1: Basic API without mapping")
        print("=" * 50)
        
        params = {
            'date': '2024-01-15',
            'aoi': self.test_polygon,
            'use_real_landsat': 'false',
            'include_map': 'false'  # No mapping
        }
        
        try:
            response = requests.get(f"{self.api_base}/carbon", params=params, timeout=30)
            print(f"✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received: {len(str(data))} chars")
                print(f"✅ Data source: {data.get('data_source', 'unknown')}")
                print(f"✅ Has result_map: {'result_map' in data}")
                
                if 'result_map' in data:
                    print(f"✅ Map included despite include_map=false: {data['result_map']}")
                else:
                    print("✅ No map included (as expected)")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"❌ Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            
        print()
    
    def test_2_api_with_geojson_mapping(self):
        """Test 2: API call with GeoJSON mapping"""
        print("🔍 TEST 2: API with GeoJSON mapping")
        print("=" * 50)
        
        params = {
            'date': '2024-01-15', 
            'aoi': self.test_polygon,
            'use_real_landsat': 'false',
            'include_map': 'true',
            'map_type': 'geojson'
        }
        
        try:
            response = requests.get(f"{self.api_base}/carbon", params=params, timeout=30)
            print(f"✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received: {len(str(data))} chars")
                
                if 'result_map' in data:
                    map_data = data['result_map']
                    print(f"✅ Map type: {map_data.get('type', 'unknown')}")
                    print(f"✅ Map success: {map_data.get('success', False)}")
                    
                    if map_data.get('success'):
                        print(f"✅ GeoJSON available: {'geojson' in map_data}")
                    else:
                        print(f"❌ Map error: {map_data.get('error', 'unknown')}")
                        if "Mapping features not available" in map_data.get('error', ''):
                            print("🎯 FOUND THE ERROR! This is the issue.")
                else:
                    print("❌ No result_map in response")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"❌ Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            
        print()
    
    def test_3_api_with_static_mapping(self):
        """Test 3: API call with static image mapping"""
        print("🔍 TEST 3: API with static image mapping")
        print("=" * 50)
        
        params = {
            'date': '2024-01-15',
            'aoi': self.test_polygon,
            'use_real_landsat': 'false',
            'include_map': 'true',
            'map_type': 'static'
        }
        
        try:
            response = requests.get(f"{self.api_base}/carbon", params=params, timeout=30)
            print(f"✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received: {len(str(data))} chars")
                
                if 'result_map' in data:
                    map_data = data['result_map']
                    print(f"✅ Map type: {map_data.get('type', 'unknown')}")
                    print(f"✅ Map success: {map_data.get('success', False)}")
                    
                    if map_data.get('success'):
                        print(f"✅ Image available: {'image_base64' in map_data}")
                        if 'image_base64' in map_data:
                            img_size = len(map_data['image_base64'])
                            print(f"✅ Image size: {img_size:,} chars")
                    else:
                        print(f"❌ Map error: {map_data.get('error', 'unknown')}")
                        if "Mapping features not available" in map_data.get('error', ''):
                            print("🎯 FOUND THE ERROR! This is the issue.")
                else:
                    print("❌ No result_map in response")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"❌ Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            
        print()
    
    def test_4_api_with_interactive_mapping(self):
        """Test 4: API call with interactive mapping"""
        print("🔍 TEST 4: API with interactive mapping")
        print("=" * 50)
        
        params = {
            'date': '2024-01-15',
            'aoi': self.test_polygon,
            'use_real_landsat': 'false', 
            'include_map': 'true',
            'map_type': 'interactive'
        }
        
        try:
            response = requests.get(f"{self.api_base}/carbon", params=params, timeout=30)
            print(f"✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received: {len(str(data))} chars")
                
                if 'result_map' in data:
                    map_data = data['result_map']
                    print(f"✅ Map type: {map_data.get('type', 'unknown')}")
                    print(f"✅ Map success: {map_data.get('success', False)}")
                    
                    if map_data.get('success'):
                        print(f"✅ HTML available: {'html' in map_data}")
                        if 'html' in map_data:
                            html_size = len(map_data['html'])
                            print(f"✅ HTML size: {html_size:,} chars")
                    else:
                        print(f"❌ Map error: {map_data.get('error', 'unknown')}")
                        if "Mapping features not available" in map_data.get('error', ''):
                            print("🎯 FOUND THE ERROR! This is the issue.")
                else:
                    print("❌ No result_map in response")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"❌ Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            
        print()
    
    def test_5_check_api_dependencies(self):
        """Test 5: Check if mapping dependencies are available on the server"""
        print("🔍 TEST 5: Check API dependencies")
        print("=" * 50)
        
        # Test API docs endpoint to see what's available
        try:
            response = requests.get(f"{self.api_base}/docs", timeout=10)
            print(f"✅ API Docs: {response.status_code}")
            
            # Test health endpoint if it exists
            response = requests.get(f"{self.api_base}/health", timeout=10)
            print(f"✅ Health endpoint: {response.status_code}")
            
        except Exception as e:
            print(f"❌ Exception checking endpoints: {e}")
        
        # Test with a minimal request to see what error we get
        try:
            params = {
                'date': '2024-01-15',
                'aoi': 'POLYGON((-123.35 48.42, -123.34 48.42, -123.34 48.43, -123.35 48.43, -123.35 48.42))',
                'include_map': 'true',
                'map_type': 'geojson'
            }
            
            response = requests.get(f"{self.api_base}/carbon", params=params, timeout=30)
            print(f"✅ Minimal request status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'result_map' in data and not data['result_map'].get('success'):
                    error_msg = data['result_map'].get('error', '')
                    print(f"🔍 Exact error message: '{error_msg}'")
                    
                    # Analyze the error
                    if "not available" in error_msg.lower():
                        print("🎯 ISSUE: Mapping libraries not installed on server")
                    elif "import" in error_msg.lower():
                        print("🎯 ISSUE: Import error for mapping dependencies")
                    elif "module" in error_msg.lower():
                        print("🎯 ISSUE: Missing Python module")
                    else:
                        print("🎯 ISSUE: Unknown mapping error")
                        
        except Exception as e:
            print(f"❌ Exception: {e}")
            
        print()
    
    def test_6_different_polygons(self):
        """Test 6: Try different polygon sizes to see if that affects mapping"""
        print("🔍 TEST 6: Different polygon sizes")
        print("=" * 50)
        
        polygons = [
            # Small polygon
            ("Small", "POLYGON((-123.350 48.420, -123.349 48.420, -123.349 48.421, -123.350 48.421, -123.350 48.420))"),
            # Medium polygon  
            ("Medium", "POLYGON((-123.35 48.42, -123.34 48.42, -123.34 48.43, -123.35 48.43, -123.35 48.42))"),
            # Large polygon
            ("Large", "POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))")
        ]
        
        for size, polygon in polygons:
            print(f"🔍 Testing {size} polygon...")
            
            params = {
                'date': '2024-01-15',
                'aoi': polygon,
                'include_map': 'true',
                'map_type': 'geojson'
            }
            
            try:
                response = requests.get(f"{self.api_base}/carbon", params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'result_map' in data:
                        success = data['result_map'].get('success', False)
                        print(f"   {size}: {'✅ Success' if success else '❌ Failed'}")
                        if not success:
                            print(f"   Error: {data['result_map'].get('error', 'unknown')}")
                    else:
                        print(f"   {size}: ❌ No result_map")
                else:
                    print(f"   {size}: ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   {size}: ❌ Exception: {e}")
        
        print()
    
    def run_all_tests(self):
        """Run all mapping error diagnostic tests"""
        print("🧪 MAPPING ERROR DIAGNOSTIC TESTS")
        print("=" * 60)
        print("Investigating: 'Map generation failed: Mapping features not available'")
        print("=" * 60)
        
        self.test_1_basic_api_without_mapping()
        self.test_2_api_with_geojson_mapping() 
        self.test_3_api_with_static_mapping()
        self.test_4_api_with_interactive_mapping()
        self.test_5_check_api_dependencies()
        self.test_6_different_polygons()
        
        print("🏁 DIAGNOSTIC TESTS COMPLETE")
        print("=" * 60)
        print("📋 NEXT STEPS:")
        print("1. Check which specific mapping features are failing")
        print("2. Verify server has required Python packages (folium, matplotlib, etc.)")
        print("3. Check server logs for import errors")
        print("4. Consider fallback to basic functionality if mapping unavailable")

if __name__ == "__main__":
    tester = MappingErrorTests()
    tester.run_all_tests() 