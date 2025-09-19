# [![FR](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/fr.svg) Français](GUIDE_TEST_LOCAL.md) | [![EN](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/gb.svg) English](GUIDE_TEST_LOCAL_EN.md) | [![ES](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/es.svg) Español](GUIDE_TEST_LOCAL_ES.md) | [![ZH](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/cn.svg) 中文](GUIDE_TEST_LOCAL_ZH.md)

# 🧪 Guide de Test Local - Écosystème O-Red

## 📋 Prérequis et Installation

### Étape 1: Vérification de l'environnement Windows

Ouvrez **PowerShell en tant qu'administrateur** et vérifiez :

```powershell
# Vérifier la version de Windows
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion

# Vérifier PowerShell
$PSVersionTable.PSVersion
```

### Étape 2: Installation de Docker Desktop

1. **Télécharger Docker Desktop** :
   - Allez sur https://docs.docker.com/desktop/install/windows/
   - Téléchargez "Docker Desktop for Windows"

2. **Installer Docker** :
   ```powershell
   # Après installation, redémarrez votre PC
   # Puis vérifiez l'installation
   docker --version
   docker-compose --version
   ```

3. **Démarrer Docker Desktop** :
   - Lancez l'application Docker Desktop
   - Attendez que l'icône Docker soit verte dans la barre des tâches

### Étape 3: Installation de Node.js

1. **Télécharger Node.js** :
   - Allez sur https://nodejs.org/
   - Téléchargez la version LTS (recommandée)

2. **Installer et vérifier** :
   ```powershell
   # Après installation
   node --version
   npm --version
   ```

### Étape 4: Installation de Python

1. **Télécharger Python** :
   - Allez sur https://www.python.org/downloads/
   - Téléchargez Python 3.9+ (cochez "Add to PATH")

2. **Vérifier l'installation** :
   ```powershell
   python --version
   pip --version
   ```

## 🚀 Déploiement et Test de l'Écosystème

### Étape 5: Préparation du projet

```powershell
# Naviguer vers le dossier du projet
cd "C:\Users\Diego\Documents\OpenRed\implementation"

# Vérifier que tous les fichiers sont présents
ls
```

Vous devriez voir :
- `central-api/`
- `node-client/`
- `web-interface/`
- `deploy.bat`
- `deploy.sh`
- `README.md`

### Étape 6: Installation des dépendances Python (API Centrale)

```powershell
# Aller dans le dossier de l'API centrale
cd central-api

# Créer un environnement virtuel Python (optionnel mais recommandé)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt

# Revenir au dossier racine
cd ..
```

### Étape 7: Installation des dépendances Node.js (Interface Web)

```powershell
# Aller dans le dossier de l'interface web
cd web-interface

# Installer les dépendances Node.js
npm install

# Revenir au dossier racine
cd ..
```

### Étape 8: Installation des dépendances du Client Nœud

```powershell
# Aller dans le dossier du client nœud
cd node-client

# Installer les dépendances
pip install -r requirements.txt

# Revenir au dossier racine
cd ..
```

## 🏃‍♂️ Lancement de l'Écosystème

### Méthode 1: Déploiement Automatique (Recommandé)

```powershell
# Lancer le script de déploiement automatique
.\deploy.bat development
```

Le script va :
1. Vérifier les prérequis
2. Configurer l'environnement
3. Construire les images Docker
4. Démarrer tous les services
5. Vérifier que tout fonctionne

### Méthode 2: Déploiement Manuel

Si le script automatique ne fonctionne pas :

```powershell
# 1. Aller dans le dossier API centrale
cd central-api

# 2. Créer le fichier .env s'il n'existe pas
if (!(Test-Path .env)) {
@"
DEBUG=true
SECRET_KEY=dev_secret_key_change_in_production
DATABASE_URL=postgresql+asyncpg://ored:ored_secure_password@postgres:5432/ored_central
REDIS_URL=redis://redis:6379/0
LOG_LEVEL=INFO
P2P_PORT=8001
"@ | Out-File -FilePath .env -Encoding UTF8
}

# 3. Lancer Docker Compose
docker-compose up -d

# 4. Attendre que les services démarrent
Start-Sleep -Seconds 30

# 5. Vérifier l'état des conteneurs
docker-compose ps
```

## 🔍 Vérification et Tests

### Étape 9: Vérifier que les services sont actifs

```powershell
# Vérifier l'état des conteneurs Docker
docker-compose -f central-api/docker-compose.yml ps

# Vérifier les logs si nécessaire
docker-compose -f central-api/docker-compose.yml logs
```

### Étape 10: Tester l'accès aux services

Ouvrez votre navigateur et testez :

1. **API Centrale** : http://localhost:8000
   - Vous devriez voir : `{"message": "O-Red Central API", "status": "healthy"}`

2. **Documentation API** : http://localhost:8000/docs
   - Interface Swagger interactive

3. **Interface Web** : http://localhost:3000
   - Interface utilisateur React (si configurée)

4. **Monitoring** : http://localhost:9090
   - Prometheus (métriques)

### Étape 11: Tests avec PowerShell

```powershell
# Test de l'API de santé
$response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
Write-Output $response

# Test d'enregistrement d'utilisateur
$userData = @{
    username = "testuser"
    email = "test@example.com"
    password = "testpassword123"
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
}

try {
    $registerResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" -Method Post -Body $userData -Headers $headers
    Write-Output "Utilisateur créé : $($registerResponse.username)"
} catch {
    Write-Output "Erreur lors de l'enregistrement : $($_.Exception.Message)"
}
```

## 🧪 Tests Automatisés

### Étape 12: Exécuter les tests unitaires

```powershell
# Tests de l'API
cd central-api
python -m pytest app/tests/ -v

# Tests de l'interface web (si configurée)
cd ../web-interface
npm test

# Tests du client nœud
cd ../node-client
python -m pytest tests/ -v
```

## 🛠️ Dépannage

### Problèmes courants et solutions

1. **Docker ne démarre pas** :
   ```powershell
   # Redémarrer Docker
   Restart-Service docker
   # Ou redémarrer Docker Desktop
   ```

2. **Port déjà utilisé** :
   ```powershell
   # Voir quels processus utilisent les ports
   netstat -ano | findstr :8000
   netstat -ano | findstr :3000
   
   # Arrêter le processus si nécessaire
   taskkill /PID <PID> /F
   ```

3. **Erreurs de dépendances Python** :
   ```powershell
   # Mettre à jour pip
   python -m pip install --upgrade pip
   
   # Réinstaller les dépendances
   pip install -r requirements.txt --force-reinstall
   ```

4. **Erreurs Node.js** :
   ```powershell
   # Nettoyer le cache npm
   npm cache clean --force
   
   # Supprimer node_modules et réinstaller
   Remove-Item -Recurse -Force node_modules
   npm install
   ```

### Étape 13: Nettoyage et arrêt

```powershell
# Arrêter tous les services
cd central-api
docker-compose down

# Nettoyer les volumes (optionnel - supprime les données)
docker-compose down -v

# Voir l'utilisation de l'espace Docker
docker system df

# Nettoyer l'espace Docker (optionnel)
docker system prune
```

## 📊 Monitoring et Logs

### Consulter les logs en temps réel

```powershell
# Logs de tous les services
docker-compose -f central-api/docker-compose.yml logs -f

# Logs d'un service spécifique
docker-compose -f central-api/docker-compose.yml logs -f ored-api
docker-compose -f central-api/docker-compose.yml logs -f postgres
docker-compose -f central-api/docker-compose.yml logs -f redis
```

### Métriques de performance

```powershell
# Statistiques des conteneurs
docker stats

# Informations détaillées sur un conteneur
docker inspect <container_name>
```

## ✅ Checklist de Validation

- [ ] Docker Desktop installé et fonctionnel
- [ ] Node.js et npm installés
- [ ] Python et pip installés
- [ ] Dépendances Python installées
- [ ] Dépendances Node.js installées
- [ ] Services Docker démarrés avec succès
- [ ] API accessible sur http://localhost:8000
- [ ] Documentation Swagger accessible sur http://localhost:8000/docs
- [ ] Tests unitaires passent
- [ ] Pas d'erreurs dans les logs Docker

## 🎯 Prochaines Étapes

Une fois que tout fonctionne localement :

1. **Tester les fonctionnalités** :
   - Créer des utilisateurs
   - Enregistrer des nœuds
   - Soumettre des requêtes IA

2. **Développer de nouvelles fonctionnalités** :
   - Modifier le code
   - Tester en local
   - Voir les changements en temps réel

3. **Préparer pour la production** :
   - Configurer l'environnement de production
   - Optimiser les performances
   - Sécuriser l'infrastructure

---

**Votre écosystème O-Red est maintenant prêt pour le développement et les tests ! 🚀**