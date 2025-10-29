#!/bin/bash
# Setup Local Virtual Environment for Web App
# Creates venv in /Users/thanhle (fast, not on Google Drive)

echo "🚀 Setting up local virtual environment for web app"
echo "=================================================="
echo ""

# Define paths
VENV_PATH="/Users/thanhle/venv_web_local"
PROJECT_PATH="/Users/thanhle/Library/CloudStorage/GoogleDrive-lenhothanh.nsl@gmail.com/.shortcut-targets-by-id/1Je2GU6cAmriwQ_9lhORCt8JeHBjH-2Yq/ELEC5620/Code/5620medai"

# Step 1: Create venv
echo "Step 1: Creating virtual environment at $VENV_PATH"
if [ -d "$VENV_PATH" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf "$VENV_PATH"
fi

python3.11 -m venv "$VENV_PATH"
if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    echo "   Make sure python3.11 is installed: brew install python@3.11"
    exit 1
fi
echo "✅ Virtual environment created"
echo ""

# Step 2: Activate venv
echo "Step 2: Activating virtual environment"
source "$VENV_PATH/bin/activate"
echo "✅ Virtual environment activated"
echo ""

# Step 3: Upgrade pip
echo "Step 3: Upgrading pip"
pip install --upgrade pip --quiet
echo "✅ Pip upgraded"
echo ""

# Step 4: Install minimal requirements
echo "Step 4: Installing minimal web app requirements"
echo "   (This will take 1-2 minutes)"

cd "$PROJECT_PATH/web_app"

# Install from minimal requirements
pip install -r requirements_minimal.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ Failed to install requirements"
    exit 1
fi
echo "✅ Requirements installed"
echo ""

# Step 5: Summary
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Activate the environment:"
echo "   source /Users/thanhle/venv_web_local/bin/activate"
echo ""
echo "2. Navigate to web app:"
echo "   cd $PROJECT_PATH/web_app"
echo ""
echo "3. Start the server:"
echo "   python app.py"
echo ""
echo "4. Access at: http://127.0.0.1:5000"
echo ""
echo "🔑 Login credentials:"
echo "   Patient: patient1 / password123"
echo "   Doctor:  dr.smith / password123"
echo "   Admin:   admin / password123"
echo ""
echo "⚠️  Note: AI document processing will be disabled"
echo "   (but all other features work perfectly!)"
echo ""

