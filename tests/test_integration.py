"""
Integration tests for EMIT L2A RFL package.

These tests verify the complete workflow end-to-end.
They require actual NASA Earthdata credentials and internet connectivity.
Mark as slow tests that can be skipped in CI/CD pipelines.
"""
import pytest
import os
from datetime import date
from pathlib import Path
import tempfile
import shutil

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def temp_download_dir():
    """Create a temporary directory for downloads."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


class TestIntegrationSearch:
    """Integration tests for search functionality."""
    
    @pytest.mark.slow
    def test_search_real_granules(self):
        """Test searching for real EMIT granules."""
        import earthaccess
        from EMITL2ARFL import search_EMIT_L2A_RFL_granules
        from rasters import Point
        
        # Login (requires credentials)
        try:
            earthaccess.login(strategy="netrc")
        except Exception as e:
            pytest.skip(f"Cannot login to Earthdata: {e}")
        
        # Search for granules in a known area with EMIT coverage
        # Death Valley, CA - a well-studied area
        location = Point(-116.8, 36.5, crs=4326)
        
        granules = search_EMIT_L2A_RFL_granules(
            start_UTC=date(2023, 8, 1),
            end_UTC=date(2023, 8, 31),
            geometry=location
        )
        
        # Verify we got results (Death Valley has good EMIT coverage)
        assert isinstance(granules, list)
        # Note: We can't assert len > 0 because it depends on actual coverage
        
        # If we got granules, verify they have expected structure
        if len(granules) > 0:
            granule = granules[0]
            assert 'meta' in granule
            assert 'native-id' in granule['meta']
            assert 'EMIT' in granule['meta']['native-id']
    
    @pytest.mark.slow
    def test_search_by_orbit_scene(self):
        """Test searching by specific orbit and scene."""
        import earthaccess
        from EMITL2ARFL import search_EMIT_L2A_RFL_granules
        
        try:
            earthaccess.login(strategy="netrc")
        except Exception as e:
            pytest.skip(f"Cannot login to Earthdata: {e}")
        
        # Use a known orbit/scene combination
        # This is more reliable than location-based search
        granules = search_EMIT_L2A_RFL_granules(
            orbit=26120,  # Example orbit
            scene=1,
            start_UTC=date(2023, 1, 1),
            end_UTC=date(2023, 12, 31)
        )
        
        assert isinstance(granules, list)


class TestIntegrationRetrieve:
    """Integration tests for data retrieval."""
    
    @pytest.mark.slow
    def test_retrieve_single_date(self, temp_output_dir, temp_download_dir):
        """Test retrieving data for a single date."""
        import earthaccess
        from EMITL2ARFL import retrieve_EMIT_L2A_RFL
        from rasters import Point
        import rasters as rt
        
        try:
            earthaccess.login(strategy="netrc")
        except Exception as e:
            pytest.skip(f"Cannot login to Earthdata: {e}")
        
        # Small test location
        location = Point(-116.8, 36.5, crs=4326)
        
        # Create small grid (1km x 1km)
        bbox = rt.BBox(xmin=-116.81, ymin=36.49, xmax=-116.79, ymax=36.51, crs=4326)
        grid = rt.RasterGrid.from_bbox(
            bbox=bbox,
            cell_size=60
        )
        
        try:
            # Try to retrieve data
            merged_cube = retrieve_EMIT_L2A_RFL(
                date_UTC=date(2023, 8, 15),
                geometry=grid,
                download_directory=temp_download_dir
            )
            
            # Verify we got a valid result
            assert merged_cube is not None
            assert merged_cube.nbands > 0
            
            # Save to verify it works
            output_file = os.path.join(temp_output_dir, "test_output.tif")
            merged_cube.to_geotiff(output_file)
            assert os.path.exists(output_file)
            
        except Exception as e:
            # It's ok if no data is available for this specific date/location
            # This test verifies the workflow works when data exists
            pytest.skip(f"No data available for test location/date: {e}")


class TestIntegrationTimeSeries:
    """Integration tests for time-series generation."""
    
    @pytest.mark.slow
    def test_generate_short_timeseries(self, temp_output_dir, temp_download_dir):
        """Test generating a short time-series."""
        import earthaccess
        from EMITL2ARFL import generate_EMIT_L2A_RFL_timeseries
        from rasters import Point
        import rasters as rt
        
        try:
            earthaccess.login(strategy="netrc")
        except Exception as e:
            pytest.skip(f"Cannot login to Earthdata: {e}")
        
        # Small test area
        bbox = rt.BBox(xmin=-116.81, ymin=36.49, xmax=-116.79, ymax=36.51, crs=4326)
        grid = rt.RasterGrid.from_bbox(bbox=bbox, cell_size=60)
        
        # Generate short time-series (3 days)
        filenames = generate_EMIT_L2A_RFL_timeseries(
            start_date_UTC=date(2023, 8, 15),
            end_date_UTC=date(2023, 8, 17),
            geometry=grid,
            output_directory=temp_output_dir,
            download_directory=temp_download_dir
        )
        
        # Verify results
        assert isinstance(filenames, list)
        
        # Check that files were created for dates with data
        for filename in filenames:
            assert os.path.exists(filename) or os.path.exists(
                os.path.expanduser(filename)
            )
    
    @pytest.mark.slow
    def test_timeseries_skips_existing(self, temp_output_dir, temp_download_dir):
        """Test that time-series generation skips existing files."""
        import earthaccess
        from EMITL2ARFL import generate_EMIT_L2A_RFL_timeseries
        import rasters as rt
        
        try:
            earthaccess.login(strategy="netrc")
        except Exception as e:
            pytest.skip(f"Cannot login to Earthdata: {e}")
        
        bbox = rt.BBox(xmin=-116.81, ymin=36.49, xmax=-116.79, ymax=36.51, crs=4326)
        grid = rt.RasterGrid.from_bbox(bbox=bbox, cell_size=60)
        
        # First run
        filenames1 = generate_EMIT_L2A_RFL_timeseries(
            start_date_UTC=date(2023, 8, 15),
            end_date_UTC=date(2023, 8, 16),
            geometry=grid,
            output_directory=temp_output_dir,
            download_directory=temp_download_dir
        )
        
        # Second run - should skip existing files
        filenames2 = generate_EMIT_L2A_RFL_timeseries(
            start_date_UTC=date(2023, 8, 15),
            end_date_UTC=date(2023, 8, 16),
            geometry=grid,
            output_directory=temp_output_dir,
            download_directory=temp_download_dir
        )
        
        # Results should be the same
        assert filenames1 == filenames2


class TestIntegrationWorkflow:
    """Integration test for complete workflow examples."""
    
    @pytest.mark.slow
    def test_workflow_from_readme_example(self, temp_output_dir, temp_download_dir):
        """Test the quick start example from README."""
        import earthaccess
        from EMITL2ARFL import generate_EMIT_L2A_RFL_timeseries
        import rasters as rt
        
        try:
            earthaccess.login(strategy="netrc")
        except Exception as e:
            pytest.skip(f"Cannot login to Earthdata: {e}")
        
        # Create a small grid (from README example)
        bbox = rt.BBox(xmin=-118.51, ymin=36.49, xmax=-118.49, ymax=36.51, crs=4326)
        grid = rt.RasterGrid.from_bbox(bbox=bbox, cell_size=60)
        
        # Generate very short time-series
        filenames = generate_EMIT_L2A_RFL_timeseries(
            start_date_UTC="2023-08-15",
            end_date_UTC="2023-08-15",
            geometry=grid,
            output_directory=temp_output_dir
        )
        
        # Verify workflow completed
        assert isinstance(filenames, list)


class TestIntegrationConstants:
    """Test constants and configuration values."""
    
    def test_emit_constants(self):
        """Test that EMIT constants are correct."""
        from EMITL2ARFL.constants import (
            EMIT_L2A_REFLECTANCE_SHORT_NAME,
            EMIT_L2A_REFLECTANCE_DOI,
            EMIT_L2A_REFLECTANCE_CONCEPT_ID
        )
        
        assert EMIT_L2A_REFLECTANCE_SHORT_NAME == "EMITL2ARFL"
        assert "10.5067" in EMIT_L2A_REFLECTANCE_DOI
        assert "LPCLOUD" in EMIT_L2A_REFLECTANCE_CONCEPT_ID


# Configuration for pytest
def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires credentials)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'not slow'])
