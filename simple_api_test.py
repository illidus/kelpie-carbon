"""
Simple API Test - Quick diagnosis
"""

def test_basic_connection():
    """Test basic API connection"""
    try:
        import requests
        print("✅ Requests library available")
        
        # Test basic connection
        print("🔍 Testing http://localhost:8000/health")
        response = requests.get("http://localhost:8000/health", timeout=3)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return True
        
    except ImportError:
        print("❌ Requests library not available")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_with_curl():
    """Alternative test using curl if available"""
    import subprocess
    try:
        print("🔍 Testing with curl...")
        result = subprocess.run(['curl', 'http://localhost:8000/health'], 
                              capture_output=True, text=True, timeout=5)
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"❌ Curl test failed: {e}")

if __name__ == "__main__":
    print("🔍 Simple API Test")
    print("==================")
    
    if not test_basic_connection():
        print("\n🔄 Trying alternative method...")
        test_with_curl()
    
    print("\n💡 If you see connection errors, the API server isn't running.")
    print("💡 If you see HTML instead of JSON, that's your dashboard problem!") 