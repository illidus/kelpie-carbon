#!/usr/bin/env python3
"""
Simple test to check if enhanced modules can be imported individually
"""

import sys
import os

# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

def test_individual_imports():
    """Test importing each enhanced module individually"""
    print("🧪 TESTING INDIVIDUAL IMPORTS")
    print("=" * 40)
    
    print("1. Testing result_mapping import...")
    try:
        import result_mapping
        print("   ✅ result_mapping imported successfully")
        
        # Test the key function
        from result_mapping import create_result_map
        print("   ✅ create_result_map function imported")
        
    except Exception as e:
        print(f"   ❌ result_mapping import failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n2. Testing landsat_integration import...")
    try:
        import landsat_integration
        print("   ✅ landsat_integration imported successfully")
        
        # Test the key function
        from landsat_integration import get_real_landsat_data
        print("   ✅ get_real_landsat_data function imported")
        
    except Exception as e:
        print(f"   ❌ landsat_integration import failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3. Testing both imports together...")
    try:
        from landsat_integration import get_real_landsat_data
        from result_mapping import create_result_map
        print("   ✅ Both modules imported together successfully")
        
    except Exception as e:
        print(f"   ❌ Combined import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_individual_imports() 