# 🚀 OpenRed One-Liner Installer for Windows
# Usage: iex ((New-Object System.Net.WebClient).DownloadString('https://install.openred.dev/install.ps1'))

$ErrorActionPreference = "Stop"

function Log($msg) { Write-Host "[INFO] $msg" -ForegroundColor Blue }
function Success($msg) { Write-Host "[SUCCESS] $msg" -ForegroundColor Green }

Write-Host "🚀 OpenRed One-Liner Installer" -ForegroundColor Magenta
Write-Host "==============================" -ForegroundColor Magenta

# Détection environnement
function Get-Environment {
    if (Get-Service -Name "W3SVC" -ErrorAction SilentlyContinue) {
        $global:HostingType = "iis"
        $global:InstallDir = "C:\inetpub\wwwroot\openred"
        Success "IIS détecté"
    } elseif (Test-Path "C:\xampp") {
        $global:HostingType = "xampp"
        $global:InstallDir = "C:\xampp\htdocs\openred"
        Success "XAMPP détecté"
    } else {
        $global:HostingType = "local"
        $global:InstallDir = "$env:USERPROFILE\openred"
        Log "Installation locale"
    }
}

# Installation
function Install-OpenRed {
    Log "Installation dans $InstallDir..."
    
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Set-Location $InstallDir
    
    # Télécharger
    $packageUrl = "https://github.com/DiegoMoralesMagri/OpenRed/releases/latest/download/openred-complete.zip"
    $packageFile = "openred.zip"
    
    try {
        (New-Object System.Net.WebClient).DownloadFile($packageUrl, $packageFile)
        
        # Extraire
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [System.IO.Compression.ZipFile]::ExtractToDirectory($packageFile, ".")
        Remove-Item $packageFile
        
        Success "OpenRed installé !"
    } catch {
        Write-Error "Erreur d'installation: $_"
    }
}

# Démarrage
function Start-Server {
    if ($HostingType -eq "local") {
        try {
            if (Get-Command python -ErrorAction SilentlyContinue) {
                Log "Démarrage du serveur..."
                Start-Process python -ArgumentList "app.py" -WindowStyle Hidden
                Success "Serveur démarré sur http://localhost:8000"
            }
        } catch {
            Log "Serveur à démarrer manuellement"
        }
    }
}

# Résultats
function Show-Results {
    Write-Host ""
    Success "🎉 Installation terminée !"
    
    switch ($HostingType) {
        "local" { Write-Host "🌐 Accès: http://localhost:8000" }
        default { Write-Host "🌐 Accès: http://votre-domaine.com/openred" }
    }
}

# Exécution
Get-Environment
Install-OpenRed
Start-Server
Show-Results