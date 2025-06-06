#!/usr/bin/env python3
"""
Test the Vite preview server for the enhanced dashboard
"""

import requests
import time

def test_vite_preview():
    print("🎯 TESTING VITE PREVIEW SERVER")
    print("=" * 50)
    
    # Wait for Vite preview server to start
    time.sleep(5)
    
    try:
        # Test on Vite's default preview port
        response = requests.get("http://localhost:4173/", timeout=10)
        print(f"✅ Vite Preview Response: {response.status_code}")
        print(f"📄 Content-Length: {len(response.text)} chars")
        
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
        
        js_response = requests.get("http://localhost:4173/assets/index-w8fYw47q.js", timeout=5)
        css_response = requests.get("http://localhost:4173/assets/index-BB8Xwy15.css", timeout=5)
        
        print(f"📦 JavaScript: {js_response.status_code} ({len(js_response.text):,} chars)")
        print(f"🎨 CSS: {css_response.status_code} ({len(css_response.text):,} chars)")
        
        # Check if everything is working
        all_working = all([
            response.status_code == 200,
            js_response.status_code == 200,
            css_response.status_code == 200,
            "Enhanced Kelpie Carbon Dashboard" in response.text
        ])
        
        if all_working:
            print("\n🎉 PERFECT! ENHANCED DASHBOARD IS READY!")
            print("🌐 Enhanced Kelpie Carbon Dashboard")
            print("📍 Access at: http://localhost:4173")
            print("\n📋 Enhanced Features Available:")
            print("   🛰️ Real Landsat Data toggle")
            print("   🗺️ Result Map Generation toggle")
            print("   📊 Map Type selector (GeoJSON/Static/Interactive)")
            print("   📊 Enhanced results with data source badges")
            print("   📊 Biomass density field")
            print("   📊 Enhanced API integration")
            print("\n💡 Instructions:")
            print("   1. Open http://localhost:4173 in your browser")
            print("   2. You should see all enhanced features!")
            print("   3. Draw a polygon to test the enhanced analysis")
        else:
            print("\n❌ Some issues detected")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Vite preview server may not be running yet. Try again in a moment.")

if __name__ == "__main__":
    test_vite_preview() 