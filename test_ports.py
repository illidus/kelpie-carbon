#!/usr/bin/env python3
"""
Test common development ports to find the running dashboard
"""

import requests
import socket

def test_port(port):
    """Test if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def test_dashboard_ports():
    """Test common development ports for the dashboard"""
    ports = [5173, 4173, 3000, 8080, 5000, 8000]
    
    print("🔍 Checking for running development servers...")
    print("=" * 50)
    
    for port in ports:
        port_open = test_port(port)
        if port_open:
            url = f"http://localhost:{port}"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    html = response.text
                    
                    # Check if it's our enhanced dashboard
                    if "Enhanced kelp biomass estimation" in html or "Enhanced Kelpie Carbon Dashboard" in html:
                        print(f"✅ Port {port}: ENHANCED DASHBOARD FOUND!")
                        print(f"   🌐 URL: {url}")
                        print(f"   📄 Title: Enhanced Kelpie Carbon Dashboard")
                        
                        # Check for enhanced features
                        features = [
                            "Try Real Landsat Data",
                            "Generate Result Map", 
                            "Map Type:",
                            "data-source-badge",
                            "Enhanced"
                        ]
                        
                        feature_count = sum(1 for f in features if f in html)
                        print(f"   🔧 Enhanced Features: {feature_count}/{len(features)}")
                        
                        return port, url
                    elif "react" in html.lower() or "vite" in html.lower() or "root" in html:
                        print(f"⚠️  Port {port}: React/Vite app")
                        print(f"   🌐 URL: {url}")
                        print(f"   📏 Length: {len(html)} chars")
                        
                        # Show a preview of the content
                        if len(html) < 2000:
                            print(f"   📄 Content preview:")
                            print(f"      {html[:200]}...")
                        
                        return port, url  # Return even if not fully enhanced
                    else:
                        print(f"🔍 Port {port}: Web server (unknown app)")
                        print(f"   🌐 URL: {url}")
                        print(f"   📄 Content preview: {html[:100]}...")
                        
                else:
                    print(f"❌ Port {port}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Port {port}: Error - {e}")
        else:
            print(f"⭕ Port {port}: Not open")
    
    return None, None

if __name__ == "__main__":
    print("🌊 Finding Enhanced Dashboard")
    print()
    
    port, url = test_dashboard_ports()
    
    if port:
        print(f"\n🎉 Dashboard found at: {url}")
        print(f"💡 You can now test the enhanced features in your browser!")
    else:
        print(f"\n❌ No dashboard found on common ports")
        print(f"💡 Try manually starting: cd dashboard && npm run dev")
        print(f"💡 Then check what port it reports") 