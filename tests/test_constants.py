"""
Unit tests for EMIT L2A RFL constants and configuration.
"""
import pytest
from EMITL2ARFL import constants


class TestConstants:
    """Test suite for package constants."""
    
    def test_emit_concept_id(self):
        """Test EMIT concept ID is properly defined."""
        assert hasattr(constants, 'EMIT_L2A_REFLECTANCE_CONCEPT_ID')
        assert isinstance(constants.EMIT_L2A_REFLECTANCE_CONCEPT_ID, str)
        assert len(constants.EMIT_L2A_REFLECTANCE_CONCEPT_ID) > 0
        assert 'LPCLOUD' in constants.EMIT_L2A_REFLECTANCE_CONCEPT_ID
    
    def test_emit_short_name(self):
        """Test EMIT short name is correct."""
        assert constants.EMIT_L2A_REFLECTANCE_SHORT_NAME == "EMITL2ARFL"
    
    def test_emit_doi(self):
        """Test EMIT DOI is properly formatted."""
        assert hasattr(constants, 'EMIT_L2A_REFLECTANCE_DOI')
        assert constants.EMIT_L2A_REFLECTANCE_DOI.startswith("10.5067")
        assert "EMIT" in constants.EMIT_L2A_REFLECTANCE_DOI
    
    def test_download_directory(self):
        """Test default download directory is defined."""
        assert hasattr(constants, 'DOWNLOAD_DIRECTORY')
        assert isinstance(constants.DOWNLOAD_DIRECTORY, str)
        assert len(constants.DOWNLOAD_DIRECTORY) > 0
    
    def test_quality_bands(self):
        """Test quality bands are properly defined."""
        assert hasattr(constants, 'QUALITY_BANDS')
        assert isinstance(constants.QUALITY_BANDS, list)
        assert len(constants.QUALITY_BANDS) == 5
        assert all(isinstance(b, int) for b in constants.QUALITY_BANDS)
        assert 0 in constants.QUALITY_BANDS
    
    def test_glt_nodata_value(self):
        """Test GLT nodata value is defined."""
        assert hasattr(constants, 'GLT_NODATA_VALUE')
        assert constants.GLT_NODATA_VALUE == 0
    
    def test_fill_value(self):
        """Test fill value is defined."""
        assert hasattr(constants, 'FILL_VALUE')
        assert constants.FILL_VALUE == -9999
    
    def test_engine(self):
        """Test netCDF engine is specified."""
        assert hasattr(constants, 'ENGINE')
        assert constants.ENGINE == "netcdf4"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
