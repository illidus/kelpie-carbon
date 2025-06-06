#!/usr/bin/env python3
import requests

try:
    response = requests.get("http://localhost:8090/", timeout=10)
    print("CONTENT BEING SERVED:")
    print("=" * 60)
    print(response.text)
    print("=" * 60)
    print(f"Length: {len(response.text)} chars")
except Exception as e:
    print(f"Error: {e}") 