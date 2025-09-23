# OpenRed Central-API v3.0 🚀

*[🇬🇧 English](docs/i18n/README_EN.md) | [🇪🇸 Español](docs/i18n/README_ES.md) | [🇨🇳 中文](docs/i18n/README_ZH.md)*

---


## 🇫🇷 Français

**Serveur d'annuaire P2P ultra-minimaliste avec empathie maximale**

### 🎯 Vision

OpenRed Central-API est un serveur d'annuaire HTTP ultra-empathique pour réseaux P2P décentralisés. Conçu avec la philosophie **"Code maison"** pour zéro dépendance critique externe.

### ✨ Caractéristiques

- 🚀 **OpenRed Micro-Engine** - Serveur HTTP custom (50KB vs 15MB FastAPI)
- 💖 **Empathie maximale** - Tolérance de 6 mois entre heartbeats
- 🔐 **Sécurité asymétrique** - Tokens cryptographiques quantum-ready
- 🌍 **100,000 nœuds** - Architecture ultra-scalable
- ⚡ **Zero framework** - Uniquement cryptography comme dépendance
- 🛡️ **États empathiques** - Gestion avancée du cycle de vie des nœuds

### 🏗️ Architecture

```
OpenRed Central-API (Annuaire HTTP)
├── Enregistrement des nœuds P2P
├── Découverte de pairs 
├── Heartbeat ultra-empathique
├── Génération de tokens sécurisés
└── Statistiques en temps réel
```

**Séparation claire :**
- **Central-API** = Annuaire HTTP (ce projet)
- **Node-API** = Communication P2P directe (projet séparé)

### 🚀 Installation

#### Prérequis
- Python 3.8+
- Git

#### Installation rapide

```bash
git clone https://github.com/DiegoMoralesMagri/OpenRed.git
cd OpenRed/central-api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install cryptography
python src/main.py
```

### 📡 API Endpoints

#### � Information
```http
GET /
```

#### 📝 Enregistrement
```http
POST /register
Content-Type: application/json

{
  "node_id": "unique_node_identifier",
  "address": "192.168.1.100",
  "port": 8080,
  "public_key": "base64_encoded_public_key",
  "services": ["file_sharing", "messaging"]
}
```

#### 🔍 Découverte
```http
GET /discover?services=file_sharing&max_results=10
```

#### 💓 Heartbeat
```http
POST /heartbeat/{node_id}
```

#### 📊 Statistiques
```http
GET /stats
```

#### 🔐 Tokens
```http
POST /security/token
Content-Type: application/json

{
  "node_id": "requesting_node_id"
}
```

### 💖 Empathie & États des nœuds

| État | Description | Durée |
|------|-------------|-------|
| `ACTIVE` | Nœud actif | Permanent |
| `PENDING_1ST` | Premier check en attente | 48h |
| `RETRY_48H` | Retry après 48h | 48h |
| `RETRY_2W` | Retry après 2 semaines | 2 semaines |
| `RETRY_2M` | Retry après 2 mois | 2 mois |
| `COMA` | Nœud en coma | Jusqu'à 2 ans |
| `DEAD` | Nœud déclaré mort | Permanent |

### 🌟 Philosophie "Code Maison"

- **Micro-Engine custom** au lieu de FastAPI (50KB vs 15MB)
- **Zero framework web** - HTTP parsing manuel optimisé
- **Cryptographie pure** - Pas de JWT/OAuth complexes
- **Empathie technique** - Tolérance maximale aux pannes réseau
- **Architecture séparée** - Central-API vs Node-API

---

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

---
