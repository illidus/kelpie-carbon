#!/usr/bin/env python3
import requests
import time

print("🧪 Testing Enhanced Dashboard on Port 8090")
print("=" * 50)

time.sleep(2)  # Wait for server to start

try:
    response = requests.get("http://localhost:8090/", timeout=10)
    print(f"✅ Server Response: {response.status_code}")
    print(f"📄 Content-Length: {len(response.text)} chars")
    
    if "Enhanced Kelpie Carbon Dashboard" in response.text:
        print("✅ Enhanced Title: Found")
    else:
        print("❌ Enhanced Title: Missing")
    
    if "/assets/index-w8fYw47q.js" in response.text:
        print("✅ JavaScript Bundle: Correctly referenced")
    else:
        print("❌ JavaScript Bundle: Wrong reference")
        
    if "/assets/index-BB8Xwy15.css" in response.text:
        print("✅ CSS Bundle: Correctly referenced")
    else:
        print("❌ CSS Bundle: Wrong reference")
    
    # Test assets
    js_response = requests.get("http://localhost:8090/assets/index-w8fYw47q.js", timeout=5)
    css_response = requests.get("http://localhost:8090/assets/index-BB8Xwy15.css", timeout=5)
    
    print(f"📦 JavaScript: {js_response.status_code} ({len(js_response.text):,} chars)")
    print(f"🎨 CSS: {css_response.status_code} ({len(css_response.text):,} chars)")
    
    if all([response.status_code == 200, js_response.status_code == 200, css_response.status_code == 200]):
        print("\n🎉 SUCCESS! Enhanced Dashboard is Ready!")
        print("🌐 Access: http://localhost:8090")
        print("💡 Clear browser cache if needed (Ctrl+Shift+R)")
    else:
        print("\n❌ Some issues detected")
        
except Exception as e:
    print(f"❌ Error: {e}") 