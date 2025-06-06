#!/usr/bin/env python3
"""
Test the mapping functionality fix - verify enhanced features work without sentinel_pipeline
"""

import sys
import os

# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
sys.path.append(os.path.dirname(__file__))

def test_enhanced_features_with_fix():
    """Test that enhanced features work even without sentinel_pipeline"""
    print("🧪 TESTING ENHANCED FEATURES FIX")
    print("=" * 60)
    
    # Temporarily remove sentinel_pipeline from path to simulate server environment
    original_path = sys.path.copy()
    
    # Remove paths that contain sentinel_pipeline
    filtered_path = [p for p in sys.path if 'sentinel_pipeline' not in p and not os.path.exists(os.path.join(p, 'sentinel_pipeline'))]
    sys.path = filtered_path
    
    # Also temporarily rename the sentinel_pipeline directory to simulate it not existing
    sentinel_dir = 'sentinel_pipeline'
    temp_dir = 'sentinel_pipeline_hidden'
    
    renamed = False
    if os.path.exists(sentinel_dir):
        try:
            os.rename(sentinel_dir, temp_dir)
            renamed = True
            print("   🔒 Temporarily hid sentinel_pipeline to simulate server environment")
        except:
            pass
    
    try:
        print("\n1. Testing enhanced imports without sentinel_pipeline...")
        
        # Test main.py imports
        try:
            # Force reload of modules to test import without sentinel_pipeline
            import importlib
            if 'api.main' in sys.modules:
                importlib.reload(sys.modules['api.main'])
            if 'api.landsat_integration' in sys.modules:
                importlib.reload(sys.modules['api.landsat_integration'])
            if 'api.result_mapping' in sys.modules:
                importlib.reload(sys.modules['api.result_mapping'])
                
            from api.main import ENHANCED_FEATURES_AVAILABLE
            print(f"   ✅ Enhanced features available: {ENHANCED_FEATURES_AVAILABLE}")
            
            if ENHANCED_FEATURES_AVAILABLE:
                from api.landsat_integration import get_real_landsat_data
                from api.result_mapping import create_result_map
                print("   ✅ Enhanced modules imported successfully")
            else:
                print("   ❌ Enhanced features still not available")
                
        except Exception as e:
            print(f"   ❌ Import error: {e}")
            
        print("\n2. Testing mapping functionality...")
        if ENHANCED_FEATURES_AVAILABLE:
            from api.result_mapping import create_result_map
            
            # Test data
            test_polygon = "POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))"
            test_results = {
                "date": "2024-01-15",
                "area_m2": 5000000,
                "biomass_t": 2500.0,
                "co2e_t": 1750.0,
                "mean_fai": 0.025,
                "mean_ndre": 0.15
            }
            
            # Test GeoJSON mapping
            try:
                geojson_map = create_result_map(test_polygon, test_results, "geojson")
                if geojson_map and geojson_map.get('success'):
                    print("   ✅ GeoJSON mapping works without sentinel_pipeline")
                else:
                    print(f"   ❌ GeoJSON mapping failed: {geojson_map.get('error') if geojson_map else 'None'}")
            except Exception as e:
                print(f"   ❌ GeoJSON mapping error: {e}")
                
            # Test static mapping
            try:
                static_map = create_result_map(test_polygon, test_results, "static")
                if static_map and static_map.get('success'):
                    print("   ✅ Static mapping works without sentinel_pipeline")
                else:
                    print(f"   ❌ Static mapping failed: {static_map.get('error') if static_map else 'None'}")
            except Exception as e:
                print(f"   ❌ Static mapping error: {e}")
                
        print("\n3. Testing fallback spectral functions...")
        try:
            from api.main import fai, ndre
            import numpy as np
            
            # Test with sample data
            test_fai = fai(np.array([0.2]), np.array([0.15]), np.array([0.1]))
            test_ndre = ndre(np.array([0.13]), np.array([0.2]))
            
            print(f"   ✅ Fallback FAI: {test_fai[0]:.3f}")
            print(f"   ✅ Fallback NDRE: {test_ndre[0]:.3f}")
            
        except Exception as e:
            print(f"   ❌ Fallback function error: {e}")
            
        print("\n4. Testing Landsat integration...")
        try:
            from api.landsat_integration import get_real_landsat_data
            
            # Test with mock data (should use fallback)
            test_wkt = "POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))"
            fai_val, ndre_val, metadata = get_real_landsat_data(test_wkt, "2024-01-15")
            
            print(f"   ✅ Landsat integration works (fallback mode)")
            print(f"   ✅ Metadata source: {metadata.get('source', 'unknown')}")
            
        except Exception as e:
            print(f"   ❌ Landsat integration error: {e}")
    
    finally:
        # Restore original state
        sys.path = original_path
        
        # Restore sentinel_pipeline directory
        if renamed and os.path.exists(temp_dir):
            try:
                os.rename(temp_dir, sentinel_dir)
                print("   🔓 Restored sentinel_pipeline directory")
            except:
                pass
    
    print("\n🏁 ENHANCED FEATURES FIX TEST COMPLETE")
    print("=" * 60)

def test_api_simulation():
    """Simulate the full API call with the fixes"""
    print("\n🧪 SIMULATING FULL API CALL")
    print("=" * 50)
    
    try:
        # Import the fixed API
        from api.main import carbon_analysis
        
        # Mock FastAPI query parameters
        class MockQuery:
            def __init__(self, value):
                self.value = value
                
        # Test parameters
        date = "2024-01-15"
        aoi = "POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))"
        use_real_landsat = False
        include_map = True
        map_type = "geojson"
        
        print(f"   Testing with: date={date}, include_map={include_map}, map_type={map_type}")
        
        # Note: We can't easily test the FastAPI endpoint directly, but we can test the core logic
        print("   ✅ API imports work with fixes")
        print("   ℹ️  Full API test requires running server")
        
    except Exception as e:
        print(f"   ❌ API simulation error: {e}")

if __name__ == "__main__":
    test_enhanced_features_with_fix()
    test_api_simulation() 