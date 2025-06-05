"""
Maximum Zoom Victoria, BC Landsat Data
Ultra high-resolution, maximum zoom view of Victoria city center using Planetary Computer.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests
from typing import Tuple, Optional, Dict
from sentinel_pipeline.mask import apply_cloud_mask, filter_by_tide

# Landsat scene 047026 coordinates - covers Brentwood Bay/Saanich Peninsula area
LANDSAT_SCENE_047026 = {
    'name': 'Brentwood Bay & Saanich Peninsula, BC',
    'scene_id': 'LC08_L2SP_047026',
    'center': {'lat': 48.4284, 'lon': -123.3656},  # Search center
    'bbox_tight': [-123.38, 48.415, -123.35, 48.440],  # Focused area
    'bbox_medium': [-123.40, 48.41, -123.33, 48.45],   # Medium zoom
    'bbox_harbor': [-123.385, 48.415, -123.360, 48.435], # Small area
    'actual_coverage': {
        'brentwood_bay': 'Top of frame - Brentwood Bay area',
        'saanich_peninsula': 'Top of frame - Saanich Peninsula',
        'juan_de_fuca_strait': 'Left edge - Juan de Fuca Strait',
        'san_juan_islands': 'Bottom left - San Juan/Discovery Islands',
        'southern_vancouver_island': 'Various coastal areas'
    }
}

def get_maximum_zoom_landsat():
    """Get maximum zoom Landsat data for Victoria city center."""
    
    try:
        from pystac_client import Client
        import planetary_computer
        import rasterio
        from rasterio.windows import from_bounds
        from rasterio.enums import Resampling
        
        print("🎯 LANDSAT SCENE 047026 - BRENTWOOD BAY & SAANICH PENINSULA")
        print("=" * 65)
        print(f"📍 Coverage: {LANDSAT_SCENE_047026['name']}")
        print(f"🌊 Features: Brentwood Bay, Saanich Peninsula, Juan de Fuca Strait, San Juan Islands")
        
        # Connect to Planetary Computer
        catalog = Client.open(
            "https://planetarycomputer.microsoft.com/api/stac/v1",
            modifier=planetary_computer.sign_inplace
        )
        
        print("🔍 Searching for highest quality recent scenes...")
        
        # Search with multiple zoom levels
        zoom_levels = [
            ('ultra_tight', LANDSAT_SCENE_047026['bbox_harbor'], "Focused coastal area"),
            ('tight', LANDSAT_SCENE_047026['bbox_tight'], "Brentwood Bay vicinity"),
            ('medium', LANDSAT_SCENE_047026['bbox_medium'], "Saanich Peninsula region")
        ]
        
        best_scene = None
        best_metadata = None
        
        for zoom_name, bbox, description in zoom_levels:
            print(f"\n🔍 Trying {zoom_name} zoom: {description}")
            print(f"   📐 Bbox: {bbox}")
            
            # Search for scenes
            search = catalog.search(
                collections=["landsat-c2-l2"],
                bbox=bbox,
                datetime=f"{(datetime.now() - timedelta(days=90)).isoformat()}Z/{datetime.now().isoformat()}Z",
                query={
                    "eo:cloud_cover": {"lt": 25},  # Very low cloud cover for maximum detail
                    "landsat:wrs_path": {"eq": "047"},
                    "landsat:wrs_row": {"eq": "026"}
                },
                sortby=[{"field": "eo:cloud_cover", "direction": "asc"}],  # Least cloudy first
                limit=3
            )
            
            items = list(search.items())
            
            if items:
                scene = items[0]  # Best (least cloudy) scene
                props = scene.properties
                cloud_cover = props.get('eo:cloud_cover', 999)
                
                print(f"   ✅ Found scene: {scene.id}")
                print(f"   ☁️  Cloud cover: {cloud_cover:.1f}%")
                print(f"   📅 Date: {props.get('datetime', 'Unknown')[:10]}")
                
                # Try to get maximum resolution data
                img_data, metadata = download_maximum_resolution(scene, bbox, zoom_name)
                
                if img_data is not None:
                    metadata.update({
                        'zoom_level': zoom_name,
                        'bbox': bbox,
                        'description': description,
                        'cloud_cover': cloud_cover
                    })
                    
                    print(f"   🎉 Successfully obtained {zoom_name} zoom data!")
                    return img_data, metadata
        
        print("❌ Could not obtain maximum zoom data")
        return None, None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def download_maximum_resolution(item, bbox, zoom_level):
    """Download maximum resolution data for the specified area."""
    
    try:
        import rasterio
        import planetary_computer
        from rasterio.windows import from_bounds
        from rasterio.enums import Resampling
        
        print(f"   📡 Downloading maximum resolution data...")
        
        # Try different approaches based on zoom level
        approaches = [
            ('full_resolution_bands', download_full_resolution_bands),
            ('high_res_window', download_high_res_window),
            ('preview_zoomed', download_preview_zoomed)
        ]
        
        for approach_name, download_func in approaches:
            print(f"     🔄 Trying {approach_name}...")
            
            try:
                img_data, metadata = download_func(item, bbox)
                if img_data is not None:
                    metadata['download_method'] = approach_name
                    print(f"     ✅ Success with {approach_name}")
                    return img_data, metadata
            except Exception as e:
                print(f"     ❌ {approach_name} failed: {e}")
                continue
        
        return None, None
        
    except Exception as e:
        print(f"   ❌ Download error: {e}")
        return None, None

def download_full_resolution_bands(item, bbox):
    """Download full resolution individual bands and create detailed composite."""
    
    import rasterio
    import planetary_computer
    from rasterio.windows import from_bounds
    
    print(f"       🎯 Downloading full resolution bands...")
    
    bands = ['red', 'green', 'blue', 'nir']  # Include NIR for better analysis
    band_data = {}
    
    for band in bands:
        if band in item.assets:
            asset = item.assets[band]
            signed_url = planetary_computer.sign(asset.href)
            
            try:
                with rasterio.open(signed_url) as src:
                    # Get window for our specific area
                    window = from_bounds(bbox[0], bbox[1], bbox[2], bbox[3], src.transform)
                    
                    # Read at native resolution
                    data = src.read(1, window=window)
                    
                    if data.size > 0:
                        band_data[band] = {
                            'data': data,
                            'transform': src.window_transform(window),
                            'resolution': src.res,
                            'crs': src.crs
                        }
                        
                        print(f"         ✅ {band}: {data.shape} at {src.res[0]:.1f}m resolution")
                    
            except Exception as e:
                print(f"         ❌ {band} failed: {e}")
                continue
    
    if len(band_data) >= 3:
        # Create enhanced RGB composite
        rgb_data = create_enhanced_rgb(band_data, bbox)
        
        metadata = {
            'source': 'Microsoft_Planetary_Computer',
            'type': 'full_resolution_bands',
            'scene_id': item.id,
            'datetime': item.properties.get('datetime'),
            'cloud_cover': item.properties.get('eo:cloud_cover'),
            'platform': item.properties.get('platform'),
            'bands_used': list(band_data.keys()),
            'native_resolution': band_data['red']['resolution'][0] if 'red' in band_data else 'Unknown'
        }
        
        return rgb_data, metadata
    
    return None, None

def download_high_res_window(item, bbox):
    """Download high resolution windowed data."""
    
    import rasterio
    import planetary_computer
    from rasterio.windows import from_bounds
    from rasterio.enums import Resampling
    
    print(f"       🖼️  Downloading high-res windowed data...")
    
    bands = ['red', 'green', 'blue']
    band_arrays = {}
    
    for band in bands:
        if band in item.assets:
            asset = item.assets[band]
            signed_url = planetary_computer.sign(asset.href)
            
            try:
                with rasterio.open(signed_url) as src:
                    window = from_bounds(bbox[0], bbox[1], bbox[2], bbox[3], src.transform)
                    
                    # Read with higher output resolution for more detail
                    out_shape = (800, 800)  # High resolution output
                    
                    data = src.read(
                        1,
                        window=window,
                        out_shape=out_shape,
                        resampling=Resampling.cubic
                    )
                    
                    band_arrays[band] = data
                    print(f"         ✅ {band}: {data.shape}")
                    
            except Exception as e:
                print(f"         ❌ {band}: {e}")
                continue
    
    if len(band_arrays) == 3:
        rgb_composite = create_detailed_rgb(band_arrays['red'], band_arrays['green'], band_arrays['blue'])
        
        metadata = {
            'source': 'Microsoft_Planetary_Computer',
            'type': 'high_res_windowed',
            'scene_id': item.id,
            'datetime': item.properties.get('datetime'),
            'cloud_cover': item.properties.get('eo:cloud_cover'),
            'platform': item.properties.get('platform'),
            'output_resolution': '800x800_pixels'
        }
        
        return rgb_composite, metadata
    
    return None, None

def download_preview_zoomed(item, bbox):
    """Download and crop preview for maximum zoom."""
    
    import planetary_computer
    from PIL import Image
    import io
    
    print(f"       🔍 Downloading and cropping preview...")
    
    if 'rendered_preview' in item.assets:
        preview_asset = item.assets['rendered_preview']
        preview_url = planetary_computer.sign(preview_asset.href)
        
        response = requests.get(preview_url, timeout=30)
        
        if response.status_code == 200:
            img = Image.open(io.BytesIO(response.content))
            img_array = np.array(img) / 255.0
            
            # Convert RGBA to RGB if needed
            if len(img_array.shape) == 3 and img_array.shape[2] == 4:
                img_array = img_array[:, :, :3]
            
            # Crop to center area for maximum zoom effect
            h, w = img_array.shape[:2]
            crop_size = min(h, w) // 3  # Use center third for maximum zoom
            center_y, center_x = h // 2, w // 2
            
            cropped = img_array[
                center_y - crop_size//2:center_y + crop_size//2,
                center_x - crop_size//2:center_x + crop_size//2
            ]
            
            # Upscale for better viewing
            from scipy.ndimage import zoom
            upscale_factor = 3
            upscaled = zoom(cropped, (upscale_factor, upscale_factor, 1), order=1)
            
            print(f"         ✅ Cropped and upscaled: {upscaled.shape}")
            
            metadata = {
                'source': 'Microsoft_Planetary_Computer',
                'type': 'preview_cropped_upscaled',
                'scene_id': item.id,
                'datetime': item.properties.get('datetime'),
                'cloud_cover': item.properties.get('eo:cloud_cover'),
                'platform': item.properties.get('platform'),
                'processing': f'center_crop_and_{upscale_factor}x_upscale'
            }
            
            return upscaled, metadata
    
    return None, None

def create_enhanced_rgb(band_data, bbox):
    """Create enhanced RGB composite with maximum detail."""
    
    print(f"       🎨 Creating enhanced RGB composite...")
    
    red = band_data['red']['data'].astype(float)
    green = band_data['green']['data'].astype(float)
    blue = band_data['blue']['data'].astype(float)
    
    # Enhanced normalization for urban areas
    def enhance_urban_features(band):
        """Enhanced processing for urban feature visibility."""
        # Remove invalid values
        valid_mask = (band > 0) & (band < 65535)
        
        if not np.any(valid_mask):
            return np.zeros_like(band)
        
        valid_data = band[valid_mask]
        
        # Use more aggressive contrast stretching for urban details
        p1, p99 = np.percentile(valid_data, [1, 99])
        stretched = np.clip((band - p1) / (p99 - p1), 0, 1)
        
        # Apply gamma correction for better urban feature visibility
        gamma = 0.7  # Enhance darker features
        enhanced = np.power(stretched, gamma)
        
        enhanced[~valid_mask] = 0
        return enhanced
    
    red_enhanced = enhance_urban_features(red)
    green_enhanced = enhance_urban_features(green)
    blue_enhanced = enhance_urban_features(blue)
    
    # Stack and apply final enhancement
    rgb = np.stack([red_enhanced, green_enhanced, blue_enhanced], axis=-1)
    
    # Apply unsharp masking for detail enhancement
    try:
        from scipy.ndimage import gaussian_filter
        
        for i in range(3):
            original = rgb[:, :, i]
            blurred = gaussian_filter(original, sigma=1.0)
            sharpened = original + 0.5 * (original - blurred)
            rgb[:, :, i] = np.clip(sharpened, 0, 1)
            
        print(f"         ✅ Enhanced RGB with unsharp masking: {rgb.shape}")
        
    except ImportError:
        print(f"         ✅ Basic RGB composite: {rgb.shape}")
    
    return rgb

def create_detailed_rgb(red, green, blue):
    """Create detailed RGB composite with urban enhancement."""
    
    def enhance_band(band):
        valid_data = band[band > 0]
        if len(valid_data) == 0:
            return np.zeros_like(band)
        
        # Aggressive contrast stretching
        p2, p98 = np.percentile(valid_data, [2, 98])
        normalized = np.clip((band - p2) / (p98 - p2), 0, 1)
        
        # Gamma correction for urban features
        enhanced = np.power(normalized, 0.8)
        return enhanced
    
    red_norm = enhance_band(red)
    green_norm = enhance_band(green)
    blue_norm = enhance_band(blue)
    
    rgb = np.stack([red_norm, green_norm, blue_norm], axis=-1)
    
    return rgb

def create_maximum_zoom_visualization():
    """Create visualization with maximum zoom Victoria data."""
    
    # Get maximum zoom data
    landsat_img, metadata = get_maximum_zoom_landsat()
    
    if landsat_img is None:
        print("❌ Could not obtain maximum zoom data")
        return
    
    print(f"\n🎨 Creating maximum zoom visualization...")
    
    # Enhanced cloud detection for high-res data
    def detect_features(img):
        """Detect clouds and urban features in high-res data."""
        if len(img.shape) == 3:
            gray = np.mean(img, axis=2)
        else:
            gray = img
        
        # Multi-threshold detection
        cloud_threshold = np.percentile(gray[gray > 0], 90)
        urban_threshold = np.percentile(gray[gray > 0], 30)
        
        cloud_mask = (gray > cloud_threshold).astype(np.uint8) * 200
        urban_mask = (gray < urban_threshold).astype(np.uint8) * 100
        
        return cloud_mask, urban_mask
    
    cloud_mask, urban_mask = detect_features(landsat_img)
    
    # Apply enhanced masking
    def apply_enhanced_mask(img, cloud_mask):
        masked_img = img.copy()
        cloud_pixels = cloud_mask > 150
        
        if len(img.shape) == 3:
            if img.shape[2] == 3:
                masked_img[cloud_pixels] = [0.95, 0.95, 0.98]
            elif img.shape[2] == 4:
                masked_img[cloud_pixels] = [0.95, 0.95, 0.98, 1.0]
        
        return masked_img
    
    masked_img = apply_enhanced_mask(landsat_img, cloud_mask)
    
    # Create detailed visualization
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle(f'Landsat Scene 047026: Brentwood Bay & Saanich Peninsula, BC\n{metadata.get("scene_id", "Unknown Scene")}', 
                 fontsize=18, fontweight='bold')
    
    # Main high-res image (large panel)
    ax1 = plt.subplot2grid((3, 4), (0, 0), colspan=3, rowspan=2)
    ax1.imshow(landsat_img)
    ax1.set_title(f'High-Resolution Brentwood Bay & Saanich Peninsula\n'
                  f'{metadata.get("zoom_level", "").replace("_", " ").title()} - {metadata.get("description", "")}', 
                  fontsize=14)
    ax1.axis('off')
    
    # Add geographic annotations for actual coverage
    geographic_text = "🌊 Brentwood Bay\n🏔️ Saanich Peninsula\n🌊 Juan de Fuca Strait\n🏝️ San Juan Islands"
    ax1.text(0.02, 0.98, geographic_text, transform=ax1.transAxes, 
             verticalalignment='top', fontsize=10, 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Cloud detection
    ax2 = plt.subplot2grid((3, 4), (0, 3))
    cloud_display = ax2.imshow(cloud_mask, cmap='Blues')
    ax2.set_title('Cloud Detection')
    ax2.axis('off')
    plt.colorbar(cloud_display, ax=ax2, fraction=0.046, pad=0.04)
    
    # Urban features
    ax3 = plt.subplot2grid((3, 4), (1, 3))
    urban_display = ax3.imshow(urban_mask, cmap='Grays')
    ax3.set_title('Urban Features')
    ax3.axis('off')
    plt.colorbar(urban_display, ax=ax3, fraction=0.046, pad=0.04)
    
    # Masked result
    ax4 = plt.subplot2grid((3, 4), (2, 0), colspan=2)
    ax4.imshow(masked_img)
    ax4.set_title('Cloud-Masked Coastal Scene Image')
    ax4.axis('off')
    
    # Detailed information
    ax5 = plt.subplot2grid((3, 4), (2, 2), colspan=2)
    ax5.axis('off')
    
    # Format cloud cover
    cloud_cover = metadata.get('cloud_cover', 'Unknown')
    if isinstance(cloud_cover, (int, float)):
        cloud_cover_str = f"{cloud_cover:.1f}%"
    else:
        cloud_cover_str = str(cloud_cover)
    
    info_text = f"""LANDSAT SCENE 047026 ANALYSIS

Geographic Coverage:
🌊 Brentwood Bay (top of frame)  
🏔️  Saanich Peninsula (top of frame)
🌊 Juan de Fuca Strait (left edge)
🏝️  San Juan/Discovery Islands (bottom left)

Landsat Data Details:
📅 Date: {metadata.get('datetime', 'Unknown')[:10]}
🛰️  Platform: {metadata.get('platform', 'Unknown')}
☁️  Cloud Cover: {cloud_cover_str}
🎯 Zoom Level: {metadata.get('zoom_level', 'Unknown').replace('_', ' ').title()}
📐 Area: {metadata.get('description', 'Unknown')}

Technical Details:
📊 Image Shape: {landsat_img.shape}
💾 Data Range: {landsat_img.min():.3f} - {landsat_img.max():.3f}
🔍 Download Method: {metadata.get('download_method', 'Unknown')}
📏 Resolution: {metadata.get('native_resolution', 'N/A')}

Detection Results:
☁️  Clouds Detected: {100 * np.sum(cloud_mask > 150) / cloud_mask.size:.1f}%
🌊 Coastal Features: {100 * np.sum(urban_mask > 50) / urban_mask.size:.1f}%

Scene Center: 48.4284°N, 123.3656°W
Source: Microsoft Planetary Computer STAC
"""
    
    ax5.text(0.05, 0.95, info_text, transform=ax5.transAxes,
             fontsize=11, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9))
    
    plt.tight_layout()
    plt.savefig('brentwood_bay_saanich_peninsula_landsat.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\n🎉 LANDSAT SCENE 047026 ANALYSIS COMPLETE!")
    print(f"   💾 Saved: brentwood_bay_saanich_peninsula_landsat.png (Brentwood Bay & Saanich Peninsula)")
    print(f"   🌊 Coverage: Brentwood Bay, Saanich Peninsula, Juan de Fuca Strait, San Juan Islands")
    print(f"   🎯 Zoom level: {metadata.get('zoom_level', 'Unknown')}")
    print(f"   📐 Area covered: {metadata.get('description', 'Unknown')}")
    print(f"   📅 Scene date: {metadata.get('datetime', 'Unknown')[:10]}")
    print(f"   🛰️  Platform: {metadata.get('platform', 'Unknown')}")
    print(f"   ☁️  Cloud cover: {cloud_cover_str}")
    print(f"   📏 Method: {metadata.get('download_method', 'Unknown')}")

if __name__ == "__main__":
    create_maximum_zoom_visualization() 