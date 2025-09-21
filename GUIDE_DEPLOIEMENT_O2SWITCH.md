# 🚀 Guide de Déploiement OpenRed sur O2Switch (Version 2.0)

## Prérequis
- Accès cPanel à votre hébergement O2Switch
- Domaine configuré (ex: votre-domaine.com)
- Accès SSH (optionnel mais recommandé)
- Python 3.8+ (généralement disponible sur O2Switch)

## 📦 Nouveautés Version 2.0
- ✅ Application optimisée pour O2Switch (`main_o2switch.py`)
- ✅ Script d'installation amélioré avec gestion d'erreurs
- ✅ Validation automatique du déploiement
- ✅ Configuration simplifiée pour hébergement partagé
- ✅ Scripts de diagnostic et de dépannage
- ✅ Gestion des sauvegardes automatiques

## Étape 1: Configuration cPanel

### 1.1 Création des sous-domaines
Dans cPanel > Sous-domaines, créez :
- `api.votre-domaine.com` → pointant vers `/home/username/openred_api`
- `node.votre-domaine.com` → pointant vers `/home/username/openred_node` (optionnel)

### 1.2 Base de données MySQL
Dans cPanel > Bases de données MySQL :
1. **Créer une base** : `openred_db` (le nom final sera préfixé par votre username)
2. **Créer un utilisateur** : `openred_user` (sera aussi préfixé)
3. **Assigner TOUS les privilèges** à l'utilisateur sur la base
4. **Noter les noms complets** avec préfixes pour la configuration

### 1.3 Certificats SSL
Dans cPanel > SSL/TLS, activez AutoSSL pour :
- votre-domaine.com
- api.votre-domaine.com

## Étape 2: Upload du Code

### 2.1 Via File Manager cPanel (Recommandé pour débutants)
1. Aller dans File Manager cPanel
2. Créer le dossier `openred_api` dans votre répertoire home
3. Uploader et extraire le contenu de `implementation/central-api/`

### 2.2 Via FTP/SFTP (Recommandé pour utilisateurs avancés)
```bash
# Upload vers le serveur
scp -r implementation/central-api/* username@votre-serveur.o2switch.net:~/openred_api/
```

### 2.3 Via Git (Si disponible)
```bash
# Sur le serveur via SSH
cd ~
git clone https://github.com/DiegoMoralesMagri/OpenRed.git
cp -r OpenRed/implementation/central-api openred_api
```

## Étape 3: Installation Automatisée

### 3.1 Via SSH (Recommandé)
```bash
# Connexion SSH
ssh username@votre-serveur.o2switch.net

# Navigation et installation
cd ~/openred_api
chmod +x install_o2switch.sh
./install_o2switch.sh
```

### 3.2 Via Terminal cPanel
Si SSH n'est pas disponible, utilisez le Terminal dans cPanel :
```bash
cd ~/openred_api
chmod +x install_o2switch.sh
bash install_o2switch.sh
```

Le script d'installation va :
- ✅ Vérifier l'environnement Python
- ✅ Créer un environnement virtuel
- ✅ Installer les dépendances (minimal ou complet)
- ✅ Créer les scripts de gestion
- ✅ Configurer les permissions
- ✅ Créer une sauvegarde si installation existante

## Étape 4: Configuration

### 4.1 Configuration de l'environnement
Le script a créé `.env.production` à partir du template. Éditez-le :

```bash
nano ~/openred_api/.env.production
```

**Variables essentielles à modifier :**
```env
# Base de données (remplacez par vos vraies valeurs)
DATABASE_URL=mysql+pymysql://username_openred_user:MOT_DE_PASSE@localhost/username_openred_db

# Sécurité (OBLIGATOIRE - générez une clé forte)
SECRET_KEY=votre_cle_secrete_super_forte_32_caracteres_minimum

# Domaine (remplacez par votre vrai domaine)
DOMAIN=votre-domaine.com
API_DOMAIN=api.votre-domaine.com
ALLOWED_ORIGINS=["https://votre-domaine.com","https://api.votre-domaine.com"]
ALLOWED_HOSTS=["votre-domaine.com","api.votre-domaine.com"]
```

### 4.2 Génération d'une clé secrète forte
```bash
# Méthode 1: Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# Méthode 2: OpenSSL (si disponible)
openssl rand -hex 32
```

## Étape 5: Configuration Python App (cPanel)

### 5.1 Création de l'application Python
Dans cPanel > Python App :
1. **Créer une nouvelle app Python**
2. **Version Python** : 3.8+ (la plus récente disponible)
3. **Domaine** : api.votre-domaine.com
4. **Répertoire** : openred_api
5. **Point d'entrée** : `app/main_o2switch.py` (version optimisée)
6. **Variable PYTHONPATH** : `/home/username/openred_api`

### 5.2 Variables d'environnement dans l'app Python
Ajouter dans l'interface Python App :
- `ENVIRONMENT=production`
- `O2SWITCH_MODE=True`
- `DEBUG=False`

## Étape 6: Validation et Tests

### 6.1 Validation automatique
```bash
cd ~/openred_api
python3 validate_o2switch.py

# Pour un rapport détaillé
python3 validate_o2switch.py --verbose --save-report
```

### 6.2 Tests manuels
```bash
# Test de base
~/openred_api/test.sh

# Diagnostic complet
~/openred_api/diagnostic_o2switch.sh
```

### 6.3 Tests via navigateur
Une fois l'app Python démarrée dans cPanel :

- **Health check** : `https://api.votre-domaine.com/health`
- **Diagnostic système** : `https://api.votre-domaine.com/diagnostic`
- **API nœuds** : `https://api.votre-domaine.com/api/v1/nodes`
- **Documentation** : `https://api.votre-domaine.com/docs` (si DEBUG=True)

## Étape 7: Premier Nœud (Optionnel)

### 7.1 Installation du nœud
Répéter le processus pour le node-client dans `openred_node/`

### 7.2 Configuration
Pointer le nœud vers l'API centrale : `https://api.votre-domaine.com`

## 🔧 Scripts de Gestion

Le script d'installation crée plusieurs utilitaires :

### Scripts principaux
- `~/openred_api/start.sh` - Démarrage manuel de l'API
- `~/openred_api/test.sh` - Tests de fonctionnement
- `~/openred_api/diagnostic_o2switch.sh` - Diagnostic complet

### Validation et diagnostic
- `python3 validate_o2switch.py` - Validation du déploiement
- `python3 diagnostic.py` - Diagnostic système simple

## 🚨 Dépannage

### Erreur 500 Internal Server Error

#### 1. Vérification des logs
```bash
# Logs d'erreur cPanel
tail -f ~/logs/error.log

# Logs d'accès
tail -f ~/logs/access.log
```

#### 2. Diagnostic système
```bash
cd ~/openred_api
python3 diagnostic_o2switch.sh
```

#### 3. Validation complète
```bash
python3 validate_o2switch.py --verbose
```

#### 4. Solutions courantes

**Modules manquants :**
```bash
cd ~/openred_api
source venv/bin/activate
pip install -r requirements-minimal.txt
```

**Configuration incorrecte :**
- Vérifiez `.env.production`
- Vérifiez la configuration Python App dans cPanel
- Vérifiez les permissions : `chmod 755 ~/openred_api`

**Base de données :**
- Vérifiez la création de la base MySQL dans cPanel
- Vérifiez les credentials dans `DATABASE_URL`
- Testez la connexion : `python3 -c "import pymysql; print('OK')"`

### Mode de secours

Si l'application principale ne fonctionne pas, utilisez la version simple :

1. Dans cPanel > Python App, changez le point d'entrée vers : `app/main_simple.py`
2. Ou utilisez : `app/index.py` (qui charge automatiquement la version appropriée)

### Erreurs communes

| Erreur | Cause | Solution |
|--------|-------|----------|
| 500 Error | Modules manquants | Réinstaller avec `install_o2switch.sh` |
| Import Error | Mauvais PYTHONPATH | Vérifier la config Python App |
| Database Error | Credentials incorrects | Vérifier `.env.production` |
| Permission Denied | Permissions fichiers | `chmod 755 ~/openred_api` |

## 📊 Monitoring et Maintenance

### Vérifications régulières
- Health check : `https://api.votre-domaine.com/health`
- Diagnostic : `https://api.votre-domaine.com/diagnostic`
- Logs : `tail -f ~/logs/openred-api.log`

### Sauvegardes
Le script d'installation crée automatiquement des sauvegardes dans :
`~/openred_backup/openred_api_backup_YYYYMMDD_HHMMSS/`

### Mises à jour
```bash
cd ~/openred_api
# Créer une sauvegarde
cp -r . ~/openred_backup/backup_$(date +%Y%m%d_%H%M%S)

# Mettre à jour le code
git pull origin main  # Si installé via Git
# Ou re-upload via FTP/cPanel

# Réinstaller les dépendances si nécessaire
source venv/bin/activate
pip install -r requirements-production.txt
```

## 🆘 Support

### Ressources
- **Documentation officielle** : https://github.com/DiegoMoralesMagri/OpenRed
- **Issues GitHub** : https://github.com/DiegoMoralesMagri/OpenRed/issues
- **Support O2Switch** : Via votre espace client O2Switch

### Informations utiles pour le support
Avant de contacter le support, collectez ces informations :

```bash
cd ~/openred_api
python3 validate_o2switch.py --save-report
# Rapport sauvegardé dans validation_report_XXXXXXXX.json
```

### Contact
- Support technique O2Switch : Pour les problèmes d'hébergement
- Issues GitHub : Pour les problèmes spécifiques à OpenRed
- Documentation : Pour les guides et tutoriels

---

## ✅ Checklist de déploiement

- [ ] Sous-domaine `api.votre-domaine.com` configuré
- [ ] Base de données MySQL créée avec utilisateur
- [ ] Code uploadé dans `~/openred_api`
- [ ] Script `install_o2switch.sh` exécuté avec succès
- [ ] Fichier `.env.production` configuré avec vraies valeurs
- [ ] Application Python créée dans cPanel
- [ ] Point d'entrée configuré : `app/main_o2switch.py`
- [ ] Variables d'environnement configurées dans Python App
- [ ] Tests de validation réussis : `python3 validate_o2switch.py`
- [ ] Health check accessible : `https://api.votre-domaine.com/health`
- [ ] Certificat SSL activé et fonctionnel

**🎉 Déploiement réussi ! Votre API OpenRed est opérationnelle sur O2Switch.**