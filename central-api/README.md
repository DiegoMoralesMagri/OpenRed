[![FR](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/fr.svg) Français](README.md) | [![EN](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/gb.svg) English](README_EN.md) | [![ES](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/es.svg) Español](README_ES.md) | [![ZH](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/cn.svg) 中文](README_ZH.md)

# OpenRed Central API v3.0

## 🚀 API Centrale Ultra-Minimaliste

Cette API sert uniquement d'**annuaire de découverte** pour l'écosystème OpenRed décentralisé.

### 📋 Fonctionnalités

- **Annuaire des nœuds** : ID ↔ URL mapping
- **Génération de tokens** : Tokens asymétriques pour établissement P2P
- **Distribution automatique** : Envoi des tokens aux nœuds
- **Aucun stockage permanent** : Pas de données utilisateur

### 🔄 Endpoints

```
POST /api/v3/nodes/register     - Enregistrement d'un nœud
POST /api/v3/tokens/request     - Demande de connexion P2P
GET  /api/v3/nodes/discover     - Découverte des nœuds
GET  /api/v3/health             - Statut de l'API
```

### 🏗️ Structure

```
central-api/
├── main.py                 # API principale (à créer)
├── crypto/                 # Moteur cryptographique (à créer)
├── models/                 # Modèles de données (à créer)
├── .env                    # Configuration
├── requirements.txt        # Dépendances
└── README.md              # Documentation
```
├── main.py             # Point d'entrée
└── README.md           # Documentation
```

## Installation

```bash
cd central-api
pip install -r requirements.txt
python main.py
```

## Endpoints

- `POST /api/v1/nodes/register` - Enregistrement d'un node
- `GET /api/v1/nodes/discover` - Découverte de nodes
- `POST /api/v1/messages/route` - Routage de messages
- `GET /api/v1/nodes/{id}/status` - Statut d'un node