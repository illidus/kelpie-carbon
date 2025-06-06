#!/usr/bin/env python3
"""
Test suite to diagnose the HTTP server issue with serving wrong index.html files
"""

import os
import sys
import requests
import subprocess
import time
import threading
from pathlib import Path

class ServerDiagnosticTests:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dashboard_dir = self.project_root / "dashboard"
        self.dist_dir = self.dashboard_dir / "dist"
        self.server_process = None
        self.test_port = 8084
        
    def test_1_directory_structure(self):
        """Test 1: Check directory structure and file existence"""
        print("🔍 TEST 1: Directory Structure Analysis")
        print("=" * 50)
        
        # Check if directories exist
        dirs_to_check = [
            self.dashboard_dir,
            self.dist_dir,
            self.dist_dir / "assets"
        ]
        
        for dir_path in dirs_to_check:
            exists = dir_path.exists()
            print(f"📁 {dir_path.relative_to(self.project_root)}: {'✅ EXISTS' if exists else '❌ MISSING'}")
        
        # Check for index.html files
        index_files = [
            self.dashboard_dir / "index.html",
            self.dist_dir / "index.html"
        ]
        
        print("\n📄 Index.html Files:")
        for index_file in index_files:
            if index_file.exists():
                print(f"✅ {index_file.relative_to(self.project_root)}")
                with open(index_file, 'r') as f:
                    content = f.read()
                    if '/src/main.jsx' in content:
                        print(f"   📌 Contains: /src/main.jsx (DEVELOPMENT)")
                    elif '/assets/' in content:
                        print(f"   📌 Contains: /assets/ references (BUILT)")
                    else:
                        print(f"   📌 Contains: Unknown references")
            else:
                print(f"❌ {index_file.relative_to(self.project_root)}")
        
        # List dist directory contents
        if self.dist_dir.exists():
            print(f"\n📂 Contents of {self.dist_dir.relative_to(self.project_root)}:")
            for item in self.dist_dir.iterdir():
                if item.is_file():
                    print(f"   📄 {item.name} ({item.stat().st_size} bytes)")
                elif item.is_dir():
                    print(f"   📁 {item.name}/ ({len(list(item.iterdir()))} items)")
        
        print("\n" + "=" * 50)
        
    def test_2_file_contents(self):
        """Test 2: Compare index.html file contents"""
        print("🔍 TEST 2: Index.html Content Analysis")
        print("=" * 50)
        
        dev_index = self.dashboard_dir / "index.html"
        built_index = self.dist_dir / "index.html"
        
        for name, file_path in [("DEVELOPMENT", dev_index), ("BUILT", built_index)]:
            if file_path.exists():
                print(f"\n📄 {name} - {file_path.relative_to(self.project_root)}:")
                with open(file_path, 'r') as f:
                    content = f.read()
                    lines = content.strip().split('\n')
                    for i, line in enumerate(lines, 1):
                        if any(keyword in line for keyword in ['src=', 'href=', 'title']):
                            print(f"   {i:2d}: {line.strip()}")
            else:
                print(f"❌ {name} file not found")
        
        print("\n" + "=" * 50)
    
    def start_test_server(self):
        """Start HTTP server for testing"""
        print("🚀 Starting test server...")
        
        # Change to dist directory
        os.chdir(self.dist_dir)
        
        # Start server
        self.server_process = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(self.test_port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        time.sleep(2)
        print(f"✅ Server started on port {self.test_port}")
        
    def stop_test_server(self):
        """Stop the test server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 Server stopped")
    
    def test_3_http_responses(self):
        """Test 3: Check HTTP responses"""
        print("🔍 TEST 3: HTTP Response Analysis")
        print("=" * 50)
        
        base_url = f"http://localhost:{self.test_port}"
        
        # Test URLs
        test_urls = [
            "/",
            "/index.html",
            "/dashboard/",
            "/vite.svg",
            "/assets/"
        ]
        
        for url in test_urls:
            try:
                response = requests.get(f"{base_url}{url}", timeout=5)
                print(f"\n🌐 GET {url}")
                print(f"   Status: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
                print(f"   Content-Length: {len(response.text)} chars")
                
                # Check for specific patterns in HTML responses
                if response.headers.get('content-type', '').startswith('text/html'):
                    content = response.text
                    if '/src/main.jsx' in content:
                        print("   📌 Contains: /src/main.jsx (DEVELOPMENT VERSION)")
                    elif '/assets/' in content:
                        print("   📌 Contains: /assets/ references (BUILT VERSION)")
                    elif '<title>' in content:
                        title_start = content.find('<title>') + 7
                        title_end = content.find('</title>')
                        title = content[title_start:title_end]
                        print(f"   📌 Title: {title}")
                    
                    # Check if it's a directory listing
                    if 'Directory listing' in content or '<ul>' in content:
                        print("   📌 Type: Directory listing")
                
            except requests.exceptions.RequestException as e:
                print(f"\n🌐 GET {url}")
                print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 50)
    
    def test_4_working_directory_check(self):
        """Test 4: Check current working directory and server behavior"""
        print("🔍 TEST 4: Working Directory Analysis")
        print("=" * 50)
        
        print(f"Current working directory: {os.getcwd()}")
        print(f"Expected directory: {self.dist_dir}")
        print(f"Match: {'✅ YES' if Path(os.getcwd()) == self.dist_dir else '❌ NO'}")
        
        # List current directory contents
        print(f"\nContents of current directory:")
        for item in Path('.').iterdir():
            if item.is_file():
                print(f"   📄 {item.name}")
            elif item.is_dir():
                print(f"   📁 {item.name}/")
        
        print("\n" + "=" * 50)
    
    def test_5_path_resolution(self):
        """Test 5: Test path resolution issues"""
        print("🔍 TEST 5: Path Resolution Analysis")
        print("=" * 50)
        
        # Test different path combinations
        test_paths = [
            ".",
            "./index.html",
            "./dashboard/",
            "./dashboard/index.html",
            "../index.html"
        ]
        
        for path in test_paths:
            full_path = Path(path).resolve()
            exists = full_path.exists()
            print(f"Path: {path:<20} → {full_path} {'✅' if exists else '❌'}")
            
            if exists and full_path.is_file() and full_path.name == 'index.html':
                with open(full_path, 'r') as f:
                    content = f.read()
                    if '/src/main.jsx' in content:
                        print(f"   📌 Type: DEVELOPMENT")
                    elif '/assets/' in content:
                        print(f"   📌 Type: BUILT")
        
        print("\n" + "=" * 50)
    
    def run_all_tests(self):
        """Run all diagnostic tests"""
        print("🧪 KELPIE CARBON SERVER DIAGNOSTIC TESTS")
        print("=" * 60)
        
        try:
            # Tests that don't require server
            self.test_1_directory_structure()
            self.test_2_file_contents()
            
            # Start server for HTTP tests
            self.start_test_server()
            
            # Tests that require server
            self.test_4_working_directory_check()
            self.test_5_path_resolution()
            self.test_3_http_responses()
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
        finally:
            self.stop_test_server()
            
        print("\n🏁 DIAGNOSTIC TESTS COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    # Change to project root
    os.chdir(Path(__file__).parent)
    
    # Run tests
    tester = ServerDiagnosticTests()
    tester.run_all_tests() 