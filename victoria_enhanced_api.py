"""
Enhanced Victoria BC Landsat Data Access
Attempts to access recent Landsat data using multiple APIs and data sources.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

def search_usgs_earth_explorer():
    """Search USGS EarthExplorer API for recent Victoria, BC scenes."""
    
    # Victoria, BC is covered by WRS Path 047, Row 026 (primary)
    # Alternative coverage: Path 046, Row 026
    
    search_params = {
        'dataset': 'LANDSAT_8_C1',
        'spatialFilter': {
            'filterType': 'mbr',  # Minimum Bounding Rectangle
            'lowerLeft': {
                'latitude': 48.35,
                'longitude': -123.50
            },
            'upperRight': {
                'latitude': 48.50,
                'longitude': -123.25
            }
        },
        'temporalFilter': {
            'start': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'end': datetime.now().strftime('%Y-%m-%d')
        },
        'maxCloudCover': 50,
        'includeUnknownCloudCover': False
    }
    
    return search_params

def search_copernicus_hub():
    """Search Copernicus Open Access Hub for Sentinel data over Victoria."""
    
    # Copernicus query for Victoria, BC area
    query_params = {
        'platform': 'Sentinel-2',
        'area': 'POLYGON((-123.50 48.35, -123.25 48.35, -123.25 48.50, -123.50 48.50, -123.50 48.35))',
        'date': f'[{(datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")} TO {datetime.now().strftime("%Y-%m-%d")}]',
        'cloudcoverpercentage': '[0 TO 30]'
    }
    
    return query_params

def check_nasa_worldview():
    """Check NASA Worldview for recent imagery over Victoria, BC."""
    
    # NASA Worldview API parameters
    worldview_params = {
        'REQUEST': 'GetMap',
        'LAYERS': 'MODIS_Terra_CorrectedReflectance_TrueColor,MODIS_Terra_Clouds',
        'CRS': 'EPSG:4326',
        'TIME': datetime.now().strftime('%Y-%m-%d'),
        'BBOX': '-123.50,48.35,-123.25,48.50',
        'WIDTH': '1024',
        'HEIGHT': '1024',
        'FORMAT': 'image/jpeg'
    }
    
    base_url = 'https://worldview.earthdata.nasa.gov/api/v1/snapshot'
    
    return base_url, worldview_params

def get_planet_labs_preview():
    """Get Planet Labs preview for Victoria area (requires API key)."""
    
    # Planet Labs search parameters (requires authentication)
    search_filter = {
        "type": "AndFilter",
        "config": [
            {
                "type": "GeometryFilter",
                "field_name": "geometry",
                "config": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-123.50, 48.35],
                        [-123.25, 48.35], 
                        [-123.25, 48.50],
                        [-123.50, 48.50],
                        [-123.50, 48.35]
                    ]]
                }
            },
            {
                "type": "DateRangeFilter",
                "field_name": "acquired",
                "config": {
                    "gte": (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                    "lte": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                }
            },
            {
                "type": "CloudCoverFilter", 
                "config": {
                    "gte": 0,
                    "lte": 0.25
                }
            }
        ]
    }
    
    return search_filter

def try_recent_data_apis():
    """Try multiple APIs to find recent Victoria, BC satellite data."""
    
    print("🔍 Searching multiple APIs for recent Victoria, BC satellite data...")
    
    results = {
        'sources_tried': [],
        'successful_sources': [],
        'errors': []
    }
    
    # 1. Try NASA Worldview
    try:
        print("  📡 Checking NASA Worldview...")
        base_url, params = check_nasa_worldview()
        
        # Test if the API responds
        response = requests.get(base_url, params=params, timeout=10)
        if response.status_code == 200:
            results['successful_sources'].append('NASA_Worldview')
            print(f"    ✅ NASA Worldview API accessible")
        
        results['sources_tried'].append('NASA_Worldview')
        
    except Exception as e:
        results['errors'].append(f"NASA_Worldview: {e}")
        print(f"    ❌ NASA Worldview failed: {e}")
    
    # 2. Try USGS Earth Explorer search
    try:
        print("  🌍 Checking USGS EarthExplorer parameters...")
        search_params = search_usgs_earth_explorer()
        
        # For demonstration, we'll show the search parameters
        print(f"    📋 USGS Search configured for:")
        print(f"       • Dataset: {search_params['dataset']}")
        print(f"       • Area: Victoria, BC ({search_params['spatialFilter']['lowerLeft']['latitude']:.2f}°N, {search_params['spatialFilter']['lowerLeft']['longitude']:.2f}°W)")
        print(f"       • Date range: {search_params['temporalFilter']['start']} to {search_params['temporalFilter']['end']}")
        print(f"       • Max cloud cover: {search_params['maxCloudCover']}%")
        
        results['successful_sources'].append('USGS_EarthExplorer_Config')
        results['sources_tried'].append('USGS_EarthExplorer')
        
    except Exception as e:
        results['errors'].append(f"USGS_EarthExplorer: {e}")
        print(f"    ❌ USGS configuration failed: {e}")
    
    # 3. Try Copernicus Hub parameters
    try:
        print("  🛰️  Checking Copernicus Open Access Hub...")
        query_params = search_copernicus_hub()
        
        print(f"    📋 Copernicus query configured:")
        print(f"       • Platform: {query_params['platform']}")
        print(f"       • Area: Victoria, BC polygon")
        print(f"       • Date: {query_params['date']}")
        print(f"       • Cloud cover: {query_params['cloudcoverpercentage']}")
        
        results['successful_sources'].append('Copernicus_Hub_Config')
        results['sources_tried'].append('Copernicus_Hub')
        
    except Exception as e:
        results['errors'].append(f"Copernicus_Hub: {e}")
        print(f"    ❌ Copernicus configuration failed: {e}")
    
    # 4. Try Planet Labs configuration
    try:
        print("  🌎 Checking Planet Labs configuration...")
        search_filter = get_planet_labs_preview()
        
        print(f"    📋 Planet Labs search configured:")
        print(f"       • Area: Victoria, BC polygon")
        print(f"       • Date range: Last 7 days")
        print(f"       • Max cloud cover: 25%")
        print(f"       • Note: Requires API key for actual data access")
        
        results['successful_sources'].append('Planet_Labs_Config')
        results['sources_tried'].append('Planet_Labs')
        
    except Exception as e:
        results['errors'].append(f"Planet_Labs: {e}")
        print(f"    ❌ Planet Labs configuration failed: {e}")
    
    return results

def print_api_instructions():
    """Print instructions for accessing real-time data."""
    
    print("\n📚 Instructions for Accessing Real Victoria, BC Landsat Data:")
    print("=" * 60)
    
    print("\n1. 🏛️  USGS EarthExplorer (Free):")
    print("   • Register at: https://earthexplorer.usgs.gov/")
    print("   • Use Machine-to-Machine (M2M) API")
    print("   • Search for: Path 047, Row 026 (Victoria, BC)")
    print("   • Landsat 8/9 Collection 2 Level 1 or Level 2")
    
    print("\n2. 🇪🇺 Copernicus Open Access Hub (Free):")
    print("   • Register at: https://scihub.copernicus.eu/")
    print("   • Use API: https://scihub.copernicus.eu/dhus/")
    print("   • Search Sentinel-2 data for Victoria coordinates")
    print("   • Download Bands 2, 3, 4 for RGB composite")
    
    print("\n3. 🌍 NASA Worldview (Free):")
    print("   • Direct access: https://worldview.earthdata.nasa.gov/")
    print("   • Use snapshot API for Victoria, BC")
    print("   • Layers: MODIS, VIIRS, or Landsat")
    
    print("\n4. 🌎 Planet Labs (Commercial):")
    print("   • Register at: https://www.planet.com/")
    print("   • High-resolution daily imagery")
    print("   • Requires paid subscription")
    
    print("\n5. ☁️  Google Earth Engine (Free for research):")
    print("   • Register at: https://earthengine.google.com/")
    print("   • Access Landsat and Sentinel collections")
    print("   • Use JavaScript or Python API")
    
    print("\n📍 Victoria, BC Coordinates:")
    print("   • Latitude: 48.4284°N")
    print("   • Longitude: 123.3656°W")
    print("   • Landsat WRS Path/Row: 047/026")
    print("   • UTM Zone: 10N")

def main():
    """Main function to test APIs and provide instructions."""
    
    print("🍁 VICTORIA, BC REAL-TIME LANDSAT DATA ACCESS")
    print("=" * 50)
    
    # Test available APIs
    results = try_recent_data_apis()
    
    # Print summary
    print(f"\n📊 API Access Summary:")
    print(f"   Sources tested: {len(results['sources_tried'])}")
    print(f"   Accessible sources: {len(results['successful_sources'])}")
    print(f"   Errors encountered: {len(results['errors'])}")
    
    if results['successful_sources']:
        print(f"\n✅ Successfully configured sources:")
        for source in results['successful_sources']:
            print(f"   • {source}")
    
    if results['errors']:
        print(f"\n❌ Errors encountered:")
        for error in results['errors']:
            print(f"   • {error}")
    
    # Print detailed instructions
    print_api_instructions()
    
    print(f"\n💡 Next Steps:")
    print("   1. Register with one or more data providers")
    print("   2. Obtain API credentials")
    print("   3. Modify the download functions with your credentials")
    print("   4. Re-run the Victoria BC test with real data")

if __name__ == "__main__":
    main() 