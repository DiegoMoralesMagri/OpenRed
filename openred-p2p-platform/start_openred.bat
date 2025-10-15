@echo off
REM OpenRed P2P Platform - Démarrage Rapide Windows

echo 🌐 Démarrage OpenRed P2P Platform...

REM Vérifier Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python non trouvé. Installez Python 3.8+ d'abord.
    echo 📥 Télécharger depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Aller dans le répertoire du script
cd /d "%~dp0"

REM Vérifier l'environnement virtuel
if not exist "venv" (
    echo 🔧 Création de l'environnement virtuel...
    python -m venv venv
)

REM Activer l'environnement virtuel
echo 🔌 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Installer les dépendances si nécessaire
if not exist "venv\installed" (
    echo 📦 Installation des dépendances...
    pip install fastapi uvicorn websockets pillow cryptography
    echo. > venv\installed
)

REM Définir les variables d'environnement par défaut
if "%OPENRED_WEB_PORT%"=="" set OPENRED_WEB_PORT=8000
if "%OPENRED_P2P_PORT%"=="" set OPENRED_P2P_PORT=8080
if "%OPENRED_DATA_DIR%"=="" set OPENRED_DATA_DIR=.\user_data
if "%OPENRED_SPIDER_ENABLED%"=="" set OPENRED_SPIDER_ENABLED=true

REM Créer le répertoire de données si nécessaire
if not exist "%OPENRED_DATA_DIR%" mkdir "%OPENRED_DATA_DIR%"

echo 🚀 Démarrage du serveur OpenRed...
echo 📱 Interface web : http://localhost:%OPENRED_WEB_PORT%
echo 🔗 Port P2P : %OPENRED_P2P_PORT%
echo 💾 Données : %OPENRED_DATA_DIR%
echo 🕷️ Spider Internet : %OPENRED_SPIDER_ENABLED%
echo.
echo 👆 Appuyez sur Ctrl+C pour arrêter
echo ================================================

REM Démarrer le serveur
python web\backend\web_api.py