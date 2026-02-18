"""
Unit tests for EMIT L2A RFL time-series generation.
"""
import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
import os

from EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries import generate_EMIT_L2A_RFL_timeseries
from EMITL2ARFL.exceptions import EMITNotAvailable


class TestTimeSeriesGeneration:
    """Test suite for time-series generation."""
    
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.retrieve_EMIT_L2A_RFL')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.exists')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.os.path.join')
    def test_generate_timeseries_single_date(self, mock_join, mock_exists, mock_retrieve):
        """Test generating time-series for a single date."""
        from rasters import Point
        
        # Setup mocks
        mock_exists.return_value = False
        mock_join.side_effect = lambda d, f: f"{d}/{f}"
        
        mock_cube = Mock()
        mock_cube.to_geotiff = Mock()
        mock_retrieve.return_value = mock_cube
        
        # Execute
        location = Point(-118.5, 36.5, crs=4326)
        filenames = generate_EMIT_L2A_RFL_timeseries(
            start_date_UTC=date(2023, 8, 15),
            end_date_UTC=date(2023, 8, 15),
            geometry=location,
            output_directory="/tmp/emit_output"
        )
        
        # Verify
        assert len(filenames) == 1
        assert "20230815" in filenames[0]
        mock_retrieve.assert_called_once()
        mock_cube.to_geotiff.assert_called_once()
    
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.retrieve_EMIT_L2A_RFL')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.exists')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.os.path.join')
    def test_generate_timeseries_date_range(self, mock_join, mock_exists, mock_retrieve):
        """Test generating time-series for multiple dates."""
        from rasters import Point
        
        # Setup mocks
        mock_exists.return_value = False
        mock_join.side_effect = lambda d, f: f"{d}/{f}"
        
        mock_cube = Mock()
        mock_cube.to_geotiff = Mock()
        mock_retrieve.return_value = mock_cube
        
        # Execute - 5 day range
        location = Point(-118.5, 36.5, crs=4326)
        filenames = generate_EMIT_L2A_RFL_timeseries(
            start_date_UTC=date(2023, 8, 1),
            end_date_UTC=date(2023, 8, 5),
            geometry=location,
            output_directory="/tmp/emit_output"
        )
        
        # Verify
        assert len(filenames) == 5
        assert mock_retrieve.call_count == 5
        assert mock_cube.to_geotiff.call_count == 5
    
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.retrieve_EMIT_L2A_RFL')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.exists')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.os.path.join')
    def test_generate_timeseries_skips_existing_files(self, mock_join, mock_exists, mock_retrieve):
        """Test that existing files are not regenerated."""
        from rasters import Point
        
        # Setup mocks - first file exists, second doesn't
        mock_join.side_effect = lambda d, f: f"{d}/{f}"
        mock_exists.side_effect = [True, False]  # First exists, second doesn't
        
        mock_cube = Mock()
        mock_cube.to_geotiff = Mock()
        mock_retrieve.return_value = mock_cube
        
        # Execute
        location = Point(-118.5, 36.5, crs=4326)
        filenames = generate_EMIT_L2A_RFL_timeseries(
            start_date_UTC=date(2023, 8, 1),
            end_date_UTC=date(2023, 8, 2),
            geometry=location,
            output_directory="/tmp/emit_output"
        )
        
        # Verify
        assert len(filenames) == 2
        # Only retrieve for the file that didn't exist
        assert mock_retrieve.call_count == 1
        assert mock_cube.to_geotiff.call_count == 1
    
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.retrieve_EMIT_L2A_RFL')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.exists')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.os.path.join')
    def test_generate_timeseries_handles_no_data(self, mock_join, mock_exists, mock_retrieve):
        """Test handling when no data is available for some dates."""
        from rasters import Point
        
        # Setup mocks
        mock_exists.return_value = False
        mock_join.side_effect = lambda d, f: f"{d}/{f}"
        
        # First date has data, second raises exception, third has data
        mock_cube = Mock()
        mock_cube.to_geotiff = Mock()
        mock_retrieve.side_effect = [
            mock_cube,
            EMITNotAvailable("No data"),
            mock_cube
        ]
        
        # Execute
        location = Point(-118.5, 36.5, crs=4326)
        filenames = generate_EMIT_L2A_RFL_timeseries(
            start_date_UTC=date(2023, 8, 1),
            end_date_UTC=date(2023, 8, 3),
            geometry=location,
            output_directory="/tmp/emit_output"
        )
        
        # Verify - only 2 files generated (skipped the one with no data)
        assert len(filenames) == 2
        assert mock_retrieve.call_count == 3
        assert mock_cube.to_geotiff.call_count == 2
    
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.retrieve_EMIT_L2A_RFL')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.exists')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.os.path.join')
    def test_generate_timeseries_with_string_dates(self, mock_join, mock_exists, mock_retrieve):
        """Test time-series generation with date strings."""
        from rasters import Point
        
        # Setup mocks
        mock_exists.return_value = False
        mock_join.side_effect = lambda d, f: f"{d}/{f}"
        
        mock_cube = Mock()
        mock_cube.to_geotiff = Mock()
        mock_retrieve.return_value = mock_cube
        
        # Execute with string dates
        location = Point(-118.5, 36.5, crs=4326)
        filenames = generate_EMIT_L2A_RFL_timeseries(
            start_date_UTC="2023-08-01",
            end_date_UTC="2023-08-03",
            geometry=location,
            output_directory="/tmp/emit_output"
        )
        
        # Verify
        assert len(filenames) == 3
    
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.retrieve_EMIT_L2A_RFL')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.exists')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.os.path.join')
    def test_generate_timeseries_uses_custom_download_dir(self, mock_join, mock_exists, mock_retrieve):
        """Test that custom download directory is passed through."""
        from rasters import Point
        
        # Setup mocks
        mock_exists.return_value = False
        mock_join.side_effect = lambda d, f: f"{d}/{f}"
        
        mock_cube = Mock()
        mock_cube.to_geotiff = Mock()
        mock_retrieve.return_value = mock_cube
        
        # Execute with custom download directory
        location = Point(-118.5, 36.5, crs=4326)
        custom_download = "/custom/download/path"
        filenames = generate_EMIT_L2A_RFL_timeseries(
            start_date_UTC=date(2023, 8, 15),
            end_date_UTC=date(2023, 8, 15),
            geometry=location,
            output_directory="/tmp/emit_output",
            download_directory=custom_download
        )
        
        # Verify download directory was passed
        call_kwargs = mock_retrieve.call_args[1]
        assert call_kwargs['download_directory'] == custom_download
    
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.retrieve_EMIT_L2A_RFL')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.exists')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.os.path.join')
    def test_generate_timeseries_filename_format(self, mock_join, mock_exists, mock_retrieve):
        """Test that output filenames follow the correct format."""
        from rasters import Point
        
        # Setup mocks
        mock_exists.return_value = False
        actual_filenames = []
        
        def join_side_effect(d, f):
            result = f"{d}/{f}"
            actual_filenames.append(f)
            return result
        
        mock_join.side_effect = join_side_effect
        
        mock_cube = Mock()
        mock_cube.to_geotiff = Mock()
        mock_retrieve.return_value = mock_cube
        
        # Execute
        location = Point(-118.5, 36.5, crs=4326)
        filenames = generate_EMIT_L2A_RFL_timeseries(
            start_date_UTC=date(2023, 8, 15),
            end_date_UTC=date(2023, 8, 15),
            geometry=location,
            output_directory="/tmp/emit_output"
        )
        
        # Verify filename format
        assert len(actual_filenames) == 1
        assert actual_filenames[0] == "EMIT_L2A_RFL_20230815.tif"
        assert actual_filenames[0].startswith("EMIT_L2A_RFL_")
        assert actual_filenames[0].endswith(".tif")


class TestTimeSeriesEdgeCases:
    """Test edge cases in time-series generation."""
    
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.retrieve_EMIT_L2A_RFL')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.exists')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.os.path.join')
    def test_generate_timeseries_long_range(self, mock_join, mock_exists, mock_retrieve):
        """Test generating time-series for a long date range."""
        from rasters import Point
        
        # Setup mocks
        mock_exists.return_value = False
        mock_join.side_effect = lambda d, f: f"{d}/{f}"
        
        mock_cube = Mock()
        mock_cube.to_geotiff = Mock()
        mock_retrieve.return_value = mock_cube
        
        # Execute - 30 day range
        location = Point(-118.5, 36.5, crs=4326)
        filenames = generate_EMIT_L2A_RFL_timeseries(
            start_date_UTC=date(2023, 8, 1),
            end_date_UTC=date(2023, 8, 30),
            geometry=location,
            output_directory="/tmp/emit_output"
        )
        
        # Verify
        assert len(filenames) == 30
    
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.retrieve_EMIT_L2A_RFL')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.exists')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.os.path.join')
    def test_generate_timeseries_all_exist(self, mock_join, mock_exists, mock_retrieve):
        """Test when all output files already exist."""
        from rasters import Point
        
        # Setup mocks - all files exist
        mock_exists.return_value = True
        mock_join.side_effect = lambda d, f: f"{d}/{f}"
        
        # Execute
        location = Point(-118.5, 36.5, crs=4326)
        filenames = generate_EMIT_L2A_RFL_timeseries(
            start_date_UTC=date(2023, 8, 1),
            end_date_UTC=date(2023, 8, 3),
            geometry=location,
            output_directory="/tmp/emit_output"
        )
        
        # Verify - no retrieval or saving occurred
        assert len(filenames) == 3
        mock_retrieve.assert_not_called()
    
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.retrieve_EMIT_L2A_RFL')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.exists')
    @patch('EMITL2ARFL.generate_EMIT_L2A_RFL_timeseries.os.path.join')
    def test_generate_timeseries_all_no_data(self, mock_join, mock_exists, mock_retrieve):
        """Test when no data is available for entire time period."""
        from rasters import Point
        
        # Setup mocks - all retrievals fail
        mock_exists.return_value = False
        mock_join.side_effect = lambda d, f: f"{d}/{f}"
        mock_retrieve.side_effect = EMITNotAvailable("No data")
        
        # Execute
        location = Point(-118.5, 36.5, crs=4326)
        filenames = generate_EMIT_L2A_RFL_timeseries(
            start_date_UTC=date(2020, 1, 1),  # Before EMIT
            end_date_UTC=date(2020, 1, 3),
            geometry=location,
            output_directory="/tmp/emit_output"
        )
        
        # Verify - empty list returned
        assert len(filenames) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
