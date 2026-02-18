# EMIT L2A Estimated Surface Reflectance and Uncertainty and Masks 60 m Search and Download Utility

This Python package is a tool for searching, downloading, and reading hyperspectral surface reflectance from the Earth Surface Mineral Dust Source Investigation (EMIT) L2A RFL data product. It provides easy-to-use functions for generating time-series of EMIT hyperspectral data for any location and time period.

Gregory H. Halverson (they/them)<br>
[gregory.h.halverson@jpl.nasa.gov](mailto:gregory.h.halverson@jpl.nasa.gov)<br>
NASA Jet Propulsion Laboratory 329G<br>

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Setup](#setup)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
  - [Generate Time-Series for a Location](#generate-time-series-for-a-location)
  - [Search for Granules](#search-for-granules)
  - [Retrieve Single Date](#retrieve-single-date)
  - [Work with Granules](#work-with-granules)
- [API Reference](#api-reference)
- [Testing](#testing)
- [References](#references)

## Features

- 🔍 **Search** EMIT L2A reflectance granules by date, location, orbit, and scene
- 📥 **Download** granules automatically from NASA's EOSDIS
- 🗺️ **Orthorectify** hyperspectral data using built-in geometry lookup tables
- 📊 **Generate time-series** of hyperspectral data for any area of interest
- 🎭 **Apply quality masks** to filter out cloudy or poor-quality pixels
- 🌍 **Spatial subsetting** to extract data for specific regions
- 📦 **Export** to GeoTIFF and other standard formats

## Installation

### From PyPI (Recommended)

```bash
pip install EMITL2ARFL
```

### From Source

```bash
git clone https://github.com/STARS-Data-Fusion/EMITL2ARFL.git
cd EMITL2ARFL
pip install -e .
```

### Development Installation

For development with testing capabilities:

```bash
pip install -e ".[dev]"
```

## Setup

### NASA Earthdata Authentication

This package requires NASA Earthdata credentials to download EMIT data. Set up authentication using one of these methods:

#### Option 1: .netrc File (Recommended)

Create a `.netrc` file in your home directory:

```bash
cat > ~/.netrc << EOF
machine urs.earthdata.nasa.gov
login YOUR_USERNAME
password YOUR_PASSWORD
EOF
chmod 600 ~/.netrc
```

#### Option 2: Interactive Login

The package will prompt you for credentials on first use:

```python
import earthaccess
earthaccess.login()
```

#### Option 3: Environment Variables

```bash
export EARTHDATA_USERNAME=your_username
export EARTHDATA_PASSWORD=your_password
```

**Note:** Get your free NASA Earthdata account at [urs.earthdata.nasa.gov](https://urs.earthdata.nasa.gov/users/new)

## Quick Start

Here's a simple example to generate a time-series of EMIT data for a location:

```python
import earthaccess
from EMITL2ARFL import generate_EMIT_L2A_RFL_timeseries
from rasters import Point
import rasters as rt

# Login to NASA Earthdata
earthaccess.login()

# Define location (latitude, longitude)
location = Point(-118.5, 36.5, crs=4326)  # Example: Southern Sierra Nevada

# Create a 1km x 1km grid at 60m resolution
bbox = rt.BBox(xmin=-118.51, ymin=36.49, xmax=-118.49, ymax=36.51, crs=4326)
grid = rt.RasterGrid.from_bbox(bbox=bbox, cell_size=60)

# Generate time-series
filenames = generate_EMIT_L2A_RFL_timeseries(
    start_date_UTC="2023-01-01",
    end_date_UTC="2023-12-31",
    geometry=grid,
    output_directory="./emit_timeseries"
)

print(f"Generated {len(filenames)} files")
```

## Usage Examples

### Generate Time-Series for a Location

Generate a time-series of EMIT reflectance data for a specific area:

```python
import earthaccess
from datetime import date
from EMITL2ARFL import generate_EMIT_L2A_RFL_timeseries
import rasters as rt

# Login
earthaccess.login(strategy="netrc")

# Define area of interest as a bounding box
bbox = rt.BBox(
    xmin=-119.0, ymin=36.0,
    xmax=-118.5, ymax=36.5,
    crs=4326
)

# Create raster grid at 60m resolution (EMIT native)
grid = rt.RasterGrid.from_bbox(bbox, cell_size=60)

# Generate time-series
filenames = generate_EMIT_L2A_RFL_timeseries(
    start_date_UTC=date(2023, 6, 1),
    end_date_UTC=date(2023, 9, 30),
    geometry=grid,
    output_directory="./my_emit_data",
    download_directory="./emit_downloads"
)

# Load and analyze results
for filename in filenames:
    raster = rt.MultiRaster.open(filename)
    print(f"Date: {filename}, Bands: {raster.nbands}, Shape: {raster.shape}")
```

### Generate Time-Series from KML/Shapefile

Use a polygon from a KML or Shapefile:

```python
import earthaccess
import geopandas as gpd
from EMITL2ARFL import generate_EMIT_L2A_RFL_timeseries
import rasters as rt

# Login
earthaccess.login(strategy="netrc")

# Load area of interest from KML/Shapefile
gdf = gpd.read_file("my_area.kml")
geometry = rt.Polygon(gdf.unary_union)

# Create UTM grid for the area
bbox_utm = geometry.UTM.bbox
grid = rt.RasterGrid.from_bbox(bbox_utm, cell_size=60, crs=bbox_utm.crs)

# Generate time-series
filenames = generate_EMIT_L2A_RFL_timeseries(
    start_date_UTC="2023-01-01",
    end_date_UTC="2023-12-31",
    geometry=grid,
    output_directory="./emit_timeseries"
)
```

### Search for Granules

Search for available EMIT granules without downloading:

```python
from EMITL2ARFL import search_EMIT_L2A_RFL_granules
from rasters import Point

# Define location
location = Point(-118.5, 36.5, crs=4326)

# Search for granules
granules = search_EMIT_L2A_RFL_granules(
    start_UTC="2023-07-01",
    end_UTC="2023-07-31",
    geometry=location
)

print(f"Found {len(granules)} granules")
for granule in granules:
    print(f"  - {granule['meta']['native-id']}")
```

### Search by Orbit and Scene

```python
from EMITL2ARFL import search_EMIT_L2A_RFL_granules

# Search for specific orbit and scene
granules = search_EMIT_L2A_RFL_granules(
    orbit=12345,
    scene=42,
    start_UTC="2023-01-01",
    end_UTC="2023-12-31"
)
```

### Retrieve Single Date

Retrieve and merge all EMIT data for a single date:

```python
from datetime import date
from EMITL2ARFL import retrieve_EMIT_L2A_RFL
import rasters as rt

# Define area
bbox = rt.BBox(xmin=-119.0, ymin=36.0, xmax=-118.5, ymax=36.5, crs=4326)
grid = rt.RasterGrid.from_bbox(bbox, cell_size=60)

# Retrieve data for one date
try:
    merged_cube = retrieve_EMIT_L2A_RFL(
        date_UTC=date(2023, 8, 15),
        geometry=grid,
        download_directory="./emit_downloads"
    )
    
    # Save to file
    merged_cube.to_geotiff("emit_20230815.tif")
    
    print(f"Retrieved {merged_cube.nbands} bands")
    print(f"Shape: {merged_cube.shape}")
    
except Exception as e:
    print(f"No data available: {e}")
```

### Work with Granules

Work with individual granule objects:

```python
from EMITL2ARFL import retrieve_EMIT_L2A_RFL_granule, search_EMIT_L2A_RFL_granules
from rasters import Point

# Search for granules
location = Point(-118.5, 36.5, crs=4326)
search_results = search_EMIT_L2A_RFL_granules(
    start_UTC="2023-08-15",
    end_UTC="2023-08-15",
    geometry=location
)

# Download and work with granule
if search_results:
    granule = retrieve_EMIT_L2A_RFL_granule(
        remote_granule=search_results[0],
        download_directory="./emit_downloads"
    )
    
    # Access reflectance data
    reflectance = granule.reflectance()
    
    # Get metadata
    print(f"Orbit: {granule.orbit}")
    print(f"Scene: {granule.scene}")
    print(f"Wavelengths: {reflectance.wavelengths}")
    
    # Subset to area of interest
    subset = granule.reflectance(geometry=location.buffer(1000))
    subset.to_geotiff("emit_subset.tif")
```

### Apply Quality Masks

Filter out cloudy or poor-quality pixels:

```python
from EMITL2ARFL import retrieve_EMIT_L2A_RFL_granule

# Retrieve granule with quality masking
granule = retrieve_EMIT_L2A_RFL_granule(
    remote_granule=search_results[0],
    download_directory="./emit_downloads"
)

# Get quality-masked reflectance
clean_reflectance = granule.reflectance(apply_mask=True)

# Or get the mask separately
mask = granule.mask()
reflectance = granule.reflectance(apply_mask=False)

# Apply custom mask logic
masked_data = reflectance.where(mask > 0)
```

## API Reference

### Main Functions

#### `generate_EMIT_L2A_RFL_timeseries`

Generate a time-series of EMIT reflectance data.

```python
def generate_EMIT_L2A_RFL_timeseries(
    start_date_UTC: Union[date, str],
    end_date_UTC: Union[date, str],
    geometry: RasterGeometry,
    output_directory: str,
    download_directory: str = "~/data/EMIT_L2A_RFL"
) -> List[str]
```

**Parameters:**
- `start_date_UTC`: Start date for time-series (date object or "YYYY-MM-DD" string)
- `end_date_UTC`: End date for time-series
- `geometry`: RasterGeometry defining the area of interest and output grid
- `output_directory`: Directory to save output GeoTIFF files
- `download_directory`: Directory for downloaded granules (optional)

**Returns:** List of output filenames

#### `search_EMIT_L2A_RFL_granules`

Search for EMIT granules.

```python
def search_EMIT_L2A_RFL_granules(
    start_UTC: Union[date, datetime, str] = None,
    end_UTC: Union[date, datetime, str] = None,
    geometry: Union[Point, Polygon, RasterGeometry] = None,
    orbit: int = None,
    scene: int = None
) -> List[DataGranule]
```

**Parameters:**
- `start_UTC`: Start date/time for search
- `end_UTC`: End date/time for search
- `geometry`: Spatial constraint (Point, Polygon, or RasterGeometry)
- `orbit`: Specific orbit number (optional)
- `scene`: Specific scene number (optional)

**Returns:** List of matching granules

#### `retrieve_EMIT_L2A_RFL`

Retrieve and merge EMIT data for a single date.

```python
def retrieve_EMIT_L2A_RFL(
    date_UTC: Union[date, datetime, str],
    geometry: Union[Point, Polygon, RasterGeometry],
    download_directory: str = "~/data/EMIT_L2A_RFL"
) -> MultiRaster
```

**Parameters:**
- `date_UTC`: Date to retrieve
- `geometry`: Area of interest
- `download_directory`: Download location

**Returns:** MultiRaster containing merged reflectance data

### Classes

#### `EMITL2ARFLGranule`

Represents a single EMIT L2A reflectance granule with methods to access reflectance, masks, and metadata.

**Key Methods:**
- `reflectance(geometry=None, apply_mask=False)`: Get reflectance data
- `mask()`: Get quality mask
- `uncertainty()`: Get uncertainty data
- `elevation(geometry=None)`: Get elevation data

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=EMITL2ARFL --cov-report=html

# Run specific test file
pytest tests/test_search.py

# Run specific test
pytest tests/test_search.py::test_search_granules_by_date
```

### Test Structure

- `test_import_dependencies.py`: Test all required dependencies import correctly
- `test_import_EMITL2ARFL.py`: Test main package imports
- `test_search.py`: Test granule search functionality
- `test_retrieve.py`: Test data retrieval and processing
- `test_timeseries.py`: Test time-series generation
- `test_integration.py`: End-to-end integration tests

## Data Format

EMIT L2A reflectance data is provided as:
- **Spatial Resolution**: 60 meters
- **Spectral Range**: 380-2500 nm (visible through shortwave infrared)
- **Spectral Bands**: ~285 bands
- **Format**: NetCDF (downloaded), GeoTIFF (output)
- **Coverage**: International Space Station orbit (±52° latitude)
- **Temporal Coverage**: 2022-08-01 to present

## Troubleshooting

### Authentication Issues

```python
# Clear cached credentials
earthaccess.login(strategy="interactive")
```

### No Data Found

EMIT has limited spatial coverage following the ISS orbit. Check:
1. Your location is within ±52° latitude
2. Data exists for your date range (post August 2022)
3. Search results: `granules = search_EMIT_L2A_RFL_granules(...)`

### Memory Issues

For large time-series or areas:
```python
# Process dates in smaller batches
# Use smaller cell_size (but not <60m)
# Enable dask for lazy loading
import dask
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

See LICENSE file for details.

## Acknowledgments

This package was developed at NASA's Jet Propulsion Laboratory, California Institute of Technology, under a contract with NASA.

## References

* Green, R. O., et al. (2023). Earth Surface Mineral Dust Source Investigation (EMIT) L2A Estimated Surface Reflectance and Uncertainty and Masks, Version 1. [Data set]. NASA EOSDIS Land Processes DAAC. [doi:10.5067/EMIT/EMITL2ARFL.001](https://doi.org/10.5067/EMIT/EMITL2ARFL.001)

* Green, R. O., et al. (2024). The Earth Surface Mineral Dust Source Investigation (EMIT) on the International Space Station: In-flight instrument performance and first results. *Remote Sensing of Environment*, 282, 113277. [doi:10.1016/j.rse.2023.113277](https://doi.org/10.1016/j.rse.2023.113277)

## Contact

Gregory H. Halverson (they/them)<br>
[gregory.h.halverson@jpl.nasa.gov](mailto:gregory.h.halverson@jpl.nasa.gov)<br>
NASA Jet Propulsion Laboratory 329G
