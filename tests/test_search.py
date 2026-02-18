"""
Unit tests for EMIT L2A RFL search functionality.
"""
import pytest
from datetime import date, datetime
from unittest.mock import Mock, patch, MagicMock

from EMITL2ARFL.search_EMIT_L2A_RFL_granules import search_EMIT_L2A_RFL_granules
from EMITL2ARFL.constants import EMIT_L2A_REFLECTANCE_CONCEPT_ID


class TestSearchGranules:
    """Test suite for granule search functionality."""
    
    @patch('EMITL2ARFL.search_earthaccess_granules.search_earthaccess_granules')
    def test_search_by_date_range(self, mock_search):
        """Test searching for granules by date range."""
        # Setup mock
        mock_granules = [Mock(), Mock()]
        mock_search.return_value = mock_granules
        
        # Execute search
        start = date(2023, 8, 1)
        end = date(2023, 8, 31)
        results = search_EMIT_L2A_RFL_granules(
            start_UTC=start,
            end_UTC=end
        )
        
        # Verify
        assert results == mock_granules
        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs['concept_ID'] == EMIT_L2A_REFLECTANCE_CONCEPT_ID
        assert call_kwargs['start_UTC'] == start
        assert call_kwargs['end_UTC'] == end
    
    @patch('EMITL2ARFL.search_earthaccess_granules.search_earthaccess_granules')
    def test_search_by_date_string(self, mock_search):
        """Test searching with date strings."""
        mock_search.return_value = []
        
        results = search_EMIT_L2A_RFL_granules(
            start_UTC="2023-08-01",
            end_UTC="2023-08-31"
        )
        
        assert results == []
        mock_search.assert_called_once()
    
    @patch('EMITL2ARFL.search_earthaccess_granules.search_earthaccess_granules')
    def test_search_by_orbit_and_scene(self, mock_search):
        """Test searching for specific orbit and scene."""
        mock_search.return_value = [Mock()]
        
        orbit = 12345
        scene = 42
        
        results = search_EMIT_L2A_RFL_granules(
            orbit=orbit,
            scene=scene,
            start_UTC="2023-01-01",
            end_UTC="2023-12-31"
        )
        
        # Verify readable_granule_name was constructed correctly
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs['readable_granule_name'] == f"*{orbit}_{scene:03d}*"
    
    @patch('EMITL2ARFL.search_earthaccess_granules.search_earthaccess_granules')
    def test_search_with_geometry(self, mock_search):
        """Test searching with spatial geometry constraint."""
        from rasters import Point
        
        mock_search.return_value = []
        
        # Create a point geometry
        location = Point(-118.5, 36.5, crs=4326)
        
        results = search_EMIT_L2A_RFL_granules(
            start_UTC="2023-08-01",
            end_UTC="2023-08-31",
            geometry=location
        )
        
        # Verify geometry was passed
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs['geometry'] == location
    
    @patch('EMITL2ARFL.search_earthaccess_granules.search_earthaccess_granules')
    def test_search_no_results(self, mock_search):
        """Test handling when no granules are found."""
        mock_search.return_value = []
        
        results = search_EMIT_L2A_RFL_granules(
            start_UTC="2020-01-01",  # Before EMIT launch
            end_UTC="2020-01-31"
        )
        
        assert results == []
        assert isinstance(results, list)
    
    @patch('EMITL2ARFL.search_earthaccess_granules.search_earthaccess_granules')
    def test_search_with_datetime(self, mock_search):
        """Test searching with datetime objects."""
        mock_search.return_value = []
        
        start = datetime(2023, 8, 1, 12, 0, 0)
        end = datetime(2023, 8, 1, 18, 0, 0)
        
        results = search_EMIT_L2A_RFL_granules(
            start_UTC=start,
            end_UTC=end
        )
        
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs['start_UTC'] == start
        assert call_kwargs['end_UTC'] == end


class TestSearchEdgeCases:
    """Test edge cases and error handling in search."""
    
    @patch('EMITL2ARFL.search_earthaccess_granules.search_earthaccess_granules')
    def test_search_single_day(self, mock_search):
        """Test searching for a single day."""
        mock_search.return_value = [Mock()]
        
        single_date = date(2023, 8, 15)
        results = search_EMIT_L2A_RFL_granules(
            start_UTC=single_date,
            end_UTC=single_date
        )
        
        assert len(results) == 1
    
    @patch('EMITL2ARFL.search_earthaccess_granules.search_earthaccess_granules')
    def test_search_with_polygon_geometry(self, mock_search):
        """Test searching with polygon geometry."""
        from rasters import BBox
        
        mock_search.return_value = []
        
        bbox = BBox(xmin=-119.0, ymin=36.0, xmax=-118.0, ymax=37.0, crs=4326)
        
        results = search_EMIT_L2A_RFL_granules(
            start_UTC="2023-08-01",
            end_UTC="2023-08-31",
            geometry=bbox
        )
        
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs['geometry'] == bbox
    
    @patch('EMITL2ARFL.search_earthaccess_granules.search_earthaccess_granules')
    def test_search_orbit_without_scene(self, mock_search):
        """Test that orbit alone doesn't create readable_granule_name."""
        mock_search.return_value = []
        
        results = search_EMIT_L2A_RFL_granules(
            orbit=12345,
            start_UTC="2023-01-01",
            end_UTC="2023-12-31"
        )
        
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs['readable_granule_name'] is None
    
    @patch('EMITL2ARFL.search_earthaccess_granules.search_earthaccess_granules')
    def test_search_scene_without_orbit(self, mock_search):
        """Test that scene alone doesn't create readable_granule_name."""
        mock_search.return_value = []
        
        results = search_EMIT_L2A_RFL_granules(
            scene=42,
            start_UTC="2023-01-01",
            end_UTC="2023-12-31"
        )
        
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs['readable_granule_name'] is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
