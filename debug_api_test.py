"""
Debug API Test - Diagnose JSON parsing issues
"""
import requests
import json
from typing import Optional

def test_api_endpoint(url: str, description: str) -> None:
    """Test an API endpoint and show detailed response info"""
    print(f"\n🔍 Testing {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        print(f"📋 Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"📏 Content Length: {len(response.text)} chars")
        
        # Show first 200 chars of response
        preview = response.text[:200].replace('\n', '\\n')
        print(f"👀 Response Preview: {preview}...")
        
        # Try to parse as JSON
        try:
            json_data = response.json()
            print(f"✅ Valid JSON Response: {json_data}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print("🔍 This explains your dashboard error!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: API server not running")
    except requests.exceptions.Timeout:
        print("❌ Timeout: API server not responding")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def test_carbon_analysis_endpoint() -> None:
    """Test the carbon analysis endpoint with sample data"""
    url = "http://localhost:8000/carbon"
    
    # Sample polygon data (small square)
    sample_data = {
        "date": "2023-06-15",
        "polygon_wkt": "POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))"
    }
    
    print(f"\n🧪 Testing Carbon Analysis Endpoint")
    print(f"URL: {url}")
    print(f"Data: {sample_data}")
    
    try:
        response = requests.post(url, json=sample_data, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        print(f"📋 Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        # Show response
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"✅ Carbon Analysis Response: {json.dumps(json_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON Response: {response.text[:500]}")
        else:
            print(f"❌ Error Response: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: API server not running")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_api_server_status() -> None:
    """Check if API server is running"""
    print("🔍 Checking API Server Status...")
    
    # Test different possible endpoints
    endpoints = [
        ("http://localhost:8000/", "Root endpoint"),
        ("http://localhost:8000/health", "Health check"),
        ("http://localhost:8000/docs", "API documentation"),
    ]
    
    for url, description in endpoints:
        test_api_endpoint(url, description)

def main():
    """Run all diagnostic tests"""
    print("🩺 API Diagnostic Test Suite")
    print("=" * 50)
    
    # Check basic server status
    check_api_server_status()
    
    # Test carbon analysis endpoint
    test_carbon_analysis_endpoint()
    
    print("\n📋 Summary:")
    print("If you see 'Connection Error', start the API with: cd api && python main.py")
    print("If you see HTML responses, check the API endpoints in main.py")
    print("If you see JSON parse errors, that's the source of your dashboard issue!")

if __name__ == "__main__":
    main() 