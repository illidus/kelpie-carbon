#!/usr/bin/env python3
"""
Comprehensive diagnosis of what's happening on the deployed server
"""

import requests
import json

def diagnose_server_issue():
    """Diagnose the mapping issue on the deployed server"""
    print("🔍 COMPREHENSIVE SERVER DIAGNOSIS")
    print("=" * 60)
    
    api_base = 'https://kelpie-carbon.onrender.com'
    
    print("1. Basic API health check...")
    try:
        response = requests.get(f"{api_base}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health: {health_data.get('status')}")
            print(f"   ✅ Model loaded: {health_data.get('model_loaded')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    print("\n2. Test basic carbon analysis (no mapping)...")
    try:
        params = {
            'date': '2024-01-15',
            'aoi': 'POLYGON((-123.35 48.42, -123.34 48.42, -123.34 48.43, -123.35 48.43, -123.35 48.42))',
            'use_real_landsat': 'false',
            'include_map': 'false'
        }
        
        response = requests.get(f"{api_base}/carbon", params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Basic analysis works")
            print(f"   ✅ Data source: {data.get('data_source')}")
            print(f"   ✅ Biomass: {data.get('biomass_t')} tonnes")
            print(f"   ✅ Result map field: {'result_map' in data}")
            
            if 'result_map' in data:
                print(f"   ⚠️  Map included despite include_map=false: {data['result_map']}")
        else:
            print(f"   ❌ Basic analysis failed: {response.status_code}")
            print(f"   ❌ Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Basic analysis error: {e}")
    
    print("\n3. Test with mapping enabled...")
    try:
        params = {
            'date': '2024-01-15',
            'aoi': 'POLYGON((-123.35 48.42, -123.34 48.42, -123.34 48.43, -123.35 48.43, -123.35 48.42))',
            'use_real_landsat': 'false',
            'include_map': 'true',
            'map_type': 'geojson'
        }
        
        response = requests.get(f"{api_base}/carbon", params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API call successful")
            
            if 'result_map' in data:
                map_data = data['result_map']
                print(f"   📊 Map data: {json.dumps(map_data, indent=2)[:300]}...")
                
                if map_data and isinstance(map_data, dict):
                    if map_data.get('success'):
                        print(f"   ✅ Mapping successful!")
                    else:
                        error = map_data.get('error', 'unknown')
                        print(f"   ❌ Mapping failed: {error}")
                        
                        # Analyze the specific error
                        if "Mapping features not available" in error:
                            print(f"   🔍 Root cause: ENHANCED_FEATURES_AVAILABLE is False")
                        elif "import" in error.lower():
                            print(f"   🔍 Root cause: Import error in enhanced modules")
                        elif "module" in error.lower():
                            print(f"   🔍 Root cause: Missing Python module")
                else:
                    print(f"   ❌ Invalid map data format: {type(map_data)}")
            else:
                print(f"   ❌ No result_map field in response")
        else:
            print(f"   ❌ Mapping test failed: {response.status_code}")
            print(f"   ❌ Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Mapping test error: {e}")
    
    print("\n4. Test API info endpoint...")
    try:
        response = requests.get(f"{api_base}/api", timeout=10)
        if response.status_code == 200:
            api_data = response.json()
            print(f"   ✅ API info: {api_data.get('message')}")
            print(f"   ✅ Version: {api_data.get('version')}")
        else:
            print(f"   ❌ API info failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API info error: {e}")
    
    print("\n5. Test dashboard access...")
    try:
        response = requests.get(api_base, timeout=10)
        if response.status_code == 200:
            content = response.text[:100]
            if "Enhanced Kelpie Carbon Dashboard" in content:
                print(f"   ✅ Dashboard serves correctly")
            elif "<!DOCTYPE html>" in content:
                print(f"   ✅ Dashboard serves HTML (check title)")
            else:
                print(f"   ⚠️  Dashboard serves JSON: {content}")
        else:
            print(f"   ❌ Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Dashboard error: {e}")
    
    print("\n🏁 DIAGNOSIS COMPLETE")
    print("=" * 60)
    print("📋 SUMMARY:")
    print("- If basic analysis works but mapping fails:")
    print("  → Enhanced features import is failing")
    print("- If ENHANCED_FEATURES_AVAILABLE is False:")
    print("  → Check server logs for import errors")
    print("- Common causes:")
    print("  → Missing dependencies in requirements.txt")
    print("  → Import errors in landsat_integration.py or result_mapping.py")

if __name__ == "__main__":
    diagnose_server_issue() 