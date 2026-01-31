#!/bin/bash

# Restaurant Ordering App - Deployment Script
# This script sets up everything needed to run the app

set -e  # Exit on error

echo ""
echo "=========================================="
echo "RESTAURANT ORDERING APP - DEPLOYMENT"
echo "=========================================="
echo ""

# Step 1: Check Python
echo "[1/4] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Step 2: Install dependencies
echo "[2/4] Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "Error: requirements.txt not found"
    exit 1
fi
echo ""

# Step 3: Initialize database
echo "[3/4] Initializing database..."
if [ -f "database/initialize.py" ]; then
    python database/initialize.py
else
    echo "Error: database/initialize.py not found"
    exit 1
fi
echo ""

# Step 4: Ready to run
echo "[4/4] Setup complete!"
echo ""
echo "=========================================="
echo "✅ DEPLOYMENT SUCCESSFUL"
echo "=========================================="
echo ""
echo "To start the app, run:"
echo "  python app.py"
echo ""
echo "Or for production:"
echo "  gunicorn -w 4 -b 0.0.0.0:5000 app:app"
echo ""
echo "App will be available at:"
echo "  http://localhost:5000"
echo ""
