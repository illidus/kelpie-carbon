"""
Result Mapping for Kelp Carbon Analysis

This module creates map visualizations of carbon analysis results,
showing the analyzed area with biomass and carbon sequestration data.
"""

import os
import io
import base64
import numpy as np
from typing import Optional, Dict, Any, Tuple
import json

# Try to import mapping libraries with better error handling
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.colors import LinearSegmentedColormap
    MATPLOTLIB_AVAILABLE = True
    print("✅ Matplotlib loaded successfully")
except ImportError as e:
    MATPLOTLIB_AVAILABLE = False
    print(f"⚠️  Matplotlib not available: {e}")

try:
    import folium
    from folium import plugins
    FOLIUM_AVAILABLE = True
    print("✅ Folium loaded successfully")
except ImportError as e:
    FOLIUM_AVAILABLE = False
    print(f"⚠️  Folium not available: {e}")

def create_result_map(
    aoi_wkt: str, 
    analysis_results: Dict[str, Any],
    map_type: str = "static"
) -> Optional[Dict[str, Any]]:
    """
    Create a map visualization of carbon analysis results.
    
    Args:
        aoi_wkt: WKT polygon string defining the analyzed area
        analysis_results: Results from carbon analysis including biomass, CO2, etc.
        map_type: "static" for matplotlib image, "interactive" for folium HTML, "geojson" for simple data
        
    Returns:
        Dictionary containing map data or None if creation failed
    """
    
    try:
        # Parse WKT polygon to get coordinates
        coords = parse_wkt_polygon(aoi_wkt)
        if not coords:
            return {
                "type": f"{map_type}_map",
                "success": False,
                "error": "Could not parse WKT polygon"
            }
        
        if map_type == "static" and MATPLOTLIB_AVAILABLE:
            return create_static_map(coords, analysis_results)
        elif map_type == "interactive" and FOLIUM_AVAILABLE:
            return create_interactive_map(coords, analysis_results)
        else:
            # Always fall back to GeoJSON which doesn't require external libraries
            return create_simple_geojson_map(coords, analysis_results)
            
    except Exception as e:
        return {
            "type": f"{map_type}_map",
            "success": False,
            "error": f"Map creation failed: {str(e)}"
        }

def parse_wkt_polygon(wkt: str) -> Optional[list]:
    """Parse WKT polygon string to extract coordinates."""
    try:
        import re
        coords_match = re.search(r'POLYGON\s*\(\s*\((.*?)\)\s*\)', wkt)
        if not coords_match:
            return None
            
        coords_str = coords_match.group(1)
        coordinates = []
        
        for pair in coords_str.split(','):
            lon, lat = map(float, pair.strip().split())
            coordinates.append([lon, lat])
        
        return coordinates
        
    except Exception as e:
        print(f"WKT parsing error: {e}")
        return None

def create_static_map(coords: list, results: Dict[str, Any]) -> Dict[str, Any]:
    """Create a static matplotlib map of the analysis results."""
    try:
        # Extract key metrics
        area_m2 = results.get("area_m2", 0)
        biomass_t = results.get("biomass_t", 0)
        co2e_t = results.get("co2e_t", 0)
        
        # Calculate center and bounds
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        center_lon, center_lat = np.mean(lons), np.mean(lats)
        
        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        
        # Set up the map area with some padding
        lon_range = max(lons) - min(lons)
        lat_range = max(lats) - min(lats)
        padding = max(lon_range, lat_range) * 0.1
        
        ax.set_xlim(min(lons) - padding, max(lons) + padding)
        ax.set_ylim(min(lats) - padding, max(lats) + padding)
        
        # Add background (simple ocean color)
        ax.set_facecolor('#e6f3ff')  # Light blue for water
        
        # Draw the analyzed area
        polygon = patches.Polygon(
            coords, 
            linewidth=3, 
            edgecolor='darkgreen', 
            facecolor='green', 
            alpha=0.6,
            label='Analyzed Kelp Area'
        )
        ax.add_patch(polygon)
        
        # Add biomass density visualization
        biomass_density = biomass_t / (area_m2 / 10000) if area_m2 > 0 else 0  # tonnes per hectare
        
        # Color intensity based on biomass density
        if biomass_density > 50:
            color_intensity = 0.9
        elif biomass_density > 20:
            color_intensity = 0.7
        elif biomass_density > 10:
            color_intensity = 0.5
        else:
            color_intensity = 0.3
            
        # Add center point with biomass info
        ax.plot(center_lon, center_lat, 'o', markersize=15, 
                color='red', markeredgecolor='white', markeredgewidth=2,
                label='Analysis Center')
        
        # Add title and information
        ax.set_title(
            f'Kelp Carbon Analysis Results\n'
            f'Victoria, BC - {results.get("date", "Unknown Date")}',
            fontsize=16, fontweight='bold', pad=20
        )
        
        # Add results text box
        info_text = f"""Analysis Results:
        
Area: {area_m2/10000:.1f} hectares
Biomass: {biomass_t:.1f} tonnes
Carbon Sequestration: {co2e_t:.1f} tonnes CO₂
Biomass Density: {biomass_density:.1f} tonnes/hectare

Spectral Indices:
FAI: {results.get('mean_fai', 0):.3f}
NDRE: {results.get('mean_ndre', 0):.3f}"""

        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', 
                facecolor='white', alpha=0.9), fontsize=10)
        
        # Add legend and labels
        ax.legend(loc='lower right')
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Convert to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            "type": "static_map",
            "image_base64": image_base64,
            "center": [center_lat, center_lon],
            "bounds": [[min(lats), min(lons)], [max(lats), max(lons)]],
            "success": True
        }
        
    except Exception as e:
        print(f"Static map creation error: {e}")
        return {"type": "static_map", "success": False, "error": str(e)}

def create_interactive_map(coords: list, results: Dict[str, Any]) -> Dict[str, Any]:
    """Create an interactive folium map of the analysis results."""
    try:
        # Calculate center
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        center_lat, center_lon = np.mean(lats), np.mean(lons)
        
        # Create folium map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        # Add satellite tile layer option
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Convert coords to lat,lon format for folium
        folium_coords = [[lat, lon] for lon, lat in coords]
        
        # Add the analyzed area polygon
        biomass_t = results.get("biomass_t", 0)
        co2e_t = results.get("co2e_t", 0)
        
        # Color based on biomass density
        area_ha = results.get("area_m2", 0) / 10000
        biomass_density = biomass_t / area_ha if area_ha > 0 else 0
        
        if biomass_density > 50:
            color = 'darkgreen'
        elif biomass_density > 20:
            color = 'green'
        elif biomass_density > 10:
            color = 'lightgreen'
        else:
            color = 'yellow'
        
        # Add polygon
        folium.Polygon(
            locations=folium_coords,
            popup=f"""
            <b>Kelp Carbon Analysis</b><br>
            Area: {area_ha:.1f} hectares<br>
            Biomass: {biomass_t:.1f} tonnes<br>
            CO₂ Sequestration: {co2e_t:.1f} tonnes<br>
            Density: {biomass_density:.1f} t/ha<br>
            FAI: {results.get('mean_fai', 0):.3f}<br>
            NDRE: {results.get('mean_ndre', 0):.3f}
            """,
            tooltip="Click for analysis details",
            color='blue',
            weight=2,
            fillColor=color,
            fillOpacity=0.6
        ).add_to(m)
        
        # Add center marker
        folium.Marker(
            location=[center_lat, center_lon],
            popup=f"Analysis Center<br>Date: {results.get('date', 'Unknown')}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Convert to HTML string
        html_string = m._repr_html_()
        
        return {
            "type": "interactive_map",
            "html": html_string,
            "center": [center_lat, center_lon],
            "bounds": [[min(lats), min(lons)], [max(lats), max(lons)]],
            "success": True
        }
        
    except Exception as e:
        print(f"Interactive map creation error: {e}")
        return {"type": "interactive_map", "success": False, "error": str(e)}

def create_simple_geojson_map(coords: list, results: Dict[str, Any]) -> Dict[str, Any]:
    """Create a simple GeoJSON representation when mapping libraries aren't available."""
    try:
        # Close the polygon if not already closed
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [coords]
                    },
                    "properties": {
                        "name": "Kelp Analysis Area",
                        "area_hectares": results.get("area_m2", 0) / 10000,
                        "biomass_tonnes": results.get("biomass_t", 0),
                        "co2_tonnes": results.get("co2e_t", 0),
                        "date": results.get("date", "unknown"),
                        "mean_fai": results.get("mean_fai", 0),
                        "mean_ndre": results.get("mean_ndre", 0)
                    }
                }
            ]
        }
        
        # Calculate bounds
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        
        return {
            "type": "geojson_map",
            "geojson": geojson,
            "center": [np.mean(lats), np.mean(lons)],
            "bounds": [[min(lats), min(lons)], [max(lats), max(lons)]],
            "success": True
        }
        
    except Exception as e:
        print(f"GeoJSON map creation error: {e}")
        return {"type": "geojson_map", "success": False, "error": str(e)} 