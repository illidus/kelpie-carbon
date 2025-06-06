#!/usr/bin/env python3
"""
Test mapping functionality locally to confirm it works when imports are available
"""

import sys
import os

# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
sys.path.append(os.path.dirname(__file__))

def test_local_mapping():
    """Test mapping functionality locally"""
    print("🧪 TESTING LOCAL MAPPING FUNCTIONALITY")
    print("=" * 50)
    
    # Test imports
    print("1. Testing imports...")
    try:
        from api.result_mapping import create_result_map, MATPLOTLIB_AVAILABLE, FOLIUM_AVAILABLE
        print(f"   ✅ result_mapping imported successfully")
        print(f"   ✅ matplotlib available: {MATPLOTLIB_AVAILABLE}")
        print(f"   ✅ folium available: {FOLIUM_AVAILABLE}")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    # Test WKT polygon
    test_polygon = "POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))"
    
    # Test results data
    test_results = {
        "date": "2024-01-15",
        "area_m2": 5000000,  # 500 hectares
        "biomass_t": 2500.0,
        "co2e_t": 1750.0,
        "mean_fai": 0.025,
        "mean_ndre": 0.15
    }
    
    print(f"\n2. Testing GeoJSON mapping...")
    try:
        geojson_map = create_result_map(test_polygon, test_results, "geojson")
        if geojson_map and geojson_map.get('success'):
            print(f"   ✅ GeoJSON map created successfully")
            print(f"   ✅ Type: {geojson_map.get('type')}")
            print(f"   ✅ Center: {geojson_map.get('center')}")
        else:
            print(f"   ❌ GeoJSON map failed: {geojson_map.get('error') if geojson_map else 'None returned'}")
    except Exception as e:
        print(f"   ❌ GeoJSON mapping error: {e}")
    
    print(f"\n3. Testing static mapping...")
    if MATPLOTLIB_AVAILABLE:
        try:
            static_map = create_result_map(test_polygon, test_results, "static")
            if static_map and static_map.get('success'):
                print(f"   ✅ Static map created successfully")
                print(f"   ✅ Type: {static_map.get('type')}")
                print(f"   ✅ Image size: {len(static_map.get('image_base64', '')):,} chars")
            else:
                print(f"   ❌ Static map failed: {static_map.get('error') if static_map else 'None returned'}")
        except Exception as e:
            print(f"   ❌ Static mapping error: {e}")
    else:
        print(f"   ⏩ Skipping static mapping (matplotlib not available)")
    
    print(f"\n4. Testing interactive mapping...")
    if FOLIUM_AVAILABLE:
        try:
            interactive_map = create_result_map(test_polygon, test_results, "interactive")
            if interactive_map and interactive_map.get('success'):
                print(f"   ✅ Interactive map created successfully")
                print(f"   ✅ Type: {interactive_map.get('type')}")
                print(f"   ✅ HTML size: {len(interactive_map.get('html', '')):,} chars")
            else:
                print(f"   ❌ Interactive map failed: {interactive_map.get('error') if interactive_map else 'None returned'}")
        except Exception as e:
            print(f"   ❌ Interactive mapping error: {e}")
    else:
        print(f"   ⏩ Skipping interactive mapping (folium not available)")
    
    print(f"\n🏁 LOCAL MAPPING TEST COMPLETE")
    return True

def test_enhanced_imports():
    """Test if enhanced features imports work locally"""
    print("\n🧪 TESTING ENHANCED IMPORTS")
    print("=" * 50)
    
    try:
        from api.landsat_integration import get_real_landsat_data
        print("✅ landsat_integration imported successfully")
    except Exception as e:
        print(f"❌ landsat_integration import failed: {e}")
        
    try:
        from api.result_mapping import create_result_map
        print("✅ result_mapping imported successfully")
    except Exception as e:
        print(f"❌ result_mapping import failed: {e}")
        
    try:
        from sentinel_pipeline.indices import fai, ndre
        print("✅ sentinel_pipeline.indices imported successfully")
    except Exception as e:
        print(f"❌ sentinel_pipeline.indices import failed: {e}")
        print("   This is likely the cause of the server issue!")

if __name__ == "__main__":
    test_enhanced_imports()
    test_local_mapping() 