# Website2PDF Test Suite

This directory contains comprehensive tests for the website2pdf project, including critical security vulnerability tests.

## Test Structure

```
tests/
├── __init__.py                # Test package initialization
├── conftest.py               # pytest configuration and fixtures
├── test_security_fixes.py    # Security vulnerability tests
├── test_pdf_processing.py    # PDF processing functionality tests
├── test_runner.py           # Custom test runner
└── README.md               # This file
```

## Running Tests

### Using the Shell Script (Recommended)

```bash
# Run all tests
./run_tests.sh

# Run only security tests
./run_tests.sh security

# Run only PDF processing tests
./run_tests.sh pdf
```

### Using Python Test Runner

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
python tests/test_runner.py

# Run specific test categories
python tests/test_runner.py --security
python tests/test_runner.py --pdf
```

### Using unittest directly

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_security_fixes
python -m unittest tests.test_pdf_processing
```

## Test Categories

### Security Tests (`test_security_fixes.py`)

These tests verify that the critical infinite loop vulnerability in PyPDF2 has been properly patched:

- **`test_infinite_loop_vulnerability_fixed`**: Verifies the core fix prevents infinite loops
- **`test_content_stream_parsing_timeout`**: Ensures PDF parsing completes within reasonable time
- **`test_empty_byte_condition_in_loop`**: Tests the specific patch condition
- **`test_vulnerability_patch_applied`**: Confirms the source code contains the security fix
- **`test_regression_normal_pdf_processing`**: Ensures normal PDF processing still works

### PDF Processing Tests (`test_pdf_processing.py`)

These tests verify the core PDF functionality used by the application:

- **`TestPdfProcessing`**: Tests basic PDF operations (reading, writing, annotations, combinations)
- **`TestApplicationIntegration`**: Tests integration with external libraries (ReportLab, PyPDF2)

## Security Vulnerability Details

**CVE Reference**: https://github.com/py-pdf/pypdf/security/advisories/GHSA-xcvp-wgc8-7hq9

**Issue**: An infinite loop vulnerability in PyPDF2's `__parse_content_stream` method could be exploited by crafting malicious PDFs with comments that don't end with newlines.

**Fix Applied**: Added empty byte (`b""`) condition to the while loop to prevent infinite loops when reaching end-of-stream:

```python
# Before (vulnerable):
while peek not in (b"\r", b"\n"):

# After (fixed):
while peek not in (b"\r", b"\n", b""):
```

## Test Coverage

The test suite covers:

- ✅ Security vulnerability mitigation
- ✅ PDF reading and writing operations
- ✅ PDF annotation creation and manipulation
- ✅ PDF combination functionality
- ✅ ReportLab integration for TOC generation
- ✅ Regression testing for normal functionality
- ✅ Timeout and performance verification

## Requirements

Tests require the same dependencies as the main application:
- PyPDF2==3.0.1 (with security patch applied)
- reportlab==3.6.13
- beautifulsoup4==4.12.2

## Contributing

When adding new tests:

1. Follow the existing naming convention (`test_*.py`)
2. Add comprehensive docstrings
3. Include both positive and negative test cases
4. Update this README if adding new test categories
5. Ensure tests run in isolation and clean up after themselves