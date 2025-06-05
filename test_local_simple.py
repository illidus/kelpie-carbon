#!/usr/bin/env python3
"""
Simple test for local enhanced dashboard - Windows compatible
"""

import requests
from datetime import datetime

def test_enhanced_dashboard():
    print("🌊 Testing Enhanced Dashboard (Windows Compatible)")
    print("=" * 50)
    print("🚀 Expected: http://localhost:5173")
    print("🌐 API: https://kelpie-carbon.onrender.com")
    print()
    
    # Test local dashboard with short timeout
    local_url = "http://localhost:5173"
    
    print("📱 Testing local dashboard...")
    try:
        response = requests.get(local_url, timeout=5)
        
        if response.status_code == 200:
            html = response.text
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📏 Length: {len(html)} chars")
            
            # Check for enhanced features quickly
            enhanced_features = [
                "Enhanced kelp biomass estimation",
                "Try Real Landsat Data",
                "Generate Result Map",
                "Map Type:",
                "data-source-badge"
            ]
            
            found_features = []
            for feature in enhanced_features:
                if feature in html:
                    found_features.append(feature)
            
            print(f"   🔧 Enhanced Features Found: {len(found_features)}/{len(enhanced_features)}")
            for feature in found_features:
                print(f"      ✅ {feature}")
            
            missing = [f for f in enhanced_features if f not in found_features]
            for feature in missing:
                print(f"      ❌ {feature}")
            
            if len(found_features) >= 3:
                print(f"\n🎉 ENHANCED DASHBOARD IS WORKING!")
                dashboard_ok = True
            else:
                print(f"\n⚠️ Dashboard might not be fully enhanced")
                dashboard_ok = False
                
        else:
            print(f"   ❌ HTTP {response.status_code}")
            dashboard_ok = False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection failed: {e}")
        dashboard_ok = False
    
    # Quick API test
    print(f"\n🔌 Testing API...")
    try:
        api_response = requests.get("https://kelpie-carbon.onrender.com/carbon", 
                                   params={
                                       "date": "2024-06-01",
                                       "aoi": "POLYGON((-123.36 48.41, -123.35 48.41, -123.35 48.40, -123.36 48.40, -123.36 48.41))",
                                       "use_real_landsat": "false",
                                       "include_map": "true",
                                       "map_type": "geojson"
                                   }, timeout=10)
        
        if api_response.status_code == 200:
            data = api_response.json()
            print(f"   ✅ API working")
            print(f"   📊 Data source: {data.get('data_source', 'unknown')}")
            api_ok = True
        else:
            print(f"   ❌ API error: {api_response.status_code}")
            api_ok = False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ API failed: {e}")
        api_ok = False
    
    # Results
    print(f"\n🎯 RESULTS:")
    print(f"   Dashboard: {'✅ WORKING' if dashboard_ok else '❌ ISSUES'}")
    print(f"   API: {'✅ WORKING' if api_ok else '❌ ISSUES'}")
    
    if dashboard_ok and api_ok:
        print(f"\n🎉 SUCCESS! Ready for manual testing!")
        print(f"   🌐 Open: {local_url}")
        print(f"   🧪 Test: Real Landsat toggle, map generation")
        return True
    else:
        print(f"\n⚠️ Issues found - check output above")
        return False

if __name__ == "__main__":
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    test_enhanced_dashboard() 