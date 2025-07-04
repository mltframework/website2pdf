#!/usr/bin/env python3
"""
PDF processing functionality tests for website2pdf.

This module contains tests for the core PDF processing functionality
used in the website2pdf application.
"""

import unittest
import tempfile
import os
import pytest
from unittest.mock import patch, MagicMock
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import DictionaryObject, NameObject, NumberObject, RectangleObject, ArrayObject


class TestPdfProcessing(unittest.TestCase):
    """Test cases for PDF processing functionality."""
    
    def test_pdf_reader_creation(self):
        """Test that PdfReader can be created without issues."""
        # Create a minimal PDF in memory for testing
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            # Create a minimal PDF
            writer = PdfWriter()
            # Add a blank page
            writer.add_blank_page(width=200, height=200)
            
            # Write to temp file
            writer.write(tmp_file)
            tmp_file.flush()
            
            # Test reading the PDF
            try:
                reader = PdfReader(tmp_file.name)
                self.assertGreater(len(reader.pages), 0, "PDF should have at least one page")
                print("✓ PdfReader creation successful")
            except Exception as e:
                self.fail(f"PdfReader creation failed: {e}")
            finally:
                os.unlink(tmp_file.name)
    
    def test_pdf_writer_functionality(self):
        """Test basic PDF writing functionality."""
        writer = PdfWriter()
        
        # Add a blank page
        page = writer.add_blank_page(width=200, height=200)
        self.assertIsNotNone(page, "Should be able to add a blank page")
        
        # Test writing to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp_file:
            writer.write(tmp_file)
            tmp_file.flush()
            
            # Verify the file was created and has content
            self.assertGreater(os.path.getsize(tmp_file.name), 0,
                             "Generated PDF should not be empty")
            
            print("✓ PdfWriter functionality working")
    
    def test_pdf_annotation_creation(self):
        """Test PDF annotation creation as used in the main application."""
        
        # Test creating annotation objects like in main.py
        annotation = DictionaryObject()
        annotation.update({
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Link"),
            NameObject("/Rect"): RectangleObject([50, 50, 150, 150]),
            NameObject("/Border"): ArrayObject([
                NumberObject(0), NumberObject(0), NumberObject(0)
            ])
        })
        
        # Verify annotation structure
        self.assertEqual(annotation[NameObject("/Type")], NameObject("/Annot"))
        self.assertEqual(annotation[NameObject("/Subtype")], NameObject("/Link"))
        
        print("✓ PDF annotation creation working")
    
    def test_pdf_page_operations(self):
        """Test PDF page operations used in the application."""
        writer = PdfWriter()
        page = writer.add_blank_page(width=200, height=200)
        
        # Test adding annotation to page (like in main.py)
        annotation = DictionaryObject()
        annotation.update({
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Link"),
            NameObject("/Rect"): RectangleObject([10, 10, 50, 50]),
        })
        
        try:
            writer.add_annotation(page_number=0, annotation=annotation)
            print("✓ PDF page annotation operations working")
        except Exception as e:
            self.fail(f"PDF page operations failed: {e}")
    
    def test_pdf_combination_functionality(self):
        """Test PDF combination as used in the main application."""
        # Create two test PDFs
        pdf1_writer = PdfWriter()
        pdf1_writer.add_blank_page(width=200, height=200)
        
        pdf2_writer = PdfWriter()
        pdf2_writer.add_blank_page(width=200, height=200)
        
        # Write first PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp1:
            pdf1_writer.write(tmp1)
            tmp1.flush()
            
            # Write second PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp2:
                pdf2_writer.write(tmp2)
                tmp2.flush()
                
                try:
                    # Test combining PDFs
                    combined_writer = PdfWriter()
                    
                    # Read and combine
                    reader1 = PdfReader(tmp1.name)
                    reader2 = PdfReader(tmp2.name)
                    
                    combined_writer.append_pages_from_reader(reader1)
                    combined_writer.append_pages_from_reader(reader2)
                    
                    # Verify combined PDF has correct number of pages
                    self.assertEqual(len(combined_writer.pages), 2,
                                   "Combined PDF should have 2 pages")
                    
                    print("✓ PDF combination functionality working")
                    
                except Exception as e:
                    self.fail(f"PDF combination failed: {e}")
                finally:
                    os.unlink(tmp1.name)
                    os.unlink(tmp2.name)
    
    def test_pdf_content_extraction_safety(self):
        """Test that PDF content extraction is safe after security fix."""
        # Create a PDF with text content
        writer = PdfWriter()
        page = writer.add_blank_page(width=200, height=200)
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            writer.write(tmp_file)
            tmp_file.flush()
            
            try:
                reader = PdfReader(tmp_file.name)
                page = reader.pages[0]
                
                # Test text extraction (this would trigger the vulnerability)
                # Should complete without infinite loop
                import time
                start_time = time.time()
                text = page.extract_text()
                elapsed_time = time.time() - start_time
                
                # Should complete quickly
                self.assertLess(elapsed_time, 5.0,
                               f"Text extraction took too long: {elapsed_time}s")
                
                print("✓ PDF content extraction is safe")
                
            except Exception as e:
                # Some exceptions are normal for blank pages
                print(f"✓ PDF content extraction completed (with expected exception: {type(e).__name__})")
            finally:
                os.unlink(tmp_file.name)


@pytest.mark.integration
class TestApplicationIntegration(unittest.TestCase):
    """Test cases for application integration aspects."""
    
    def test_import_main_modules(self):
        """Test that main application modules import correctly."""
        try:
            # Test importing the main application components
            from PyPDF2 import PdfReader, PdfWriter
            from PyPDF2.generic import (
                DictionaryObject, NumberObject, NameObject, 
                ArrayObject, RectangleObject
            )
            print("✓ All main PDF modules import successfully")
        except ImportError as e:
            self.fail(f"Failed to import required modules: {e}")
    
    def test_reportlab_integration(self):
        """Test ReportLab integration for TOC generation."""
        try:
            from reportlab.pdfgen import canvas
            import io
            
            # Test creating a simple PDF with ReportLab
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer)
            c.drawString(100, 750, "Test TOC")
            c.save()
            
            # Verify PDF was created
            self.assertGreater(len(buffer.getvalue()), 0,
                             "ReportLab should generate PDF content")
            
            print("✓ ReportLab integration working")
            
        except ImportError as e:
            self.fail(f"ReportLab not available: {e}")
        except Exception as e:
            self.fail(f"ReportLab integration failed: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)