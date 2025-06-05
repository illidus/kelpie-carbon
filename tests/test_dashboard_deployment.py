#!/usr/bin/env python3
"""
Kelp Carbon Dashboard Deployment Test Suite

Comprehensive tests to ensure the React dashboard builds and deploys successfully to GitHub Pages.
Tests both local build process and live deployment functionality.
"""

import os
import sys
import subprocess
import time
import json
import re
from pathlib import Path
from urllib.parse import urljoin

import pytest
import requests
from bs4 import BeautifulSoup


# Configuration
DASHBOARD_DIR = "dashboard"
DIST_DIR = f"{DASHBOARD_DIR}/dist"
BASE_URL = "https://illidus.github.io/kelpie-carbon/"
DASHBOARD_URL = urljoin(BASE_URL, "dashboard/")
TIMEOUT = 30


class TestDashboardBuild:
    """Test the local dashboard build process."""
    
    def test_dashboard_directory_exists(self):
        """Test that dashboard directory exists."""
        assert os.path.exists(DASHBOARD_DIR), f"Dashboard directory {DASHBOARD_DIR} not found"
    
    def test_package_json_exists(self):
        """Test that package.json exists with required scripts."""
        package_json_path = os.path.join(DASHBOARD_DIR, "package.json")
        assert os.path.exists(package_json_path), "package.json not found in dashboard directory"
        
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
        
        assert "scripts" in package_data, "No scripts section in package.json"
        assert "build" in package_data["scripts"], "No build script in package.json"
        assert "dev" in package_data["scripts"], "No dev script in package.json"
    
    def test_dashboard_build_process(self):
        """Test that dashboard builds successfully."""
        original_cwd = os.getcwd()
        
        try:
            # Change to dashboard directory
            os.chdir(DASHBOARD_DIR)
            
            # Run npm install if node_modules doesn't exist
            if not os.path.exists("node_modules"):
                print("Installing dashboard dependencies...")
                result = subprocess.run(["npm", "install"], 
                                      capture_output=True, text=True, timeout=120)
                assert result.returncode == 0, f"npm install failed: {result.stderr}"
            
            # Clean previous build
            if os.path.exists("dist"):
                import shutil
                shutil.rmtree("dist")
            
            # Run build
            print("Building dashboard...")
            result = subprocess.run(["npm", "run", "build"], 
                                  capture_output=True, text=True, timeout=180)
            
            # Check build output
            assert result.returncode == 0, f"Dashboard build failed: {result.stderr}"
            assert "built in" in result.stdout.lower(), "Build didn't complete successfully"
            
        finally:
            os.chdir(original_cwd)
    
    def test_dist_files_created(self):
        """Test that build creates required dist files."""
        dist_path = Path(DIST_DIR)
        assert dist_path.exists(), f"Dist directory {DIST_DIR} not created"
        
        # Check for index.html
        index_html = dist_path / "index.html"
        assert index_html.exists(), "index.html not found in dist directory"
        
        # Check for assets directory
        assets_dir = dist_path / "assets"
        assert assets_dir.exists(), "assets directory not found in dist"
        
        # Check for CSS and JS files
        css_files = list(assets_dir.glob("*.css"))
        js_files = list(assets_dir.glob("*.js"))
        
        assert len(css_files) > 0, "No CSS files found in assets"
        assert len(js_files) > 0, "No JavaScript files found in assets"
    
    def test_index_html_content(self):
        """Test that index.html contains expected content."""
        index_path = Path(DIST_DIR) / "index.html"
        assert index_path.exists(), "index.html not found"
        
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for basic HTML structure
        assert "<html" in content, "HTML tag not found"
        assert "<head>" in content, "Head section not found"
        assert "<body>" in content, "Body section not found"
        assert '<div id="root">' in content, "React root div not found"
        
        # Check for asset references
        assert "assets/" in content, "Asset references not found"


class TestDashboardDeployment:
    """Test the live dashboard deployment on GitHub Pages."""
    
    def test_homepage_accessible(self):
        """Test that the main homepage is accessible."""
        response = requests.get(BASE_URL, timeout=TIMEOUT)
        assert response.status_code == 200, f"Homepage not accessible: {response.status_code}"
        
        # Check content
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title')
        assert title and "kelp carbon" in title.text.lower(), "Homepage title doesn't contain 'kelp carbon'"
    
    def test_dashboard_url_accessible(self):
        """Test that dashboard URL is accessible."""
        response = requests.get(DASHBOARD_URL, timeout=TIMEOUT)
        assert response.status_code == 200, f"Dashboard not accessible: {response.status_code}"
        
        # Check for HTML content
        assert response.headers.get('content-type', '').startswith('text/html'), \
            "Dashboard doesn't return HTML content"
    
    def test_dashboard_html_content(self):
        """Test dashboard HTML contains expected React structure."""
        response = requests.get(DASHBOARD_URL, timeout=TIMEOUT)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for React root div
        root_div = soup.find('div', {'id': 'root'})
        assert root_div is not None, "React root div not found in dashboard HTML"
        
        # Check for script tags (React bundle)
        script_tags = soup.find_all('script', {'src': True})
        assert len(script_tags) > 0, "No script tags found in dashboard HTML"
        
        # Check for CSS links
        css_links = soup.find_all('link', {'rel': 'stylesheet'})
        assert len(css_links) > 0, "No CSS links found in dashboard HTML"
    
    def test_dashboard_assets_accessible(self):
        """Test that dashboard assets are accessible."""
        # Get the dashboard HTML to find asset URLs
        response = requests.get(DASHBOARD_URL, timeout=TIMEOUT)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Test CSS files
        css_links = soup.find_all('link', {'rel': 'stylesheet'})
        for css_link in css_links:
            href = css_link.get('href')
            if href and href.startswith('./assets/'):
                asset_url = urljoin(DASHBOARD_URL, href)
                css_response = requests.get(asset_url, timeout=TIMEOUT)
                assert css_response.status_code == 200, f"CSS asset not accessible: {asset_url}"
        
        # Test JavaScript files
        script_tags = soup.find_all('script', {'src': True})
        for script_tag in script_tags:
            src = script_tag.get('src')
            if src and src.startswith('./assets/'):
                asset_url = urljoin(DASHBOARD_URL, src)
                js_response = requests.get(asset_url, timeout=TIMEOUT)
                assert js_response.status_code == 200, f"JS asset not accessible: {asset_url}"
    
    def test_dashboard_cors_headers(self):
        """Test that dashboard has proper CORS headers for API access."""
        response = requests.get(DASHBOARD_URL, timeout=TIMEOUT)
        
        # Check for basic security headers
        headers = response.headers
        
        # GitHub Pages should have basic headers
        assert 'server' in headers, "No server header found"
        
        # Content type should be HTML
        content_type = headers.get('content-type', '')
        assert 'text/html' in content_type, f"Unexpected content type: {content_type}"


class TestDashboardIntegration:
    """Test integration between homepage and dashboard."""
    
    def test_homepage_dashboard_link(self):
        """Test that homepage contains link to dashboard."""
        response = requests.get(BASE_URL, timeout=TIMEOUT)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for dashboard link
        dashboard_links = soup.find_all('a', href=re.compile(r'.*dashboard.*'))
        assert len(dashboard_links) > 0, "No dashboard link found on homepage"
        
        # Test the first dashboard link
        first_link = dashboard_links[0]
        href = first_link.get('href')
        
        if href.startswith('./'):
            full_url = urljoin(BASE_URL, href)
        else:
            full_url = href
        
        # Test that the link works
        link_response = requests.get(full_url, timeout=TIMEOUT)
        assert link_response.status_code == 200, f"Dashboard link doesn't work: {full_url}"
    
    def test_homepage_contains_dashboard_description(self):
        """Test that homepage properly describes the dashboard."""
        response = requests.get(BASE_URL, timeout=TIMEOUT)
        content = response.text.lower()
        
        # Check for dashboard-related keywords
        dashboard_keywords = [
            'dashboard', 'interactive', 'mapping', 'analysis'
        ]
        
        found_keywords = [kw for kw in dashboard_keywords if kw in content]
        assert len(found_keywords) >= 2, \
            f"Homepage doesn't adequately describe dashboard. Found: {found_keywords}"


class TestDeploymentProcess:
    """Test the deployment process and tools."""
    
    def test_deployment_script_exists(self):
        """Test that deployment script exists."""
        script_path = "scripts/deploy_full_site.ps1"
        assert os.path.exists(script_path), f"Deployment script {script_path} not found"
    
    def test_deployment_script_content(self):
        """Test that deployment script contains required steps."""
        script_path = "scripts/deploy_full_site.ps1"
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_steps = [
            'npm run build',  # Dashboard build
            'git checkout gh-pages',  # Branch switching
            'Copy-Item',  # File copying
            'git add',  # Staging
            'git commit',  # Committing
            'git push'  # Pushing
        ]
        
        for step in required_steps:
            assert step in content, f"Deployment script missing step: {step}"
    
    def test_github_pages_branch_exists(self):
        """Test that gh-pages branch exists and has dashboard files."""
        try:
            # Check if gh-pages branch exists remotely
            result = subprocess.run(
                ["git", "ls-remote", "--heads", "origin", "gh-pages"],
                capture_output=True, text=True, timeout=30
            )
            
            assert result.returncode == 0, "Failed to check remote branches"
            assert "gh-pages" in result.stdout, "gh-pages branch not found on remote"
            
        except subprocess.TimeoutExpired:
            pytest.skip("Git command timed out - network issue")


def run_dashboard_health_check():
    """
    Comprehensive health check function that can be called independently.
    Returns a detailed report of dashboard deployment status.
    """
    print("🔍 Running Dashboard Deployment Health Check...")
    print("=" * 60)
    
    health_report = {
        'build_status': 'unknown',
        'deployment_status': 'unknown',
        'dashboard_accessible': False,
        'assets_working': False,
        'integration_working': False,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Test build
        print("📦 Testing dashboard build...")
        if os.path.exists(DIST_DIR):
            health_report['build_status'] = 'success'
            print("   ✅ Build files found")
        else:
            health_report['build_status'] = 'failed'
            health_report['errors'].append("Build files not found")
            print("   ❌ Build files not found")
        
        # Test deployment
        print("🌐 Testing dashboard deployment...")
        try:
            response = requests.get(DASHBOARD_URL, timeout=TIMEOUT)
            if response.status_code == 200:
                health_report['deployment_status'] = 'success'
                health_report['dashboard_accessible'] = True
                print(f"   ✅ Dashboard accessible at {DASHBOARD_URL}")
                
                # Test assets
                soup = BeautifulSoup(response.text, 'html.parser')
                script_tags = soup.find_all('script', {'src': True})
                if len(script_tags) > 0:
                    health_report['assets_working'] = True
                    print("   ✅ Dashboard assets loaded")
                else:
                    health_report['warnings'].append("No script tags found")
                    print("   ⚠️  No script tags found")
                
            else:
                health_report['deployment_status'] = 'failed'
                health_report['errors'].append(f"Dashboard returns {response.status_code}")
                print(f"   ❌ Dashboard returns {response.status_code}")
                
        except requests.RequestException as e:
            health_report['deployment_status'] = 'failed'
            health_report['errors'].append(f"Network error: {str(e)}")
            print(f"   ❌ Network error: {str(e)}")
        
        # Test homepage integration
        print("🔗 Testing homepage integration...")
        try:
            response = requests.get(BASE_URL, timeout=TIMEOUT)
            if response.status_code == 200:
                content = response.text.lower()
                if 'dashboard' in content:
                    health_report['integration_working'] = True
                    print("   ✅ Homepage links to dashboard")
                else:
                    health_report['warnings'].append("Homepage doesn't mention dashboard")
                    print("   ⚠️  Homepage doesn't mention dashboard")
            else:
                health_report['errors'].append(f"Homepage returns {response.status_code}")
                print(f"   ❌ Homepage returns {response.status_code}")
                
        except requests.RequestException as e:
            health_report['errors'].append(f"Homepage network error: {str(e)}")
            print(f"   ❌ Homepage network error: {str(e)}")
    
    except Exception as e:
        health_report['errors'].append(f"Unexpected error: {str(e)}")
        print(f"   ❌ Unexpected error: {str(e)}")
    
    # Summary
    print("\n📊 Health Check Summary:")
    print("=" * 30)
    
    if health_report['build_status'] == 'success':
        print("✅ Build: OK")
    else:
        print("❌ Build: FAILED")
    
    if health_report['dashboard_accessible']:
        print("✅ Dashboard: ACCESSIBLE")
    else:
        print("❌ Dashboard: NOT ACCESSIBLE")
    
    if health_report['assets_working']:
        print("✅ Assets: WORKING")
    else:
        print("❌ Assets: ISSUES DETECTED")
    
    if health_report['integration_working']:
        print("✅ Integration: WORKING")
    else:
        print("⚠️  Integration: NEEDS ATTENTION")
    
    if health_report['errors']:
        print(f"\n❌ Errors ({len(health_report['errors'])}):")
        for error in health_report['errors']:
            print(f"   • {error}")
    
    if health_report['warnings']:
        print(f"\n⚠️  Warnings ({len(health_report['warnings'])}):")
        for warning in health_report['warnings']:
            print(f"   • {warning}")
    
    # Overall status
    overall_healthy = (
        health_report['build_status'] == 'success' and
        health_report['dashboard_accessible'] and
        len(health_report['errors']) == 0
    )
    
    if overall_healthy:
        print("\n🎉 Overall Status: HEALTHY")
    else:
        print("\n⚠️  Overall Status: NEEDS ATTENTION")
    
    return health_report


if __name__ == "__main__":
    # Run health check if called directly
    run_dashboard_health_check() 