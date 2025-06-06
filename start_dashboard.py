#!/usr/bin/env python3
"""
Start the enhanced dashboard server from the correct directory and test it
"""

import os
import subprocess
import time
import requests
from pathlib import Path

def start_and_test_dashboard():
    print("🚀 STARTING ENHANCED DASHBOARD")
    print("=" * 50)
    
    # Change to the correct directory
    project_root = Path(__file__).parent
    dist_dir = project_root / "dashboard" / "dist"
    
    print(f"📂 Project root: {project_root}")
    print(f"📂 Dist directory: {dist_dir}")
    print(f"📂 Dist exists: {dist_dir.exists()}")
    
    if not dist_dir.exists():
        print("❌ Dist directory doesn't exist! Run 'npm run build' first.")
        return
    
    # List contents of dist directory
    print(f"\n📁 Contents of dist directory:")
    for item in dist_dir.iterdir():
        if item.is_file():
            print(f"   📄 {item.name} ({item.stat().st_size} bytes)")
        elif item.is_dir():
            print(f"   📁 {item.name}/")
    
    # Change to dist directory and start server
    os.chdir(dist_dir)
    print(f"\n🔄 Changed to: {os.getcwd()}")
    
    # Start server
    print("🚀 Starting HTTP server on port 5000...")
    server_process = subprocess.Popen(
        ["python", "-m", "http.server", "5000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test the server
        print("\n🧪 Testing server...")
        response = requests.get("http://localhost:5000/", timeout=10)
        print(f"✅ Server Response: {response.status_code}")
        print(f"📄 Content-Length: {len(response.text)} chars")
        
        # Check if it's the correct HTML
        if "Enhanced Kelpie Carbon Dashboard" in response.text:
            print("✅ Enhanced Title: Found")
        else:
            print("❌ Enhanced Title: Missing")
            print("📄 First 200 chars of response:")
            print(response.text[:200])
        
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
            print("\n🔄 Server is running in the background...")
            print("   Press Ctrl+C to stop the server")
            
            # Keep server running
            try:
                server_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
                server_process.terminate()
                server_process.wait()
                print("✅ Server stopped")
        else:
            print("\n❌ Issues detected - stopping server")
            server_process.terminate()
            server_process.wait()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    start_and_test_dashboard() 