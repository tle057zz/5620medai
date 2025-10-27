#!/bin/bash
# Quick start script for Clinical AI Web Application (single env: ../venv_ai)
set -e

echo "=============================================="
echo "🏥 Clinical AI System - Web Application"
echo "=============================================="
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$PROJECT_DIR/venv_ai"

# Check virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at: $VENV_DIR"
    echo "Create it once with:"
    echo "  cd \"$PROJECT_DIR\" && python3.11 -m venv venv_ai"
    exit 1
fi

echo "📦 Activating virtual environment (venv_ai)..."
source "$VENV_DIR/bin/activate"

# Python executable
PYTHON="python3.11"
command -v $PYTHON >/dev/null 2>&1 || PYTHON="python3"

# Ensure minimal web/AI runtime deps (idempotent, fast if already installed)
echo "🔍 Ensuring required packages (Flask + pandas + PDF/OCR)..."
pip install -q Flask Flask-Login Flask-WTF pandas pdfplumber PyMuPDF pytesseract pdf2image >/dev/null 2>&1 && echo "✅ Web runtime OK"

echo ""
echo "Killing any process on port 5000 (if running)..."
if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -t -i:5000 || true)
  if [ -n "$PIDS" ]; then
    kill -9 $PIDS || true
  fi
fi

echo ""
echo "=============================================="
echo "🚀 Starting Web Application..."
echo "=============================================="
echo ""
echo "📋 Demo Credentials (Password: password123)"
echo "----------------------------------------------"
echo "  Doctor:  dr.smith, dr.jones, dr.chen"
echo "  Patient: patient1, patient2, patient3"
echo "  Admin:   admin, it.admin"
echo "----------------------------------------------"
echo ""
echo "🌐 Access at: http://127.0.0.1:5000"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

cd "$PROJECT_DIR/web_app"
$PYTHON app.py

