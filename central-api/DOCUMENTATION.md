# 📖 OpenRed Central API v2.0 - Documentation Technique Complète

## 🎯 Vue d'ensemble

L'**OpenRed Central API v2.0** est une API REST moderne construite avec FastAPI pour gérer un réseau décentralisé de nœuds OpenRed. Elle fournit des services d'authentification, de routage de messages, et de découverte de nœuds avec une architecture robuste et sécurisée.

## 🏗️ Architecture

### Stack Technologique
- **Framework Web** : FastAPI 0.104+ (Python 3.11+)
- **Base de données** : SQLite (dev) / PostgreSQL (prod)
- **ORM** : SQLAlchemy avec support async
- **Authentification** : JWT avec refresh tokens
- **Configuration** : Pydantic Settings avec variables d'environnement
- **Logging** : Structured JSON logging
- **Tests** : Pytest avec tests async

### Structure du Projet
```
central-api/
├── src/
│   ├── api/v1/endpoints/     # Endpoints REST organisés par domaine
│   ├── models/               # Modèles SQLAlchemy et schémas Pydantic
│   ├── config/               # Configuration et settings
│   ├── database/             # Connexions et utilitaires DB
│   └── utils/                # Utilitaires partagés
├── tests/                    # Suite de tests complète
├── main.py                   # Point d'entrée principal
└── requirements.txt          # Dépendances Python
```

## 🗄️ Modèle de Données

### Tables Principales

#### Nodes
Stocke les informations des nœuds du réseau OpenRed.
```sql
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT UNIQUE NOT NULL,          -- Identifiant unique du nœud
    display_name TEXT,                     -- Nom d'affichage
    server_url TEXT NOT NULL,              -- URL du serveur du nœud
    public_key TEXT NOT NULL,              -- Clé publique pour chiffrement
    version TEXT DEFAULT '2.0.0',          -- Version du protocole
    capabilities TEXT DEFAULT '[]',         -- Capacités supportées (JSON)
    status TEXT DEFAULT 'active',          -- État : active, inactive, banned
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Statistiques
    total_messages_sent INTEGER DEFAULT 0,
    total_messages_received INTEGER DEFAULT 0
);
```

#### Messages
Gère le routage et la livraison des messages entre nœuds.
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT UNIQUE NOT NULL,       -- ID unique du message
    from_node_id TEXT NOT NULL,            -- Nœud expéditeur
    to_node_id TEXT NOT NULL,              -- Nœud destinataire
    content_type TEXT NOT NULL,            -- Type de contenu
    encrypted_content TEXT NOT NULL,       -- Contenu chiffré
    content_hash TEXT NOT NULL,            -- Hash pour intégrité
    priority TEXT DEFAULT 'normal',        -- Priorité : low, normal, high
    ttl TIMESTAMP NOT NULL,                -- Time to live
    status TEXT DEFAULT 'pending',         -- État de livraison
    delivery_attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Auth_Sessions
Gère les sessions d'authentification JWT.
```sql
CREATE TABLE auth_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    node_id TEXT NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

#### Audit_Logs
Logs d'audit pour traçabilité et sécurité.
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT,
    event_type TEXT NOT NULL,              -- Type d'événement
    action TEXT NOT NULL,                  -- Action effectuée
    details TEXT,                          -- Détails JSON
    ip_address TEXT,
    success BOOLEAN NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🌐 API Endpoints

### 🏥 Health & Monitoring

#### `GET /health`
Check de santé général de l'API
```json
{
    "status": "healthy",
    "timestamp": "2025-09-21T10:30:00Z",
    "version": "2.0.0",
    "uptime_seconds": 3600,
    "checks": {
        "database": "ok",
        "memory": "ok",
        "disk": "ok"
    }
}
```

#### `GET /health/liveness`
Probe de liveness pour Kubernetes
```json
{
    "status": "alive",
    "timestamp": "2025-09-21T10:30:00Z"
}
```

#### `GET /health/readiness`
Probe de readiness pour vérifier la disponibilité
```json
{
    "status": "ready",
    "timestamp": "2025-09-21T10:30:00Z",
    "dependencies": {
        "database": "connected",
        "cache": "available"
    }
}
```

### 🔐 Authentication

#### `POST /auth/register`
Enregistrement d'un nouveau nœud
```json
// Request
{
    "node_id": "node_001",
    "display_name": "Mon Node OpenRed",
    "server_url": "https://mon-node.example.com",
    "public_key": "-----BEGIN PUBLIC KEY-----...",
    "version": "2.0.0",
    "capabilities": ["messaging", "routing", "storage"]
}

// Response
{
    "message": "Node registered successfully",
    "node_id": "node_001",
    "status": "pending_verification"
}
```

#### `POST /auth/login`
Authentification et génération de tokens JWT
```json
// Request
{
    "node_id": "node_001",
    "signature": "signed_challenge_with_private_key"
}

// Response
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "node_id": "node_001"
}
```

#### `POST /auth/refresh`
Renouvellement de token d'accès
```json
// Request
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

// Response
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 900
}
```

### 🔍 Node Discovery

#### `GET /nodes`
Liste des nœuds disponibles avec filtrage
```json
// Query params: ?status=active&limit=10&offset=0

// Response
{
    "nodes": [
        {
            "node_id": "node_001",
            "display_name": "Mon Node OpenRed",
            "server_url": "https://mon-node.example.com",
            "status": "active",
            "capabilities": ["messaging", "routing"],
            "last_heartbeat": "2025-09-21T10:25:00Z",
            "version": "2.0.0"
        }
    ],
    "total": 1,
    "limit": 10,
    "offset": 0
}
```

#### `GET /nodes/{node_id}`
Détails d'un nœud spécifique
```json
{
    "node_id": "node_001",
    "display_name": "Mon Node OpenRed",
    "server_url": "https://mon-node.example.com",
    "public_key": "-----BEGIN PUBLIC KEY-----...",
    "status": "active",
    "capabilities": ["messaging", "routing", "storage"],
    "version": "2.0.0",
    "created_at": "2025-09-21T09:00:00Z",
    "last_heartbeat": "2025-09-21T10:25:00Z",
    "statistics": {
        "messages_sent": 150,
        "messages_received": 89,
        "uptime_hours": 25.5
    }
}
```

### 📨 Message Routing

#### `POST /messages/send`
Envoi d'un message vers un autre nœud
```json
// Request
{
    "to_node_id": "node_002",
    "content_type": "text/plain",
    "content": "Hello from node_001!",
    "priority": "normal",
    "ttl_hours": 24
}

// Response
{
    "message_id": "msg_12345",
    "status": "queued",
    "estimated_delivery": "2025-09-21T10:35:00Z"
}
```

#### `GET /messages/inbox`
Messages reçus pour le nœud authentifié
```json
{
    "messages": [
        {
            "message_id": "msg_67890",
            "from_node_id": "node_003",
            "content_type": "application/json",
            "content": "{\"type\": \"friend_request\"}",
            "received_at": "2025-09-21T10:20:00Z",
            "status": "delivered"
        }
    ],
    "total": 1,
    "unread_count": 1
}
```

## 🔧 Configuration

### Variables d'Environnement

#### Base
```bash
# Environment
ENVIRONMENT=development|production
DEBUG=true|false
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR

# API
API_HOST=0.0.0.0
API_PORT=8000
API_VERSION=v1

# Database
DATABASE_URL=sqlite:///openred_dev.db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Security
SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Features
ENABLE_CORS=true
ENABLE_METRICS=true
ENABLE_AUDIT_LOGS=true
```

#### Production
```bash
# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/openred

# Security
SECRET_KEY=complex-production-secret-key
ALLOWED_HOSTS=api.openred.com,central.openred.com

# Performance
WORKERS=4
MAX_CONNECTIONS=100
CONNECTION_TIMEOUT=30

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
METRICS_ENDPOINT=/metrics
HEALTH_CHECK_INTERVAL=30
```

## 🧪 Tests

### Suite de Tests Actuelle

#### Tests Unitaires
- **test_auth.py** : Tests d'authentification JWT
- **test_crud.py** : Tests CRUD sur les modèles
- **test_health.py** : Tests des endpoints de santé

#### Tests d'Intégration
- **test_final_simple.py** : Tests de bout en bout simplifiés
- **test_database.py** : Tests de la couche base de données

#### Tests de Performance
- **test_load.py** : Tests de charge avec locust/pytest-benchmark

### Lancement des Tests
```bash
# Tous les tests
pytest

# Tests spécifiques
pytest tests/test_auth.py -v

# Tests avec couverture
pytest --cov=src --cov-report=html

# Tests de performance
pytest tests/test_load.py --benchmark-only
```

## 🚀 Déploiement

### Développement Local
```bash
# 1. Cloner le repo
git clone https://github.com/DiegoMoralesMagri/OpenRed.git
cd OpenRed/central-api

# 2. Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configuration
cp .env.example .env
# Éditer .env avec vos paramètres

# 5. Initialiser la base de données
python init_simple_db.py

# 6. Lancer l'API
python main.py
# ou
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production avec Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY main.py .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openred-central-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: openred-central-api
  template:
    metadata:
      labels:
        app: openred-central-api
    spec:
      containers:
      - name: api
        image: openred/central-api:2.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: openred-secrets
              key: database-url
        livenessProbe:
          httpGet:
            path: /health/liveness
            port: 8000
          initialDelaySeconds: 30
        readinessProbe:
          httpGet:
            path: /health/readiness
            port: 8000
          initialDelaySeconds: 5
```

## 📊 Métriques et Monitoring

### Métriques Exposées
- **Endpoints** : Latence, débit, codes d'erreur
- **Base de données** : Connexions, temps de requête
- **Messages** : Volume, délais de livraison
- **Nœuds** : Nombre actifs, heartbeats

### Dashboards Recommandés
- **Grafana** : Tableaux de bord pour métriques métier
- **Prometheus** : Collecte et stockage des métriques
- **Sentry** : Monitoring d'erreurs et performance
- **ELK Stack** : Logs centralisés et recherche

## 🔒 Sécurité

### Mesures Implémentées
- **JWT** : Tokens sécurisés avec expiration
- **HTTPS** : Chiffrement en transit obligatoire
- **Rate Limiting** : Protection contre le spam
- **Validation** : Pydantic pour toutes les entrées
- **Audit Logs** : Traçabilité complète des actions

### Bonnes Pratiques
- Rotation régulière des clés JWT
- Hachage sécurisé des mots de passe
- Validation stricte des entrées
- Headers de sécurité (CORS, CSRF)
- Monitoring des tentatives d'intrusion

## 🎯 Roadmap

### Version 2.1 (Q4 2025)
- [ ] WebSocket pour temps réel
- [ ] Cache Redis pour performance
- [ ] Rate limiting avancé
- [ ] Métriques Prometheus natives

### Version 2.2 (Q1 2026)
- [ ] Support multi-tenant
- [ ] Chiffrement end-to-end
- [ ] Federation entre APIs centrales
- [ ] GraphQL endpoints

### Version 3.0 (Q2 2026)
- [ ] Architecture microservices
- [ ] Support blockchain
- [ ] AI pour routage intelligent
- [ ] Interface web d'administration

## 📞 Support

### Ressources
- **Documentation** : https://docs.openred.com
- **GitHub Issues** : https://github.com/DiegoMoralesMagri/OpenRed/issues
- **Discord** : https://discord.gg/openred
- **Email** : support@openred.com

### Contribution
1. Fork du repository
2. Créer une branche feature
3. Tests et documentation
4. Pull request avec description détaillée

---

**OpenRed Central API v2.0** - Construire l'internet décentralisé, un nœud à la fois. 🌐🔗
