# 🚀 Guide de Déploiement OpenRed sur O2Switch

## Prérequis
- Accès cPanel à votre hébergement O2Switch
- Domaine o-red.org configuré
- Accès SSH (optionnel mais recommandé)

## Étape 1: Configuration cPanel

### 1.1 Création des sous-domaines
Dans cPanel > Sous-domaines, créez :
- `api.o-red.org` → pointant vers `/home/username/openred_api`
- `node.o-red.org` → pointant vers `/home/username/openred_node`
- `docs.o-red.org` → pointant vers `/home/username/openred_docs`

### 1.2 Base de données MySQL
Dans cPanel > Bases de données MySQL :
1. Créer une base : `openred_db`
2. Créer un utilisateur : `openred_user` 
3. Assigner TOUS les privilèges à l'utilisateur sur la base

### 1.3 Certificats SSL
Dans cPanel > SSL/TLS, activez AutoSSL pour :
- o-red.org
- api.o-red.org
- node.o-red.org

## Étape 2: Upload du Code

### 2.1 Via File Manager cPanel
1. Aller dans File Manager
2. Créer le dossier `openred_api`
3. Uploader tout le contenu de `implementation/central-api/`

### 2.2 Via FTP (recommandé)
```bash
# Upload vers le serveur
ftp your-server.o2switch.net
cd openred_api
put -r implementation/central-api/*
```

## Étape 3: Installation

### 3.1 Configuration de l'environnement
1. Copier `.env.production.template` vers `.env.production`
2. Éditer `.env.production` avec vos vraies valeurs :
   ```env
   DATABASE_URL=mysql+pymysql://openred_user:VOTRE_MOT_DE_PASSE@localhost/openred_db
   SECRET_KEY=VOTRE_CLE_SECRETE_SUPER_FORTE
   DOMAIN=o-red.org
   ```

### 3.2 Installation des dépendances
Via SSH ou Terminal cPanel :
```bash
cd ~/openred_api
chmod +x install_o2switch.sh
./install_o2switch.sh
```

### 3.3 Configuration du serveur web
Créer un fichier `.htaccess` dans `/openred_api` :
```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.py/$1 [QSA,L]
```

## Étape 4: Configuration Python pour cPanel

### 4.1 Application Python
Dans cPanel > Python App :
1. Créer une nouvelle app Python
2. Version Python : 3.9+
3. Domaine : api.o-red.org
4. Répertoire : openred_api
5. Point d'entrée : app/main.py
6. Variable PYTHONPATH : /home/username/openred_api

### 4.2 Variables d'environnement
Ajouter dans l'app Python :
- `ENVIRONMENT=production`
- `DATABASE_URL=mysql+pymysql://...`
- `SECRET_KEY=...`

## Étape 5: Tests

### 5.1 Test de l'API
Vérifier : `https://api.o-red.org/health`
Réponse attendue : `{"status": "healthy"}`

### 5.2 Test de la base de données
Vérifier : `https://api.o-red.org/api/v1/nodes`
Réponse : Liste des nœuds (vide au début)

## Étape 6: Premier Nœud

### 6.1 Installation du nœud
Répéter le processus pour le node-client dans `openred_node/`

### 6.2 Configuration
Pointer le nœud vers l'API centrale : `https://api.o-red.org`

## Dépannage

### Erreurs communes
- **500 Error** : Vérifier les logs dans cPanel
- **Database Error** : Vérifier les credentials MySQL
- **Import Error** : Vérifier l'installation des dépendances

### Logs
Consulter les logs dans :
- cPanel > Logs d'erreur
- `/home/username/logs/openred-api.log`

## Support
- Documentation : https://github.com/DiegoMoralesMagri/OpenRed
- Issues : https://github.com/DiegoMoralesMagri/OpenRed/issues