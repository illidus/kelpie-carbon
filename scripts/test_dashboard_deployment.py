#!/usr/bin/env python3
"""
Simple Dashboard Deployment Test

Standalone test script to verify that the dashboard deploys successfully.
Tests build process, GitHub Pages deployment, and functionality.
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("⚠️  Missing dependencies. Install with: pip install requests beautifulsoup4")


# Configuration
DASHBOARD_DIR = "dashboard"
DIST_DIR = f"{DASHBOARD_DIR}/dist"
BASE_URL = "https://illidus.github.io/kelpie-carbon/"
DASHBOARD_URL = urljoin(BASE_URL, "dashboard/")
TIMEOUT = 30


def test_build_process():
    """Test the dashboard build process."""
    print("🔨 Testing Dashboard Build Process...")
    
    results = {
        'directory_exists': False,
        'package_json_valid': False,
        'build_successful': False,
        'dist_files_created': False,
        'errors': []
    }
    
    # Check dashboard directory
    if not os.path.exists(DASHBOARD_DIR):
        results['errors'].append(f"Dashboard directory {DASHBOARD_DIR} not found")
        return results
    
    results['directory_exists'] = True
    print(f"   ✅ Dashboard directory found: {DASHBOARD_DIR}")
    
    # Check package.json
    package_json_path = os.path.join(DASHBOARD_DIR, "package.json")
    if not os.path.exists(package_json_path):
        results['errors'].append("package.json not found")
        return results
    
    try:
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
        
        if "scripts" not in package_data or "build" not in package_data["scripts"]:
            results['errors'].append("package.json missing build script")
            return results
        
        results['package_json_valid'] = True
        print("   ✅ Valid package.json with build script")
        
    except Exception as e:
        results['errors'].append(f"Error reading package.json: {str(e)}")
        return results
    
    # Test build process
    original_cwd = os.getcwd()
    try:
        os.chdir(DASHBOARD_DIR)
        
        # Check if we need to install dependencies
        if not os.path.exists("node_modules"):
            print("   📥 Installing dependencies...")
            result = subprocess.run(["npm", "install"], 
                                  capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                results['errors'].append(f"npm install failed: {result.stderr}")
                return results
        
        # Clean previous build
        if os.path.exists("dist"):
            import shutil
            shutil.rmtree("dist")
        
        # Run build
        print("   🏗️  Building dashboard...")
        result = subprocess.run(["npm", "run", "build"], 
                              capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0 and "built in" in result.stdout.lower():
            results['build_successful'] = True
            print("   ✅ Build completed successfully")
        else:
            results['errors'].append(f"Build failed: {result.stderr}")
            return results
        
    except subprocess.TimeoutExpired:
        results['errors'].append("Build process timed out")
        return results
    except Exception as e:
        results['errors'].append(f"Build error: {str(e)}")
        return results
    finally:
        os.chdir(original_cwd)
    
    # Check dist files
    dist_path = Path(DIST_DIR)
    if not dist_path.exists():
        results['errors'].append(f"Dist directory {DIST_DIR} not created")
        return results
    
    index_html = dist_path / "index.html"
    assets_dir = dist_path / "assets"
    
    if not index_html.exists():
        results['errors'].append("index.html not found in dist")
        return results
    
    if not assets_dir.exists():
        results['errors'].append("assets directory not found")
        return results
    
    css_files = list(assets_dir.glob("*.css"))
    js_files = list(assets_dir.glob("*.js"))
    
    if len(css_files) == 0:
        results['errors'].append("No CSS files found in assets")
        return results
    
    if len(js_files) == 0:
        results['errors'].append("No JavaScript files found in assets")
        return results
    
    results['dist_files_created'] = True
    print(f"   ✅ Dist files created: {len(css_files)} CSS, {len(js_files)} JS files")
    
    return results


def test_live_deployment():
    """Test the live GitHub Pages deployment."""
    print("🌐 Testing Live Deployment...")
    
    if not DEPENDENCIES_AVAILABLE:
        print("   ❌ Cannot test live deployment - missing requests/beautifulsoup4")
        return {'accessible': False, 'errors': ['Missing dependencies']}
    
    results = {
        'homepage_accessible': False,
        'dashboard_accessible': False,
        'assets_working': False,
        'integration_working': False,
        'errors': []
    }
    
    try:
        # Test homepage
        print(f"   🔍 Testing homepage: {BASE_URL}")
        response = requests.get(BASE_URL, timeout=TIMEOUT)
        if response.status_code == 200:
            results['homepage_accessible'] = True
            print("   ✅ Homepage accessible")
            
            # Check for dashboard links
            if 'dashboard' in response.text.lower():
                results['integration_working'] = True
                print("   ✅ Homepage mentions dashboard")
            else:
                results['errors'].append("Homepage doesn't mention dashboard")
        else:
            results['errors'].append(f"Homepage returns {response.status_code}")
    
    except requests.RequestException as e:
        results['errors'].append(f"Homepage error: {str(e)}")
    
    try:
        # Test dashboard
        print(f"   🔍 Testing dashboard: {DASHBOARD_URL}")
        response = requests.get(DASHBOARD_URL, timeout=TIMEOUT)
        if response.status_code == 200:
            results['dashboard_accessible'] = True
            print("   ✅ Dashboard accessible")
            
            # Check HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for React root
            root_div = soup.find('div', {'id': 'root'})
            if root_div:
                print("   ✅ React root div found")
            else:
                results['errors'].append("React root div not found")
            
            # Check for script tags
            script_tags = soup.find_all('script', {'src': True})
            if len(script_tags) > 0:
                results['assets_working'] = True
                print(f"   ✅ {len(script_tags)} script tags found")
            else:
                results['errors'].append("No script tags found")
            
            # Test asset accessibility
            asset_errors = 0
            for script_tag in script_tags[:2]:  # Test first 2 assets
                src = script_tag.get('src')
                if src and src.startswith('./assets/'):
                    asset_url = urljoin(DASHBOARD_URL, src)
                    try:
                        asset_response = requests.get(asset_url, timeout=10)
                        if asset_response.status_code != 200:
                            asset_errors += 1
                    except:
                        asset_errors += 1
            
            if asset_errors == 0:
                print("   ✅ Dashboard assets accessible")
            else:
                results['errors'].append(f"{asset_errors} assets not accessible")
                
        else:
            results['errors'].append(f"Dashboard returns {response.status_code}")
    
    except requests.RequestException as e:
        results['errors'].append(f"Dashboard error: {str(e)}")
    
    return results


def test_deployment_infrastructure():
    """Test deployment infrastructure and scripts."""
    print("🛠️  Testing Deployment Infrastructure...")
    
    results = {
        'deployment_script_exists': False,
        'gh_pages_branch_exists': False,
        'errors': []
    }
    
    # Check deployment script
    script_path = "scripts/deploy_full_site.ps1"
    if os.path.exists(script_path):
        results['deployment_script_exists'] = True
        print(f"   ✅ Deployment script found: {script_path}")
        
        # Check script content
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_steps = ['npm run build', 'git checkout gh-pages', 'Copy-Item', 'git add', 'git commit', 'git push']
        missing_steps = [step for step in required_steps if step not in content]
        
        if missing_steps:
            results['errors'].append(f"Deployment script missing steps: {missing_steps}")
        else:
            print("   ✅ Deployment script contains all required steps")
    else:
        results['errors'].append(f"Deployment script not found: {script_path}")
    
    # Check gh-pages branch
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", "origin", "gh-pages"],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0 and "gh-pages" in result.stdout:
            results['gh_pages_branch_exists'] = True
            print("   ✅ gh-pages branch exists on remote")
        else:
            results['errors'].append("gh-pages branch not found on remote")
    
    except subprocess.TimeoutExpired:
        results['errors'].append("Git command timed out")
    except Exception as e:
        results['errors'].append(f"Git error: {str(e)}")
    
    return results


def run_comprehensive_test():
    """Run all tests and provide a comprehensive report."""
    print("🧪 Running Comprehensive Dashboard Deployment Test")
    print("=" * 60)
    
    # Run all tests
    build_results = test_build_process()
    deployment_results = test_live_deployment()
    infrastructure_results = test_deployment_infrastructure()
    
    # Compile overall results
    all_errors = (
        build_results.get('errors', []) + 
        deployment_results.get('errors', []) + 
        infrastructure_results.get('errors', [])
    )
    
    print("\n📊 Test Summary")
    print("=" * 30)
    
    # Build status
    if build_results.get('build_successful') and build_results.get('dist_files_created'):
        print("✅ Build: PASSING")
    else:
        print("❌ Build: FAILING")
    
    # Deployment status
    if deployment_results.get('dashboard_accessible') and deployment_results.get('assets_working'):
        print("✅ Live Deployment: PASSING")
    else:
        print("❌ Live Deployment: FAILING")
    
    # Infrastructure status
    if infrastructure_results.get('deployment_script_exists') and infrastructure_results.get('gh_pages_branch_exists'):
        print("✅ Infrastructure: PASSING")
    else:
        print("❌ Infrastructure: FAILING")
    
    # Overall assessment
    critical_checks = [
        deployment_results.get('dashboard_accessible', False),
        deployment_results.get('assets_working', False),
        infrastructure_results.get('gh_pages_branch_exists', False)
    ]
    
    if all(critical_checks):
        print("\n🎉 Overall: DASHBOARD DEPLOYMENT SUCCESSFUL")
        success = True
    else:
        print("\n⚠️  Overall: DASHBOARD DEPLOYMENT NEEDS ATTENTION")
        success = False
    
    # Error details
    if all_errors:
        print(f"\n❌ Issues Found ({len(all_errors)}):")
        for i, error in enumerate(all_errors, 1):
            print(f"   {i}. {error}")
    
    # URLs for reference
    print(f"\n🔗 Deployment URLs:")
    print(f"   Homepage: {BASE_URL}")
    print(f"   Dashboard: {DASHBOARD_URL}")
    
    return success, {
        'build': build_results,
        'deployment': deployment_results,
        'infrastructure': infrastructure_results,
        'overall_success': success,
        'total_errors': len(all_errors)
    }


if __name__ == "__main__":
    success, results = run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1) 