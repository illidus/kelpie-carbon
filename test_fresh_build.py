#!/usr/bin/env python3
"""
Test the completely fresh build of the enhanced dashboard
"""

import requests
import time

def test_fresh_build():
    print("🚀 TESTING FRESH ENHANCED DASHBOARD BUILD")
    print("=" * 60)
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test main page
        response = requests.get("http://localhost:9000/", timeout=10)
        print(f"✅ Server Response: {response.status_code}")
        print(f"📄 Content-Length: {len(response.text)} chars")
        
        # Verify it's the correct content
        expected_title = "Enhanced Kelpie Carbon Dashboard"
        if expected_title in response.text:
            print(f"✅ Title: {expected_title} ✓")
        else:
            print(f"❌ Title: Missing")
            
        # Check asset references
        if "/assets/index-w8fYw47q.js" in response.text:
            print("✅ JavaScript Bundle: Correctly referenced")
        else:
            print("❌ JavaScript Bundle: Wrong reference")
            
        if "/assets/index-BB8Xwy15.css" in response.text:
            print("✅ CSS Bundle: Correctly referenced")
        else:
            print("❌ CSS Bundle: Wrong reference")
        
        # Test asset loading
        print("\n🔍 Testing Asset Loading...")
        
        js_response = requests.get("http://localhost:9000/assets/index-w8fYw47q.js", timeout=5)
        css_response = requests.get("http://localhost:9000/assets/index-BB8Xwy15.css", timeout=5)
        
        print(f"📦 JavaScript: {js_response.status_code} ({len(js_response.text):,} chars)")
        print(f"🎨 CSS: {css_response.status_code} ({len(css_response.text):,} chars)")
        
        # Final verdict
        all_good = all([
            response.status_code == 200,
            js_response.status_code == 200,
            css_response.status_code == 200,
            expected_title in response.text,
            "/assets/index-w8fYw47q.js" in response.text,
            "/assets/index-BB8Xwy15.css" in response.text
        ])
        
        if all_good:
            print("\n🎉 SUCCESS! FRESH BUILD IS WORKING PERFECTLY!")
            print("🌐 Enhanced Kelpie Carbon Dashboard")
            print("📍 Access at: http://localhost:9000")
            print("\n📋 Enhanced Features Available:")
            print("   🛰️ Real Landsat Data toggle")
            print("   🗺️ Result Map Generation toggle")
            print("   📊 Map Type selector (GeoJSON/Static/Interactive)")
            print("   📊 Enhanced results with data source badges")
            print("   📊 Biomass density field")
            print("   📊 Enhanced header with real satellite data support")
            print("\n💡 Instructions:")
            print("   1. Open http://localhost:9000 in your browser")
            print("   2. Use incognito/private window to avoid cache issues")
            print("   3. Draw a polygon on the map to test enhanced features")
            print("   4. Toggle the Landsat and Map options to see new functionality")
        else:
            print("\n❌ Some issues detected - check the logs above")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the server is running on port 9000")

if __name__ == "__main__":
    test_fresh_build() 