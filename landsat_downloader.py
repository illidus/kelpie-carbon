"""
Dedicated Landsat imagery downloader for real satellite data testing.
This script downloads actual Landsat scenes from public repositories.
"""

import requests
import numpy as np
from PIL import Image
import io
import os
from typing import Tuple, Optional

def download_landsat_from_usgs_samples():
    """Download Landsat samples from USGS public galleries."""
    
    # Known working Landsat sample URLs from USGS and NASA
    sample_urls = [
        {
            'name': 'Landsat8_Yellowstone',
            'url': 'https://earthexplorer.usgs.gov/files/docs/2016/Yellowstone_Landsat8.jpg',
            'description': 'Landsat 8 Yellowstone National Park'
        },
        {
            'name': 'Landsat_Earth_Day',
            'url': 'https://www.usgs.gov/media/images/earth-day-landsat-image-gallery',
            'description': 'USGS Earth Day Landsat Collection'
        },
        {
            'name': 'NASA_Landsat_Gallery',
            'url': 'https://landsat.gsfc.nasa.gov/wp-content/uploads/2021/12/mississippi_river_ice_jam.jpg',
            'description': 'NASA Landsat Gallery - Mississippi River'
        }
    ]
    
    for sample in sample_urls:
        try:
            print(f"Downloading: {sample['description']}")
            response = requests.get(sample['url'], timeout=15)
            
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                img_array = np.array(img) / 255.0
                
                # Ensure RGB format
                if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
                    print(f"✅ Successfully downloaded {sample['name']}")
                    return img_array[:, :, :3], sample['name']
                    
        except Exception as e:
            print(f"❌ Failed to download {sample['name']}: {e}")
            continue
    
    return None, None

def download_sample_geotiff():
    """Download a sample GeoTIFF that works with PIL."""
    
    # These are known working sample files
    geotiff_samples = [
        {
            'name': 'Sample_RGB_TIFF',
            'url': 'https://github.com/rasterio/rasterio/raw/main/tests/data/RGB.byte.tif',
            'description': 'Sample RGB GeoTIFF from rasterio test data'
        },
        {
            'name': 'Sample_Landsat_Scene',
            'url': 'https://storage.googleapis.com/gcp-public-data-landsat/sample_files/LC08_L1TP_050050_20180215_20180308_01_T1_B1.TIF',
            'description': 'Sample Landsat scene from Google Cloud'
        }
    ]
    
    for sample in geotiff_samples:
        try:
            print(f"Downloading GeoTIFF: {sample['description']}")
            response = requests.get(sample['url'], timeout=15, stream=True)
            
            if response.status_code == 200:
                # Save temporarily
                temp_file = f"temp_{sample['name']}.tif"
                
                with open(temp_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                try:
                    # Try to open with PIL
                    with Image.open(temp_file) as img:
                        img_array = np.array(img)
                        
                        # Handle different data types
                        if img_array.dtype == np.uint16:
                            img_array = (img_array / 65535.0)
                        elif img_array.dtype == np.uint8:
                            img_array = (img_array / 255.0)
                        else:
                            img_array = img_array.astype(float) / img_array.max()
                        
                        # Convert single band to RGB
                        if len(img_array.shape) == 2:
                            img_array = np.stack([img_array] * 3, axis=-1)
                        
                        # Clean up
                        os.remove(temp_file)
                        
                        print(f"✅ Successfully processed {sample['name']}")
                        return img_array, sample['name']
                        
                except Exception as e:
                    print(f"❌ Failed to process {sample['name']}: {e}")
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                    continue
                    
        except Exception as e:
            print(f"❌ Failed to download {sample['name']}: {e}")
            continue
    
    return None, None

def get_real_landsat_data() -> Tuple[Optional[np.ndarray], Optional[str]]:
    """
    Main function to get real Landsat data.
    
    Returns:
        Tuple of (image_array, source_name) or (None, None) if failed
    """
    
    print("🛰️  Attempting to download real Landsat imagery...")
    
    # Try USGS samples first
    img, source = download_landsat_from_usgs_samples()
    if img is not None:
        return img, source
    
    # Try GeoTIFF samples
    print("Trying GeoTIFF samples...")
    img, source = download_sample_geotiff()
    if img is not None:
        return img, source
    
    # Try a few more direct links to known Landsat images
    direct_links = [
        {
            'name': 'Landsat_Earth_Observatory',
            'url': 'https://eoimages.gsfc.nasa.gov/images/imagerecords/1000/1752/world.topo.200407.3x5400x2700.jpg',
            'description': 'NASA Earth Observatory Landsat mosaic'
        }
    ]
    
    print("Trying direct image links...")
    for sample in direct_links:
        try:
            response = requests.get(sample['url'], timeout=10)
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                img_array = np.array(img) / 255.0
                
                if len(img_array.shape) == 3:
                    print(f"✅ Downloaded {sample['name']}")
                    return img_array[:, :, :3], sample['name']
                    
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue
    
    print("❌ All real Landsat downloads failed")
    return None, None

if __name__ == "__main__":
    img, source = get_real_landsat_data()
    if img is not None:
        print(f"Successfully obtained: {source}")
        print(f"Image shape: {img.shape}")
        print(f"Image data type: {img.dtype}")
        print(f"Value range: {img.min():.3f} to {img.max():.3f}")
    else:
        print("No real Landsat data could be obtained") 