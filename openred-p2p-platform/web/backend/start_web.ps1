# === Script de démarrage Web Interface Windows ===
# Lance l'interface web OpenRed P2P Platform sur Windows PowerShell

Write-Host "🌐 Starting OpenRed P2P Web Interface..." -ForegroundColor Green

# Variables d'environnement par défaut
if (-not $env:OPENRED_NODE_ID) { $env:OPENRED_NODE_ID = "web_node_$(Get-Date -UFormat %s)" }
if (-not $env:OPENRED_SECTOR) { $env:OPENRED_SECTOR = "general" }
if (-not $env:OPENRED_P2P_PORT) { $env:OPENRED_P2P_PORT = "8080" }
if (-not $env:OPENRED_WEB_PORT) { $env:OPENRED_WEB_PORT = "8000" }

Write-Host "📡 Node ID: $env:OPENRED_NODE_ID" -ForegroundColor Cyan
Write-Host "🎯 Sector: $env:OPENRED_SECTOR" -ForegroundColor Cyan
Write-Host "🔗 P2P Port: $env:OPENRED_P2P_PORT" -ForegroundColor Cyan
Write-Host "🌐 Web Port: $env:OPENRED_WEB_PORT" -ForegroundColor Cyan

# Vérifier Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "🐍 Python: $pythonVersion" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Installation des dépendances
Write-Host "📦 Installing/updating dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Starting FastAPI web server..." -ForegroundColor Green
Write-Host "👉 Web Interface: http://localhost:$env:OPENRED_WEB_PORT" -ForegroundColor Magenta

python web_api.py