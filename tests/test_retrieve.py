"""
Unit tests for EMIT L2A RFL data retrieval functionality.
"""
import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

from EMITL2ARFL.retrieve_EMIT_L2A_RFL import retrieve_EMIT_L2A_RFL
from EMITL2ARFL.exceptions import EMITNotAvailable


class TestRetrieveEMITData:
    """Test suite for EMIT data retrieval."""
    
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL.retrieve_EMIT_L2A_RFL_granule')
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL.search_EMIT_L2A_RFL_granules')
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL.rt.mosaic')
    def test_retrieve_single_granule(self, mock_mosaic, mock_search, mock_retrieve_granule):
        """Test retrieving data when one granule covers the area."""
        from rasters import Point
        
        # Setup mocks
        mock_search_result = Mock()
        mock_search.return_value = [mock_search_result]
        
        mock_granule = Mock()
        mock_cube = Mock()
        mock_granule.reflectance.return_value = mock_cube
        mock_retrieve_granule.return_value = mock_granule
        
        mock_merged = Mock()
        mock_mosaic.return_value = mock_merged
        
        # Execute
        location = Point(-118.5, 36.5, crs=4326)
        result = retrieve_EMIT_L2A_RFL(
            date_UTC=date(2023, 8, 15),
            geometry=location,
            download_directory="/tmp/emit"
        )
        
        # Verify
        assert result == mock_merged
        mock_search.assert_called_once()
        mock_retrieve_granule.assert_called_once_with(
            remote_granule=mock_search_result,
            download_directory="/tmp/emit"
        )
        mock_granule.reflectance.assert_called_once_with(geometry=location)
        mock_mosaic.assert_called_once()
    
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL.retrieve_EMIT_L2A_RFL_granule')
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL.search_EMIT_L2A_RFL_granules')
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL.rt.mosaic')
    def test_retrieve_multiple_granules(self, mock_mosaic, mock_search, mock_retrieve_granule):
        """Test retrieving and merging multiple granules."""
        from rasters import BBox
        
        # Setup mocks - simulate 3 granules covering the area
        mock_search_results = [Mock(), Mock(), Mock()]
        mock_search.return_value = mock_search_results
        
        mock_granules = [Mock(), Mock(), Mock()]
        mock_cubes = [Mock(), Mock(), Mock()]
        
        for granule, cube in zip(mock_granules, mock_cubes):
            granule.reflectance.return_value = cube
        
        mock_retrieve_granule.side_effect = mock_granules
        
        mock_merged = Mock()
        mock_mosaic.return_value = mock_merged
        
        # Execute
        bbox = BBox(xmin=-119.0, ymin=36.0, xmax=-118.0, ymax=37.0, crs=4326)
        result = retrieve_EMIT_L2A_RFL(
            date_UTC=date(2023, 8, 15),
            geometry=bbox
        )
        
        # Verify
        assert result == mock_merged
        assert mock_retrieve_granule.call_count == 3
        assert mock_mosaic.call_count == 1
        
        # Check that mosaic was called with all cubes
        mosaic_call_args = mock_mosaic.call_args[0]
        assert len(mosaic_call_args[0]) == 3
    
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL.search_EMIT_L2A_RFL_granules')
    def test_retrieve_no_data_available(self, mock_search):
        """Test handling when no granules are available."""
        from rasters import Point
        
        # Setup mock - no granules found
        mock_search.return_value = []
        
        # Execute and verify exception
        location = Point(-118.5, 36.5, crs=4326)
        
        with pytest.raises(EMITNotAvailable) as exc_info:
            retrieve_EMIT_L2A_RFL(
                date_UTC=date(2020, 1, 1),  # Before EMIT
                geometry=location
            )
        
        assert "No EMIT L2A RFL granules found" in str(exc_info.value)
    
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL.retrieve_EMIT_L2A_RFL_granule')
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL.search_EMIT_L2A_RFL_granules')
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL.rt.mosaic')
    def test_retrieve_with_string_date(self, mock_mosaic, mock_search, mock_retrieve_granule):
        """Test retrieving with date as string."""
        from rasters import Point
        
        # Setup mocks
        mock_search.return_value = [Mock()]
        mock_granule = Mock()
        mock_granule.reflectance.return_value = Mock()
        mock_retrieve_granule.return_value = mock_granule
        mock_mosaic.return_value = Mock()
        
        # Execute
        location = Point(-118.5, 36.5, crs=4326)
        result = retrieve_EMIT_L2A_RFL(
            date_UTC="2023-08-15",
            geometry=location
        )
        
        # Verify it worked
        assert result is not None
        mock_search.assert_called_once()
    
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL.retrieve_EMIT_L2A_RFL_granule')
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL.search_EMIT_L2A_RFL_granules')
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL.rt.mosaic')
    def test_retrieve_uses_default_download_directory(self, mock_mosaic, mock_search, mock_retrieve_granule):
        """Test that default download directory is used when not specified."""
        from rasters import Point
        from EMITL2ARFL.constants import DOWNLOAD_DIRECTORY
        
        # Setup mocks
        mock_search.return_value = [Mock()]
        mock_granule = Mock()
        mock_granule.reflectance.return_value = Mock()
        mock_retrieve_granule.return_value = mock_granule
        mock_mosaic.return_value = Mock()
        
        # Execute without download_directory
        location = Point(-118.5, 36.5, crs=4326)
        retrieve_EMIT_L2A_RFL(
            date_UTC=date(2023, 8, 15),
            geometry=location
        )
        
        # Verify default was used
        call_kwargs = mock_retrieve_granule.call_args[1]
        assert call_kwargs['download_directory'] == DOWNLOAD_DIRECTORY


class TestRetrieveGranule:
    """Test suite for individual granule retrieval."""
    
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL_granule.EMITL2ARFLGranule')
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL_granule.earthaccess.download')
    def test_retrieve_granule_downloads_file(self, mock_download, mock_granule_class):
        """Test that granule retrieval downloads the file."""
        from EMITL2ARFL.retrieve_EMIT_L2A_RFL_granule import retrieve_EMIT_L2A_RFL_granule
        
        # Setup mocks
        mock_remote = Mock()
        mock_local_path = "/tmp/emit/granule.nc"
        mock_download.return_value = [mock_local_path]
        
        mock_granule_instance = Mock()
        mock_granule_class.return_value = mock_granule_instance
        
        # Execute
        result = retrieve_EMIT_L2A_RFL_granule(
            remote_granule=mock_remote,
            download_directory="/tmp/emit"
        )
        
        # Verify
        assert result == mock_granule_instance
        mock_download.assert_called_once()
        mock_granule_class.assert_called_once_with(mock_local_path)
    
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL_granule.EMITL2ARFLGranule')
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL_granule.earthaccess.download')
    @patch('EMITL2ARFL.retrieve_EMIT_L2A_RFL_granule.exists')
    def test_retrieve_granule_uses_cached_file(self, mock_exists, mock_download, mock_granule_class):
        """Test that cached files are reused."""
        from EMITL2ARFL.retrieve_EMIT_L2A_RFL_granule import retrieve_EMIT_L2A_RFL_granule
        
        # Setup mocks - file already exists
        mock_remote = Mock()
        mock_remote.__getitem__ = Mock(side_effect=lambda k: "test_granule.nc" if k == "meta" else {"native-id": "test_granule.nc"})
        
        mock_exists.return_value = True
        mock_granule_instance = Mock()
        mock_granule_class.return_value = mock_granule_instance
        
        # Execute
        result = retrieve_EMIT_L2A_RFL_granule(
            remote_granule=mock_remote,
            download_directory="/tmp/emit"
        )
        
        # Verify download was not called
        mock_download.assert_not_called()
        assert result == mock_granule_instance


class TestDataQuality:
    """Test suite for data quality and masking."""
    
    def test_quality_mask_bands(self):
        """Test that quality bands constant is correct."""
        from EMITL2ARFL.constants import QUALITY_BANDS
        
        # EMIT quality mask has specific bands
        assert isinstance(QUALITY_BANDS, list)
        assert len(QUALITY_BANDS) == 5
        assert 0 in QUALITY_BANDS


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
