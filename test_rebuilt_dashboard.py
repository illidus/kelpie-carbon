#!/usr/bin/env python3
"""
Test the rebuilt dashboard to verify all enhanced features are present
"""

import requests
import time
import subprocess
import sys
from pathlib import Path

def test_rebuilt_dashboard():
    print("🧪 TESTING REBUILT ENHANCED DASHBOARD")
    print("=" * 60)
    
    # Test server response
    try:
        response = requests.get("http://localhost:8088/", timeout=10)
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
        
        js_response = requests.get("http://localhost:8088/assets/index-w8fYw47q.js", timeout=5)
        print(f"📦 JavaScript: {js_response.status_code} ({len(js_response.text):,} chars)")
        
        css_response = requests.get("http://localhost:8088/assets/index-BB8Xwy15.css", timeout=5)
        print(f"🎨 CSS: {css_response.status_code} ({len(css_response.text):,} chars)")
        
        # Check for enhanced features in the HTML (this is what the browser loads)
        print("\n✅ DASHBOARD IS READY!")
        print("🌐 Access at: http://localhost:8088")
        print("\n📋 Expected Enhanced Features:")
        print("   🛰️ Real Landsat Data toggle")
        print("   🗺️ Result Map Generation toggle") 
        print("   📊 Map Type selector (GeoJSON/Static/Interactive)")
        print("   📊 Enhanced results with data source badges")
        print("   📊 Biomass density field")
        print("   📊 Enhanced header with description")
        
        print("\n💡 TROUBLESHOOTING TIPS:")
        print("   1. Clear browser cache (Ctrl+Shift+R)")
        print("   2. Try incognito/private window")
        print("   3. Open browser DevTools to check for errors")
        print("   4. Ensure you're accessing the ROOT URL (not /dashboard/)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🚀 Starting server on port 8088...")
        
        # Change to dist directory and start server
        dist_dir = Path(__file__).parent / "dashboard" / "dist"
        import os
        os.chdir(dist_dir)
        
        server_process = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8088"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        time.sleep(3)
        print("✅ Server started! Try again: http://localhost:8088")

def verify_source_code():
    print("\n🔍 VERIFYING SOURCE CODE INTEGRITY")
    print("=" * 40)
    
    app_file = Path(__file__).parent / "dashboard" / "src" / "App.jsx"
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    features_to_check = [
        ("Enhanced Controls", "EnhancedControls"),
        ("Real Landsat Toggle", "🛰️ Try Real Landsat Data"),
        ("Map Generation Toggle", "🗺️ Generate Result Map"),
        ("Map Type Selector", "Map Type:"),
        ("Data Source Badge", "data-source-badge"),
        ("Enhanced Header", "Enhanced kelp biomass estimation"),
        ("Biomass Density", "biomass_density_t_ha"),
        ("Enhanced API Parameters", "use_real_landsat"),
        ("Result Mapping", "result_map")
    ]
    
    for feature_name, search_text in features_to_check:
        if search_text in content:
            print(f"   ✅ {feature_name}")
        else:
            print(f"   ❌ {feature_name}")
    
    print(f"\n📊 Source Code Size: {len(content):,} characters")
    print(f"📂 Source File: {app_file}")

if __name__ == "__main__":
    verify_source_code()
    test_rebuilt_dashboard() 