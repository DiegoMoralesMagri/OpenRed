#!/bin/bash
# Guide de déploiement rapide O2Switch
# Quick O2Switch deployment guide

echo "🔧 Configuration O2Switch pour OpenRed Central API"

# 1. Vérifications préliminaires
echo "📍 Vérifications système..."
echo "Python version: $(python3 --version)"
echo "Pip version: $(pip3 --version)"
echo "Répertoire actuel: $(pwd)"
echo "Utilisateur: $(whoami)"

# 2. Installation sans environnement virtuel
echo "📦 Installation des dépendances..."
pip3 install --user fastapi uvicorn sqlalchemy pymysql python-jose passlib python-multipart pydantic python-dotenv

# 3. Configuration des variables d'environnement
echo "⚙️ Configuration environnement..."
cp .env.o2switch .env

# 4. Création des répertoires nécessaires
mkdir -p keys logs

# 5. Génération des clés (si OpenSSL disponible)
if command -v openssl &> /dev/null; then
    echo "🔐 Génération des clés RSA..."
    openssl genrsa -out keys/jwt_private.pem 2048
    openssl rsa -in keys/jwt_private.pem -outform PEM -pubout -out keys/jwt_public.pem
    chmod 600 keys/*.pem
else
    echo "⚠️ OpenSSL non disponible, utilisation de clés par défaut"
fi

# 6. Test de l'application
echo "🧪 Test de l'application..."
python3 -c "
try:
    from passenger_wsgi import application
    print('✅ Application WSGI chargée avec succès')
except Exception as e:
    print(f'❌ Erreur: {e}')
"

echo "✅ Configuration O2Switch terminée"
echo "📝 N'oubliez pas de:"
echo "   1. Configurer votre base de données MySQL dans .env"
echo "   2. Modifier les CORS pour votre domaine"
echo "   3. Changer les clés secrètes"
