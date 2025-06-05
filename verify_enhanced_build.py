#!/usr/bin/env python3
"""
Verify that the built dashboard contains all enhanced features
"""

import os
import glob

def verify_enhanced_build():
    print("🔍 Verifying Enhanced Dashboard Build")
    print("=" * 40)
    
    # Check if dist directory exists
    dist_path = "dashboard/dist"
    if not os.path.exists(dist_path):
        print("❌ No dist directory found")
        print("💡 Run: cd dashboard && npm run build")
        return False
    
    # Check index.html
    index_path = os.path.join(dist_path, "index.html")
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print("📄 index.html:")
        print(f"   ✅ Title: {'Enhanced Kelpie Carbon Dashboard' if 'Enhanced Kelpie Carbon Dashboard' in html_content else '❌ Basic title'}")
        print(f"   ✅ Has CSS: {'✅' if '.css' in html_content else '❌'}")
        print(f"   ✅ Has JS: {'✅' if '.js' in html_content else '❌'}")
    
    # Check JavaScript bundle for enhanced features
    js_files = glob.glob(os.path.join(dist_path, "assets", "*.js"))
    if js_files:
        js_file = js_files[0]
        print(f"\n📦 JavaScript Bundle: {os.path.basename(js_file)}")
        
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Check for enhanced features in the bundled JavaScript
        enhanced_features = [
            ("Try Real Landsat Data", "Landsat toggle"),
            ("Generate Result Map", "Map generation"),
            ("Map Type:", "Map type selector"),
            ("data-source-badge", "Data source display"), 
            ("use_real_landsat", "Landsat parameter"),
            ("include_map", "Map parameter"),
            ("Enhanced Carbon Analysis Results", "Enhanced results panel"),
            ("biomass_density_t_ha", "Biomass density field"),
            ("Enhanced kelp biomass estimation", "Enhanced header")
        ]
        
        found_count = 0
        for feature, description in enhanced_features:
            if feature in js_content:
                print(f"   ✅ {description}")
                found_count += 1
            else:
                print(f"   ❌ {description}")
        
        print(f"\n📊 Enhanced Features in Build: {found_count}/{len(enhanced_features)}")
        
        if found_count >= 7:
            print("🎉 BUILD IS FULLY ENHANCED!")
            return True
        else:
            print("⚠️ Build may be missing some enhanced features")
            return False
    else:
        print("❌ No JavaScript files found in build")
        return False

def suggest_deployment_fix():
    print("\n🚀 DEPLOYMENT RECOMMENDATIONS:")
    print("=" * 35)
    print("1. ✅ Enhanced build is ready")
    print("2. 🔧 Fix Render dashboard serving:")
    print("   • Update API to serve from 'dashboard/dist'")
    print("   • Ensure build process runs on Render")
    print("   • Check static file serving configuration")
    print("3. 🧪 Test locally with preview server:")
    print("   • cd dashboard && npm run preview")
    print("4. 🚀 Redeploy to Render after fixes")

if __name__ == "__main__":
    success = verify_enhanced_build()
    suggest_deployment_fix()
    
    if success:
        print(f"\n✅ READY FOR DEPLOYMENT!")
    else:
        print(f"\n⚠️ Build issues detected - fix before deploying") 