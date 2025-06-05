#!/usr/bin/env python3
"""
Quick API Test Runner for Enhanced Kelp Carbon API

Run this script anytime to verify your enhanced API features are working.
"""

import sys
import subprocess
from datetime import datetime

def run_test_suite(test_type="focused"):
    """Run the specified test suite."""
    print("🌊 Kelp Carbon API - Test Runner")
    print("=" * 50)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if test_type == "focused":
        print("Running focused test suite (quick verification)...")
        result = subprocess.run([sys.executable, "test_enhanced_clean.py"], 
                              capture_output=False, text=True)
        return result.returncode == 0
        
    elif test_type == "comprehensive":
        print("Running comprehensive test suite (detailed analysis)...")
        result = subprocess.run([sys.executable, "tests/test_enhanced_features.py"], 
                              capture_output=False, text=True)
        return result.returncode == 0
        
    elif test_type == "basic":
        print("Running basic functionality test...")
        result = subprocess.run([sys.executable, "test_enhanced_api.py"], 
                              capture_output=False, text=True)
        return result.returncode == 0
    
    else:
        print(f"Unknown test type: {test_type}")
        return False

def main():
    """Main test runner with options."""
    print("🧪 Enhanced API Test Options:")
    print("1. Focused Test (recommended) - Quick verification of key features")
    print("2. Comprehensive Test - Detailed unittest analysis")  
    print("3. Basic Test - Original enhanced features test")
    print("4. All Tests - Run everything")
    print()
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("Choose test type (1-4, or press Enter for focused): ").strip() or "1"
    
    success = True
    
    if choice == "1":
        success = run_test_suite("focused")
    elif choice == "2":
        success = run_test_suite("comprehensive")
    elif choice == "3":
        success = run_test_suite("basic")
    elif choice == "4":
        print("Running all test suites...")
        print("\n" + "="*50)
        print("1. FOCUSED TEST SUITE")
        print("="*50)
        success1 = run_test_suite("focused")
        
        print("\n" + "="*50)
        print("2. COMPREHENSIVE TEST SUITE")
        print("="*50)
        success2 = run_test_suite("comprehensive")
        
        print("\n" + "="*50)
        print("3. BASIC TEST SUITE")
        print("="*50)
        success3 = run_test_suite("basic")
        
        success = success1 and success2 and success3
        
        print("\n" + "="*50)
        print("OVERALL RESULTS")
        print("="*50)
        print(f"Focused Test: {'✅ PASS' if success1 else '❌ FAIL'}")
        print(f"Comprehensive Test: {'✅ PASS' if success2 else '❌ FAIL'}")
        print(f"Basic Test: {'✅ PASS' if success3 else '❌ FAIL'}")
    else:
        print("Invalid choice. Running focused test...")
        success = run_test_suite("focused")
    
    print("\n" + "="*50)
    print("TEST RUNNER SUMMARY")
    print("="*50)
    if success:
        print("🎉 TESTS PASSED - Enhanced API features working!")
        print("✅ Your kelp carbon analysis API is ready for use")
        print("🌐 API URL: https://kelpie-carbon.onrender.com")
        print("📚 Docs: https://kelpie-carbon.onrender.com/docs")
    else:
        print("⚠️  Some tests failed - check output above")
        print("📝 See TEST_RESULTS_SUMMARY.md for detailed analysis")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 