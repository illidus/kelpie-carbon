#!/usr/bin/env python3
"""
Test to verify correct dashboard access
"""

import requests
import subprocess
import time
import sys
import os
from pathlib import Path

def test_correct_dashboard_access():
    print("🧪 TESTING CORRECT DASHBOARD ACCESS")
    print("=" * 50)
    
    # Change to dist directory
    dist_dir = Path(__file__).parent / "dashboard" / "dist"
    os.chdir(dist_dir)
    
    # Start server
    server_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8085"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(2)
    
    try:
        # Test correct access
        print("🌐 Testing localhost:8085/ (ROOT - CORRECT)")
        response = requests.get("http://localhost:8085/", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Length: {len(response.text)} chars")
        
        if response.status_code == 200:
            content = response.text
            if '/assets/' in content:
                print("   ✅ SUCCESS: Serves BUILT dashboard with /assets/ references")
                print("   ✅ Enhanced Kelpie Carbon Dashboard should load properly!")
            else:
                print("   ❌ ERROR: Wrong content served")
        else:
            print("   ❌ ERROR: Server not responding correctly")
            
        # Test incorrect access for comparison
        print("\n🌐 Testing localhost:8085/dashboard/ (WRONG PATH)")
        response = requests.get("http://localhost:8085/dashboard/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 404:
            print("   ✅ EXPECTED: 404 error (path doesn't exist)")
        else:
            print(f"   ❌ UNEXPECTED: Got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        server_process.terminate()
        server_process.wait()
        print("\n🛑 Server stopped")
    
    print("\n" + "=" * 50)
    print("📋 INSTRUCTIONS:")
    print("1. Start server: python -m http.server 8083")
    print("2. Access: http://localhost:8083 (NOT /dashboard/)")
    print("3. You should see the Enhanced Kelpie Carbon Dashboard!")

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    test_correct_dashboard_access() 