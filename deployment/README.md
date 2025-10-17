# 🚀 OpenRed Deployment System

Ce dossier contient tous les fichiers nécessaires pour le déploiement d'OpenRed sur différents types d'hébergement.

## 📁 Structure

### 🎯 Scripts d'Installation
- `install-openred.sh` - Installation Linux/macOS (VPS, serveurs dédiés)
- `install-openred.ps1` - Installation Windows (serveurs Windows)  
- `install-openred-shared.sh` - Installation hébergement mutualisé Linux
- `install-openred-shared.ps1` - Installation hébergement mutualisé Windows

### 📦 Packages de Déploiement
- `openred-complete.zip` - Package complet (951 KB) pour VPS/serveurs
- `openred-shared-hosting.zip` - Package optimisé (127 KB) pour hébergement mutualisé

### 🛠️ Outils de Création
- `create_complete_package.py` - Générateur du package complet
- `create_shared_hosting_package.py` - Générateur du package hébergement mutualisé
- `install_o2switch.py` - Installateur spécialisé O2Switch

### 📖 Documentation
- `INSTALLATION_GUIDE.md` - Guide complet d'installation
- `ONE_LINER_SYSTEM.md` - Documentation du système one-liner
- `install-page.html` - Page d'installation web interactive

## 🚀 Utilisation Rapide

### Installation VPS/Serveur Dédié
```bash
curl -sSL https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/install-openred.sh | bash
```

### Installation Hébergement Mutualisé
```bash
curl -sSL https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/install-openred-shared.sh | bash
```

### Installation Windows
```powershell
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/install-openred.ps1'))
```

## 🎯 Types d'Hébergement Supportés

### ✅ Hébergement Mutualisé
- O2Switch
- OVH
- 1&1 IONOS
- HostGator
- GoDaddy
- Et tous les autres avec PHP/Python

### ✅ VPS & Serveurs Dédiés
- Ubuntu/Debian
- CentOS/RHEL
- Windows Server
- Docker

### ✅ Cloud Platforms
- AWS
- Google Cloud
- Microsoft Azure
- DigitalOcean

## 🛡️ Sécurité

Tous les packages sont vérifiés avec des checksums et les installations utilisent HTTPS uniquement.

## 📊 Métriques

- **Package complet** : 951 KB - 100+ fichiers
- **Package mutualisé** : 127 KB - 15 fichiers essentiels
- **Installation** : ~30 secondes
- **Compatibilité** : 95% des hébergeurs

- `INSTALLATION_GUIDE.md` - Guide détaillé
- `ONE_LINER_SYSTEM.md` - Documentation du système one-liner