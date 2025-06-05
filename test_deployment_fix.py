#!/usr/bin/env python3
"""
Test the deployed enhanced dashboard after the fix
"""

import requests
import time
from datetime import datetime

def test_deployed_dashboard():
    print("🚀 Testing Deployed Enhanced Dashboard")
    print("=" * 45)
    print("🌐 URL: https://kelpie-carbon.onrender.com")
    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Test deployed dashboard
    url = "https://kelpie-carbon.onrender.com"
    
    print("📱 Testing deployed dashboard...")
    try:
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            html = response.text
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"   📏 Length: {len(html)} chars")
            
            # Check if it's serving the enhanced dashboard
            if "Enhanced Kelpie Carbon Dashboard" in html:
                print(f"   🎉 ENHANCED DASHBOARD FOUND!")
                
                # Check for enhanced features in the HTML/JS
                features = [
                    ("Try Real Landsat Data", "🛰️ Landsat toggle"),
                    ("Generate Result Map", "🗺️ Map toggle"),
                    ("Map Type:", "🎛️ Map selector"),
                    ("data-source-badge", "🏷️ Data source badge"),
                    ("Enhanced", "📝 Enhanced content")
                ]
                
                found_features = []
                for feature, description in features:
                    if feature in html:
                        found_features.append((feature, description))
                        print(f"      ✅ {description}")
                    else:
                        print(f"      ❌ {description}")
                
                enhanced_score = len(found_features) / len(features) * 100
                print(f"\n   📊 Enhanced Score: {enhanced_score:.0f}%")
                
                if enhanced_score >= 60:
                    print(f"   🎉 DEPLOYMENT SUCCESSFUL!")
                    dashboard_status = "enhanced"
                else:
                    print(f"   ⚠️ Partial enhancement detected")
                    dashboard_status = "partial"
                    
            elif len(html) > 2000:  # Likely React app
                print(f"   ⚠️ Dashboard serving but may not be enhanced")
                print(f"   📄 Title: {html[html.find('<title>')+7:html.find('</title>')] if '<title>' in html else 'No title'}")
                dashboard_status = "basic"
            else:
                print(f"   ❌ Serving API response instead of dashboard")
                print(f"   📄 Content preview: {html[:200]}...")
                dashboard_status = "api_fallback"
                
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            dashboard_status = "error"
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection failed: {e}")
        dashboard_status = "error"
    
    # Test enhanced API functionality
    print(f"\n🔌 Testing enhanced API...")
    try:
        api_response = requests.get(f"{url}/carbon", params={
            "date": "2024-06-01",
            "aoi": "POLYGON((-123.36 48.41, -123.35 48.41, -123.35 48.40, -123.36 48.40, -123.36 48.41))",
            "use_real_landsat": "true",
            "include_map": "true",
            "map_type": "geojson"
        }, timeout=20)
        
        if api_response.status_code == 200:
            data = api_response.json()
            enhanced_fields = ['data_source', 'biomass_density_t_ha', 'result_map']
            api_enhanced = all(field in data for field in enhanced_fields)
            
            print(f"   ✅ API working")
            print(f"   📊 Enhanced API: {'Yes' if api_enhanced else 'No'}")
            print(f"   🛰️ Data source: {data.get('data_source', 'unknown')}")
            print(f"   🗺️ Map included: {'Yes' if data.get('result_map') else 'No'}")
            api_status = "enhanced" if api_enhanced else "basic"
        else:
            print(f"   ❌ API Error: {api_response.status_code}")
            api_status = "error"
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ API failed: {e}")
        api_status = "error"
    
    # Overall results
    print(f"\n🎯 DEPLOYMENT TEST RESULTS:")
    print(f"   Dashboard: {dashboard_status.upper()}")
    print(f"   API: {api_status.upper()}")
    
    if dashboard_status == "enhanced" and api_status == "enhanced":
        print(f"\n🎉 SUCCESS! Enhanced dashboard is live!")
        print(f"   🌐 Visit: {url}")
        print(f"   🧪 All enhanced features available")
        return True
    elif dashboard_status in ["enhanced", "partial"] and api_status == "enhanced":
        print(f"\n✅ MOSTLY WORKING! Dashboard deployed with enhanced API")
        print(f"   🌐 Visit: {url}")
        return True
    else:
        print(f"\n⚠️ Issues detected - may need additional fixes")
        suggest_next_steps(dashboard_status, api_status)
        return False

def suggest_next_steps(dashboard_status, api_status):
    print(f"\n🔧 NEXT STEPS:")
    
    if dashboard_status == "api_fallback":
        print("   • Dashboard build may have failed on Render")
        print("   • Check Render build logs")
        print("   • Verify dashboard/dist exists after build")
    elif dashboard_status == "basic":
        print("   • Dashboard serving but not enhanced")
        print("   • May be serving old cached version")
        print("   • Wait for deployment completion")
    elif dashboard_status == "error":
        print("   • Dashboard not accessible")
        print("   • Check Render service status")
    
    if api_status == "error":
        print("   • API not working")
        print("   • Check Render API service")

def wait_for_deployment():
    print("⏳ Waiting for Render deployment...")
    print("   (Render deployments typically take 2-5 minutes)")
    print()
    
    for i in range(10):
        print(f"   {i+1}/10 - Checking deployment status...")
        try:
            response = requests.get("https://kelpie-carbon.onrender.com/health", timeout=10)
            if response.status_code == 200:
                print(f"   ✅ Service responding!")
                break
        except:
            pass
        
        if i < 9:  # Don't sleep on last iteration
            time.sleep(30)  # Wait 30 seconds between checks
    
    print()

if __name__ == "__main__":
    print(f"🌊 Enhanced Dashboard Deployment Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Wait a bit for deployment
    wait_for_deployment()
    
    # Test the deployment
    success = test_deployed_dashboard()
    
    print(f"\n{'='*50}")
    if success:
        print("🎉 DEPLOYMENT FIX SUCCESSFUL!")
    else:
        print("⚠️ Additional fixes may be needed") 