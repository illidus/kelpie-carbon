"""
Spectral indices calculations for satellite imagery.

This module provides vectorized numpy implementations of key spectral indices:
- FAI (Floating Algae Index): Detects floating algae and kelp biomass
- NDRE (Normalized Difference Red Edge): Vegetation health and biomass indicator
"""

import warnings

import numpy as np


def fai(b8: np.ndarray, b11: np.ndarray, b4: np.ndarray, mask_invalid: bool = True) -> np.ndarray:
    """
    Calculate Floating Algae Index (FAI) for kelp biomass detection.

    FAI = NIR - (RED + (SWIR - RED) * ((lambda_NIR - lambda_RED) / (lambda_SWIR - lambda_RED)))

    For Sentinel-2:
    - b8 (NIR): Band 8 (842nm)
    - b11 (SWIR): Band 11 (1610nm)
    - b4 (RED): Band 4 (665nm)

    Parameters:
    -----------
    b8 : np.ndarray
        Near-infrared reflectance values (Band 8)
    b11 : np.ndarray
        Short-wave infrared reflectance values (Band 11)
    b4 : np.ndarray
        Red reflectance values (Band 4)
    mask_invalid : bool, default=True
        Whether to mask invalid values (NaN, inf, negative) as NaN

    Returns:
    --------
    np.ndarray
        FAI values, typically ranging from -0.1 to 0.3
        Higher values indicate more floating algae/kelp biomass

    Notes:
    ------
    - Valid FAI range is approximately -0.2 to 0.5
    - Values > 0.01 often indicate algae presence
    - Values > 0.05 indicate significant biomass
    """
    # Sentinel-2 band wavelengths
    lambda_nir = 842
    lambda_red = 665
    lambda_swir = 1610
    
    # Calculate FAI using the standard formula
    fai_rayleigh = b4 + (b11 - b4) * ((lambda_nir - lambda_red) / (lambda_swir - lambda_red))
    fai_value = b8 - fai_rayleigh
    
    if mask_invalid:
        # Mask invalid input values
        invalid_mask = (
            ~np.isfinite(b8)
            | ~np.isfinite(b11)
            | ~np.isfinite(b4)
            | (b8 < 0)
            | (b11 < 0)
            | (b4 < 0)
            | (b8 > 1)
            | (b11 > 1)
            | (b4 > 1)  # Assuming reflectance [0,1]
        )
        fai_value[invalid_mask] = np.nan

        # Warn about extreme values
        extreme_mask = np.isfinite(fai_value) & (
            (fai_value < -0.5) | (fai_value > 1.0)
        )
        if np.any(extreme_mask):
            n_extreme = np.sum(extreme_mask)
            warnings.warn(
                f"Found {n_extreme} FAI values outside typical range [-0.5, 1.0]"
            )

    return np.asarray(fai_value, dtype=np.float64)


def ndre(red_edge: np.ndarray, nir: np.ndarray, mask_invalid: bool = True) -> np.ndarray:
    """
    Calculate Normalized Difference Red Edge (NDRE) index for vegetation health.

    NDRE = (NIR - RedEdge) / (NIR + RedEdge)

    For Sentinel-2:
    - red_edge: Band 5 (705nm), Band 6 (740nm), or Band 7 (783nm)
    - nir: Band 8 (842nm) or Band 8A (865nm)

    Parameters:
    -----------
    red_edge : np.ndarray
        Red edge reflectance values (Band 5, 6, or 7)
    nir : np.ndarray
        Near-infrared reflectance values (Band 8 or 8A)
    mask_invalid : bool, default=True
        Whether to mask invalid values as NaN

    Returns:
    --------
    np.ndarray
        NDRE values ranging from -1 to 1
        Higher values indicate healthier/more vegetation

    Notes:
    ------
    - Valid NDRE range is -1 to 1
    - Values > 0.2 typically indicate healthy vegetation
    - Values > 0.4 indicate dense vegetation/high biomass
    - Negative values may indicate water, bare soil, or stressed vegetation
    """
    # Avoid division by zero
    denominator = nir + red_edge
    denominator = np.where(denominator == 0, np.finfo(float).eps, denominator)
    
    ndre_value = (nir - red_edge) / denominator
    
    if mask_invalid:
        # Mask invalid input values
        invalid_mask = (
            ~np.isfinite(red_edge)
            | ~np.isfinite(nir)
            | (red_edge < 0)
            | (nir < 0)
            | (red_edge > 1)
            | (nir > 1)  # Assuming reflectance [0,1]
        )
        ndre_value[invalid_mask] = np.nan

        # Theoretical bounds check - NDRE should be in [-1, 1]
        extreme_mask = np.isfinite(ndre_value) & (
            (ndre_value < -1.1) | (ndre_value > 1.1)
        )
        if np.any(extreme_mask):
            n_extreme = np.sum(extreme_mask)
            warnings.warn(
                f"Found {n_extreme} NDRE values outside theoretical range [-1, 1]"
            )

    return np.asarray(ndre_value, dtype=np.float64)


def validate_spectral_index(
    values: np.ndarray, index_name: str, expected_range: tuple = (-1, 1)
) -> dict:
    """
    Validate spectral index results and provide statistics.

    Parameters:
    -----------
    values : np.ndarray
        Computed spectral index values
    index_name : str
        Name of the spectral index (for reporting)
    expected_range : tuple
        Expected (min, max) range for the index

    Returns:
    --------
    dict
        Statistics and validation results
    """
    values = np.asarray(values)
    finite_values = values[np.isfinite(values)]

    if len(finite_values) == 0:
        return {
            "index_name": index_name,
            "total_pixels": values.size,
            "valid_pixels": 0,
            "invalid_pixels": values.size,
            "percent_valid": 0.0,
            "min_value": np.nan,
            "max_value": np.nan,
            "mean_value": np.nan,
            "std_value": np.nan,
            "in_expected_range": 0,
            "percent_in_range": 0.0,
        }

    # Count values in expected range
    in_range = np.sum(
        (finite_values >= expected_range[0]) & (finite_values <= expected_range[1])
    )

    return {
        "index_name": index_name,
        "total_pixels": values.size,
        "valid_pixels": len(finite_values),
        "invalid_pixels": values.size - len(finite_values),
        "percent_valid": 100.0 * len(finite_values) / values.size,
        "min_value": np.min(finite_values),
        "max_value": np.max(finite_values),
        "mean_value": np.mean(finite_values),
        "std_value": np.std(finite_values),
        "in_expected_range": in_range,
        "percent_in_range": 100.0 * in_range / len(finite_values),
    }
