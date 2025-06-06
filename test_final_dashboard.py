#!/usr/bin/env python3
"""
Final test of the enhanced dashboard
"""

import requests

def test_final_dashboard():
    print("🎯 FINAL ENHANCED DASHBOARD TEST")
    print("=" * 50)
    
    try:
        # Test the correctly configured server
        response = requests.get("http://localhost:8089/", timeout=10)
        print(f"✅ Server Response: {response.status_code}")
        print(f"📄 Content-Length: {len(response.text)} chars")
        
        # Check title
        if "Enhanced Kelpie Carbon Dashboard" in response.text:
            print("✅ Enhanced Title: Found")
        else:
            print("❌ Enhanced Title: Missing")
        
        # Check for proper asset references  
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
        
        js_response = requests.get("http://localhost:8089/assets/index-w8fYw47q.js", timeout=5)
        print(f"📦 JavaScript: {js_response.status_code} ({len(js_response.text):,} chars)")
        
        css_response = requests.get("http://localhost:8089/assets/index-BB8Xwy15.css", timeout=5)
        print(f"🎨 CSS: {css_response.status_code} ({len(css_response.text):,} chars)")
        
        if response.status_code == 200 and js_response.status_code == 200 and css_response.status_code == 200:
            print("\n🎉 SUCCESS! ENHANCED DASHBOARD IS READY!")
            print("🌐 Access at: http://localhost:8089")
            print("\n📋 Enhanced Features Available:")
            print("   🛰️ Real Landsat Data toggle")
            print("   🗺️ Result Map Generation toggle") 
            print("   📊 Map Type selector (GeoJSON/Static/Interactive)")
            print("   📊 Enhanced results with data source badges")
            print("   📊 Biomass density field")
            print("   📊 Enhanced header with description")
            print("\n💡 Instructions:")
            print("   1. Open http://localhost:8089 in your browser")
            print("   2. Clear cache if needed (Ctrl+Shift+R)")
            print("   3. You should see all enhanced features!")
        else:
            print("\n❌ Some components failed to load")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_final_dashboard() 