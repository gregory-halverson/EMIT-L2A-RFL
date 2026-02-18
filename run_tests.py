#!/usr/bin/env python3
"""
Test runner script for EMIT L2A RFL package.

This script provides convenient commands for running different test suites:
- Unit tests: Fast tests with mocked dependencies
- Integration tests: Tests that require real data and credentials
- All tests: Complete test suite
"""

import sys
import subprocess
import argparse


def run_unit_tests():
    """Run only unit tests (fast, no credentials needed)."""
    print("Running unit tests...")
    cmd = [
        "pytest",
        "tests/",
        "-v",
        "-m", "not integration and not slow",
        "--tb=short"
    ]
    return subprocess.run(cmd).returncode


def run_integration_tests():
    """Run integration tests (requires credentials)."""
    print("Running integration tests...")
    print("Note: These tests require NASA Earthdata credentials")
    cmd = [
        "pytest",
        "tests/",
        "-v",
        "-m", "integration",
        "--tb=short"
    ]
    return subprocess.run(cmd).returncode


def run_all_tests():
    """Run all tests."""
    print("Running all tests...")
    cmd = [
        "pytest",
        "tests/",
        "-v",
        "--tb=short"
    ]
    return subprocess.run(cmd).returncode


def run_with_coverage():
    """Run tests with coverage report."""
    print("Running tests with coverage...")
    cmd = [
        "pytest",
        "tests/",
        "-v",
        "--cov=EMITL2ARFL",
        "--cov-report=html",
        "--cov-report=term",
        "-m", "not integration and not slow"
    ]
    returncode = subprocess.run(cmd).returncode
    if returncode == 0:
        print("\nCoverage report generated in htmlcov/index.html")
    return returncode


def main():
    parser = argparse.ArgumentParser(
        description="Run tests for EMIT L2A RFL package"
    )
    parser.add_argument(
        "suite",
        choices=["unit", "integration", "all", "coverage"],
        default="unit",
        nargs="?",
        help="Test suite to run (default: unit)"
    )
    
    args = parser.parse_args()
    
    runners = {
        "unit": run_unit_tests,
        "integration": run_integration_tests,
        "all": run_all_tests,
        "coverage": run_with_coverage
    }
    
    return runners[args.suite]()


if __name__ == "__main__":
    sys.exit(main())
