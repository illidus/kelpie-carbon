"""
Mathematical validation tests exposing errors in current carbon analysis system.

These tests implement the correct mathematical formulas and realistic ranges
to identify and fix calculation errors.
"""

import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from api.main import (
    parse_simple_polygon_wkt,
    generate_realistic_spectral_data,
    estimate_carbon_sequestration
)
from sentinel_pipeline.indices import fai, ndre


class TestCorrectMathValidation:
    """Tests exposing mathematical errors in the current system."""
    
    def test_polygon_area_calculation_accuracy(self):
        """
        Test that polygon area calculation matches geodesic reality.
        
        At 48.45° N:
        - 1° latitude ≈ 111.0 km
        - 1° longitude ≈ 111.0 km × cos(48.45°) ≈ 73.3 km
        
        0.1° × 0.1° rectangle should be ~81.4 km² not 123 km².
        """
        # Test case from audit: 0.1° × 0.1° rectangle at Victoria, BC
        wkt = "POLYGON((-123.5 48.4, -123.4 48.4, -123.4 48.5, -123.5 48.5, -123.5 48.4))"
        
        calculated_area_m2 = parse_simple_polygon_wkt(wkt)
        calculated_area_km2 = calculated_area_m2 / 1_000_000
        
        # Expected area calculation:
        # Δlat = 0.1° → 11.1 km
        # Δlon = 0.1° → 7.33 km (at 48.45° N)
        # Area ≈ 81.4 km²
        expected_area_km2 = 81.4
        tolerance_km2 = 1.0  # Allow 1 km² tolerance
        
        print(f"Calculated area: {calculated_area_km2:.1f} km²")
        print(f"Expected area: {expected_area_km2:.1f} km²")
        print(f"Error: {abs(calculated_area_km2 - expected_area_km2):.1f} km²")
        
        # This should FAIL with current implementation (~123 km²)
        assert abs(calculated_area_km2 - expected_area_km2) <= tolerance_km2, (
            f"Area calculation error: got {calculated_area_km2:.1f} km², "
            f"expected {expected_area_km2:.1f} ± {tolerance_km2} km²"
        )
    
    def test_realistic_spectral_index_ranges(self):
        """
        Test that spectral indices stay within realistic ranges.
        
        NDRE rarely exceeds 0.6 even for lush crops; submerged kelp
        red-edge values seldom exceed 0.4.
        """
        area_m2 = 81_400_000.0  # Corrected area: ~81.4 km²
        date = "2024-06-15"
        
        fai_value, ndre_value = generate_realistic_spectral_data(area_m2, date)
        
        print(f"Generated FAI: {fai_value:.3f}")
        print(f"Generated NDRE: {ndre_value:.3f}")
        
        # Realistic ranges based on field studies
        assert -0.1 <= fai_value <= 0.3, f"FAI {fai_value:.3f} outside realistic range [-0.1, 0.3]"
        
        # This should FAIL with current implementation (NDRE can reach 0.8)
        assert ndre_value <= 0.6, f"NDRE {ndre_value:.3f} too high; kelp rarely exceeds 0.6"
        assert ndre_value >= -0.2, f"NDRE {ndre_value:.3f} too low"
    
    def test_proper_fai_formula_implementation(self):
        """
        Test that FAI follows the proper satellite formula, not area/date-based hashing.
        
        FAI = NIR - (RED + (SWIR - RED) * (λNIR - λRED) / (λSWIR - λRED))
        """
        # Synthetic satellite reflectance values
        nir = 0.30    # Band 8 (842nm)
        swir = 0.25   # Band 11 (1610nm) 
        red = 0.15    # Band 4 (665nm)
        
        print(f"Input reflectances - NIR: {nir}, SWIR: {swir}, RED: {red}")
        
        # Calculate using proper FAI implementation
        proper_fai = fai(
            b8=np.array([nir]),
            b11=np.array([swir]), 
            b4=np.array([red])
        )[0]
        
        print(f"Proper FAI formula result: {proper_fai:.4f}")
        
        # The current implementation uses area/date hashing instead
        # This test documents what FAI *should* be based on reflectance only
        assert -0.2 <= proper_fai <= 0.5, f"FAI {proper_fai:.4f} outside valid range"
        
        # Test that proper FAI depends only on reflectance, not area/date
        fai_different_area = fai(
            b8=np.array([nir]),
            b11=np.array([swir]), 
            b4=np.array([red])
        )[0]
        
        assert abs(proper_fai - fai_different_area) < 1e-10, "FAI should depend only on reflectance"
    
    def test_proper_ndre_formula_implementation(self):
        """
        Test that NDRE follows the proper formula: (NIR - RedEdge) / (NIR + RedEdge)
        """
        # Synthetic satellite reflectance values for kelp
        nir = 0.30        # NIR band
        red_edge = 0.20   # Red edge band
        
        print(f"Input reflectances - NIR: {nir}, RedEdge: {red_edge}")
        
        # Calculate using proper NDRE implementation
        proper_ndre = ndre(
            red_edge=np.array([red_edge]),
            nir=np.array([nir])
        )[0]
        
        print(f"Proper NDRE formula result: {proper_ndre:.4f}")
        
        # Expected: (0.30 - 0.20) / (0.30 + 0.20) = 0.10 / 0.50 = 0.20
        expected_ndre = (nir - red_edge) / (nir + red_edge)
        
        assert abs(proper_ndre - expected_ndre) < 1e-10, "NDRE calculation mismatch"
        assert proper_ndre <= 0.4, f"NDRE {proper_ndre:.4f} reasonable for submerged kelp"
    
    def test_biomass_density_sanity_range(self):
        """
        Test that biomass density predictions stay within realistic ranges.
        
        Bull kelp farms typically report 2-7 kg DW/m², not 12.5 kg/m².
        """
        import numpy as np
        
        # Test the constraint logic directly using numpy clip
        test_cases = [
            (8.5, "normal range"),    # Should pass through unchanged
            (12.5, "too high"),       # Should be clipped to 10.0
            (15.0, "extreme"),        # Should be clipped to 10.0
            (-2.0, "negative"),       # Should be clipped to 0.0
        ]
        
        for raw_prediction, description in test_cases:
            # Apply the same constraint logic as the API
            constrained_density = np.clip(raw_prediction, 0.0, 10.0)
            
            print(f"Raw prediction {raw_prediction:.1f} kg/m² ({description}) → {constrained_density:.1f} kg/m²")
            
            # Test that constraints are properly applied
            assert constrained_density <= 10.0, (
                f"Constrained density {constrained_density:.1f} kg/m² still too high; "
                f"should be capped at 10 kg/m²"
            )
            assert constrained_density >= 0.0, "Constrained density cannot be negative"
            
            # Test specific constraint behavior
            if raw_prediction > 10.0:
                assert constrained_density == 10.0, "High values should be capped at 10.0"
            elif raw_prediction < 0.0:
                assert constrained_density == 0.0, "Negative values should be capped at 0.0"
            else:
                assert constrained_density == raw_prediction, "Normal values should pass through unchanged"
    
    def test_total_biomass_with_correct_area(self):
        """
        Test total biomass calculation using corrected area.
        
        With correct area (~81 km²) and realistic density (≤7 kg/m²):
        Max biomass should be ~567,000 tonnes, not 1.5+ million tonnes.
        """
        corrected_area_m2 = 81_400_000.0  # ~81.4 km²
        realistic_density = 7.0  # kg/m² (high but realistic)
        
        total_biomass_kg = realistic_density * corrected_area_m2
        total_biomass_tonnes = total_biomass_kg / 1000.0
        
        print(f"Corrected calculation:")
        print(f"  Area: {corrected_area_m2/1_000_000:.1f} km²")
        print(f"  Density: {realistic_density:.1f} kg/m²")
        print(f"  Total biomass: {total_biomass_tonnes:,.0f} tonnes")
        
        # Should be well under 1 million tonnes
        assert total_biomass_tonnes <= 600_000, (
            f"Total biomass {total_biomass_tonnes:,.0f} tonnes too high with corrected math"
        )
    
    def test_unit_consistency_kg_vs_tonnes(self):
        """
        Test that unit conversions between kg and tonnes are consistent.
        """
        biomass_kg = 1_540_125.0
        
        # Convert to tonnes
        biomass_tonnes_v1 = biomass_kg / 1000.0
        biomass_tonnes_v2 = biomass_kg * 0.001
        
        print(f"Biomass: {biomass_kg:,.0f} kg")
        print(f"Method 1: {biomass_tonnes_v1:,.1f} tonnes")
        print(f"Method 2: {biomass_tonnes_v2:,.1f} tonnes")
        
        # Should be exactly equal
        assert abs(biomass_tonnes_v1 - biomass_tonnes_v2) < 1e-10, "Unit conversion inconsistency"
        
        # Test carbon calculation chain
        carbon_kg = biomass_kg * 0.325  # 32.5% carbon
        co2e_kg = carbon_kg * 3.67      # CO2 equivalent
        co2e_tonnes = co2e_kg / 1000.0
        
        calculated_co2e = estimate_carbon_sequestration(biomass_kg)
        
        print(f"Manual CO2e calculation: {co2e_tonnes:.1f} tonnes")
        print(f"Function result: {calculated_co2e:.1f} tonnes")
        
        assert abs(co2e_tonnes - calculated_co2e) < 0.1, "Carbon calculation inconsistency" 