#!/bin/bash
# Quick start script for Clinical AI Web Application

echo "=============================================="
echo "🏥 Clinical AI System - Web Application"
echo "=============================================="
echo ""

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please set up the environment first:"
    echo "  cd .."
    echo "  source venv/bin/activate"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source ../venv/bin/activate

# Check if Flask dependencies are installed
echo "🔍 Checking Flask dependencies..."
pip show Flask > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "📥 Installing Flask dependencies..."
    pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements_flask.txt
else
    echo "✅ Flask dependencies already installed"
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

# Run the Flask application
python app.py

