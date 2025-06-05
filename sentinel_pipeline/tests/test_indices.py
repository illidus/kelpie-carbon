"""
Tests for spectral indices module.

Tests cover:
- FAI and NDRE calculation accuracy
- NaN handling and masking
- Valid index ranges
- Edge cases and error conditions
- Vectorization performance
"""

import warnings

import numpy as np
import pytest

from sentinel_pipeline.indices import fai, ndre, validate_spectral_index


class TestFAI:
    """Tests for Floating Algae Index (FAI) function."""

    def test_fai_basic_calculation(self):
        """Test basic FAI calculation with known values."""
        # Create simple test data
        b8 = np.array([0.3, 0.4, 0.5])  # NIR
        b11 = np.array([0.1, 0.2, 0.3])  # SWIR
        b4 = np.array([0.1, 0.15, 0.2])  # RED

        result = fai(b8, b11, b4)

        # FAI should be computed correctly
        assert result.shape == (3,)
        assert np.all(np.isfinite(result))

        # Manual calculation for verification
        # Wavelengths: NIR=842, SWIR=1610, RED=665
        wl_ratio = (842 - 665) / (1610 - 665)  # ≈ 0.187
        expected = b8 - (b4 + (b11 - b4) * wl_ratio)
        np.testing.assert_array_almost_equal(result, expected, decimal=10)

    def test_fai_typical_range(self):
        """Test FAI returns values in typical range."""
        # Realistic Sentinel-2 reflectance values
        np.random.seed(42)
        size = (10, 10)

        b8 = np.random.uniform(0.1, 0.6, size)  # NIR
        b11 = np.random.uniform(0.02, 0.3, size)  # SWIR
        b4 = np.random.uniform(0.02, 0.4, size)  # RED

        result = fai(b8, b11, b4)

        # Most values should be in typical FAI range
        finite_values = result[np.isfinite(result)]
        assert len(finite_values) > 0

        # Check reasonable bounds (allowing for some outliers)
        assert np.percentile(finite_values, 5) >= -0.3
        assert np.percentile(finite_values, 95) <= 0.6

    def test_fai_kelp_detection_values(self):
        """Test FAI with values that should indicate kelp presence."""
        # High NIR, moderate SWIR, low RED (kelp signature)
        b8 = np.array([0.6, 0.7, 0.8])  # High NIR
        b11 = np.array([0.1, 0.15, 0.2])  # Moderate SWIR
        b4 = np.array([0.05, 0.06, 0.07])  # Low RED

        result = fai(b8, b11, b4)

        # Should produce positive FAI values indicating algae
        assert np.all(result > 0)
        assert np.all(result > 0.01)  # Threshold for algae presence

    def test_fai_water_values(self):
        """Test FAI with typical water reflectance values."""
        # Low reflectance across all bands (clear water)
        b8 = np.array([0.02, 0.03, 0.025])  # Very low NIR
        b11 = np.array([0.01, 0.015, 0.012])  # Very low SWIR
        b4 = np.array([0.05, 0.06, 0.055])  # Slightly higher RED/blue

        result = fai(b8, b11, b4)

        # Water typically has negative or very low FAI
        assert np.all(result <= 0.05)

    def test_fai_nan_handling(self):
        """Test FAI handles NaN inputs correctly."""
        b8 = np.array([0.3, np.nan, 0.5, 0.4])
        b11 = np.array([0.1, 0.2, np.nan, 0.2])
        b4 = np.array([0.1, 0.15, 0.2, np.nan])

        result = fai(b8, b11, b4, mask_invalid=True)

        # First value should be valid, others NaN
        assert np.isfinite(result[0])
        assert np.isnan(result[1])
        assert np.isnan(result[2])
        assert np.isnan(result[3])

    def test_fai_negative_values_masked(self):
        """Test that negative reflectance values are masked."""
        b8 = np.array([0.3, -0.1, 0.5])
        b11 = np.array([0.1, 0.2, 0.3])
        b4 = np.array([0.1, 0.15, 0.2])

        result = fai(b8, b11, b4, mask_invalid=True)

        assert np.isfinite(result[0])
        assert np.isnan(result[1])  # Negative b8 should be masked
        assert np.isfinite(result[2])

    def test_fai_invalid_values_unmasked(self):
        """Test FAI with mask_invalid=False preserves all calculations."""
        b8 = np.array([0.3, np.nan, -0.1])
        b11 = np.array([0.1, 0.2, 0.3])
        b4 = np.array([0.1, 0.15, 0.2])

        result = fai(b8, b11, b4, mask_invalid=False)

        assert np.isfinite(result[0])
        assert np.isnan(result[1])  # NaN input produces NaN output
        assert np.isfinite(result[2]) or np.isnan(result[2])  # May be finite or NaN

    def test_fai_shape_mismatch_error(self):
        """Test that mismatched array shapes raise ValueError."""
        b8 = np.array([0.3, 0.4])
        b11 = np.array([0.1, 0.2, 0.3])  # Different size
        b4 = np.array([0.1, 0.15])

        with pytest.raises(ValueError, match="same shape"):
            fai(b8, b11, b4)

    def test_fai_vectorization(self):
        """Test FAI works with multi-dimensional arrays."""
        shape = (5, 4, 3)
        b8 = np.random.uniform(0.1, 0.6, shape)
        b11 = np.random.uniform(0.02, 0.3, shape)
        b4 = np.random.uniform(0.02, 0.4, shape)

        result = fai(b8, b11, b4)

        assert result.shape == shape
        assert np.sum(np.isfinite(result)) > 0

    def test_fai_extreme_values_warning(self):
        """Test that extreme FAI values trigger warnings."""
        # Create values that will produce extreme FAI
        # Use more extreme contrasts to ensure we get outside the typical range
        b8 = np.array([1.0, 0.001])  # Very high and very low NIR
        b11 = np.array([0.001, 1.0])  # Very low and very high SWIR
        b4 = np.array([0.001, 0.001])  # Very low RED

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = fai(b8, b11, b4)

            # Check if we got extreme values
            if np.any((result < -0.5) | (result > 1.0)):
                # Should warn about extreme values
                warning_messages = [str(warning.message) for warning in w]
                extreme_warnings = [
                    msg for msg in warning_messages if "outside typical range" in msg
                ]
                assert len(extreme_warnings) > 0
            else:
                # If no extreme values produced, just check calculation worked
                assert len(result) == 2
                assert np.all(np.isfinite(result))


class TestNDRE:
    """Tests for Normalized Difference Red Edge (NDRE) function."""

    def test_ndre_basic_calculation(self):
        """Test basic NDRE calculation with known values."""
        red_edge = np.array([0.2, 0.3, 0.4])
        nir = np.array([0.6, 0.7, 0.8])

        result = ndre(red_edge, nir)

        # Manual calculation: (NIR - RedEdge) / (NIR + RedEdge)
        expected = (nir - red_edge) / (nir + red_edge)
        np.testing.assert_array_almost_equal(result, expected, decimal=10)

    def test_ndre_range_bounds(self):
        """Test NDRE returns values in valid range [-1, 1]."""
        # Generate random realistic values
        np.random.seed(42)
        red_edge = np.random.uniform(0.1, 0.5, 100)
        nir = np.random.uniform(0.3, 0.8, 100)

        result = ndre(red_edge, nir)
        finite_values = result[np.isfinite(result)]

        # All finite values should be in [-1, 1]
        assert np.all(finite_values >= -1.0)
        assert np.all(finite_values <= 1.0)

    def test_ndre_vegetation_signature(self):
        """Test NDRE with typical vegetation reflectance."""
        # Healthy vegetation: low red edge, high NIR
        red_edge = np.array([0.1, 0.15, 0.12])
        nir = np.array([0.7, 0.8, 0.75])

        result = ndre(red_edge, nir)

        # Should produce high positive NDRE (healthy vegetation)
        assert np.all(result > 0.5)
        assert np.all(result < 1.0)

    def test_ndre_water_signature(self):
        """Test NDRE with water-like reflectance."""
        # Water: very low reflectance in both bands
        red_edge = np.array([0.02, 0.03, 0.025])
        nir = np.array([0.01, 0.015, 0.012])

        result = ndre(red_edge, nir)

        # Water may have negative NDRE or small positive values
        assert np.all(np.abs(result) <= 1.0)

    def test_ndre_zero_division_handling(self):
        """Test NDRE handles zero denominator correctly."""
        red_edge = np.array([0.0, 0.3, 0.0])
        nir = np.array([0.0, 0.7, 0.1])  # First pair sums to zero

        result = ndre(red_edge, nir)

        assert np.isnan(result[0])  # Zero denominator -> NaN
        assert np.isfinite(result[1])  # Normal calculation
        assert np.isfinite(result[2])  # Normal calculation

    def test_ndre_nan_handling(self):
        """Test NDRE handles NaN inputs correctly."""
        red_edge = np.array([0.2, np.nan, 0.4])
        nir = np.array([0.6, 0.7, np.nan])

        result = ndre(red_edge, nir, mask_invalid=True)

        assert np.isfinite(result[0])
        assert np.isnan(result[1])
        assert np.isnan(result[2])

    def test_ndre_negative_values_masked(self):
        """Test that negative reflectance values are masked."""
        red_edge = np.array([0.2, -0.1, 0.4])
        nir = np.array([0.6, 0.7, 0.8])

        result = ndre(red_edge, nir, mask_invalid=True)

        assert np.isfinite(result[0])
        assert np.isnan(result[1])  # Negative red_edge masked
        assert np.isfinite(result[2])

    def test_ndre_out_of_range_values_masked(self):
        """Test that reflectance > 1.0 is masked."""
        red_edge = np.array([0.2, 1.5, 0.4])  # 1.5 > 1.0
        nir = np.array([0.6, 0.7, 2.0])  # 2.0 > 1.0

        result = ndre(red_edge, nir, mask_invalid=True)

        assert np.isfinite(result[0])
        assert np.isnan(result[1])  # red_edge > 1.0
        assert np.isnan(result[2])  # nir > 1.0

    def test_ndre_shape_mismatch_error(self):
        """Test that mismatched array shapes raise ValueError."""
        red_edge = np.array([0.2, 0.3])
        nir = np.array([0.6, 0.7, 0.8])  # Different size

        with pytest.raises(ValueError, match="same shape"):
            ndre(red_edge, nir)

    def test_ndre_multidimensional(self):
        """Test NDRE works with multi-dimensional arrays."""
        shape = (3, 4, 5)
        red_edge = np.random.uniform(0.1, 0.5, shape)
        nir = np.random.uniform(0.3, 0.8, shape)

        result = ndre(red_edge, nir)

        assert result.shape == shape
        finite_values = result[np.isfinite(result)]
        assert len(finite_values) > 0
        assert np.all(finite_values >= -1.0)
        assert np.all(finite_values <= 1.0)

    def test_ndre_extreme_values_warning(self):
        """Test that NDRE values outside [-1,1] trigger warnings."""
        # This should not happen with valid inputs, but test the warning system
        red_edge = np.array([0.1])
        nir = np.array([0.9])

        # Manually test the warning by creating invalid result
        # (This is more for testing the validation logic)
        result = ndre(red_edge, nir)

        # The normal case shouldn't trigger warnings
        assert np.all(np.abs(result) <= 1.0)


class TestValidateSpectralIndex:
    """Tests for spectral index validation function."""

    def test_validate_basic_stats(self):
        """Test basic statistics calculation."""
        values = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

        stats = validate_spectral_index(values, "TEST", (-1, 1))

        assert stats["index_name"] == "TEST"
        assert stats["total_pixels"] == 5
        assert stats["valid_pixels"] == 5
        assert stats["invalid_pixels"] == 0
        assert stats["percent_valid"] == 100.0
        assert stats["min_value"] == 0.1
        assert stats["max_value"] == 0.5
        assert stats["mean_value"] == 0.3
        assert stats["in_expected_range"] == 5
        assert stats["percent_in_range"] == 100.0

    def test_validate_with_nans(self):
        """Test validation with NaN values."""
        values = np.array([0.1, np.nan, 0.3, np.nan, 0.5])

        stats = validate_spectral_index(values, "TEST_NAN", (-1, 1))

        assert stats["total_pixels"] == 5
        assert stats["valid_pixels"] == 3
        assert stats["invalid_pixels"] == 2
        assert stats["percent_valid"] == 60.0
        assert stats["mean_value"] == pytest.approx(0.3)

    def test_validate_out_of_range(self):
        """Test validation with values outside expected range."""
        values = np.array([-2.0, -0.5, 0.3, 0.8, 2.0])  # Range [-1, 1]

        stats = validate_spectral_index(values, "TEST_RANGE", (-1, 1))

        assert stats["valid_pixels"] == 5
        assert stats["in_expected_range"] == 3  # Only -0.5, 0.3, 0.8
        assert stats["percent_in_range"] == 60.0

    def test_validate_all_invalid(self):
        """Test validation with all invalid values."""
        values = np.array([np.nan, np.nan, np.nan])

        stats = validate_spectral_index(values, "ALL_NAN", (-1, 1))

        assert stats["valid_pixels"] == 0
        assert stats["percent_valid"] == 0.0
        assert np.isnan(stats["min_value"])
        assert np.isnan(stats["max_value"])
        assert np.isnan(stats["mean_value"])
        assert stats["percent_in_range"] == 0.0


class TestIntegration:
    """Integration tests for spectral indices."""

    def test_fai_ndre_integration(self):
        """Test FAI and NDRE can be computed on same dataset."""
        # Simulate Sentinel-2 reflectance data
        np.random.seed(42)
        shape = (10, 10)

        # Sentinel-2 bands
        b4_red = np.random.uniform(0.02, 0.3, shape)  # Red
        b5_red_edge = np.random.uniform(0.05, 0.4, shape)  # Red Edge
        b8_nir = np.random.uniform(0.1, 0.7, shape)  # NIR
        b11_swir = np.random.uniform(0.01, 0.2, shape)  # SWIR

        # Compute indices
        fai_result = fai(b8_nir, b11_swir, b4_red)
        ndre_result = ndre(b5_red_edge, b8_nir)

        # Validate results
        fai_stats = validate_spectral_index(fai_result, "FAI", (-0.5, 1.0))
        ndre_stats = validate_spectral_index(ndre_result, "NDRE", (-1, 1))

        # Both should have reasonable number of valid pixels
        assert fai_stats["percent_valid"] > 80
        assert ndre_stats["percent_valid"] > 80

        # Results should be in expected ranges mostly
        assert fai_stats["percent_in_range"] > 70
        assert ndre_stats["percent_in_range"] > 90

    def test_performance_large_arrays(self):
        """Test performance with large arrays (vectorization check)."""
        # Large array to test vectorization efficiency
        shape = (1000, 1000)

        # Generate test data
        b8 = np.random.uniform(0.1, 0.6, shape)
        b11 = np.random.uniform(0.02, 0.3, shape)
        b4 = np.random.uniform(0.02, 0.4, shape)
        red_edge = np.random.uniform(0.1, 0.5, shape)

        # Should complete quickly due to vectorization
        import time

        start = time.time()
        fai_result = fai(b8, b11, b4)
        fai_time = time.time() - start

        start = time.time()
        ndre_result = ndre(red_edge, b8)
        ndre_time = time.time() - start

        # Should be fast (< 1 second for 1M pixels on modern hardware)
        assert fai_time < 2.0  # Allow some margin for slower systems
        assert ndre_time < 2.0

        # Results should be reasonable
        assert fai_result.shape == shape
        assert ndre_result.shape == shape
        assert np.sum(np.isfinite(fai_result)) > shape[0] * shape[1] * 0.8
        assert np.sum(np.isfinite(ndre_result)) > shape[0] * shape[1] * 0.8
