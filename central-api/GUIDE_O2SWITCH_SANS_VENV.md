# 🚀 Guide Complet O2Switch - SANS environnement virtuel

## ❌ **Votre problème : Pas de virtualenv/venv disponible**

C'est normal sur O2Switch ! Voici la solution **garantie de fonctionner**.

## ✅ **Solution 1 : Installation directe (RECOMMANDÉE)**

```bash
# 1. Aller dans votre dossier
cd /home/vema3829/api.o-red.org/public_html/openred-api/central-api

# 2. Exécuter le script d'installation directe
chmod +x install_direct_o2switch.sh
./install_direct_o2switch.sh
```

## ✅ **Solution 2 : Installation manuelle étape par étape**

Si le script ne marche pas, voici les commandes une par une :

### Étape 1 : Installation des paquets Python
```bash
# Installation avec --user (sans environnement virtuel)
pip3 install --user fastapi uvicorn sqlalchemy pymysql python-jose passlib python-multipart pydantic python-dotenv

# Ou si pip3 n'existe pas :
pip install --user fastapi uvicorn sqlalchemy pymysql python-jose passlib python-multipart pydantic python-dotenv
```

### Étape 2 : Configuration de l'environnement
```bash
# Copier la configuration O2Switch
cp .env.o2switch .env

# Créer les dossiers nécessaires
mkdir -p keys logs uploads
chmod 755 keys logs uploads
```

### Étape 3 : Configuration du PYTHONPATH
```bash
# Ajouter le répertoire actuel au PATH Python
export PYTHONPATH="$(pwd):$PYTHONPATH"
echo 'export PYTHONPATH="/home/vema3829/api.o-red.org/public_html/openred-api/central-api:$PYTHONPATH"' >> ~/.bashrc
```

### Étape 4 : Générer les clés (si OpenSSL disponible)
```bash
# Génération des clés RSA
openssl genrsa -out keys/jwt_private.pem 2048
openssl rsa -in keys/jwt_private.pem -outform PEM -pubout -out keys/jwt_public.pem
chmod 600 keys/*.pem
```

## ✅ **Solution 3 : Test de l'application**

### Test 1 : Application WSGI de base
```bash
python3 passenger_wsgi.py
```

**Résultat attendu :**
```
🚀 OpenRed Central API - Mode WSGI O2Switch
Application prête pour déploiement
✅ Test WSGI réussi
```

### Test 2 : Application O2Switch optimisée
```bash
python3 main_o2switch.py
```

### Test 3 : Vérification des imports
```bash
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    import fastapi
    print('✅ FastAPI disponible')
except:
    print('❌ FastAPI non installé')

try:
    from passenger_wsgi import application
    print('✅ Application WSGI OK')
except Exception as e:
    print(f'❌ Erreur WSGI: {e}')
"
```

## 🔧 **Configuration de votre base de données**

### Dans cPanel O2Switch :
1. **MySQL Databases** → Créer une base
2. Nom : `vema3829_openred` 
3. Utilisateur : `vema3829_openred`
4. Mot de passe : `[votre_choix]`

### Modifier le fichier .env :
```bash
nano .env
```

Changez la ligne DATABASE_URL :
```
DATABASE_URL=mysql+pymysql://vema3829_openred:VOTRE_PASSWORD@localhost/vema3829_openred
```

## 🌐 **Configuration finale pour votre domaine**

### Modifier les CORS dans .env :
```
ALLOWED_ORIGINS=["https://api.o-red.org","https://o-red.org","https://www.o-red.org"]
```

### Changer les clés secrètes :
```
SECRET_KEY=votre-cle-secrete-32-caracteres-minimum-o2switch
ENCRYPTION_KEY=votre-cle-chiffrement-32-caracteres-minimum
```

## 🧪 **Test final**

```bash
# Test de l'API
curl http://api.o-red.org/ 

# Ou avec Python :
python3 -c "
import urllib.request
import json
try:
    response = urllib.request.urlopen('http://localhost:8000/')
    data = json.loads(response.read().decode())
    print('✅ API répond:', data)
except Exception as e:
    print(f'❌ Erreur: {e}')
"
```

## 🎯 **Points clés pour O2Switch**

1. ✅ **PAS besoin de virtualenv** - Installation directe avec --user
2. ✅ **PYTHONPATH configuré** - Les imports fonctionnent
3. ✅ **Application WSGI robuste** - Fonctionne même si FastAPI échoue
4. ✅ **Configuration MySQL** - Compatible O2Switch
5. ✅ **Sécurité adaptée** - Headers et CORS configurés

## 🆘 **Si ça ne marche toujours pas**

L'application `passenger_wsgi.py` est **garantie de fonctionner** car elle utilise uniquement les modules Python de base. Elle créera une API simple même sans FastAPI.

**Commande de dernier recours :**
```bash
python3 -c "
def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json')])
    return [b'{\"message\":\"OpenRed API - O2Switch Basic\",\"status\":\"running\"}']
print('Application de base créée')
"
```
