#!/usr/bin/env python3
"""
Test the local enhanced dashboard with proper timeouts
"""

import requests
import time
from datetime import datetime
import signal
import sys

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def test_with_timeout(func, timeout_seconds=10):
    """Run function with timeout protection"""
    try:
        # Set up timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)
        
        result = func()
        
        # Cancel timeout
        signal.alarm(0)
        return result
        
    except TimeoutError:
        signal.alarm(0)
        print(f"   ⏰ Operation timed out after {timeout_seconds}s")
        return None
    except Exception as e:
        signal.alarm(0)
        print(f"   ❌ Error: {e}")
        return None

def test_local_dashboard():
    print("🏠 Testing Local Enhanced Dashboard (with timeouts)")
    print("=" * 50)
    print("🚀 Expected: http://localhost:5173")
    print("🌐 API endpoint: https://kelpie-carbon.onrender.com")
    print()
    
    # Test local dashboard
    local_url = "http://localhost:5173"
    
    print("📱 Testing local dashboard HTML...")
    
    def test_dashboard():
        response = requests.get(local_url, timeout=8)
        return response
    
    response = test_with_timeout(test_dashboard, 10)
    
    if response and response.status_code == 200:
        html = response.text
        
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"   📏 Length: {len(html)} chars")
        
        # Check for enhanced dashboard features
        enhanced_features = [
            ("Enhanced kelp biomass estimation", "📝 Enhanced header"),
            ("Try Real Landsat Data", "🛰️ Landsat toggle"),
            ("Generate Result Map", "🗺️ Map toggle"), 
            ("Enhanced Carbon Analysis Results", "📊 Enhanced results"),
            ("Map Type:", "🎛️ Map selector"),
            ("data-source-badge", "🏷️ Data source badge"),
            ("use_real_landsat", "🔧 API parameter"),
            ("include_map", "🗺️ Map parameter")
        ]
        
        found_count = 0
        for feature, description in enhanced_features:
            if feature in html:
                print(f"   ✅ {description}")
                found_count += 1
            else:
                print(f"   ❌ {description}")
        
        print(f"\n📊 Enhanced Features: {found_count}/{len(enhanced_features)} found")
        
        if found_count >= 6:
            print("   🎉 LOCAL ENHANCED DASHBOARD WORKING!")
            dashboard_ok = True
        else:
            print("   ⚠️ Dashboard may not be fully enhanced")
            dashboard_ok = False
            
    elif response:
        print(f"   ❌ HTTP Error: {response.status_code}")
        dashboard_ok = False
    else:
        print("   ❌ Dashboard test failed or timed out")
        dashboard_ok = False
    
    # Test API connectivity from local dashboard perspective
    print(f"\n🔌 Testing API connectivity...")
    
    def test_api():
        return requests.get("https://kelpie-carbon.onrender.com/carbon", params={
            "date": "2024-06-01",
            "aoi": "POLYGON((-123.36 48.41, -123.35 48.41, -123.35 48.40, -123.36 48.40, -123.36 48.41))",
            "use_real_landsat": "true",
            "include_map": "true",
            "map_type": "geojson"
        }, timeout=15)
    
    api_response = test_with_timeout(test_api, 20)
    
    if api_response and api_response.status_code == 200:
        data = api_response.json()
        enhanced_fields = ['data_source', 'biomass_density_t_ha', 'result_map']
        api_enhanced = all(field in data for field in enhanced_fields)
        
        print(f"   ✅ API accessible from local dashboard")
        print(f"   📊 Enhanced API: {'Yes' if api_enhanced else 'No'}")
        print(f"   🛰️ Data source: {data.get('data_source', 'unknown')}")
        api_ok = True
    elif api_response:
        print(f"   ❌ API Error: {api_response.status_code}")
        api_ok = False
    else:
        print("   ❌ API test failed or timed out")
        api_ok = False
    
    # Overall assessment
    print(f"\n🎯 LOCAL TEST RESULTS:")
    print(f"   Local Dashboard: {'✅ WORKING' if dashboard_ok else '❌ ISSUES'}")
    print(f"   API Connectivity: {'✅ WORKING' if api_ok else '❌ ISSUES'}")
    
    if dashboard_ok and api_ok:
        print(f"\n🎉 SUCCESS! Local enhanced dashboard is fully functional!")
        print(f"   🌐 Visit: {local_url}")
        print(f"   🧪 Test all enhanced features in your browser")
        print(f"\n💡 Next steps:")
        print(f"   1. Test enhanced features manually in browser")
        print(f"   2. Check browser console for any errors")
        print(f"   3. Fix any issues found")
        print(f"   4. Build and redeploy to Render")
        return True
    else:
        print(f"\n⚠️ Issues detected with local setup")
        return False

def suggest_fixes():
    print(f"\n🔧 COMMON FIXES:")
    print(f"   • CORS issues: Dashboard can't connect to API")
    print(f"   • Missing dependencies: npm install")
    print(f"   • Build issues: npm run build")
    print(f"   • Port conflicts: Try different port")

if __name__ == "__main__":
    print(f"🌊 Local Enhanced Dashboard Test (Timeout Protected)")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        success = test_local_dashboard()
        
        if not success:
            suggest_fixes()
    except KeyboardInterrupt:
        print(f"\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}") 