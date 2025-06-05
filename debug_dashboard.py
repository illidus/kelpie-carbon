#!/usr/bin/env python3
"""
Debug what the local dashboard is actually serving
"""

import requests

def debug_dashboard():
    print("🔍 Debugging Local Dashboard Content")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        
        if response.status_code == 200:
            html = response.text
            
            print(f"📄 Status: {response.status_code}")
            print(f"📏 Length: {len(html)} characters")
            print(f"📋 Content-Type: {response.headers.get('content-type', 'unknown')}")
            print()
            print("📝 HTML Content:")
            print("-" * 50)
            print(html)
            print("-" * 50)
            
            # Check for specific issues
            if len(html) < 1000:
                print("\n⚠️ HTML is very short - likely basic template")
            
            if "vite" in html.lower():
                print("✅ Vite detected")
            
            if "react" in html.lower():
                print("✅ React detected")
                
            if "Enhanced" in html:
                print("✅ Enhanced features detected")
            else:
                print("❌ No enhanced features found")
                
            if "error" in html.lower():
                print("🚨 Error found in HTML")
                
        else:
            print(f"❌ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_dashboard() 