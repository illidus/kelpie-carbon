#!/usr/bin/env python3
"""
Live API Test - Tests the deployed Kelpie Carbon API on Render

This script tests all endpoints of the live API to ensure deployment is working.
"""

import requests
import json
import time
from datetime import datetime

# Live API URL
API_BASE_URL = "https://kelpie-carbon.onrender.com"

def test_root_endpoint():
    """Test the root endpoint for basic API info."""
    print("🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint working!")
            print(f"   API Message: {data.get('message', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
            print(f"   Docs: {data.get('docs', 'N/A')}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_health_endpoint():
    """Test the health check endpoint."""
    print("\n🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint working!")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Model Loaded: {data.get('model_loaded', 'N/A')}")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_analyze_endpoint():
    """Test the carbon analysis endpoint with sample data."""
    print("\n🧪 Testing carbon analysis endpoint...")
    
    # Test data - using the correct API format with date and WKT polygon
    test_date = "2024-06-01"
    # Simple square polygon representing ~100 hectares around Victoria BC
    test_polygon = "POLYGON((-123.3656 48.4284, -123.3556 48.4284, -123.3556 48.4184, -123.3656 48.4184, -123.3656 48.4284))"
    
    try:
        print(f"Testing with date: {test_date}")
        print(f"Polygon: {test_polygon}")
        
        # Use GET with query parameters as per the API design
        response = requests.get(
            f"{API_BASE_URL}/carbon",
            params={
                "date": test_date,
                "aoi": test_polygon
            },
            timeout=30  # Analysis might take a bit longer
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis endpoint working!")
            print(f"   Date: {data.get('date', 'N/A')}")
            print(f"   Area (m²): {data.get('area_m2', 'N/A'):,}")
            print(f"   Mean FAI: {data.get('mean_fai', 'N/A'):.4f}")
            print(f"   Mean NDRE: {data.get('mean_ndre', 'N/A'):.4f}")
            print(f"   Biomass (tonnes): {data.get('biomass_t', 'N/A'):,.2f}")
            print(f"   Carbon (tonnes CO₂): {data.get('co2e_t', 'N/A'):,.2f}")
            return True
        else:
            print(f"❌ Analysis endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Analysis endpoint error: {e}")
        return False

def test_docs_endpoint():
    """Test that the docs endpoint is accessible."""
    print("\n📚 Testing documentation endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Documentation accessible!")
            print(f"   URL: {API_BASE_URL}/docs")
            return True
        else:
            print(f"❌ Documentation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Documentation error: {e}")
        return False

def main():
    """Run all API tests."""
    print("🌊 Kelpie Carbon API - Live Deployment Test")
    print("=" * 50)
    print(f"Testing API at: {API_BASE_URL}")
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Root Endpoint", test_root_endpoint),
        ("Health Check", test_health_endpoint),
        ("Documentation", test_docs_endpoint),
        ("Carbon Analysis", test_analyze_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        if test_func():
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your API is fully functional!")
        print(f"\n🌐 Your API is live at: {API_BASE_URL}")
        print(f"📖 Interactive docs: {API_BASE_URL}/docs")
        print(f"💚 Health check: {API_BASE_URL}/health")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 