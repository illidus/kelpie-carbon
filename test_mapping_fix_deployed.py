#!/usr/bin/env python3
"""
Test the deployed mapping fix - verify the "Mapping features not available" error is resolved
"""

import requests
import time

def test_deployed_mapping_fix():
    """Test that the mapping error is fixed on the deployed server"""
    print("🧪 TESTING DEPLOYED MAPPING FIX")
    print("=" * 50)
    
    api_base = 'https://kelpie-carbon.onrender.com'
    test_polygon = "POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))"
    
    print("⏳ Waiting for deployment to complete (60 seconds)...")
    time.sleep(60)
    
    print("\n1. Testing GeoJSON mapping...")
    test_mapping_type("geojson", api_base, test_polygon)
    
    print("\n2. Testing static mapping...")
    test_mapping_type("static", api_base, test_polygon)
    
    print("\n3. Testing interactive mapping...")  
    test_mapping_type("interactive", api_base, test_polygon)
    
    print("\n🏁 MAPPING FIX TEST COMPLETE")

def test_mapping_type(map_type, api_base, test_polygon):
    """Test a specific mapping type"""
    params = {
        'date': '2024-01-15',
        'aoi': test_polygon,
        'use_real_landsat': 'false',
        'include_map': 'true',
        'map_type': map_type
    }
    
    try:
        response = requests.get(f"{api_base}/carbon", params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'result_map' in data:
                map_data = data['result_map']
                success = map_data.get('success', False)
                
                if success:
                    print(f"   ✅ {map_type.title()} mapping: SUCCESS!")
                    print(f"      Type: {map_data.get('type', 'unknown')}")
                    
                    if map_type == "geojson" and 'geojson' in map_data:
                        print(f"      GeoJSON features: {len(map_data['geojson'].get('features', []))}")
                    elif map_type == "static" and 'image_base64' in map_data:
                        print(f"      Image size: {len(map_data['image_base64']):,} chars")
                    elif map_type == "interactive" and 'html' in map_data:
                        print(f"      HTML size: {len(map_data['html']):,} chars")
                        
                else:
                    error = map_data.get('error', 'unknown')
                    if "Mapping features not available" in error:
                        print(f"   ❌ {map_type.title()} mapping: STILL BROKEN - {error}")
                    else:
                        print(f"   ⚠️  {map_type.title()} mapping: Different error - {error}")
            else:
                print(f"   ❌ {map_type.title()} mapping: No result_map in response")
        else:
            print(f"   ❌ {map_type.title()} mapping: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ {map_type.title()} mapping: Exception - {e}")

if __name__ == "__main__":
    test_deployed_mapping_fix() 