@echo off
echo 🚀 TBL SACCOS Loan Management System Setup
echo ================================================
echo.

echo 🔄 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo    Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

echo 🔄 Running setup script...
python setup.py
echo.

echo 📋 Setup completed! 
echo.
echo To start the system:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Run server: python manage.py runserver
echo 3. Open browser: http://127.0.0.1:8000/
echo.
pause

