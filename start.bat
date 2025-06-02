@echo off
echo 🌱 Plant Monitoring System - Quick Start
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python is installed
echo.

REM Check if MongoDB is running
echo 🔍 Checking MongoDB connection...
python -c "from pymongo import MongoClient; MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=3000).admin.command('ping')" >nul 2>&1
if errorlevel 1 (
    echo ❌ MongoDB is not running or not accessible
    echo.
    echo 🔧 Please start MongoDB:
    echo    1. Open Command Prompt as Administrator
    echo    2. Run: net start MongoDB
    echo    3. Or start MongoDB Compass
    echo.
    pause
    exit /b 1
)

echo ✅ MongoDB is running
echo.

REM Install dependencies if needed
echo 📦 Installing/checking dependencies...
pip install -r requirements.txt >nul 2>&1

echo.
echo 🚀 Starting Plant Monitoring System...
echo 📱 Open your browser and go to: http://127.0.0.1:5000
echo 🔑 Demo login - Username: admin, Password: admin123
echo ⏹️  Press Ctrl+C to stop the application
echo.
echo ==========================================

REM Start the application
python start.py

pause
