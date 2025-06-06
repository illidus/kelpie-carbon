#!/usr/bin/env python3
"""
Debug script to identify why the browser is requesting development files
"""

import requests
import subprocess
import time
import sys
import os
from pathlib import Path

def debug_serving_issue():
    print("🔍 DEBUGGING SERVING ISSUE")
    print("=" * 60)
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    
    # Change to dist directory
    dist_dir = Path(__file__).parent / "dashboard" / "dist"
    print(f"Dist directory: {dist_dir}")
    print(f"Dist directory exists: {dist_dir.exists()}")
    
    if not dist_dir.exists():
        print("❌ Dist directory doesn't exist!")
        return
    
    os.chdir(dist_dir)
    print(f"Changed to: {os.getcwd()}")
    
    # Check files in current directory
    print("\n📂 Files in current directory:")
    for item in Path('.').iterdir():
        if item.is_file():
            print(f"   📄 {item.name} ({item.stat().st_size} bytes)")
        elif item.is_dir():
            print(f"   📁 {item.name}/")
    
    # Read the actual index.html file
    print("\n📄 ACTUAL index.html content:")
    with open('index.html', 'r') as f:
        content = f.read()
        print(content)
    
    # Start server
    print("\n🚀 Starting server on port 8086...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8086"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(3)
    
    try:
        # Test what's actually being served
        print("\n🌐 Testing what's actually being served...")
        response = requests.get("http://localhost:8086/", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content-Length: {len(response.text)}")
        
        print("\n📄 SERVED CONTENT:")
        print("-" * 40)
        print(response.text)
        print("-" * 40)
        
        # Check if the served content matches the file content
        if response.text.strip() == content.strip():
            print("✅ Served content matches file content")
        else:
            print("❌ Served content DOES NOT match file content")
            print("This suggests a server or caching issue")
        
        # Test specific asset requests
        print("\n🔍 Testing asset requests...")
        
        # Test CSS file
        try:
            css_response = requests.get("http://localhost:8086/assets/index-BB8Xwy15.css", timeout=5)
            print(f"CSS file: {css_response.status_code} ({len(css_response.text)} chars)")
        except:
            print("CSS file: Failed to load")
        
        # Test JS file
        try:
            js_response = requests.get("http://localhost:8086/assets/index-w8fYw47q.js", timeout=5)
            print(f"JS file: {js_response.status_code} ({len(js_response.text)} chars)")
        except:
            print("JS file: Failed to load")
        
        # Test vite.svg
        try:
            svg_response = requests.get("http://localhost:8086/vite.svg", timeout=5)
            print(f"Vite SVG: {svg_response.status_code} ({len(svg_response.text)} chars)")
        except:
            print("Vite SVG: Failed to load")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    finally:
        server_process.terminate()
        server_process.wait()
        print("\n🛑 Server stopped")
    
    print("\n" + "=" * 60)

def create_cache_busting_solution():
    """Create a solution that forces browser cache refresh"""
    print("🔧 CREATING CACHE-BUSTING SOLUTION")
    print("=" * 60)
    
    dist_dir = Path(__file__).parent / "dashboard" / "dist"
    
    # Read current index.html
    index_file = dist_dir / "index.html"
    if not index_file.exists():
        print("❌ index.html not found!")
        return
    
    with open(index_file, 'r') as f:
        content = f.read()
    
    # Add cache-busting meta tags and modify for better compatibility
    cache_busting_content = content.replace(
        '<head>',
        '''<head>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">'''
    )
    
    # Write cache-busting version
    cache_busting_file = dist_dir / "index_cache_busted.html"
    with open(cache_busting_file, 'w') as f:
        f.write(cache_busting_content)
    
    print(f"✅ Created cache-busting version: {cache_busting_file}")
    print("📋 To test:")
    print("1. Start server: python -m http.server 8087")
    print("2. Access: http://localhost:8087/index_cache_busted.html")
    print("3. Or try hard refresh (Ctrl+Shift+R) on regular index.html")

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    debug_serving_issue()
    create_cache_busting_solution() 