# Test Suite Status

## Overview

The EMIT L2A RFL package includes a comprehensive test suite with multiple types of tests. Currently, basic functionality tests are passing, while advanced mock-based unit tests require refinement of the mocking strategy.

## ✅ Passing Tests (27 tests)

### Basic Functionality Tests
- **test_basic.py** (9 tests): Package structure, imports, function signatures
- **test_constants.py** (8 tests): Configuration constants validation  
- **test_import_dependencies.py** (9 tests): All required dependencies
- **test_import_EMITL2ARFL.py** (1 test): Main package import

These tests verify:
- All modules can be imported correctly
- Functions have expected signatures
- Constants are properly defined
- Dependencies are available

## 🔄 In Progress

### Mock-Based Unit Tests  
The following test files use extensive mocking to test functions in isolation:
- **test_search.py**: Granule search functionality
- **test_retrieve.py**: Data retrieval operations
- **test_timeseries.py**: Time-series generation

**Status**: These tests are structurally complete but require adjustment of mock paths to match the package's import structure. The tests demonstrate best practices for:
- Using `unittest.mock` for isolation
- Testing edge cases and error handling
- Verifying function call arguments
- Handling missing data scenarios

### Integration Tests
- **test_integration.py**: End-to-end workflows with real data

**Status**: Require NASA Earthdata credentials. These are marked with `@pytest.mark.integration` and `@pytest.mark.slow` and can be run separately when credentials are available.

## Running Tests

### Run Passing Tests Only
```bash
# Using pytest directly
pytest tests/test_basic.py tests/test_constants.py tests/test_import_dependencies.py tests/test_import_EMITL2ARFL.py -v

# Using conda environment
conda run -n EMITL2ARFL pytest tests/test_basic.py tests/test_constants.py tests/test_import_dependencies.py tests/test_import_EMITL2ARFL.py -v
```

### Run All Tests (including those in progress)
```bash
pytest tests/ -v
```

### Skip Integration Tests
```bash
pytest tests/ -v -m "not integration and not slow"
```

## Test Coverage

Current test coverage focuses on:
- ✅ Package structure and imports
- ✅ Constants and configuration
- ✅ Function signatures and availability
- ✅ Dependency availability
- 🔄 Mocked unit tests for isolated function testing
- 🔄 Integration tests for real-world workflows

## Next Steps

To complete the mock-based unit tests:

1. **Refactor Mock Paths**: Adjust `@patch` decorators to correctly patch at the module import location
2. **Add Test Fixtures**: Create reusable fixtures for common test data
3. **Expand Coverage**: Add tests for additional edge cases
4. **Integration Test Setup**: Document NASA Earthdata credential setup for integration tests

## For Contributors

When adding new features:
1. Add basic import/structure tests in `test_basic.py`
2. Add constant tests in `test_constants.py`  
3. Consider adding integration tests in `test_integration.py`
4. Update this status document

## Test Philosophy

The test suite follows a layered approach:

1. **Basic Tests** (test_basic.py): Fast, no mocking, verify structure
2. **Unit Tests** (test_*.py): Isolated, mocked dependencies, test logic
3. **Integration Tests** (test_integration.py): Real data, end-to-end workflows

This ensures that basic functionality is always testable even if external services are unavailable.

## References

- [TESTING.md](TESTING.md): Comprehensive testing guide
- [pytest documentation](https://docs.pytest.org/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
