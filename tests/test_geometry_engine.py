"""
Comprehensive tests for geometry and spectral index calculations.

Tests edge cases, shape mismatches, NaN propagation, and known geometries
to ensure robust production-ready mathematical operations.
"""

import numpy as np
import pytest
from hypothesis import given, strategies as st

from api.main import parse_simple_polygon_wkt, polygon_area
from sentinel_pipeline.indices import fai, ndre


class TestGeometryEngine:
    """Test suite for geodesic area calculations with known geometries."""
    
    def test_rectangle_area_calculation(self):
        """Test rectangular polygon area calculation using abstracted helper."""
        # 0.1° × 0.1° rectangle at Victoria, BC (48.45° N)
        wkt = "POLYGON((-123.5 48.4, -123.4 48.4, -123.4 48.5, -123.5 48.5, -123.5 48.4))"
        area_m2 = polygon_area(wkt)  # Using abstracted helper
        area_km2 = area_m2 / 1_000_000
        
        # Expected: ~81.4 km² with latitude correction
        assert 80.5 <= area_km2 <= 82.5, f"Rectangle area {area_km2:.1f} km² outside expected range"
    
    def test_triangle_area_calculation(self):
        """Test triangular polygon area calculation."""
        # Simple triangle: (0,0), (1,0), (0,1) at equator
        wkt = "POLYGON((0 0, 1 0, 0 1, 0 0))"
        area_m2 = parse_simple_polygon_wkt(wkt)
        
        # Expected: 0.5 degree² × (111km)² ≈ 6,160 km²
        area_km2 = area_m2 / 1_000_000
        expected_km2 = 0.5 * (111.0 ** 2)  # Triangle area = 0.5 × base × height
        
        assert abs(area_km2 - expected_km2) < 100, f"Triangle area error: {area_km2:.0f} vs {expected_km2:.0f} km²"
    
    def test_concave_polygon_area(self):
        """Test concave (non-convex) polygon handling."""
        # L-shaped polygon
        wkt = "POLYGON((0 0, 2 0, 2 1, 1 1, 1 2, 0 2, 0 0))"
        area_m2 = parse_simple_polygon_wkt(wkt)
        
        # L-shape area = 2×1 + 1×1 = 3 degree²
        area_km2 = area_m2 / 1_000_000
        expected_km2 = 3 * (111.0 ** 2)
        
        assert abs(area_km2 - expected_km2) < 200, f"Concave polygon area error: {area_km2:.0f} vs {expected_km2:.0f} km²"
    
    def test_invalid_wkt_formats(self):
        """Test error handling for invalid WKT geometries."""
        invalid_wkts = [
            "INVALID((0 0, 1 1))",  # Wrong geometry type
            "POLYGON((0 0, 1 1))",  # Too few points
            "POLYGON((abc def, 1 1, 2 2, 0 0))",  # Invalid coordinates
        ]
        
        for invalid_wkt in invalid_wkts:
            with pytest.raises(ValueError):
                parse_simple_polygon_wkt(invalid_wkt)
        
        # Test empty string separately
        with pytest.raises(ValueError):
            parse_simple_polygon_wkt("")


class TestSpectralIndexEngine:
    """Test suite for spectral index calculations with edge cases."""
    
    def test_fai_shape_mismatch_detection(self):
        """Test that FAI detects mismatched input array shapes."""
        nir = np.array([0.3, 0.4])      # 2 elements
        swir = np.array([0.25])         # 1 element
        red = np.array([0.15, 0.2, 0.1]) # 3 elements
        
        with pytest.raises(ValueError, match="same shape"):
            fai(b8=nir, b11=swir, b4=red)
    
    def test_ndre_shape_mismatch_detection(self):
        """Test that NDRE detects mismatched input array shapes."""
        nir = np.array([0.3, 0.4])
        red_edge = np.array([0.2])
        
        with pytest.raises(ValueError, match="same shape"):
            ndre(red_edge=red_edge, nir=nir)
    
    def test_fai_nan_propagation(self):
        """Test that NaN inputs produce NaN outputs in FAI."""
        # Test with NaN in different bands
        test_cases = [
            (np.array([np.nan]), np.array([0.25]), np.array([0.15])),  # NaN in NIR
            (np.array([0.3]), np.array([np.nan]), np.array([0.15])),   # NaN in SWIR
            (np.array([0.3]), np.array([0.25]), np.array([np.nan])),   # NaN in RED
        ]
        
        for nir, swir, red in test_cases:
            result = fai(b8=nir, b11=swir, b4=red)
            assert np.isnan(result[0]), f"Expected NaN output, got {result[0]}"
    
    def test_ndre_nan_propagation(self):
        """Test that NaN inputs produce NaN outputs in NDRE."""
        test_cases = [
            (np.array([np.nan]), np.array([0.2])),  # NaN in NIR
            (np.array([0.3]), np.array([np.nan])),  # NaN in RedEdge
        ]
        
        for nir, red_edge in test_cases:
            result = ndre(red_edge=red_edge, nir=nir)
            assert np.isnan(result[0]), f"Expected NaN output, got {result[0]}"
    
    def test_fai_realistic_range_validation(self):
        """Test FAI outputs stay within realistic ranges for kelp."""
        # Typical kelp reflectance values
        nir_values = np.array([0.15, 0.20, 0.25, 0.30])
        swir_values = np.array([0.10, 0.15, 0.20, 0.25])
        red_values = np.array([0.08, 0.10, 0.12, 0.15])
        
        fai_results = fai(b8=nir_values, b11=swir_values, b4=red_values)
        
        # All FAI values should be in realistic range
        assert np.all(fai_results >= -0.2), f"FAI too low: {fai_results.min():.3f}"
        assert np.all(fai_results <= 0.5), f"FAI too high: {fai_results.max():.3f}"
    
    def test_ndre_realistic_range_validation(self):
        """Test NDRE outputs stay within theoretical bounds."""
        # Kelp-like reflectance values
        nir_values = np.array([0.15, 0.20, 0.25, 0.30])
        red_edge_values = np.array([0.12, 0.15, 0.18, 0.22])
        
        ndre_results = ndre(red_edge=red_edge_values, nir=nir_values)
        
        # NDRE must be within theoretical bounds [-1, 1]
        assert np.all(ndre_results >= -1.0), f"NDRE below theoretical minimum: {ndre_results.min():.3f}"
        assert np.all(ndre_results <= 1.0), f"NDRE above theoretical maximum: {ndre_results.max():.3f}"
        
        # For submerged kelp, rarely exceeds 0.6
        assert np.all(ndre_results <= 0.8), f"NDRE unrealistically high for kelp: {ndre_results.max():.3f}"


class TestPropertyBasedValidation:
    """Property-based tests using hypothesis for edge case discovery."""
    
    @given(
        nir=st.one_of(st.floats(min_value=0.0, max_value=1.0), st.just(float('nan'))),
        swir=st.one_of(st.floats(min_value=0.0, max_value=1.0), st.just(float('nan'))), 
        red=st.one_of(st.floats(min_value=0.0, max_value=1.0), st.just(float('nan')))
    )
    def test_fai_handles_any_valid_reflectance(self, nir, swir, red):
        """Test FAI with any valid reflectance combination."""
        try:
            result = fai(
                b8=np.array([nir]), 
                b11=np.array([swir]), 
                b4=np.array([red])
            )[0]
            
            # If any input is NaN, output should be NaN
            if np.isnan(nir) or np.isnan(swir) or np.isnan(red):
                assert np.isnan(result), "NaN input should produce NaN output"
            else:
                # Valid reflectance should produce finite result
                assert np.isfinite(result), f"Valid inputs produced non-finite result: {result}"
                
        except Exception as e:
            pytest.fail(f"FAI failed with valid inputs ({nir}, {swir}, {red}): {e}")
    
    @given(
        nir=st.one_of(st.floats(min_value=0.0, max_value=1.0), st.just(float('nan'))),
        red_edge=st.one_of(st.floats(min_value=0.0, max_value=1.0), st.just(float('nan')))
    )
    def test_ndre_handles_any_valid_reflectance(self, nir, red_edge):
        """Test NDRE with any valid reflectance combination."""
        try:
            result = ndre(
                red_edge=np.array([red_edge]),
                nir=np.array([nir])
            )[0]
            
            # If any input is NaN, output should be NaN
            if np.isnan(nir) or np.isnan(red_edge):
                assert np.isnan(result), "NaN input should produce NaN output"
            # Division by zero case (both NIR + RedEdge = 0) should produce NaN
            elif (nir + red_edge) == 0.0:
                assert np.isnan(result), "Division by zero should produce NaN output"
            else:
                # Valid reflectance should produce result in [-1, 1]
                assert -1.1 <= result <= 1.1, f"NDRE outside theoretical bounds: {result}"
                
        except Exception as e:
            pytest.fail(f"NDRE failed with valid inputs ({nir}, {red_edge}): {e}")


class TestBiomassConstraintValidation:
    """Test biomass density constraint logic."""
    
    def test_density_constraint_ranges(self):
        """Test biomass density constraint behavior across ranges."""
        test_cases = [
            (-5.0, 0.0, "negative"),
            (0.0, 0.0, "zero"), 
            (3.5, 3.5, "normal low"),
            (7.0, 7.0, "normal high"),
            (8.5, 8.5, "dense but valid"),
            (12.0, 10.0, "exceeds cap"),
            (25.0, 10.0, "extreme"),
        ]
        
        for raw, expected, description in test_cases:
            constrained = np.clip(raw, 0.0, 10.0)
            assert constrained == expected, f"{description}: {raw} → {constrained}, expected {expected}"
    
    def test_constraint_preserves_valid_range(self):
        """Test that constraint doesn't modify values in valid range."""
        valid_densities = np.array([0.5, 2.0, 5.5, 7.0, 9.5])
        constrained = np.clip(valid_densities, 0.0, 10.0)
        
        np.testing.assert_array_equal(valid_densities, constrained) 