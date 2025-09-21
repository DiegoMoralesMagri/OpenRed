# OpenRed Central API v2.0 - Documentation Complète

## 🚀 Vue d'ensemble

L'**OpenRed Central API v2.0** est une refonte complète de l'API centrale pour l'écosystème OpenRed décentralisé. Cette version apporte une architecture sécurisée, scalable et performante pour gérer l'enregistrement, la découverte et la communication entre les nodes du réseau.

## ✨ Nouvelles Fonctionnalités v2.0

### 🔐 Sécurité Renforcée
- **Authentification cryptographique** avec signatures RSA
- **JWT avec rotation automatique** (tokens courts + refresh)
- **Rate limiting adaptatif** par endpoint et IP
- **Chiffrement end-to-end** des données sensibles
- **Audit logging complet** avec anonymisation

### ⚡ Performance et Scalabilité
- **Architecture stateless** pour la scalabilité horizontale
- **Cache Redis distribué** pour les performances
- **Base de données optimisée** avec index composites
- **Monitoring et métriques** temps réel
- **Load balancing intelligent**

### 🛡️ Protection Avancée
- **Headers de sécurité OWASP**
- **Protection CSRF/XSS**
- **Validation stricte des données**
- **Détection d'anomalies**
- **Circuit breaker pattern**

## 📁 Architecture du Projet

```
central-api/
├── SECURITY_REQUIREMENTS.md      # Exigences de sécurité détaillées
├── ARCHITECTURE.md               # Documentation technique complète
├── main_new.py                   # Point d'entrée principal optimisé
├── requirements.txt              # Dépendances mises à jour
├── src/
│   ├── core/                     # Configuration et services centraux
│   │   ├── config.py            # Configuration centralisée
│   │   ├── security.py          # Services cryptographiques
│   │   └── logging.py           # Logging structuré sécurisé
│   ├── models/
│   │   ├── database.py          # Modèles SQLAlchemy optimisés
│   │   └── schemas.py           # Schemas Pydantic de validation
│   ├── services/
│   │   ├── auth_service.py      # Service d'authentification complet
│   │   ├── node_service.py      # Gestion des nodes
│   │   └── message_service.py   # Routage des messages
│   ├── middleware/
│   │   ├── rate_limiting.py     # Rate limiting avancé
│   │   ├── security_headers.py  # Headers de sécurité
│   │   └── request_logging.py   # Logging des requêtes
│   ├── api/v1/                  # Routes API versionnées
│   └── utils/                   # Utilitaires et helpers
└── docs/                        # Documentation détaillée
```

## 🔧 Installation et Configuration

### 1. Installation des Dépendances

```bash
cd central-api
pip install -r requirements.txt
```

### 2. Configuration des Variables d'Environnement

Créez un fichier `.env` basé sur l'exemple :

```bash
# Configuration de base
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-super-secret-key-32-chars-min

# Base de données
DATABASE_URL=postgresql://user:password@localhost/openred_central
REDIS_URL=redis://localhost:6379/0

# Sécurité JWT
JWT_PRIVATE_KEY_PATH=./keys/jwt_private.pem
JWT_PUBLIC_KEY_PATH=./keys/jwt_public.pem
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Chiffrement
ENCRYPTION_KEY=your-encryption-key-32-chars-minimum

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=100

# CORS (production)
ALLOWED_ORIGINS=["https://yourdomain.com"]
ALLOWED_METHODS=["GET","POST","PUT","DELETE"]

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 3. Génération des Clés RSA

```bash
# Clé privée
openssl genrsa -out keys/jwt_private.pem 2048

# Clé publique
openssl rsa -in keys/jwt_private.pem -outform PEM -pubout -out keys/jwt_public.pem
```

### 4. Initialisation de la Base de Données

```bash
# Migration Alembic
alembic upgrade head
```

## 🚀 Démarrage

### Développement
```bash
python main_new.py
```

### Production (avec Gunicorn)
```bash
gunicorn main_new:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker
```bash
docker build -t openred-central-api .
docker run -p 8000:8000 --env-file .env openred-central-api
```

## 📊 Endpoints API v2.0

### Authentification
- `POST /api/v1/auth/register` - Enregistrement de node avec validation crypto
- `POST /api/v1/auth/login` - Connexion avec signature RSA
- `POST /api/v1/auth/refresh` - Renouvellement de token
- `POST /api/v1/auth/logout` - Déconnexion et révocation

### Gestion des Nodes
- `GET /api/v1/nodes/discover` - Découverte sécurisée de nodes
- `POST /api/v1/nodes/heartbeat` - Mise à jour du statut
- `GET /api/v1/nodes/{id}/status` - Statut détaillé d'un node

### Routage de Messages
- `POST /api/v1/messages/send` - Envoi de message chiffré
- `GET /api/v1/messages/receive` - Réception de messages
- `GET /api/v1/messages/{id}/status` - Statut de livraison

### Administration
- `GET /api/v1/admin/stats` - Statistiques du réseau
- `GET /api/v1/admin/nodes` - Gestion des nodes
- `POST /api/v1/admin/maintenance` - Mode maintenance

### Monitoring
- `GET /health` - Health check
- `GET /metrics` - Métriques Prometheus

## 🔒 Sécurité

### Authentification des Nodes
1. **Enregistrement** avec validation de clé publique RSA
2. **Challenge-Response** avec nonces temporels
3. **Tokens JWT courts** (15 min) + refresh tokens (7 jours)
4. **Signature cryptographique** de toutes les requêtes

### Protection contre les Abus
- **Rate limiting granulaire** par endpoint et utilisateur
- **Détection d'anomalies** comportementales
- **Blacklisting automatique** d'IPs suspectes
- **Audit trail complet** de toutes les actions

### Chiffrement des Données
- **TLS 1.3 obligatoire** pour toutes les communications
- **Chiffrement AES-256** des données sensibles en base
- **Clés RSA 2048+ bits** pour les signatures
- **Hashing Argon2id** pour les mots de passe

## 📈 Performance et Monitoring

### Métriques Clés
- **Latence** : p50, p95, p99 par endpoint
- **Throughput** : Requêtes par seconde
- **Taux d'erreur** : 4xx et 5xx par type
- **Utilisation ressources** : CPU, mémoire, DB

### SLOs (Service Level Objectives)
- ✅ **Disponibilité** : 99.9% uptime
- ✅ **Latence** : p95 < 200ms pour endpoints critiques
- ✅ **Débit** : > 10,000 RPS par instance
- ✅ **Fiabilité** : < 0.1% d'erreurs 5xx

### Dashboards
- **Grafana** : Visualisation temps réel
- **Prometheus** : Collecte de métriques
- **Alerting** : Notifications automatiques

## 🧪 Tests et Qualité

### Tests Automatisés
```bash
# Tests unitaires
pytest src/tests/unit/

# Tests d'intégration
pytest src/tests/integration/

# Tests de sécurité
pytest src/tests/security/

# Coverage
pytest --cov=src --cov-report=html
```

### Sécurité
```bash
# Scan de vulnérabilités
bandit -r src/

# Audit des dépendances
safety check

# Analyse statique
mypy src/
```

## 🚀 Déploiement

### Kubernetes
```yaml
# Utilisation des manifestes dans k8s/
kubectl apply -f k8s/
```

### Docker Compose
```bash
# Environnement complet
docker-compose up -d
```

### CI/CD
- **GitHub Actions** pour l'intégration continue
- **Tests automatisés** sur chaque PR
- **Déploiement automatique** en staging/production

## 📞 Support

### Documentation Complète
- `SECURITY_REQUIREMENTS.md` - Exigences de sécurité
- `ARCHITECTURE.md` - Architecture technique détaillée
- `/docs` - Documentation API interactive (développement)

### Logs et Debug
```bash
# Logs structurés JSON
tail -f logs/openred-central-api.log | jq

# Monitoring en temps réel
curl http://localhost:8000/metrics
```

---

## 🎯 Roadmap v2.1

- [ ] **WebSocket** pour notifications temps réel
- [ ] **GraphQL** API alternative
- [ ] **Blockchain** integration pour la preuve de consensus
- [ ] **Machine Learning** pour la détection d'anomalies
- [ ] **Multi-région** deployment avec réplication

---

*Cette API centrale v2.0 constitue le cœur sécurisé et scalable de l'écosystème OpenRed décentralisé, garantissant la souveraineté numérique et la protection des données des utilisateurs.*
