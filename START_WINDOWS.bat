@echo off
REM Quick Start Script for Agrotrace-DNA on Windows

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         Agrotrace-DNA — Quick Start Setup                  ║
echo ║         Agricultural Supply Chain Tracking System          ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from python.org
    pause
    exit /b 1
)

echo ✅ Python found

REM Navigate to backend
cd /d backend
if errorlevel 1 (
    echo ❌ ERROR: Could not navigate to backend directory
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 1: Setting up Virtual Environment
echo ========================================
echo.

REM Check if venv exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated

echo.
echo ========================================
echo Step 2: Installing Dependencies
echo ========================================
echo.

echo Installing Python packages...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ❌ ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed

echo.
echo ========================================
echo Step 3: Setting up Environment Variables
echo ========================================
echo.

if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env >nul
    echo ✅ .env file created
    echo.
    echo ⚠️  Please review .env and update:
    echo    - SECRET_KEY
    echo    - JWT_SECRET_KEY
    echo    - DATABASE_URL (if needed)
    echo.
) else (
    echo ✅ .env file already exists
)

echo.
echo ========================================
echo Step 4: Starting Backend Server
echo ========================================
echo.

echo Starting Flask server at http://localhost:5000
echo Press CTRL+C to stop the server
echo.

python run.py

pause
