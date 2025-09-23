# Script de lancement pour OpenRed Central-API v3.0
# Launch script for OpenRed Central-API v3.0
# Script de lanzamiento para OpenRed Central-API v3.0
# OpenRed Central-API v3.0 启动脚本

Write-Host "🚀 OpenRed Central-API v3.0 Launcher" -ForegroundColor Green
Write-Host "📋 Ultra-minimalist P2P directory server" -ForegroundColor Cyan
Write-Host "🧹 Ultra-clean virtual environment" -ForegroundColor Yellow
Write-Host ""

# Navigation vers le projet
Write-Host "📁 Navigating to project directory..." -ForegroundColor Yellow
Set-Location "C:\Users\serveur\Documents\OpenRed"

# Activation de l'environnement virtuel ultra-propre
Write-Host "🔧 Activating ultra-clean virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Affichage de l'environnement
Write-Host "✅ Environment: Python 3.9.5 + cryptography only" -ForegroundColor Green

# Navigation vers le serveur
Write-Host "🗂️ Navigating to server directory..." -ForegroundColor Yellow
Set-Location "central-api\src"

# Lancement du serveur
Write-Host "🚀 Starting OpenRed Central-API..." -ForegroundColor Green
Write-Host "💖 Empathy level: Maximum" -ForegroundColor Magenta
Write-Host ""
python main.py