# 🚀 OpenRed Universal Deployment Guide

## 📋 Guide Complet de Déploiement

Déployez OpenRed sur n'importe quel hébergeur en quelques minutes !

---

## 🎯 Installation One-Click

### Option 1: Package ZIP (Recommandé)

1. **Téléchargez** le package: `openred_simple_YYYYMMDD_HHMM.zip`
2. **Décompressez** sur votre ordinateur
3. **Uploadez** via FTP/cPanel dans votre répertoire web
4. **Accédez** à votre site → OpenRed sera opérationnel !

### Option 2: Commande Terminal (VPS/SSH)

```bash
# Télécharger et installer automatiquement
curl -L https://votre-repo.com/install.sh | bash

# Ou si wget est disponible
wget -O - https://votre-repo.com/install.sh | bash
```

---

## 🏢 Configuration par Hébergeur

### 🟢 O2Switch

**Répertoire d'installation:** `/public_html/openred/`

**Méthode 1: FTP**
1. Connectez-vous à votre FTP O2Switch
2. Naviguez vers `/public_html/`
3. Créez le dossier `openred`
4. Uploadez tous les fichiers du package
5. URL d'accès: `http://votre-domaine.com/openred`

**Méthode 2: cPanel File Manager**
1. Connectez-vous à cPanel O2Switch
2. Ouvrez "Gestionnaire de fichiers"
3. Naviguez vers `public_html`
4. Créez le dossier `openred`
5. Uploadez le ZIP et décompressez-le directement

**Méthode 3: Script Auto (si SSH disponible)**
```bash
cd ~/public_html
mkdir openred
cd openred
# Uploadez puis exécutez:
python3 install_o2switch.py
```

**✅ Spécificités O2Switch:**
- Python 3 disponible
- .htaccess supporté
- SQLite autorisé
- Répertoire: `public_html`
- URL: `http://votre-domaine.com/openred`

---

### 🟠 OVH

**Répertoire d'installation:** `/www/openred/`

**Installation FTP:**
1. Connectez-vous à votre FTP OVH
2. Naviguez vers `/www/`
3. Créez le dossier `openred`
4. Uploadez tous les fichiers
5. URL d'accès: `http://votre-domaine.com/openred`

**Installation SSH (si disponible):**
```bash
cd ~/www
mkdir openred
cd openred
# Uploadez les fichiers puis:
python3 app.py  # Test local
```

**✅ Spécificités OVH:**
- Python supporté selon l'offre
- SSH sur certaines offres
- .htaccess supporté
- Répertoire: `www`

---

### 🔵 Hostinger

**Répertoire d'installation:** `/public_html/openred/`

**Installation via File Manager:**
1. Connectez-vous à hPanel Hostinger
2. Ouvrez "Gestionnaire de fichiers"
3. Naviguez vers `public_html`
4. Créez le dossier `openred`
5. Uploadez et décompressez le package

**✅ Spécificités Hostinger:**
- Python disponible sur certaines offres
- .htaccess supporté
- Interface hPanel intuitive
- Répertoire: `public_html`

---

### 🟣 VPS/Serveur Dédié

**Répertoire d'installation:** `/var/www/html/openred/`

**Installation complète:**
```bash
# Se connecter en SSH
ssh user@votre-serveur.com

# Naviguer vers le répertoire web
cd /var/www/html

# Créer le répertoire OpenRed
sudo mkdir openred
cd openred

# Télécharger et installer
wget https://votre-repo.com/openred_package.zip
unzip openred_package.zip

# Configurer les permissions
sudo chown -R www-data:www-data .
sudo chmod 755 app.py

# Tester l'installation
python3 app.py
```

**Configuration Nginx (optionnel):**
```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    root /var/www/html/openred;
    index app.py index.html;
    
    location / {
        try_files $uri $uri/ @python;
    }
    
    location @python {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/openred.sock;
    }
}
```

---

## 🔧 Configuration Post-Installation

### 1. Première Connexion

**URL d'accès:** `http://votre-domaine.com/openred`

**Vérifications:**
- ✅ Page d'accueil OpenRed s'affiche
- ✅ Message "Déployé avec succès"
- ✅ Boutons fonctionnels

### 2. Test API

Cliquez sur "Test API" ou accédez à:
`http://votre-domaine.com/openred/api/status`

**Réponse attendue:**
```json
{
    "status": "running",
    "app": "OpenRed", 
    "timestamp": "2025-10-14T18:17:00"
}
```

### 3. Sécurisation (Recommandé)

**HTTPS:**
- Activez SSL/TLS dans votre panneau d'hébergement
- Ou utilisez Let's Encrypt (VPS)

**Permissions (VPS):**
```bash
sudo chown -R www-data:www-data /var/www/html/openred
sudo chmod 644 *.py
sudo chmod 644 .htaccess
sudo chmod 755 app.py
```

---

## 🛠️ Personnalisation

### Modifier l'Application

**Éditer `app.py`:**
```python
# Personnaliser le titre
APP_NAME = "Mon Application"

# Modifier la page d'accueil
def get_html():
    return """<!DOCTYPE html>
    <html>
    <head><title>Mon App Personnalisée</title></head>
    <body>
        <h1>Ma Super Application !</h1>
        <!-- Votre contenu ici -->
    </body>
    </html>"""
```

### Ajouter des Fonctionnalités

**Nouveaux endpoints API:**
```python
if path == '/api/custom':
    content = json.dumps({
        'message': 'Mon endpoint personnalisé'
    })
```

### Fichiers Statiques

Créez le dossier `static/` et ajoutez:
- `static/css/style.css` - Styles personnalisés
- `static/js/app.js` - JavaScript personnalisé
- `static/images/` - Vos images

---

## 🔍 Dépannage

### Erreur 500 - Internal Server Error

**Causes possibles:**
1. Python non disponible → Active le mode HTML automatiquement
2. Permissions incorrectes → Corrigez avec `chmod 755`
3. .htaccess mal configuré → Vérifiez la syntaxe

**Solutions:**
```bash
# Vérifier les logs d'erreur (VPS)
sudo tail -f /var/log/apache2/error.log

# Tester Python manuellement
python3 app.py

# Vérifier les permissions
ls -la app.py
```

### Page blanche

**Vérifications:**
1. Tous les fichiers sont uploadés
2. Le fichier `.htaccess` est présent
3. Le nom de domaine pointe vers le bon répertoire

### Python ne fonctionne pas

**Fallback automatique:**
- L'application bascule automatiquement en mode HTML
- La page `index.html` s'affiche
- Contactez votre hébergeur pour activer Python

---

## 📞 Support

### 🔧 Auto-diagnostic

Accédez à: `http://votre-domaine.com/openred/api/status`

**Si ça fonctionne:** ✅ Installation réussie  
**Si erreur 404:** ⚠️ Problème de configuration  
**Si erreur 500:** ❌ Erreur serveur  

### 📚 Ressources

- **Documentation:** `README.md` dans le package
- **Configuration:** Commentaires dans `app.py`
- **Hébergeur:** Consultez la documentation de votre hébergeur

### 💡 Optimisations

**Performance:**
- Activez la compression GZIP
- Configurez le cache navigateur  
- Optimisez les images

**Sécurité:**
- Activez HTTPS
- Mettez à jour régulièrement
- Surveillez les accès

---

## 🎉 Fonctionnalités Incluses

### 🌐 Interface Web
- ✅ Dashboard moderne responsive
- ✅ Compatible mobile et desktop
- ✅ Design professionnel

### 🔌 API REST
- ✅ Endpoints JSON
- ✅ Status système
- ✅ Extensible facilement

### 💾 Base de Données
- ✅ SQLite portable (si Python disponible)
- ✅ Schemas automatiques
- ✅ Pas de configuration requise

### 🔒 Sécurité
- ✅ Protection des fichiers sensibles
- ✅ Configuration sécurisée
- ✅ Headers de sécurité

### 📱 Compatibilité
- ✅ Tous navigateurs modernes
- ✅ Mobile-first design
- ✅ Progressive Web App ready

---

## 🚀 Cas d'Usage

### Site Web Personnel
- Portfolio professionnel
- Blog personnel
- Showcase projets

### Application Métier
- Dashboard interne
- API pour applications mobiles
- Interface d'administration

### Prototype/Demo
- Validation concept
- Présentation client
- Test rapide d'idées

---

**OpenRed Universal Deployment System**  
*Installation en 5 minutes • Compatible tous hébergeurs • Production ready*

🔗 **URL après installation:** `http://votre-domaine.com/openred`  
🔑 **Login par défaut:** Aucun (interface publique)  
📧 **Support:** Consultez la documentation intégrée