"""Tests for biomass regression model."""

import numpy as np
import pytest
from joblib import load
import os


class TestBiomassModel:
    """Test cases for biomass regression model."""

    def test_model_predict_shape(self):
        """Test that model predictions have correct shape and non-negative values."""
        model_path = "models/biomass_rf.pkl"
        
        # Skip test if model doesn't exist yet
        if not os.path.exists(model_path):
            pytest.skip("Model file not found. Run the biomass regression notebook first.")
        
        # Load the model
        mdl = load(model_path)
        
        # Test with random FAI, NDRE values
        x = np.random.rand(5, 2)  # FAI, NDRE
        y = mdl.predict(x)
        
        # Check shape and non-negative values
        assert y.shape == (5,), f"Expected shape (5,), got {y.shape}"
        assert np.all(y >= 0), f"Found negative predictions: {y[y < 0]}"

    def test_model_predict_realistic_values(self):
        """Test model with realistic spectral index values."""
        model_path = "models/biomass_rf.pkl"
        
        if not os.path.exists(model_path):
            pytest.skip("Model file not found. Run the biomass regression notebook first.")
        
        mdl = load(model_path)
        
        # Test with realistic FAI and NDRE ranges
        # FAI typically ranges from -0.05 to 0.3
        # NDRE typically ranges from -0.2 to 0.8
        realistic_values = np.array([
            [0.05, 0.2],   # Low biomass
            [0.15, 0.4],   # Medium biomass
            [0.25, 0.6],   # High biomass
        ])
        
        predictions = mdl.predict(realistic_values)
        
        # Check that predictions are reasonable (0-50 kg range)
        assert len(predictions) == 3
        assert np.all(predictions >= 0)
        assert np.all(predictions <= 50), f"Unrealistic high predictions: {predictions}"

    def test_model_predict_single_sample(self):
        """Test model prediction for a single sample."""
        model_path = "models/biomass_rf.pkl"
        
        if not os.path.exists(model_path):
            pytest.skip("Model file not found. Run the biomass regression notebook first.")
        
        mdl = load(model_path)
        
        # Single sample
        x_single = np.array([[0.1, 0.3]])
        y_single = mdl.predict(x_single)
        
        assert y_single.shape == (1,)
        assert y_single[0] >= 0

    def test_model_feature_importance(self):
        """Test that the model has feature importance attributes."""
        model_path = "models/biomass_rf.pkl"
        
        if not os.path.exists(model_path):
            pytest.skip("Model file not found. Run the biomass regression notebook first.")
        
        mdl = load(model_path)
        
        # Random Forest should have feature_importances_ attribute
        assert hasattr(mdl, 'feature_importances_'), "Model should have feature importance"
        assert len(mdl.feature_importances_) == 2, "Should have importance for 2 features (FAI, NDRE)"
        assert np.allclose(np.sum(mdl.feature_importances_), 1.0), "Feature importances should sum to 1"

    def test_model_with_edge_cases(self):
        """Test model with edge case values."""
        model_path = "models/biomass_rf.pkl"
        
        if not os.path.exists(model_path):
            pytest.skip("Model file not found. Run the biomass regression notebook first.")
        
        mdl = load(model_path)
        
        # Edge cases
        edge_cases = np.array([
            [0.0, 0.0],     # Minimum values
            [-0.05, -0.2],  # Lower bounds
            [0.3, 0.8],     # Upper bounds
        ])
        
        predictions = mdl.predict(edge_cases)
        
        assert len(predictions) == 3
        assert np.all(predictions >= 0), "All predictions should be non-negative"
        assert np.all(np.isfinite(predictions)), "All predictions should be finite" 