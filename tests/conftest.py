#!/usr/bin/env python3
"""
pytest configuration and fixtures for website2pdf tests.
"""

import pytest
import tempfile
import os
from PyPDF2 import PdfWriter


@pytest.fixture
def temp_pdf():
    """Create a temporary PDF file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        writer.write(tmp_file)
        tmp_file.flush()
        
        yield tmp_file.name
        
        # Cleanup
        if os.path.exists(tmp_file.name):
            os.unlink(tmp_file.name)


@pytest.fixture
def mock_pdf_content():
    """Mock PDF content for testing."""
    return b"BT /F1 12 Tf 72 720 Td (Hello World) Tj ET"


@pytest.fixture
def malicious_pdf_content():
    """Malicious PDF content that would trigger the vulnerability."""
    return b"% This is a comment without proper line ending"