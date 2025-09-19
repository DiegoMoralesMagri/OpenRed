# Architecture Technique O-Red

## Vue d'ensemble du Système

O-Red est composé de trois couches principales qui interagissent pour créer un réseau social décentralisé :

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Serveur A     │    │   Serveur B     │    │   Serveur C     │
│  (Utilisateur)  │    │  (Utilisateur)  │    │  (Utilisateur)  │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │Node Client│  │◄──►│  │Node Client│  │◄──►│  │Node Client│  │
│  │    +DB    │  │    │  │    +DB    │  │    │  │    +DB    │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      API Centrale         │
                    │   (Registry Service)      │
                    │                           │
                    │  ┌─────────────────────┐  │
                    │  │   Annuaire Nodes    │  │
                    │  │   Service Discovery │  │
                    │  │   Routage Messages  │  │
                    │  └─────────────────────┘  │
                    └───────────────────────────┘
```

## Composants Détaillés

### 1. API Centrale (Central Registry)

**Responsabilités :**
- Enregistrement et validation des nouveaux nodes
- Maintien d'un annuaire des nodes actifs
- Service de découverte pour la localisation des utilisateurs
- Routage des messages entre nodes
- Gestion des certificats et de la sécurité

**Technologies :**
- **Backend** : FastAPI (Python) ou Express.js (Node.js)
- **Base de données** : PostgreSQL pour la persistance
- **Cache** : Redis pour les performances
- **Sécurité** : JWT pour l'authentification, TLS pour le chiffrement

**Endpoints principaux :**
```
POST /api/v1/nodes/register     # Enregistrement d'un nouveau node
GET  /api/v1/nodes/discover     # Découverte de nodes par critères
POST /api/v1/messages/route     # Routage de messages inter-nodes
GET  /api/v1/nodes/{id}/status  # Statut d'un node
```

### 2. Node Client (Application Utilisateur)

**Responsabilités :**
- Interface utilisateur complète (SPA)
- Gestion des données locales de l'utilisateur
- Communication avec l'API centrale
- Communication directe avec d'autres nodes
- Auto-installation et configuration

**Technologies :**
- **Frontend** : React ou Vue.js avec PWA capabilities
- **Backend local** : Node.js avec Express ou Python avec Flask
- **Base de données** : SQLite pour la portabilité, PostgreSQL en option
- **Installation** : Script shell/batch pour auto-déploiement

**Structure de données locales :**
```sql
-- Profil utilisateur
CREATE TABLE user_profile (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    email VARCHAR(255),
    display_name VARCHAR(255),
    bio TEXT,
    avatar_url VARCHAR(255),
    node_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP
);

-- Publications
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    content TEXT,
    media_urls JSON,
    visibility VARCHAR(50), -- public, friends, private
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Connexions (amis/followers)
CREATE TABLE connections (
    id INTEGER PRIMARY KEY,
    target_node_id VARCHAR(255),
    target_username VARCHAR(255),
    target_server_url VARCHAR(255),
    relationship_type VARCHAR(50), -- friend, follower, blocked
    status VARCHAR(50), -- pending, accepted, rejected
    created_at TIMESTAMP
);
```

### 3. Protocoles de Communication

**Protocol O-Red Federation (ORF) :**

```json
{
  "version": "1.0",
  "type": "message_type",
  "from": {
    "node_id": "unique_node_identifier",
    "server_url": "https://user-server.com",
    "username": "john_doe"
  },
  "to": {
    "node_id": "target_node_identifier",
    "server_url": "https://target-server.com",
    "username": "jane_smith"
  },
  "timestamp": "2025-09-19T10:30:00Z",
  "payload": {
    // Contenu spécifique au type de message
  },
  "signature": "cryptographic_signature"
}
```

**Types de messages :**
- `friend_request` : Demande d'ajout en ami
- `post_share` : Partage d'une publication
- `direct_message` : Message privé
- `activity_update` : Mise à jour d'activité
- `content_sync` : Synchronisation de contenu

## Flux de Données

### 1. Enregistrement d'un nouveau node

```
1. Utilisateur installe Node Client sur son serveur
2. Node Client génère clés cryptographiques
3. Node Client contacte API Centrale pour enregistrement
4. API Centrale valide et attribue node_id unique
5. Node Client stocke node_id et met à jour statut
6. Node devient découvrable par autres utilisateurs
```

### 2. Communication entre utilisateurs

```
1. User A recherche User B via API Centrale
2. API Centrale retourne informations de connexion pour Node B
3. User A envoie message directement au Node B
4. Node B valide signature et traite message
5. Node B peut répondre directement au Node A
```

### 3. Partage de contenu

```
1. User A publie nouveau contenu sur son Node
2. Node A notifie API Centrale de la nouvelle publication
3. Amis de User A reçoivent notification via leurs Nodes
4. Contenu reste stocké sur Node A, seules métadonnées partagées
5. Autres utilisateurs peuvent demander accès au contenu complet
```

## Sécurité et Confidentialité

### Chiffrement
- **En transit** : TLS 1.3 pour toutes communications
- **Au repos** : Chiffrement AES-256 des données sensibles
- **End-to-end** : Messages privés chiffrés avec clés publiques

### Authentification
- **Inter-nodes** : Signatures cryptographiques avec clés publiques/privées
- **Utilisateur** : JWT tokens avec rotation automatique
- **API Centrale** : OAuth2 pour l'authentification des nodes

### Validation
- Vérification de l'intégrité des messages
- Protection contre replay attacks
- Rate limiting pour prévenir spam et DoS

## Déploiement et Maintenance

### Auto-installation
```bash
# Script d'installation automatique
curl -sSL https://o-red.org/install.sh | bash

# Ou téléchargement manuel
wget https://o-red.org/releases/latest/ored-installer.tar.gz
tar -xzf ored-installer.tar.gz
./install.sh
```

### Configuration automatique
- Détection de l'environnement serveur
- Configuration automatique de la base de données
- Génération des certificats SSL
- Configuration du proxy web (nginx/apache)

### Mises à jour
- Système de mise à jour automatique
- Versioning sémantique
- Migration automatique des données
- Rollback en cas d'échec