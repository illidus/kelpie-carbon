#!/usr/bin/env python3
"""
Simple API Test - Non-hanging version

This script tests the API without getting stuck like curl commands.
"""

import sys

def test_api_import():
    """Test if we can import the API module."""
    try:
        sys.path.append('api')
        import main
        print("✅ API module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Cannot import API module: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing API: {e}")
        return False

def test_model_file():
    """Test if the model file exists."""
    import os
    model_path = "models/biomass_rf.pkl"
    if os.path.exists(model_path):
        size = os.path.getsize(model_path)
        print(f"✅ Model file found: {model_path} ({size:,} bytes)")
        return True
    else:
        print(f"❌ Model file missing: {model_path}")
        return False

def test_sentinel_pipeline():
    """Test if sentinel_pipeline can be imported."""
    try:
        from sentinel_pipeline import indices
        print("✅ Sentinel pipeline imported successfully")
        
        # Test a simple calculation
        import numpy as np
        fai_result = indices.fai(np.array([0.2]), np.array([0.1]), np.array([0.05]))
        print(f"✅ FAI calculation works: {fai_result[0]:.4f}")
        return True
    except Exception as e:
        print(f"❌ Sentinel pipeline error: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 Simple API Tests")
    print("=" * 30)
    
    tests = [
        ("Model File", test_model_file),
        ("Sentinel Pipeline", test_sentinel_pipeline),
        ("API Import", test_api_import),
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n🧪 Testing {name}...")
        if test_func():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! API should be working.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main() 