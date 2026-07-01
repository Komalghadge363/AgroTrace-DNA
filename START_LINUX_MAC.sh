#!/bin/bash

# Quick Start Script for Agrotrace-DNA on Linux/Mac

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Agrotrace-DNA — Quick Start Setup                  ║"
echo "║         Agricultural Supply Chain Tracking System          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo "Please install Python 3.11+ from python.org"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Navigate to backend
cd backend || {
    echo "❌ ERROR: Could not navigate to backend directory"
    exit 1
}

echo ""
echo "========================================"
echo "Step 1: Setting up Virtual Environment"
echo "========================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated"

echo ""
echo "========================================"
echo "Step 2: Installing Dependencies"
echo "========================================"
echo ""

echo "Installing Python packages..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"

echo ""
echo "========================================"
echo "Step 3: Setting up Environment Variables"
echo "========================================"
echo ""

if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  Please review .env and update:"
    echo "   - SECRET_KEY"
    echo "   - JWT_SECRET_KEY"
    echo "   - DATABASE_URL (if needed)"
    echo ""
else
    echo "✅ .env file already exists"
fi

echo ""
echo "========================================"
echo "Step 4: Starting Backend Server"
echo "========================================"
echo ""

echo "Starting Flask server at http://localhost:5000"
echo "Press CTRL+C to stop the server"
echo ""

python3 run.py
