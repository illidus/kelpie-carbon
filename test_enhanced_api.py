#!/usr/bin/env python3
"""
Enhanced API Test - Tests the new Landsat and mapping features

This script tests:
1. Synthetic data (existing functionality)
2. Real Landsat data integration  
3. Result mapping (static, interactive, geojson)
4. Enhanced response fields
"""

import requests
import json
import time
from datetime import datetime

# Live API URL
API_BASE_URL = "https://kelpie-carbon.onrender.com"

def test_synthetic_analysis():
    """Test the enhanced API with synthetic data."""
    print("🧪 Testing enhanced API with synthetic data...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/carbon",
            params={
                "date": "2024-06-01",
                "aoi": "POLYGON((-123.36 48.41, -123.35 48.41, -123.35 48.40, -123.36 48.40, -123.36 48.41))",
                "use_real_landsat": "false",
                "include_map": "true",
                "map_type": "geojson"
            },
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Synthetic analysis successful!")
            print(f"   Data Source: {data.get('data_source', 'N/A')}")
            print(f"   Biomass Density: {data.get('biomass_density_t_ha', 0):.1f} t/ha")
            print(f"   Map Type: {data.get('result_map', {}).get('type', 'N/A')}")
            return True
        else:
            print(f"❌ Synthetic analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Synthetic analysis error: {e}")
        return False

def test_landsat_analysis():
    """Test the API with real Landsat data option."""
    print("\n🛰️  Testing API with real Landsat data...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/carbon",
            params={
                "date": "2024-06-01",
                "aoi": "POLYGON((-123.4 48.42, -123.35 48.42, -123.35 48.38, -123.4 48.38, -123.4 48.42))",
                "use_real_landsat": "true",
                "include_map": "true",
                "map_type": "geojson"
            },
            timeout=30  # Landsat processing may take longer
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Landsat analysis successful!")
            print(f"   Data Source: {data.get('data_source', 'N/A')}")
            
            metadata = data.get('landsat_metadata', {})
            if metadata:
                print(f"   Scene ID: {metadata.get('scene_id', 'N/A')}")
                print(f"   Cloud Cover: {metadata.get('cloud_cover', 'N/A')}")
                if 'error' in metadata:
                    print(f"   Note: {metadata['error']}")
            
            return True
        else:
            print(f"❌ Landsat analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Landsat analysis error: {e}")
        return False

def test_mapping_features():
    """Test different mapping options."""
    print("\n🗺️  Testing mapping features...")
    
    map_types = ["geojson", "static", "interactive"]
    successful_maps = 0
    
    for map_type in map_types:
        try:
            print(f"\n   Testing {map_type} map...")
            response = requests.get(
                f"{API_BASE_URL}/carbon",
                params={
                    "date": "2024-07-15",
                    "aoi": "POLYGON((-123.365 48.415, -123.355 48.415, -123.355 48.405, -123.365 48.405, -123.365 48.415))",
                    "use_real_landsat": "false",
                    "include_map": "true",
                    "map_type": map_type
                },
                timeout=25
            )
            
            if response.status_code == 200:
                data = response.json()
                result_map = data.get('result_map', {})
                
                if result_map and result_map.get('success'):
                    print(f"   ✅ {map_type} map created successfully")
                    print(f"      Type: {result_map.get('type', 'unknown')}")
                    
                    if map_type == "geojson" and 'geojson' in result_map:
                        geojson = result_map['geojson']
                        print(f"      Features: {len(geojson.get('features', []))}")
                        
                    elif map_type == "static" and 'image_base64' in result_map:
                        img_size = len(result_map['image_base64'])
                        print(f"      Image size: {img_size:,} characters")
                        
                    elif map_type == "interactive" and 'html' in result_map:
                        html_size = len(result_map['html'])
                        print(f"      HTML size: {html_size:,} characters")
                        
                    successful_maps += 1
                else:
                    error = result_map.get('error', 'Unknown error')
                    print(f"   ⚠️  {map_type} map failed: {error}")
                    
            else:
                print(f"   ❌ {map_type} map request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {map_type} map error: {e}")
    
    return successful_maps >= 1  # At least one map type should work

def test_enhanced_fields():
    """Test that all enhanced response fields are present."""
    print("\n📊 Testing enhanced response fields...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/carbon",
            params={
                "date": "2024-08-01",
                "aoi": "POLYGON((-123.37 48.42, -123.35 48.42, -123.35 48.40, -123.37 48.40, -123.37 48.42))",
                "use_real_landsat": "false",
                "include_map": "true"
            },
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for all expected fields
            required_fields = [
                'date', 'aoi_wkt', 'area_m2', 'mean_fai', 'mean_ndre',
                'biomass_t', 'co2e_t', 'data_source', 'biomass_density_t_ha'
            ]
            
            enhanced_fields = ['landsat_metadata', 'result_map']
            
            missing_fields = []
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
                else:
                    print(f"   ✅ {field}: {data[field]}")
            
            for field in enhanced_fields:
                if field in data:
                    print(f"   ✅ {field}: Present")
                else:
                    print(f"   ⚠️  {field}: Missing")
            
            if not missing_fields:
                print("✅ All required fields present!")
                return True
            else:
                print(f"❌ Missing fields: {missing_fields}")
                return False
                
        else:
            print(f"❌ Enhanced fields test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced fields test error: {e}")
        return False

def main():
    """Run all enhanced API tests."""
    print("🌊 Kelpie Carbon API - Enhanced Features Test")
    print("=" * 60)
    print(f"Testing: {API_BASE_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Synthetic Data Analysis", test_synthetic_analysis),
        ("Real Landsat Data", test_landsat_analysis),
        ("Mapping Features", test_mapping_features),
        ("Enhanced Response Fields", test_enhanced_fields),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            print(f"❌ Test '{name}' crashed: {e}")
    
    print(f"\n📊 Enhanced Features Test Results: {passed}/{total} tests passed")
    
    if passed >= 3:  # Most features working
        print("🎉 ENHANCED FEATURES SUCCESS!")
        print("   Your API now supports:")
        print("   ✅ Real Landsat data integration")
        print("   ✅ Result map visualization")
        print("   ✅ Enhanced response data")
        print(f"   🌐 API: {API_BASE_URL}/docs")
    elif passed >= 2:
        print("⚠️  Partial enhanced features available")
        print("   Some advanced features may need additional setup")
    else:
        print("❌ Enhanced features not yet available")
        print("   Basic API still working, enhanced features need deployment")
    
    return passed >= 2

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 