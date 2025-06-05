#!/usr/bin/env python3
"""
Run local API server and test the dashboard functionality.

This script starts the FastAPI server locally and runs tests against it.
"""

import subprocess
import time
import sys
import os
import requests
import signal
from contextlib import contextmanager

def start_api_server():
    """Start the FastAPI server."""
    print("🚀 Starting FastAPI server...")
    
    # Add current directory to Python path
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()
    
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "localhost", "--port", "8000"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        for i in range(30):
            try:
                response = requests.get("http://localhost:8000/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Server started successfully!")
                    return process
            except:
                time.sleep(1)
                if i % 5 == 0:
                    print(f"   Still waiting... ({i+1}/30 seconds)")
        
        # If we get here, server failed to start
        process.terminate()
        stdout, stderr = process.communicate()
        print(f"❌ Server failed to start")
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
        return None
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def test_api_endpoints():
    """Test the API endpoints."""
    print("\n🧪 Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    test_polygon = "POLYGON((-123.4 48.4, -123.3 48.4, -123.3 48.5, -123.4 48.5, -123.4 48.4))"
    test_date = "2024-07-15"
    
    tests = [
        {
            "name": "Health Check",
            "url": f"{base_url}/health",
            "expected_fields": ["status", "model_loaded", "timestamp"]
        },
        {
            "name": "API Info",
            "url": f"{base_url}/api",
            "expected_fields": ["message", "version", "endpoints"]
        },
        {
            "name": "Carbon Analysis",
            "url": f"{base_url}/carbon?date={test_date}&aoi={test_polygon}",
            "expected_fields": ["date", "aoi_wkt", "area_m2", "mean_fai", "mean_ndre", "biomass_t", "co2e_t"]
        }
    ]
    
    results = []
    
    for test in tests:
        try:
            print(f"\n  Testing {test['name']}...")
            response = requests.get(test["url"], timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                missing_fields = []
                for field in test["expected_fields"]:
                    if field not in data:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"    ⚠️  Missing fields: {missing_fields}")
                    results.append(False)
                else:
                    print(f"    ✅ All fields present")
                    
                    # Print some key results for carbon analysis
                    if "biomass_t" in data:
                        print(f"       Area: {data.get('area_m2', 0):,.0f} m²")
                        print(f"       Biomass: {data.get('biomass_t', 0):.2f} tonnes")
                        print(f"       CO₂ Sequestered: {data.get('co2e_t', 0):.2f} tonnes")
                    
                    results.append(True)
            else:
                print(f"    ❌ HTTP {response.status_code}: {response.text}")
                results.append(False)
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            results.append(False)
    
    return all(results)

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n🧪 Testing edge cases...")
    
    base_url = "http://localhost:8000"
    
    edge_tests = [
        {
            "name": "Invalid Date",
            "url": f"{base_url}/carbon?date=invalid&aoi=POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            "expected_status": 400
        },
        {
            "name": "Invalid WKT",
            "url": f"{base_url}/carbon?date=2024-01-01&aoi=INVALID",
            "expected_status": 400
        },
        {
            "name": "Missing Parameters",
            "url": f"{base_url}/carbon",
            "expected_status": 422
        }
    ]
    
    results = []
    
    for test in edge_tests:
        try:
            print(f"\n  Testing {test['name']}...")
            response = requests.get(test["url"], timeout=5)
            
            if response.status_code == test["expected_status"]:
                print(f"    ✅ Correctly returned HTTP {response.status_code}")
                results.append(True)
            else:
                print(f"    ⚠️  Expected {test['expected_status']}, got {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            results.append(False)
    
    return all(results)

def main():
    """Main function to run the local test suite."""
    print("🔬 LOCAL DASHBOARD API TEST SUITE")
    print("=" * 50)
    
    # Start the server
    server_process = start_api_server()
    if not server_process:
        print("❌ Cannot start server, exiting...")
        return False
    
    try:
        # Run tests
        api_test_passed = test_api_endpoints()
        edge_test_passed = test_edge_cases()
        
        # Summary
        print("\n📊 TEST RESULTS")
        print("=" * 20)
        print(f"API Endpoints: {'✅ PASS' if api_test_passed else '❌ FAIL'}")
        print(f"Edge Cases: {'✅ PASS' if edge_test_passed else '❌ FAIL'}")
        
        overall_success = api_test_passed and edge_test_passed
        print(f"\nOverall: {'🎉 SUCCESS' if overall_success else '💥 FAILURE'}")
        
        if overall_success:
            print("\n💡 Next Steps:")
            print("  - The API is working correctly!")
            print("  - You can now test the dashboard UI at http://localhost:8000")
            print("  - Try drawing polygons and running analysis")
            print("  - For UI testing, install Selenium and run tests/test_dashboard_analysis.py")
        
        return overall_success
        
    finally:
        # Clean up
        print("\n🧹 Cleaning up...")
        server_process.terminate()
        server_process.wait()
        print("✅ Server stopped")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 