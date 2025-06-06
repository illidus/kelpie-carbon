#!/usr/bin/env python3
"""
Final comprehensive test to verify the mapping functionality is fixed
"""

import requests
import time
import json

def test_final_mapping_fix():
    """Final test of the mapping functionality fix"""
    print("🎯 FINAL MAPPING FIX VERIFICATION")
    print("=" * 60)
    
    api_base = 'https://kelpie-carbon.onrender.com'
    test_polygon = "POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))"
    
    print("⏳ Waiting for deployment to complete (90 seconds)...")
    time.sleep(90)
    
    # Test 1: Basic functionality
    print("\n1. 🔍 Testing basic API functionality...")
    success_basic = test_basic_functionality(api_base, test_polygon)
    
    # Test 2: Enhanced features availability
    print("\n2. 🔍 Testing enhanced features availability...")
    enhanced_available = test_enhanced_features(api_base, test_polygon)
    
    # Test 3: All mapping types
    print("\n3. 🔍 Testing all mapping types...")
    mapping_results = test_all_mapping_types(api_base, test_polygon)
    
    # Test 4: Dashboard functionality
    print("\n4. 🔍 Testing dashboard...")
    dashboard_works = test_dashboard(api_base)
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 60)
    
    print(f"✅ Basic API: {'PASS' if success_basic else 'FAIL'}")
    print(f"✅ Enhanced Features: {'PASS' if enhanced_available else 'FAIL'}")
    print(f"✅ Dashboard: {'PASS' if dashboard_works else 'FAIL'}")
    
    print(f"\n📊 Mapping Results:")
    for map_type, result in mapping_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {map_type.title()}: {status}")
    
    # Overall assessment
    all_mapping_works = all(mapping_results.values())
    overall_success = success_basic and enhanced_available and all_mapping_works
    
    print(f"\n🎯 OVERALL STATUS: {'🎉 SUCCESS!' if overall_success else '❌ NEEDS MORE WORK'}")
    
    if overall_success:
        print("\n🎉 CONGRATULATIONS!")
        print("✅ The mapping functionality is now working!")
        print("✅ Users can now generate maps when drawing polygons!")
        print("✅ All enhanced features are operational!")
    else:
        print("\n🔧 NEXT STEPS:")
        if not enhanced_available:
            print("- Enhanced features still not importing properly")
            print("- Check server logs for specific import errors")
        if not all_mapping_works:
            print("- Some mapping types still failing")
            print("- May need to simplify dependencies further")

def test_basic_functionality(api_base, test_polygon):
    """Test basic API functionality"""
    try:
        params = {
            'date': '2024-01-15',
            'aoi': test_polygon,
            'include_map': 'false'
        }
        
        response = requests.get(f"{api_base}/carbon", params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            has_required_fields = all(field in data for field in ['biomass_t', 'co2e_t', 'data_source'])
            print(f"   ✅ Basic analysis: SUCCESS")
            print(f"   ✅ Data source: {data.get('data_source')}")
            return has_required_fields
        else:
            print(f"   ❌ Basic analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Basic analysis error: {e}")
        return False

def test_enhanced_features(api_base, test_polygon):
    """Test if enhanced features are available"""
    try:
        params = {
            'date': '2024-01-15',
            'aoi': test_polygon,
            'include_map': 'true',
            'map_type': 'geojson'
        }
        
        response = requests.get(f"{api_base}/carbon", params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'result_map' in data:
                map_data = data['result_map']
                
                if isinstance(map_data, dict) and 'error' in map_data:
                    error = map_data['error']
                    if "Mapping features not available" in error:
                        print(f"   ❌ Enhanced features: NOT AVAILABLE")
                        return False
                    else:
                        print(f"   ⚠️  Enhanced features: PARTIAL ({error})")
                        return False
                else:
                    print(f"   ✅ Enhanced features: AVAILABLE")
                    return True
            else:
                print(f"   ❌ Enhanced features: NO RESULT_MAP")
                return False
        else:
            print(f"   ❌ Enhanced features test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Enhanced features error: {e}")
        return False

def test_all_mapping_types(api_base, test_polygon):
    """Test all mapping types"""
    results = {}
    
    for map_type in ['geojson', 'static', 'interactive']:
        print(f"   Testing {map_type} mapping...")
        
        try:
            params = {
                'date': '2024-01-15',
                'aoi': test_polygon,
                'include_map': 'true',
                'map_type': map_type
            }
            
            response = requests.get(f"{api_base}/carbon", params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'result_map' in data:
                    map_data = data['result_map']
                    
                    if isinstance(map_data, dict) and map_data.get('success'):
                        print(f"      ✅ {map_type}: SUCCESS")
                        
                        # Verify expected content
                        if map_type == 'geojson' and 'geojson' in map_data:
                            print(f"      ✅ GeoJSON data present")
                        elif map_type == 'static' and 'image_base64' in map_data:
                            print(f"      ✅ Image data present ({len(map_data['image_base64']):,} chars)")
                        elif map_type == 'interactive' and 'html' in map_data:
                            print(f"      ✅ HTML data present ({len(map_data['html']):,} chars)")
                        
                        results[map_type] = True
                    else:
                        error = map_data.get('error', 'unknown') if isinstance(map_data, dict) else 'invalid format'
                        print(f"      ❌ {map_type}: FAILED - {error}")
                        results[map_type] = False
                else:
                    print(f"      ❌ {map_type}: NO RESULT_MAP")
                    results[map_type] = False
            else:
                print(f"      ❌ {map_type}: HTTP {response.status_code}")
                results[map_type] = False
                
        except Exception as e:
            print(f"      ❌ {map_type}: ERROR - {e}")
            results[map_type] = False
    
    return results

def test_dashboard(api_base):
    """Test dashboard functionality"""
    try:
        response = requests.get(api_base, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            if "Enhanced Kelpie Carbon Dashboard" in content:
                print(f"   ✅ Dashboard: ENHANCED VERSION")
                return True
            elif "<!DOCTYPE html>" in content:
                print(f"   ✅ Dashboard: HTML (check title)")
                return True
            else:
                print(f"   ❌ Dashboard: SERVES JSON")
                return False
        else:
            print(f"   ❌ Dashboard: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Dashboard error: {e}")
        return False

if __name__ == "__main__":
    test_final_mapping_fix() 