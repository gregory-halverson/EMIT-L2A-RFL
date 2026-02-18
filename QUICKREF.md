# EMIT L2A RFL - Quick Reference Card

## Installation

```bash
pip install EMITL2ARFL  # From PyPI
pip install -e ".[dev]"  # Development mode with tests
```

## Setup Credentials

```bash
# Create .netrc file (recommended)
cat > ~/.netrc << EOF
machine urs.earthdata.nasa.gov
login YOUR_USERNAME
password YOUR_PASSWORD
EOF
chmod 600 ~/.netrc
```

## Generate Time-Series (Quick Start)

```python
import earthaccess
from EMITL2ARFL import generate_EMIT_L2A_RFL_timeseries
import rasters as rt

earthaccess.login()

bbox = rt.BBox(xmin=-118.51, ymin=36.49, xmax=-118.49, ymax=36.51, crs=4326)
grid = rt.RasterGrid.from_bbox(bbox=bbox, cell_size=60)

filenames = generate_EMIT_L2A_RFL_timeseries(
    start_date_UTC="2023-01-01",
    end_date_UTC="2023-12-31",
    geometry=grid,
    output_directory="./emit_data"
)
```

## Search for Data

```python
from EMITL2ARFL import search_EMIT_L2A_RFL_granules
from rasters import Point

location = Point(-118.5, 36.5, crs=4326)
granules = search_EMIT_L2A_RFL_granules(
    start_UTC="2023-07-01",
    end_UTC="2023-07-31",
    geometry=location
)
```

## Retrieve Single Date

```python
from EMITL2ARFL import retrieve_EMIT_L2A_RFL
from datetime import date

data = retrieve_EMIT_L2A_RFL(
    date_UTC=date(2023, 8, 15),
    geometry=grid
)
data.to_geotiff("output.tif")
```

## Run Tests

```bash
# Unit tests (fast)
pytest tests/ -v -m "not integration and not slow"

# With coverage
pytest tests/ --cov=EMITL2ARFL --cov-report=html

# Integration tests (requires credentials)
pytest tests/ -v -m "integration"

# Using test runner
python run_tests.py unit
python run_tests.py coverage
```

## Common Patterns

### From KML/Shapefile

```python
import geopandas as gpd
gdf = gpd.read_file("area.kml")
geometry = rt.Polygon(gdf.unary_union)
bbox_utm = geometry.UTM.bbox
grid = rt.RasterGrid.from_bbox(bbox_utm, cell_size=60, crs=bbox_utm.crs)
```

### Search by Orbit/Scene

```python
granules = search_EMIT_L2A_RFL_granules(
    orbit=12345,
    scene=42,
    start_UTC="2023-01-01",
    end_UTC="2023-12-31"
)
```

### With Quality Masking

```python
granule = retrieve_EMIT_L2A_RFL_granule(remote_granule=search_results[0])
clean_data = granule.reflectance(apply_mask=True)
```

## Key Parameters

- `start_date_UTC` / `end_date_UTC`: date, datetime, or "YYYY-MM-DD" string
- `geometry`: Point, Polygon, BBox, or RasterGeometry
- `cell_size`: 60 (EMIT native resolution in meters)
- `output_directory`: Where to save GeoTIFF files
- `download_directory`: Where to cache downloaded granules (default: `~/data/EMIT_L2A_RFL`)

## Data Specs

- **Resolution**: 60m
- **Spectral Range**: 380-2500 nm
- **Bands**: ~285
- **Coverage**: ±52° latitude (ISS orbit)
- **Available**: August 2022 - present
- **Format**: NetCDF (input), GeoTIFF (output)

## Troubleshooting

### Authentication
```python
earthaccess.login(strategy="interactive")  # Re-login
```

### No Data Found
- Check location within ±52° latitude
- Verify date range (post Aug 2022)
- Search first: `search_EMIT_L2A_RFL_granules(...)`

### Import Errors
```bash
pip install -e .  # Reinstall in dev mode
```

## File Structure

```
EMIT-L2A-RFL/
├── EMITL2ARFL/          # Main package
├── tests/               # Test suite
├── README.md            # Full documentation
├── TESTING.md           # Testing guide
├── pytest.ini           # Test configuration
├── run_tests.py         # Test runner
└── .github/workflows/   # CI/CD
```

## Resources

- [README.md](README.md) - Full documentation with examples
- [TESTING.md](TESTING.md) - Complete testing guide
- [EMIT Product Page](https://lpdaac.usgs.gov/products/emitl2arflv001/)
- [NASA Earthdata](https://urs.earthdata.nasa.gov/)
- [GitHub Repo](https://github.com/STARS-Data-Fusion/EMITL2ARFL)

## Contact

Gregory H. Halverson<br>
gregory.h.halverson@jpl.nasa.gov<br>
NASA JPL 329G
