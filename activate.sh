#!/bin/bash
# Quick activation script for the medical AI environment

# Navigate to project directory
cd "$(dirname "$0")"

# Activate the virtual environment
source venv/bin/activate

echo "✅ Medical AI environment activated!"
echo ""
echo "Python version: $(python --version)"
echo ""
echo "Quick commands:"
echo "  cd ai_medical              - Go to modules directory"
echo "  python ocr/extract_text.py - Run OCR module"
echo "  deactivate                 - Exit environment"
echo ""

