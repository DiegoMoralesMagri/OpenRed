#!/bin/bash
# Installation directe sans environnement virtuel pour O2Switch
# Direct installation without virtual environment for O2Switch

echo "🚀 Configuration OpenRed pour O2Switch (sans virtualenv)"
echo "🚀 OpenRed configuration for O2Switch (without virtualenv)"

# 1. Vérifications système
echo "📍 Vérifications système..."
echo "Python version: $(python3 --version 2>/dev/null || python --version)"
echo "Pip version: $(pip3 --version 2>/dev/null || pip --version)"
echo "Répertoire actuel: $(pwd)"
echo "Utilisateur: $(whoami)"

# 2. Installation directe des paquets essentiels avec --user
echo "📦 Installation des dépendances (mode --user)..."

# Paquets essentiels un par un pour éviter les conflits
pip3 install --user fastapi==0.104.1 || pip install --user fastapi==0.104.1
pip3 install --user uvicorn==0.24.0 || pip install --user uvicorn==0.24.0
pip3 install --user sqlalchemy==2.0.23 || pip install --user sqlalchemy==2.0.23
pip3 install --user pymysql==1.1.0 || pip install --user pymysql==1.1.0
pip3 install --user "python-jose[cryptography]==3.3.0" || pip install --user "python-jose[cryptography]==3.3.0"
pip3 install --user "passlib[bcrypt]==1.7.4" || pip install --user "passlib[bcrypt]==1.7.4"
pip3 install --user python-multipart==0.0.6 || pip install --user python-multipart==0.0.6
pip3 install --user pydantic==2.5.0 || pip install --user pydantic==2.5.0
pip3 install --user python-dotenv==1.0.0 || pip install --user python-dotenv==1.0.0

echo "✅ Dépendances installées"

# 3. Configuration de l'environnement
echo "⚙️ Configuration de l'environnement..."

# Copier le fichier de configuration O2Switch
if [ -f ".env.o2switch" ]; then
    cp .env.o2switch .env
    echo "✅ Fichier .env configuré"
else
    echo "⚠️ Fichier .env.o2switch non trouvé, création manuelle..."
fi

# 4. Création des répertoires nécessaires
mkdir -p keys logs uploads
chmod 755 keys logs uploads

# 5. Génération des clés RSA (si OpenSSL disponible)
if command -v openssl &> /dev/null; then
    echo "🔐 Génération des clés RSA..."
    if [ ! -f "keys/jwt_private.pem" ]; then
        openssl genrsa -out keys/jwt_private.pem 2048 2>/dev/null
        openssl rsa -in keys/jwt_private.pem -outform PEM -pubout -out keys/jwt_public.pem 2>/dev/null
        chmod 600 keys/*.pem
        echo "✅ Clés RSA générées"
    else
        echo "✅ Clés RSA déjà présentes"
    fi
else
    echo "⚠️ OpenSSL non disponible, utilisez les clés par défaut"
fi

# 6. Configuration du PYTHONPATH pour les imports
echo "🔧 Configuration du PYTHONPATH..."
CURRENT_DIR=$(pwd)
export PYTHONPATH="$CURRENT_DIR:$PYTHONPATH"
echo "export PYTHONPATH=\"$CURRENT_DIR:\$PYTHONPATH\"" >> ~/.bashrc

# 7. Test de l'application
echo "🧪 Test de l'application..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from passenger_wsgi import application
    print('✅ Application WSGI chargée avec succès')
except Exception as e:
    print(f'❌ Erreur: {e}')
    print('Création d\'une application de base...')
"

echo ""
echo "✅ Configuration terminée sans environnement virtuel"
echo "📝 Étapes suivantes:"
echo "   1. Configurez votre base de données MySQL dans .env"
echo "   2. Modifiez les CORS pour votre domaine dans .env"
echo "   3. Changez les clés secrètes dans .env"
echo "   4. Testez avec: python3 passenger_wsgi.py"
