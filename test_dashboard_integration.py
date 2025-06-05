#!/usr/bin/env python3
"""
Dashboard Integration Test - Tests the live dashboard and API integration

This script tests:
1. Dashboard serving (HTML, CSS, JS files)
2. API endpoints functionality  
3. Dashboard-API integration capability
"""

import requests
import json
import time
from datetime import datetime
import re

# Live URL
BASE_URL = "https://kelpie-carbon.onrender.com"

def test_root_serves_dashboard():
    """Test if the root URL serves the React dashboard."""
    print("🏠 Testing dashboard serving at root URL...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check if it's serving the dashboard (React app)
            if "<!DOCTYPE html>" in content and ("react" in content.lower() or "vite" in content.lower() or "app" in content.lower()):
                print("✅ Dashboard HTML is being served!")
                
                # Check for essential dashboard elements
                checks = [
                    ("HTML structure", "<!DOCTYPE html>" in content),
                    ("Title tag", "<title>" in content),
                    ("React root div", 'id="root"' in content or 'id="app"' in content),
                    ("CSS/JS assets", "/assets/" in content or ".css" in content or ".js" in content)
                ]
                
                for check_name, passed in checks:
                    status = "✅" if passed else "❌"
                    print(f"   {status} {check_name}")
                
                return True
            else:
                # Check if it's returning API JSON instead
                try:
                    data = json.loads(content)
                    if "message" in data and "Kelp Carbon Analysis API" in data["message"]:
                        print("⚠️  API JSON response detected instead of dashboard")
                        print("   This means dashboard build is not included yet")
                        print(f"   Message: {data.get('message', 'N/A')}")
                        print(f"   Dashboard status: {data.get('dashboard', 'N/A')}")
                        return False
                except:
                    pass
                
                print("❌ Dashboard not detected - unknown content type")
                print(f"   Content preview: {content[:200]}...")
                return False
        else:
            print(f"❌ Root URL failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root URL error: {e}")
        return False

def test_dashboard_assets():
    """Test if dashboard assets (CSS/JS) are accessible."""
    print("\n🎨 Testing dashboard assets...")
    
    # Common asset paths for Vite builds
    asset_paths = [
        "/assets/index.css",
        "/assets/index.js", 
        "/vite.svg"
    ]
    
    assets_working = 0
    for path in asset_paths:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=5)
            if response.status_code == 200:
                print(f"✅ Asset accessible: {path}")
                assets_working += 1
            else:
                print(f"❌ Asset missing: {path} (status: {response.status_code})")
        except Exception as e:
            print(f"❌ Asset error {path}: {e}")
    
    if assets_working > 0:
        print(f"✅ {assets_working}/{len(asset_paths)} assets working")
        return True
    else:
        print("⚠️  No dashboard assets found - dashboard likely not built")
        return False

def test_api_endpoints_still_work():
    """Test that API endpoints still work when dashboard is served."""
    print("\n🔌 Testing API endpoints (should work alongside dashboard)...")
    
    endpoints = [
        ("/health", "Health Check"),
        ("/docs", "API Documentation"),
        ("/carbon?date=2024-06-01&aoi=POLYGON((-123.3656 48.4284, -123.3556 48.4284, -123.3556 48.4184, -123.3656 48.4184, -123.3656 48.4284))", "Carbon Analysis")
    ]
    
    working_endpoints = 0
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=15)
            if response.status_code == 200:
                print(f"✅ {name}: Working")
                working_endpoints += 1
            else:
                print(f"❌ {name}: Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    return working_endpoints == len(endpoints)

def test_dashboard_api_integration():
    """Test if dashboard would be able to integrate with API."""
    print("\n🔗 Testing dashboard-API integration readiness...")
    
    # Test the specific API format the dashboard expects
    test_cases = [
        {
            "name": "Victoria BC Test Area",
            "date": "2024-06-01", 
            "polygon": "POLYGON((-123.4 48.42, -123.35 48.42, -123.35 48.38, -123.4 48.38, -123.4 48.42))"
        },
        {
            "name": "Small Kelp Farm",
            "date": "2024-07-15",
            "polygon": "POLYGON((-123.36 48.41, -123.355 48.41, -123.355 48.405, -123.36 48.405, -123.36 48.41))"
        }
    ]
    
    successful_calls = 0
    for test_case in test_cases:
        try:
            print(f"\n   Testing: {test_case['name']}")
            response = requests.get(
                f"{BASE_URL}/carbon",
                params={
                    "date": test_case["date"],
                    "aoi": test_case["polygon"]
                },
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Analysis successful")
                print(f"      Area: {data.get('area_m2', 0):,.0f} m²")
                print(f"      Biomass: {data.get('biomass_t', 0):,.1f} tonnes")
                print(f"      CO₂: {data.get('co2e_t', 0):,.1f} tonnes")
                successful_calls += 1
            else:
                print(f"   ❌ Analysis failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Integration test error: {e}")
    
    return successful_calls == len(test_cases)

def check_build_status():
    """Check if the service is currently building."""
    print("\n🔨 Checking service build status...")
    
    # Try to detect if service is in build/deploy state
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Service is live and responding")
            return True
        elif response.status_code == 503:
            print("⚠️  Service temporarily unavailable (might be building)")
            return False
        else:
            print(f"⚠️  Service responding with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Service not responding (might be building/restarting)")
        return False
    except Exception as e:
        print(f"❌ Build status check error: {e}")
        return False

def main():
    """Run comprehensive dashboard and integration tests."""
    print("🌊 Kelpie Carbon - Dashboard Integration Test")
    print("=" * 55)
    print(f"Testing: {BASE_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if service is available
    if not check_build_status():
        print("\n⚠️  Service appears to be building or unavailable.")
        print("   Please wait for deployment to complete and try again.")
        return False
    
    tests = [
        ("Dashboard Serving", test_root_serves_dashboard),
        ("Dashboard Assets", test_dashboard_assets),
        ("API Endpoints", test_api_endpoints_still_work),
        ("Dashboard-API Integration", test_dashboard_api_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            print(f"❌ Test '{name}' crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 FULL INTEGRATION SUCCESS!")
        print(f"   Dashboard: {BASE_URL}/")
        print(f"   API: {BASE_URL}/docs")
        print("   Your kelp carbon analysis app is fully functional! 🌱")
    elif passed >= 2:
        print("⚠️  Partial success - API working, dashboard needs build update")
        print("\n🔧 Next steps:")
        print("   1. Update Render build command to include dashboard build")
        print("   2. Trigger manual deploy")
        print("   3. Re-run this test")
    else:
        print("❌ Multiple issues detected - check deployment status")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 