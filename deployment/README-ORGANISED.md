# 🚀 OpenRed Deployment System - Structure Organisée

## 📁 Structure du Dossier

```
deployment/
├── 📦 packages/                 # Packages de déploiement finaux
│   ├── openred-authentic-platform.zip    # (173.9 KB) Système complet
│   ├── openred-cpanel-python.zip         # (164.8 KB) Version cPanel
│   ├── openred-shared-hosting.zip        # (6.7 KB) Version hébergement mutualisé
│   ├── openred-complete.zip              # (951 KB) Package complet VPS
│   └── openred-social-hosting.zip        # (59.6 KB) Interface sociale
│
├── 🚀 scripts/                  # Scripts d'installation
│   ├── install-authentic-fixed.sh        # ✅ RECOMMANDÉ - Installation corrigée
│   ├── install-authentic-no-pip.sh       # Pour hébergeurs sans pip
│   ├── install-openred.sh               # Installation VPS/serveurs
│   ├── install-openred-shared.sh        # Hébergement mutualisé
│   ├── install-social-platform.sh       # Interface sociale
│   └── install_o2switch.py              # Spécialisé O2Switch
│
├── 🔧 testing/                  # Scripts de test et debug
│   ├── repair_openred.sh               # Réparation installation
│   └── install-openred-shared-debug.sh # Debug hébergement mutualisé
│
├── ⚙️ htaccess-variants/        # Variantes .htaccess
│   ├── .htaccess-o2switch              # Compatible O2Switch
│   ├── .htaccess-ultra-minimal         # Version minimaliste
│   ├── .htaccess-vide                  # Version vide
│   └── .htaccess-shared-hosting        # Hébergement mutualisé
│
├── 🛠️ archive/                  # Anciens fichiers
│
└── 📖 Documentation
    ├── README.md                       # Ce fichier
    ├── INSTALLATION_GUIDE.md           # Guide complet
    ├── ONE_LINER_SYSTEM.md            # Documentation one-liner
    └── STRUCTURE.md                    # Structure détaillée
```

## 🎯 Utilisation Rapide

### ✅ Installation Recommandée
```bash
curl -sSL https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/scripts/install-authentic-fixed.sh | bash
```

### 🌐 Pour cPanel Python App
1. Télécharger : `packages/openred-cpanel-python.zip`
2. Déployer via gestionnaire Python cPanel

### 🔧 En cas de problème
```bash
curl -sSL https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/testing/repair_openred.sh | bash
```

## 📦 Packages Disponibles

| Package | Taille | Usage | Fonctionnalités |
|---------|--------|-------|-----------------|
| **openred-authentic-platform.zip** | 173.9 KB | ✅ **RECOMMANDÉ** | Système OpenRed complet |
| **openred-cpanel-python.zip** | 164.8 KB | cPanel Python App | Compatible gestionnaire cPanel |
| **openred-shared-hosting.zip** | 6.7 KB | Hébergement mutualisé | Version légère |
| **openred-complete.zip** | 951 KB | VPS/Serveurs | Toutes fonctionnalités |
| **openred-social-hosting.zip** | 59.6 KB | Interface sociale | Login, profils, amis |

## 🎯 Quelle version choisir ?

- **Hébergement mutualisé (O2Switch, OVH, etc.)** → `openred-authentic-platform.zip`
- **cPanel avec Python App** → `openred-cpanel-python.zip`  
- **VPS/Serveur dédié** → `openred-complete.zip`
- **Démonstration sociale** → `openred-social-hosting.zip`

## 🚨 Résolution Problèmes

### Erreur 403 Forbidden
1. Tester : `htaccess-variants/.htaccess-vide`
2. Utiliser : `htaccess-variants/.htaccess-o2switch`
3. Si échec : Supprimer complètement le .htaccess

### Processus Python tué
→ Utiliser `openred-cpanel-python.zip` avec gestionnaire Python cPanel

### Dépendances manquantes
→ Utiliser `scripts/install-authentic-no-pip.sh`

## 📖 Documentation Complète

- **Guide d'installation** : `INSTALLATION_GUIDE.md`
- **Système one-liner** : `ONE_LINER_SYSTEM.md`
- **Architecture détaillée** : `STRUCTURE.md`

---

**Structure organisée - Fini le désordre ! 🎉**