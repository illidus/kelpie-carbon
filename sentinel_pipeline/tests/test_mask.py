"""Tests for the mask module."""

from datetime import datetime
from unittest.mock import patch

import numpy as np
import pytest

from sentinel_pipeline.mask import apply_cloud_mask, filter_by_tide


class TestApplyCloudMask:
    """Test cases for apply_cloud_mask function."""

    def test_apply_cloud_mask_same_shape(self):
        """Test cloud mask with same shape arrays."""
        img = np.random.rand(100, 100, 3)
        qa = np.random.randint(0, 255, (100, 100))

        result = apply_cloud_mask(img, qa)

        assert result.shape == img.shape
        assert isinstance(result, np.ndarray)
        np.testing.assert_array_equal(result, img)  # Placeholder returns copy

    def test_apply_cloud_mask_different_shapes(self):
        """Test cloud mask with incompatible array shapes."""
        img = np.random.rand(100, 100, 3)
        qa = np.random.randint(0, 255, (50, 50))

        with pytest.raises(ValueError, match="compatible spatial dimensions"):
            apply_cloud_mask(img, qa)

    def test_apply_cloud_mask_multispectral(self):
        """Test cloud mask with multispectral image."""
        img = np.random.rand(200, 200, 6)  # 6-band image
        qa = np.random.randint(0, 255, (200, 200))

        result = apply_cloud_mask(img, qa)

        assert result.shape == img.shape
        assert result.dtype == img.dtype


class TestFilterByTide:
    """Test cases for filter_by_tide function."""

    @pytest.fixture
    def mock_tide_response(self):
        """Mock tide API response."""
        return {
            "data": [
                {"datetime": "2023-10-15T12:00:00Z", "height": 2.5, "type": "high"},
                {"datetime": "2023-10-15T18:30:00Z", "height": 0.8, "type": "low"},
            ],
            "station": "test_station",
            "units": "meters",
        }

    @pytest.fixture
    def mock_invalid_tide_response(self):
        """Mock invalid tide API response."""
        return {
            "station": "test_station",
            "units": "meters"
            # Missing 'data' field
        }

    def test_filter_by_tide_valid_response(self, mock_tide_response):
        """Test tide filter with valid API response."""
        scene_datetime = datetime(2023, 10, 15, 12, 0, 0)

        result = filter_by_tide(scene_datetime, mock_tide_response)

        assert isinstance(result, bool)
        assert result is True  # Placeholder implementation returns True

    def test_filter_by_tide_missing_data_field(self, mock_invalid_tide_response):
        """Test tide filter with missing data field."""
        scene_datetime = datetime(2023, 10, 15, 12, 0, 0)

        with pytest.raises(KeyError, match="Missing 'data' field"):
            filter_by_tide(scene_datetime, mock_invalid_tide_response)

    def test_filter_by_tide_empty_data(self):
        """Test tide filter with empty data array."""
        scene_datetime = datetime(2023, 10, 15, 12, 0, 0)
        empty_response = {"data": []}

        result = filter_by_tide(scene_datetime, empty_response)

        assert result is True  # Placeholder implementation

    @patch("sentinel_pipeline.mask.datetime")
    def test_filter_by_tide_with_mocked_datetime(
        self, mock_datetime, mock_tide_response
    ):
        """Test tide filter with mocked datetime module."""
        # Mock the current time
        mock_datetime.now.return_value = datetime(2023, 10, 15, 14, 0, 0)

        scene_datetime = datetime(2023, 10, 15, 12, 0, 0)
        result = filter_by_tide(scene_datetime, mock_tide_response)

        assert result is True

    def test_filter_by_tide_various_datetime_formats(self, mock_tide_response):
        """Test tide filter with various datetime inputs."""
        test_datetimes = [
            datetime(2023, 10, 15, 6, 0, 0),
            datetime(2023, 10, 15, 12, 30, 0),
            datetime(2023, 10, 15, 23, 59, 59),
        ]

        for dt in test_datetimes:
            result = filter_by_tide(dt, mock_tide_response)
            assert isinstance(result, bool)


class TestMaskIntegration:
    """Integration tests for mask module functions."""

    def test_mask_pipeline_integration(self, mock_tide_response=None):
        """Test integration of cloud masking and tide filtering."""
        if mock_tide_response is None:
            mock_tide_response = {
                "data": [
                    {"datetime": "2023-10-15T12:00:00Z", "height": 1.5, "type": "mid"}
                ]
            }

        # Create test data
        img = np.random.rand(50, 50, 4)
        qa = np.random.randint(0, 255, (50, 50))
        scene_datetime = datetime(2023, 10, 15, 12, 0, 0)

        # Apply cloud mask
        masked_img = apply_cloud_mask(img, qa)

        # Filter by tide
        tide_filter_result = filter_by_tide(scene_datetime, mock_tide_response)

        # Both operations should succeed
        assert masked_img.shape == img.shape
        assert isinstance(tide_filter_result, bool)
