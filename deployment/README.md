# 🚀 OpenRed Deployment System

## Installation One-Liner

### Linux / macOS
```bash
curl -sSL https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/install-openred.sh | bash
```

### Windows PowerShell  
```powershell
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/install-openred.ps1'))
```

## Fichiers Essentiels

- **`install-openred.sh`** - Script d'installation Linux/macOS
- **`install-openred.ps1`** - Script d'installation Windows
- **`create_simple_package.py`** - Générateur de packages ZIP
- **`install_o2switch.py`** - Installateur spécialisé O2Switch
- **`openred_simple_*.zip`** - Package prêt-à-déployer (5.1 KB)

## Compatible Avec

✅ **O2Switch** ✅ **OVH** ✅ **Hostinger** ✅ **VPS** ✅ **Serveurs dédiés** ✅ **Installation locale**

## Utilisation

### 1. One-Liner (Recommandé)
Copiez-collez la commande ci-dessus selon votre OS

### 2. Package ZIP
```bash
python create_simple_package.py
# Upload du ZIP généré sur votre hébergeur
```

### 3. O2Switch spécialisé
```bash
python install_o2switch.py
```

## Accès Final

L'application sera accessible sur :
- **Web** : `http://votre-domaine.com/openred`
- **Local** : `http://localhost:8000`

## Documentation

- `INSTALLATION_GUIDE.md` - Guide détaillé
- `ONE_LINER_SYSTEM.md` - Documentation du système one-liner