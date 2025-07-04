#!/usr/bin/env python3
"""
Test runner for website2pdf test suite.
"""

import unittest
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_all_tests():
    """Run all tests in the test suite."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_security_tests():
    """Run only security-related tests."""
    from test_security_fixes import TestSecurityFixes
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSecurityFixes)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_pdf_processing_tests():
    """Run only PDF processing tests."""
    from test_pdf_processing import TestPdfProcessing, TestApplicationIntegration
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPdfProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestApplicationIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run website2pdf tests')
    parser.add_argument('--security', action='store_true', 
                       help='Run only security tests')
    parser.add_argument('--pdf', action='store_true',
                       help='Run only PDF processing tests')
    
    args = parser.parse_args()
    
    success = True
    
    if args.security:
        print("Running security tests...")
        success = run_security_tests()
    elif args.pdf:
        print("Running PDF processing tests...")
        success = run_pdf_processing_tests()
    else:
        print("Running all tests...")
        success = run_all_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)