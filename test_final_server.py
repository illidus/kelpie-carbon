#!/usr/bin/env python3
"""
Final test of the correctly configured enhanced dashboard server
"""

import requests
import time

def test_final_server():
    print("🎯 FINAL TEST - ENHANCED DASHBOARD")
    print("=" * 50)
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test the server
        response = requests.get("http://localhost:5000/", timeout=10)
        print(f"✅ Server Response: {response.status_code}")
        print(f"📄 Content-Length: {len(response.text)} chars")
        
        # Show actual content for debugging
        print(f"\n📄 Actual HTML Content:")
        print("-" * 40)
        print(response.text)
        print("-" * 40)
        
        # Check for enhanced title
        if "Enhanced Kelpie Carbon Dashboard" in response.text:
            print("✅ Enhanced Title: Found")
        else:
            print("❌ Enhanced Title: Missing")
        
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
        
        js_response = requests.get("http://localhost:5000/assets/index-w8fYw47q.js", timeout=5)
        css_response = requests.get("http://localhost:5000/assets/index-BB8Xwy15.css", timeout=5)
        
        print(f"📦 JavaScript: {js_response.status_code} ({len(js_response.text):,} chars)")
        print(f"🎨 CSS: {css_response.status_code} ({len(css_response.text):,} chars)")
        
        # Final verdict
        if (response.status_code == 200 and 
            js_response.status_code == 200 and 
            css_response.status_code == 200 and
            "Enhanced Kelpie Carbon Dashboard" in response.text):
            
            print("\n🎉 SUCCESS! ENHANCED DASHBOARD IS WORKING!")
            print("🌐 Enhanced Kelpie Carbon Dashboard")
            print("📍 Access at: http://localhost:5000")
            print("\n📋 Enhanced Features Available:")
            print("   🛰️ Real Landsat Data toggle")
            print("   🗺️ Result Map Generation toggle")
            print("   📊 Map Type selector (GeoJSON/Static/Interactive)")
            print("   📊 Enhanced results with data source badges")
            print("   📊 Biomass density field")
            print("   📊 Enhanced API integration")
            print("\n💡 Instructions:")
            print("   1. Open http://localhost:5000 in your browser")
            print("   2. Clear cache if needed (Ctrl+Shift+R)")
            print("   3. Draw a polygon to test enhanced features")
        else:
            print("\n❌ Issues detected - check logs above")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_final_server() 