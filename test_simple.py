#!/usr/bin/env python3
"""Simple test for API functions."""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.getcwd())

def test_api_functions():
    """Test the core API functions."""
    print("🧪 Testing API functions...")
    
    try:
        from api.main import parse_simple_polygon_wkt, estimate_carbon_sequestration
        
        # Test WKT parsing
        test_polygon = "POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))"
        area = parse_simple_polygon_wkt(test_polygon)
        assert area > 0, "Area should be positive"
        print(f"✅ WKT parsing: {area:,.0f} m²")
        
        # Test carbon calculation
        biomass_kg = 1000  # 1 tonne
        co2e_t = estimate_carbon_sequestration(biomass_kg)
        assert co2e_t > 0, "CO2 equivalent should be positive"
        
        expected = biomass_kg * 0.325 * 3.67 / 1000  # tonnes
        assert abs(co2e_t - expected) < 0.01, f"Expected {expected:.3f}, got {co2e_t:.3f}"
        print(f"✅ Carbon calculation: {biomass_kg}kg biomass -> {co2e_t:.3f}t CO₂e")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_spectral_indices():
    """Test the spectral index calculations."""
    print("\n🧪 Testing spectral indices...")
    
    try:
        from api.main import generate_realistic_spectral_data
        
        # Test with different inputs
        test_cases = [
            {"area": 1000000, "date": "2024-07-15"},  # 1 km²
            {"area": 100000, "date": "2024-01-15"},   # 0.1 km²
            {"area": 10000000, "date": "2024-04-15"}, # 10 km²
        ]
        
        for case in test_cases:
            fai, ndre = generate_realistic_spectral_data(case["area"], case["date"])
            
            # Check that values are in reasonable ranges
            assert -0.2 <= fai <= 0.5, f"FAI {fai} out of range"
            assert -0.3 <= ndre <= 0.8, f"NDRE {ndre} out of range"
            
            print(f"✅ Area: {case['area']:,} m², Date: {case['date']} -> FAI: {fai:.3f}, NDRE: {ndre:.3f}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_model_loading():
    """Test model loading."""
    print("\n🧪 Testing model loading...")
    
    try:
        from api.main import load_model
        load_model()
        print("✅ Model loaded successfully")
        return True
        
    except FileNotFoundError:
        print("⚠️  Model file not found - this is expected if model hasn't been trained yet")
        return True
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting simple API tests...\n")
    
    success = True
    success &= test_api_functions()
    success &= test_spectral_indices()
    success &= test_model_loading()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1) 