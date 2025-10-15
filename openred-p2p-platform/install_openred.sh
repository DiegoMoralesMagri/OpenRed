#!/bin/bash
# === OpenRed P2P Platform - Auto Installation Script ===
# One-command installation for Linux/macOS

set -e

echo "🚀 OpenRed P2P Platform - Auto Installation"
echo "============================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detected"

# Check pip
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed."
    exit 1
fi

PIP_CMD="pip3"
if command -v pip &> /dev/null; then
    PIP_CMD="pip"
fi

echo "✅ pip detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv openred_env

# Activate virtual environment
source openred_env/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
$PIP_CMD install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
$PIP_CMD install fastapi uvicorn websockets pillow cryptography

echo "✅ All dependencies installed!"

# Create start script
cat > start_openred.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source openred_env/bin/activate
echo "🚀 Starting OpenRed P2P Platform..."
echo "Open http://localhost:8000 in your browser"
python web/backend/web_api.py
EOF

chmod +x start_openred.sh

# Create Windows start script
cat > start_openred.bat << 'EOF'
@echo off
cd /d "%~dp0"
call openred_env\Scripts\activate.bat
echo 🚀 Starting OpenRed P2P Platform...
echo Open http://localhost:8000 in your browser
python web\backend\web_api.py
pause
EOF

echo ""
echo "🎉 OpenRed Installation Complete!"
echo ""
echo "To start OpenRed:"
echo "  Linux/macOS: ./start_openred.sh"
echo "  Windows:     start_openred.bat"
echo ""
echo "Then open http://localhost:8000 in your browser"
echo ""
echo "🌟 Welcome to the decentralized future!"