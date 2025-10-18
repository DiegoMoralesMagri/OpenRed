# 🌐 OpenRed - Installateur PowerShell pour Hébergement Mutualisé
# Installation automatique sur serveurs Windows partagés

param(
    [string]$InstallPath = ".",
    [switch]$Verbose
)

# Configuration
$ErrorActionPreference = "Stop"
$PackageUrls = @(
    "https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/openred-shared-hosting.zip",
    "https://github.com/DiegoMoralesMagri/OpenRed/raw/main/deployment/openred-shared-hosting.zip"
)
$PackageFile = "openred-shared-hosting.zip"

# Couleurs pour l'affichage
function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    
    $colors = @{
        "Red" = [ConsoleColor]::Red
        "Green" = [ConsoleColor]::Green
        "Yellow" = [ConsoleColor]::Yellow
        "Blue" = [ConsoleColor]::Blue
        "Cyan" = [ConsoleColor]::Cyan
        "White" = [ConsoleColor]::White
    }
    
    Write-Host $Text -ForegroundColor $colors[$Color]
}

function Write-Status {
    param([string]$Message)
    Write-ColorText "[INFO] $Message" "Blue"
}

function Write-Success {
    param([string]$Message)
    Write-ColorText "[✓] $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorText "[⚠] $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorText "[✗] $Message" "Red"
}

# En-tête
function Show-Header {
    Write-ColorText "🌐 OpenRed - Installation Hébergement Mutualisé" "Cyan"
    Write-ColorText "================================================" "Cyan"
    Write-Host ""
}

# Vérification de l'environnement
function Test-Environment {
    Write-Status "Vérification de l'environnement..."
    
    # Vérifier PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 3) {
        Write-Error "PowerShell 3.0+ requis"
        exit 1
    }
    Write-Success "PowerShell $($PSVersionTable.PSVersion.Major).$($PSVersionTable.PSVersion.Minor) détecté"
    
    # Vérifier les modules requis
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        Write-Success "Module de compression disponible"
    }
    catch {
        Write-Error "Module de compression non disponible"
        exit 1
    }
    
    # Créer le dossier d'installation si nécessaire
    if (!(Test-Path $InstallPath)) {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
        Write-Success "Dossier d'installation créé: $InstallPath"
    }
}

# Téléchargement du package
function Get-Package {
    Write-Status "Téléchargement du package OpenRed..."
    
    $packagePath = Join-Path $InstallPath $PackageFile
    
    foreach ($url in $PackageUrls) {
        Write-Status "Essai: $url"
        
        try {
            # Utiliser Invoke-WebRequest avec gestion d'erreurs
            $webClient = New-Object System.Net.WebClient
            $webClient.Headers.Add("User-Agent", "OpenRed-Installer/1.0")
            $webClient.DownloadFile($url, $packagePath)
            
            # Vérifier que le fichier existe et n'est pas vide
            if ((Test-Path $packagePath) -and ((Get-Item $packagePath).Length -gt 0)) {
                Write-Success "Package téléchargé avec succès ($([math]::Round((Get-Item $packagePath).Length / 1KB, 1)) KB)"
                return $packagePath
            }
        }
        catch {
            Write-Warning "Échec du téléchargement depuis $url : $($_.Exception.Message)"
            if (Test-Path $packagePath) {
                Remove-Item $packagePath -Force
            }
        }
    }
    
    Write-Error "Impossible de télécharger le package depuis aucune URL"
    exit 1
}

# Extraction et installation
function Install-Package {
    param([string]$PackagePath)
    
    Write-Status "Installation d'OpenRed..."
    
    try {
        # Vérifier l'intégrité du ZIP
        $zip = [System.IO.Compression.ZipFile]::OpenRead($PackagePath)
        $zip.Dispose()
        Write-Success "Package vérifié"
    }
    catch {
        Write-Error "Package corrompu: $($_.Exception.Message)"
        exit 1
    }
    
    try {
        # Extraction
        [System.IO.Compression.ZipFile]::ExtractToDirectory($PackagePath, $InstallPath)
        Write-Success "Fichiers extraits"
        
        # Supprimer le package
        Remove-Item $PackagePath -Force
        Write-Success "Package nettoyé"
    }
    catch {
        Write-Error "Erreur lors de l'extraction: $($_.Exception.Message)"
        exit 1
    }
}

# Test de l'installation
function Test-Installation {
    Write-Status "Test de l'installation..."
    
    $requiredFiles = @(
        "index.html",
        "app\index.html",
        "app\api.cgi",
        ".htaccess"
    )
    
    $allGood = $true
    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $InstallPath $file
        if (Test-Path $filePath) {
            Write-Success "✓ $file"
        }
        else {
            Write-Error "✗ $file manquant"
            $allGood = $false
        }
    }
    
    if (!$allGood) {
        Write-Error "Installation incomplète"
        exit 1
    }
    
    Write-Success "Installation vérifiée"
}

# Affichage des informations post-installation
function Show-Completion {
    Write-Host ""
    Write-ColorText "🎉 Installation terminée !" "Green"
    Write-ColorText "==========================" "Green"
    Write-Host ""
    
    Write-Host "📁 Fichiers installés dans: $((Resolve-Path $InstallPath).Path)"
    Write-Host "🌐 Page d'accueil: index.html"
    Write-Host "⚙️  Interface OpenRed: app\index.html"
    Write-Host "🔌 API: app\api.cgi"
    Write-Host ""
    
    Write-ColorText "📋 Prochaines étapes:" "Yellow"
    Write-Host "1. Uploadez ces fichiers vers votre hébergeur Windows"
    Write-Host "2. Configurez IIS pour supporter CGI/Python"
    Write-Host "3. Accédez à votre site web"
    Write-Host ""
    
    Write-ColorText "🔧 Hébergeurs Windows compatibles:" "Yellow"
    Write-Host "  ✅ Windows Shared Hosting avec IIS"
    Write-Host "  ✅ Plesk-based hosting"
    Write-Host "  ✅ DiscountASP.NET"
    Write-Host "  ✅ SmarterASP.NET"
    Write-Host ""
    
    Write-ColorText "💡 Configuration IIS requise:" "Yellow"
    Write-Host "  - Activer CGI dans les fonctionnalités IIS"
    Write-Host "  - Configurer .cgi pour exécuter Python"
    Write-Host "  - Vérifier les permissions d'exécution"
}

# Programme principal
function Main {
    try {
        Show-Header
        Write-Status "🚀 Démarrage de l'installation..."
        
        Test-Environment
        $packagePath = Get-Package
        Install-Package -PackagePath $packagePath
        Test-Installation
        Show-Completion
        
        Write-Host ""
        Write-Success "OpenRed installé avec succès ! 🎉"
    }
    catch {
        Write-Error "Erreur lors de l'installation: $($_.Exception.Message)"
        if ($Verbose) {
            Write-Host $_.ScriptStackTrace
        }
        exit 1
    }
}

# Point d'entrée
Main