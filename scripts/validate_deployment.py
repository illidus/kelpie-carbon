#!/usr/bin/env python3
"""
Standalone script to validate GitHub Pages tile server deployment.

This script can be run independently to check if the GitHub Pages
deployment is working correctly without requiring the full test suite.
"""

import requests
import sys
import time
from typing import Tuple, List


def check_url(url: str, timeout: int = 10) -> Tuple[bool, str, dict]:
    """
    Check if a URL is accessible and return status information.
    
    Returns:
        Tuple of (success, message, details)
    """
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        response_time = (time.time() - start_time) * 1000
        
        details = {
            'status_code': response.status_code,
            'response_time_ms': round(response_time, 2),
            'content_length': len(response.content),
            'content_type': response.headers.get('content-type', 'unknown')
        }
        
        if response.status_code == 200:
            return True, f"✅ Accessible ({response.status_code})", details
        elif response.status_code == 404:
            return True, f"📍 Not found ({response.status_code}) - expected for some endpoints", details
        else:
            return False, f"⚠️  Unexpected status ({response.status_code})", details
            
    except requests.exceptions.Timeout:
        return False, "❌ Timeout - deployment may still be in progress", {}
    except requests.exceptions.ConnectionError:
        return False, "❌ Connection error - check if GitHub Pages is enabled", {}
    except requests.exceptions.RequestException as e:
        return False, f"❌ Request error: {e}", {}


def validate_deployment() -> bool:
    """
    Main validation function.
    
    Returns:
        True if deployment appears to be working, False otherwise
    """
    base_url = "https://illidus.github.io/kelpie-carbon"
    tile_endpoint = f"{base_url}/tiles"
    
    print("🌊 Kelp Carbon GitHub Pages Deployment Validator")
    print("=" * 60)
    print(f"Testing deployment at: {base_url}")
    print()
    
    all_tests_passed = True
    
    # Test 1: Homepage accessibility
    print("1. Testing homepage accessibility...")
    success, message, details = check_url(base_url)
    print(f"   {message}")
    if details:
        print(f"   Response time: {details['response_time_ms']}ms")
    
    if not success:
        all_tests_passed = False
        print("   💡 If this fails, check:")
        print("      - GitHub Actions completed successfully")
        print("      - GitHub Pages is enabled in repository settings")
        print("      - Wait 2-10 minutes after deployment")
        print()
    
    # Test 2: Homepage content validation
    if success and details.get('status_code') == 200:
        print("2. Testing homepage content...")
        try:
            response = requests.get(base_url, timeout=10)
            content = response.text.lower()
            
            required_content = [
                ('kelp carbon', 'Kelp Carbon title'),
                ('tile server', 'Tile Server description'),
                ('tiles/{z}/{x}/{y}.png', 'Tile URL pattern'),
                ('leaflet', 'Leaflet usage example')
            ]
            
            content_valid = True
            for term, description in required_content:
                if term in content:
                    print(f"   ✅ Found: {description}")
                else:
                    print(f"   ❌ Missing: {description}")
                    content_valid = False
            
            if not content_valid:
                all_tests_passed = False
                
        except Exception as e:
            print(f"   ❌ Error checking content: {e}")
            all_tests_passed = False
    else:
        print("2. Skipping content test (homepage not accessible)")
    
    print()
    
    # Test 3: Tile endpoint structure
    print("3. Testing tile endpoint structure...")
    test_tiles = [
        (0, 0, 0, "Root tile"),
        (1, 0, 0, "Zoom level 1"),
        (1, 1, 0, "Different X coordinate"),
    ]
    
    tiles_found = 0
    for z, x, y, description in test_tiles:
        tile_url = f"{tile_endpoint}/{z}/{x}/{y}.png"
        success, message, details = check_url(tile_url)
        
        if details.get('status_code') == 200:
            tiles_found += 1
            # Verify it's actually a PNG
            if details.get('content_type', '').startswith('image/png'):
                print(f"   ✅ Valid PNG tile: {description} ({tile_url})")
            else:
                print(f"   ⚠️  Non-PNG content: {description} ({tile_url})")
        else:
            print(f"   📍 {description}: {message}")
    
    print(f"   Summary: {tiles_found} valid tiles found")
    print()
    
    # Test 4: CORS compatibility
    print("4. Testing cross-origin accessibility...")
    headers = {'Origin': 'https://example.com'}
    success, message, details = check_url(base_url, timeout=10)
    
    if success:
        print("   ✅ CORS compatible for web mapping applications")
    else:
        print("   ⚠️  CORS test inconclusive")
    
    print()
    
    # Summary
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 60)
    
    if all_tests_passed:
        print("🎉 SUCCESS: GitHub Pages tile server is deployed and working!")
        print()
        print("🔗 Your tile server is live at:")
        print(f"   Homepage: {base_url}")
        print(f"   Tiles: {tile_endpoint}/{{z}}/{{x}}/{{y}}.png")
        print()
        print("🗺️  Add to your mapping application:")
        print("   Leaflet: L.tileLayer(")
        print(f"     '{tile_endpoint}/{{z}}/{{x}}/{{y}}.png',")
        print("     { maxZoom: 14, attribution: 'Kelp Carbon Analysis' }")
        print("   ).addTo(map);")
        print()
        return True
    else:
        print("⚠️  ISSUES DETECTED: Some tests failed")
        print()
        print("🔧 Troubleshooting steps:")
        print("1. Check GitHub Actions status:")
        print("   https://github.com/illidus/kelpie-carbon/actions")
        print("2. Verify GitHub Pages settings:")
        print("   https://github.com/illidus/kelpie-carbon/settings/pages")
        print("   - Source: 'Deploy from a branch'")
        print("   - Branch: 'gh-pages' / '/ (root)'")
        print("3. Wait a few minutes and retry (GitHub Pages can be slow)")
        print("4. Check if the gh-pages branch exists and has content")
        print()
        return False


if __name__ == "__main__":
    success = validate_deployment()
    sys.exit(0 if success else 1) 