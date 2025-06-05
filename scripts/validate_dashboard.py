#!/usr/bin/env python3
"""
Dashboard Deployment Validator

Quick validation script for CI/CD pipelines to ensure dashboard deployment success.
Returns exit code 0 for success, 1 for failure.
"""

import sys
import requests
from urllib.parse import urljoin

# Configuration
BASE_URL = "https://illidus.github.io/kelpie-carbon/"
DASHBOARD_URL = urljoin(BASE_URL, "dashboard/")
TIMEOUT = 30


def validate_dashboard():
    """Quick dashboard validation."""
    try:
        print(f"🔍 Validating dashboard at: {DASHBOARD_URL}")
        
        # Test dashboard accessibility
        response = requests.get(DASHBOARD_URL, timeout=TIMEOUT)
        
        if response.status_code != 200:
            print(f"❌ Dashboard not accessible: HTTP {response.status_code}")
            return False
        
        # Check content type
        if not response.headers.get('content-type', '').startswith('text/html'):
            print("❌ Dashboard doesn't return HTML content")
            return False
        
        # Check for React structure
        html_content = response.text
        
        if '<div id="root">' not in html_content:
            print("❌ React root div not found")
            return False
        
        if 'assets/' not in html_content:
            print("❌ Asset references not found")
            return False
        
        print("✅ Dashboard validation successful")
        return True
        
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False


def main():
    """Main validation function."""
    print("🧪 Quick Dashboard Validation")
    print("=" * 40)
    
    success = validate_dashboard()
    
    if success:
        print("\n🎉 VALIDATION PASSED")
        sys.exit(0)
    else:
        print("\n❌ VALIDATION FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main() 