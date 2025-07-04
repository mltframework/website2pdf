#!/bin/bash
# Test runner script for website2pdf

set -e  # Exit on error

echo "🧪 Website2PDF Test Suite"
echo "========================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if required packages are installed
echo "Checking dependencies..."
python -c "import PyPDF2, reportlab, bs4" 2>/dev/null || {
    echo "❌ Missing dependencies. Please install requirements.txt"
    exit 1
}

# Run tests based on argument
case "${1:-all}" in
    "security")
        echo "Running security tests..."
        python tests/test_runner.py --security
        ;;
    "pdf")
        echo "Running PDF processing tests..."
        python tests/test_runner.py --pdf
        ;;
    "all")
        echo "Running all tests..."
        python tests/test_runner.py
        ;;
    *)
        echo "Usage: $0 [security|pdf|all]"
        exit 1
        ;;
esac

echo "✅ Test run completed!"