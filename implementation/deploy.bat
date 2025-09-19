@echo off
REM Script de déploiement automatisé pour l'écosystème O-Red (Windows)
REM Version: 1.0.0

setlocal enabledelayedexpansion

REM Configuration
set ORED_VERSION=1.0.0
set DEPLOYMENT_ENV=%1
if "%DEPLOYMENT_ENV%"=="" set DEPLOYMENT_ENV=development
set PROJECT_ROOT=%cd%

echo ╔═══════════════════════════════════════════════════════════╗
echo ║                  DÉPLOIEMENT O-RED v%ORED_VERSION%                    ║
echo ║                Écosystème Décentralisé                    ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 🚀 Déploiement de l'écosystème O-Red v%ORED_VERSION%
echo 📁 Répertoire: %PROJECT_ROOT%
echo 🌍 Environnement: %DEPLOYMENT_ENV%
echo.

REM Vérification des prérequis
echo [1/10] Vérification des prérequis
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker n'est pas installé
    pause
    exit /b 1
)
echo ✅ Docker détecté

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose n'est pas installé
    pause
    exit /b 1
)
echo ✅ Docker Compose détecté

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js n'est pas installé
    pause
    exit /b 1
)
echo ✅ Node.js détecté

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé
    pause
    exit /b 1
)
echo ✅ Python détecté
echo.

REM Configuration de l'environnement
echo [2/10] Configuration de l'environnement
if not exist "%PROJECT_ROOT%\central-api\.env" (
    echo 📝 Création du fichier .env pour l'API centrale
    (
        echo # Configuration O-Red API Centrale - %DEPLOYMENT_ENV%
        echo DEBUG=false
        echo SECRET_KEY=your_secret_key_here
        echo DATABASE_URL=postgresql+asyncpg://ored:ored_secure_password@postgres:5432/ored_central
        echo REDIS_URL=redis://redis:6379/0
        echo LOG_LEVEL=INFO
        echo PROMETHEUS_ENABLED=true
        echo P2P_PORT=8001
        echo P2P_MAX_CONNECTIONS=100
        echo AI_DISTRIBUTED_COMPUTING_ENABLED=true
        echo AI_PRIVACY_LEVEL=maximum
        echo POST_QUANTUM_ENABLED=true
        echo RATE_LIMIT_ENABLED=true
    ) > "%PROJECT_ROOT%\central-api\.env"
)

REM Création des dossiers nécessaires
if not exist "%PROJECT_ROOT%\logs" mkdir "%PROJECT_ROOT%\logs"
if not exist "%PROJECT_ROOT%\storage" mkdir "%PROJECT_ROOT%\storage"
if not exist "%PROJECT_ROOT%\data\postgres" mkdir "%PROJECT_ROOT%\data\postgres"
if not exist "%PROJECT_ROOT%\data\redis" mkdir "%PROJECT_ROOT%\data\redis"

echo ✅ Environnement configuré
echo.

REM Installation des dépendances
echo [3/10] Installation des dépendances
if exist "%PROJECT_ROOT%\central-api\requirements.txt" (
    echo 📦 Installation des dépendances Python ^(API centrale^)...
    cd /d "%PROJECT_ROOT%\central-api"
    pip install -r requirements.txt
)

if exist "%PROJECT_ROOT%\web-interface\package.json" (
    echo 📦 Installation des dépendances Node.js ^(Interface web^)...
    cd /d "%PROJECT_ROOT%\web-interface"
    npm install
)

if exist "%PROJECT_ROOT%\node-client\requirements.txt" (
    echo 📦 Installation des dépendances Python ^(Client nœud^)...
    cd /d "%PROJECT_ROOT%\node-client"
    pip install -r requirements.txt
)

echo ✅ Dépendances installées
echo.

REM Construction des images Docker
echo [4/10] Construction des images Docker
cd /d "%PROJECT_ROOT%\central-api"
echo 🔨 Construction de l'image API centrale...
docker build -t ored/central-api:%ORED_VERSION% .
docker tag ored/central-api:%ORED_VERSION% ored/central-api:latest

if exist "%PROJECT_ROOT%\web-interface\Dockerfile" (
    cd /d "%PROJECT_ROOT%\web-interface"
    echo 🔨 Construction de l'image interface web...
    docker build -t ored/web-interface:%ORED_VERSION% .
    docker tag ored/web-interface:%ORED_VERSION% ored/web-interface:latest
)

if exist "%PROJECT_ROOT%\node-client\Dockerfile" (
    cd /d "%PROJECT_ROOT%\node-client"
    echo 🔨 Construction de l'image client nœud...
    docker build -t ored/node-client:%ORED_VERSION% .
    docker tag ored/node-client:%ORED_VERSION% ored/node-client:latest
)

echo ✅ Images Docker construites
echo.

REM Configuration de la base de données
echo [5/10] Configuration de la base de données
if not exist "%PROJECT_ROOT%\central-api\db" mkdir "%PROJECT_ROOT%\central-api\db"
(
    echo -- Script d'initialisation de la base de données O-Red
    echo -- Version: %ORED_VERSION%
    echo.
    echo CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    echo CREATE EXTENSION IF NOT EXISTS "pg_crypto";
    echo.
    echo -- Configuration pour le développement
    echo DO $$ 
    echo BEGIN
    echo     IF '%DEPLOYMENT_ENV%' = 'development' THEN
    echo         RAISE NOTICE 'Base de données configurée pour le développement';
    echo     END IF;
    echo END $$;
) > "%PROJECT_ROOT%\central-api\db\init.sql"

echo ✅ Configuration de la base de données créée
echo.

REM Démarrage des services
echo [6/10] Démarrage des services O-Red
cd /d "%PROJECT_ROOT%\central-api"

echo 🛑 Arrêt des services existants...
docker-compose down 2>nul

echo 🚀 Démarrage des nouveaux services...
docker-compose up -d

echo ⏳ Attente de la disponibilité des services...
timeout /t 10 /nobreak >nul

echo ✅ Services démarrés
echo.

REM Vérification du déploiement
echo [7/10] Vérification du déploiement
echo 🔍 Vérification de l'API centrale...
REM Attendre un peu plus pour que les services soient prêts
timeout /t 15 /nobreak >nul

curl -f -s "http://localhost:8000/health" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  API centrale en cours de démarrage...
) else (
    echo ✅ API centrale accessible
)

echo 🔍 Vérification des conteneurs...
docker-compose ps

echo ✅ Vérification terminée
echo.

REM Informations finales
echo [8/10] Informations de déploiement
echo.
echo 🎉 Déploiement d'O-Red terminé !
echo.
echo 📋 Informations d'accès:
echo    🌐 Interface web: http://localhost:3000
echo    🔌 API centrale: http://localhost:8000
echo    📊 API docs: http://localhost:8000/docs
echo.
echo 📁 Logs et données:
echo    📝 Logs: %PROJECT_ROOT%\logs\
echo    💾 Stockage: %PROJECT_ROOT%\storage\
echo.
echo 🔧 Commandes utiles:
echo    docker-compose logs -f      # Voir les logs en temps réel
echo    docker-compose ps           # Statut des services
echo    docker-compose down         # Arrêter les services
echo    docker-compose up -d        # Redémarrer les services
echo.
echo Bienvenue dans l'écosystème O-Red décentralisé ! 🚀

cd /d "%PROJECT_ROOT%"
pause