@echo off
REM === OpenRed P2P Platform - Auto Installation Script ===
REM One-command installation for Windows

echo 🚀 OpenRed P2P Platform - Auto Installation
echo ============================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is required but not installed.
    echo Please install Python 3.8+ from https://python.org and try again.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% detected

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is required but not installed.
    pause
    exit /b 1
)

echo ✅ pip detected

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv openred_env

REM Activate virtual environment
call openred_env\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📦 Installing dependencies...
pip install fastapi uvicorn websockets pillow cryptography

echo ✅ All dependencies installed!

REM Create start script
echo @echo off > start_openred.bat
echo cd /d "%%~dp0" >> start_openred.bat
echo call openred_env\Scripts\activate.bat >> start_openred.bat
echo echo 🚀 Starting OpenRed P2P Platform... >> start_openred.bat
echo echo Open http://localhost:8000 in your browser >> start_openred.bat
echo python web\backend\web_api.py >> start_openred.bat
echo pause >> start_openred.bat

echo.
echo 🎉 OpenRed Installation Complete!
echo.
echo To start OpenRed: start_openred.bat
echo Then open http://localhost:8000 in your browser
echo.
echo 🌟 Welcome to the decentralized future!
pause