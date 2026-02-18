# Testing Guide for EMIT L2A RFL Package

This document provides comprehensive information about testing the EMIT L2A RFL package.

## Table of Contents

- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Types](#test-types)
- [Writing Tests](#writing-tests)
- [Continuous Integration](#continuous-integration)
- [Coverage](#coverage)

## Quick Start

### Install Test Dependencies

```bash
# Install package with dev dependencies
pip install -e ".[dev]"

# Or install test requirements separately
pip install -r requirements-test.txt
```

### Run All Unit Tests

```bash
# Using pytest directly
pytest tests/ -v -m "not integration and not slow"

# Using the test runner script
python run_tests.py unit
```

### Run with Coverage

```bash
python run_tests.py coverage
```

## Test Structure

The test suite is organized as follows:

```
tests/
├── test_import_dependencies.py  # Dependency import tests
├── test_import_EMITL2ARFL.py   # Package import tests
├── test_constants.py            # Constants and configuration tests
├── test_search.py               # Granule search functionality tests
├── test_retrieve.py             # Data retrieval tests
├── test_timeseries.py          # Time-series generation tests
└── test_integration.py         # End-to-end integration tests
```

### Test Categories

1. **Import Tests**: Verify all dependencies and the package itself can be imported
2. **Unit Tests**: Test individual functions with mocked dependencies
3. **Integration Tests**: Test complete workflows with real data (requires credentials)
4. **Slow Tests**: Tests that download real data (marked for optional execution)

## Running Tests

### Using pytest Directly

```bash
# Run all unit tests
pytest tests/ -v -m "not integration and not slow"

# Run specific test file
pytest tests/test_search.py -v

# Run specific test function
pytest tests/test_search.py::TestSearchGranules::test_search_by_date_range -v

# Run tests matching a pattern
pytest tests/ -k "search" -v

# Run with verbose output
pytest tests/ -vv

# Run with coverage
pytest tests/ --cov=EMITL2ARFL --cov-report=html
```

### Using the Test Runner Script

The `run_tests.py` script provides convenient commands:

```bash
# Run unit tests only (fast, no credentials needed)
python run_tests.py unit

# Run integration tests (requires NASA Earthdata credentials)
python run_tests.py integration

# Run all tests
python run_tests.py all

# Run with coverage report
python run_tests.py coverage
```

## Test Types

### Unit Tests

Unit tests are fast and don't require external resources. They use mocking to simulate:
- earthaccess API calls
- File system operations
- Network requests

**Markers**: No special markers (default)

**Example**:
```python
@patch('EMITL2ARFL.search_EMIT_L2A_RFL_granules.search_earthaccess_granules')
def test_search_by_date_range(self, mock_search):
    mock_search.return_value = [Mock(), Mock()]
    results = search_EMIT_L2A_RFL_granules(
        start_UTC=date(2023, 8, 1),
        end_UTC=date(2023, 8, 31)
    )
    assert len(results) == 2
```

### Integration Tests

Integration tests verify the complete workflow with real data.

**Requirements**:
- NASA Earthdata credentials (netrc or interactive login)
- Internet connectivity
- Sufficient disk space for downloads

**Markers**: `@pytest.mark.integration`, `@pytest.mark.slow`

**Running**:
```bash
# Run integration tests only
pytest tests/ -v -m "integration"

# Skip integration and slow tests
pytest tests/ -v -m "not integration and not slow"
```

**Example**:
```python
@pytest.mark.integration
@pytest.mark.slow
def test_retrieve_real_data(self):
    earthaccess.login(strategy="netrc")
    location = Point(-116.8, 36.5, crs=4326)
    data = retrieve_EMIT_L2A_RFL(
        date_UTC=date(2023, 8, 15),
        geometry=location
    )
    assert data is not None
```

## Writing Tests

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Best Practices

1. **Use descriptive names**:
   ```python
   def test_search_by_date_range_returns_correct_granules(self):
   ```

2. **Follow AAA pattern** (Arrange, Act, Assert):
   ```python
   def test_example(self):
       # Arrange - set up test data
       location = Point(-118.5, 36.5, crs=4326)
       
       # Act - perform the action
       results = search_EMIT_L2A_RFL_granules(geometry=location)
       
       # Assert - verify results
       assert isinstance(results, list)
   ```

3. **Mock external dependencies**:
   ```python
   @patch('EMITL2ARFL.module.external_function')
   def test_with_mock(self, mock_func):
       mock_func.return_value = expected_value
       result = function_under_test()
       assert result == expected_value
   ```

4. **Use fixtures for common setup**:
   ```python
   @pytest.fixture
   def test_location():
       return Point(-118.5, 36.5, crs=4326)
   
   def test_with_fixture(test_location):
       results = search_EMIT_L2A_RFL_granules(geometry=test_location)
   ```

5. **Test edge cases**:
   - Empty results
   - Invalid inputs
   - Network failures
   - Missing files

### Example Test Class

```python
class TestSearchFunctionality:
    """Test suite for search functionality."""
    
    @patch('module.search_function')
    def test_search_with_date_range(self, mock_search):
        """Test searching with date range."""
        # Arrange
        mock_search.return_value = [Mock(), Mock()]
        start = date(2023, 8, 1)
        end = date(2023, 8, 31)
        
        # Act
        results = search_EMIT_L2A_RFL_granules(
            start_UTC=start,
            end_UTC=end
        )
        
        # Assert
        assert len(results) == 2
        mock_search.assert_called_once()
    
    def test_search_with_invalid_date(self):
        """Test error handling with invalid date."""
        with pytest.raises(ValueError):
            search_EMIT_L2A_RFL_granules(
                start_UTC="invalid-date"
            )
```

## Continuous Integration

The package uses GitHub Actions for automated testing.

### CI Workflow

The CI pipeline runs on:
- **Events**: Push to main/develop, Pull requests
- **OS**: Ubuntu, macOS, Windows
- **Python**: 3.10, 3.11, 3.12

### Configuration

See `.github/workflows/tests.yml` for the complete configuration.

### Local Testing Before Push

```bash
# Run the same tests as CI
pytest tests/ -v -m "not integration and not slow"

# Check code style
flake8 EMITL2ARFL tests

# Format code
black EMITL2ARFL tests
isort EMITL2ARFL tests
```

## Coverage

### Generate Coverage Report

```bash
# Generate HTML coverage report
pytest tests/ --cov=EMITL2ARFL --cov-report=html -m "not integration"

# Open report in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Goals

- **Minimum**: 70% code coverage
- **Target**: 85% code coverage
- **Focus**: Critical paths (search, retrieve, time-series generation)

### Viewing Coverage

```bash
# Terminal output
pytest tests/ --cov=EMITL2ARFL --cov-report=term

# See missing lines
pytest tests/ --cov=EMITL2ARFL --cov-report=term-missing
```

## Troubleshooting

### Import Errors

If you get import errors:
```bash
# Reinstall package in development mode
pip install -e .
```

### Missing Dependencies

```bash
# Install all test dependencies
pip install -e ".[dev]"
```

### Integration Test Failures

If integration tests fail:
1. Verify NASA Earthdata credentials are set up
2. Check internet connectivity
3. Verify the test location has EMIT coverage
4. Check date range (EMIT launched August 2022)

### Slow Tests

Skip slow tests during development:
```bash
pytest tests/ -v -m "not slow"
```

## Advanced Testing

### Running Tests in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest tests/ -n auto
```

### Testing Specific Python Version

```bash
# Using tox (requires tox installation)
tox -e py310
tox -e py311
```

### Debugging Tests

```bash
# Drop into debugger on failure
pytest tests/ --pdb

# Print output even for passing tests
pytest tests/ -s

# Very verbose output
pytest tests/ -vv
```

## Contributing Tests

When contributing new features:

1. Write unit tests for new functions
2. Add integration tests for complete workflows
3. Update this guide if adding new test categories
4. Ensure tests pass locally before submitting PR
5. Maintain or improve code coverage

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [EMIT documentation](https://lpdaac.usgs.gov/products/emitl2arflv001/)
