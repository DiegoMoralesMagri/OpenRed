# 🚀 Guide de Déploiement - OpenRed Central API v2.0

## 📋 Prérequis

### Système
- **OS** : Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- **RAM** : 2GB minimum, 4GB recommandé
- **Stockage** : 10GB minimum, SSD recommandé
- **CPU** : 2 cores minimum, 4 cores recommandé

### Logiciels
- **Python** : 3.11+
- **Git** : Pour cloner le repository
- **Database** : SQLite (dev) / PostgreSQL 13+ (prod)
- **Reverse Proxy** : Nginx (recommandé)
- **Process Manager** : systemd / PM2 / Docker

## 🏠 Déploiement Local (Développement)

### 1. Préparation de l'Environnement

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip git nginx

# CentOS/RHEL
sudo dnf update
sudo dnf install python3.11 python3-pip git nginx

# Windows (avec Chocolatey)
choco install python git nginx
```

### 2. Clonage et Configuration

```bash
# Cloner le repository
git clone https://github.com/DiegoMoralesMagri/OpenRed.git
cd OpenRed/central-api

# Créer l'environnement virtuel
python3.11 -m venv .venv

# Activer l'environnement
# Linux/Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configuration de l'Application

```bash
# Créer le fichier de configuration
cp .env.example .env

# Éditer la configuration
nano .env
```

**Fichier .env pour développement :**
```bash
# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# API Configuration
API_HOST=127.0.0.1
API_PORT=8000
API_VERSION=v1

# Database
DATABASE_URL=sqlite:///openred_dev.db

# Security
SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Features
ENABLE_CORS=true
ENABLE_METRICS=true
ENABLE_AUDIT_LOGS=true
```

### 4. Initialisation de la Base de Données

```bash
# Initialiser le schéma
python init_simple_db.py

# Vérifier la création
ls -la *.db
```

### 5. Lancement de l'Application

```bash
# Méthode 1 : Python direct
python main.py

# Méthode 2 : Uvicorn avec reload
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Méthode 3 : Avec logs détaillés
uvicorn main:app --reload --host 127.0.0.1 --port 8000 --log-level info
```

### 6. Vérification

```bash
# Test de l'API
curl http://localhost:8000/health

# Test avec navigateur
# Ouvrir: http://localhost:8000/docs (Swagger UI)
```

## 🏭 Déploiement Production

### 1. Serveur Ubuntu 20.04 LTS

#### Préparation du Système
```bash
# Mise à jour
sudo apt update && sudo apt upgrade -y

# Installation des paquets essentiels
sudo apt install -y python3.11 python3.11-venv python3-pip \
    nginx postgresql postgresql-contrib redis-server \
    supervisor ufw fail2ban certbot python3-certbot-nginx

# Création d'un utilisateur dédié
sudo useradd -m -s /bin/bash openred
sudo usermod -aG sudo openred
```

#### Configuration PostgreSQL
```bash
# Démarrer PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Créer la base de données
sudo -u postgres psql
```

```sql
-- Dans psql
CREATE DATABASE openred_prod;
CREATE USER openred_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE openred_prod TO openred_user;
\q
```

### 2. Déploiement de l'Application

```bash
# Basculer vers l'utilisateur openred
sudo su - openred

# Cloner l'application
git clone https://github.com/DiegoMoralesMagri/OpenRed.git
cd OpenRed/central-api

# Environnement virtuel
python3.11 -m venv .venv
source .venv/bin/activate

# Installation des dépendances
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

#### Configuration Production
```bash
# Fichier de configuration production
cat > .env << EOF
# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_VERSION=v1

# Database
DATABASE_URL=postgresql+asyncpg://openred_user:secure_password_here@localhost/openred_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Security
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# Features
ENABLE_CORS=false
ENABLE_METRICS=true
ENABLE_AUDIT_LOGS=true

# Performance
WORKERS=4
MAX_CONNECTIONS=100
CONNECTION_TIMEOUT=30
EOF
```

### 3. Configuration Gunicorn

```bash
# Fichier de configuration Gunicorn
cat > gunicorn_config.py << EOF
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/openred/access.log"
errorlog = "/var/log/openred/error.log"
loglevel = "info"

# Process naming
proc_name = "openred_central_api"

# Daemonize
daemon = False
pidfile = "/var/run/openred/openred.pid"
user = "openred"
group = "openred"
EOF
```

### 4. Configuration Systemd

```bash
# Service systemd
sudo cat > /etc/systemd/system/openred-api.service << EOF
[Unit]
Description=OpenRed Central API
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=openred
Group=openred
WorkingDirectory=/home/openred/OpenRed/central-api
Environment=PATH=/home/openred/OpenRed/central-api/.venv/bin
ExecStart=/home/openred/OpenRed/central-api/.venv/bin/gunicorn -c gunicorn_config.py main:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Créer les répertoires de logs
sudo mkdir -p /var/log/openred /var/run/openred
sudo chown openred:openred /var/log/openred /var/run/openred

# Activer et démarrer le service
sudo systemctl daemon-reload
sudo systemctl enable openred-api
sudo systemctl start openred-api
sudo systemctl status openred-api
```

### 5. Configuration Nginx

```bash
# Configuration Nginx
sudo cat > /etc/nginx/sites-available/openred-api << EOF
upstream openred_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";

    # Logging
    access_log /var/log/nginx/openred_access.log;
    error_log /var/log/nginx/openred_error.log;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    location / {
        proxy_pass http://openred_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    # Health check endpoint (no rate limiting)
    location /health {
        limit_req off;
        proxy_pass http://openred_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files (if any)
    location /static/ {
        alias /home/openred/OpenRed/central-api/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Activer le site
sudo ln -s /etc/nginx/sites-available/openred-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL avec Let's Encrypt

```bash
# Obtenir le certificat SSL
sudo certbot --nginx -d api.yourdomain.com

# Vérifier le renouvellement automatique
sudo certbot renew --dry-run
```

### 7. Configuration du Firewall

```bash
# Configuration UFW
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Fail2ban pour la protection
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 🐳 Déploiement avec Docker

### 1. Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

LABEL maintainer="OpenRed Team"
LABEL version="2.0.0"

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Créer un utilisateur non-root
RUN groupadd -r openred && useradd -r -g openred openred

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ src/
COPY main.py .
COPY init_simple_db.py .

# Changer la propriété
RUN chown -R openred:openred /app

# Passer à l'utilisateur non-root
USER openred

# Port exposé
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Commande par défaut
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    container_name: openred-central-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql+asyncpg://openred:password@postgres:5432/openred
      - SECRET_KEY=${SECRET_KEY}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
    networks:
      - openred-network

  postgres:
    image: postgres:15-alpine
    container_name: openred-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=openred
      - POSTGRES_USER=openred
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - openred-network

  redis:
    image: redis:7-alpine
    container_name: openred-redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - openred-network

  nginx:
    image: nginx:alpine
    container_name: openred-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    networks:
      - openred-network

volumes:
  postgres_data:
  redis_data:

networks:
  openred-network:
    driver: bridge
```

### 3. Déploiement Docker

```bash
# Cloner et préparer
git clone https://github.com/DiegoMoralesMagri/OpenRed.git
cd OpenRed/central-api

# Variables d'environnement
echo "SECRET_KEY=$(openssl rand -hex 32)" > .env

# Construire et démarrer
docker-compose up -d

# Vérifier les logs
docker-compose logs -f api

# Vérifier le statut
curl http://localhost:8000/health
```

## ☸️ Déploiement Kubernetes

### 1. Namespace et ConfigMap

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: openred
---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: openred-config
  namespace: openred
data:
  ENVIRONMENT: "production"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  LOG_LEVEL: "INFO"
```

### 2. Secrets

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: openred-secrets
  namespace: openred
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret>
  DATABASE_URL: <base64-encoded-db-url>
```

### 3. Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openred-central-api
  namespace: openred
  labels:
    app: openred-central-api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
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
        envFrom:
        - configMapRef:
            name: openred-config
        - secretRef:
            name: openred-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/liveness
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/readiness
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
```

### 4. Service et Ingress

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: openred-central-api-service
  namespace: openred
spec:
  selector:
    app: openred-central-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: openred-ingress
  namespace: openred
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "10"
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: openred-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: openred-central-api-service
            port:
              number: 80
```

## 🔧 Post-Déploiement

### 1. Monitoring et Logs

```bash
# Monitoring avec Prometheus (optionnel)
# Ajouter au requirements.txt:
# prometheus-client==0.18.0

# Dans l'application
from prometheus_client import Counter, Histogram, generate_latest
```

### 2. Backup de la Base de Données

```bash
# Script de backup PostgreSQL
cat > /home/openred/backup_db.sh << EOF
#!/bin/bash
BACKUP_DIR="/home/openred/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -h localhost -U openred_user openred_prod | gzip > $BACKUP_DIR/openred_backup_$DATE.sql.gz

# Garder seulement les 7 derniers backups
find $BACKUP_DIR -name "openred_backup_*.sql.gz" -mtime +7 -delete
EOF

chmod +x /home/openred/backup_db.sh

# Crontab pour backup quotidien
(crontab -l 2>/dev/null; echo "0 2 * * * /home/openred/backup_db.sh") | crontab -
```

### 3. Surveillance

```bash
# Script de surveillance
cat > /home/openred/health_check.sh << EOF
#!/bin/bash
HEALTH_URL="http://localhost:8000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE != "200" ]; then
    echo "API is down! Response code: $RESPONSE"
    # Envoyer une alerte (email, Slack, etc.)
    systemctl restart openred-api
fi
EOF

chmod +x /home/openred/health_check.sh

# Vérification toutes les 2 minutes
(crontab -l 2>/dev/null; echo "*/2 * * * * /home/openred/health_check.sh") | crontab -
```

## 🚨 Dépannage

### Problèmes Courants

#### 1. Service ne démarre pas
```bash
# Vérifier les logs
sudo journalctl -u openred-api -f

# Vérifier la configuration
python -c "from src.config.settings import settings; print(settings)"
```

#### 2. Base de données inaccessible
```bash
# Tester la connexion
psql -h localhost -U openred_user -d openred_prod

# Vérifier les permissions
sudo -u postgres psql -c "\du"
```

#### 3. Problèmes de performance
```bash
# Monitoring des ressources
htop
iostat -x 1
```

### Logs Utiles

```bash
# Logs de l'application
tail -f /var/log/openred/error.log

# Logs Nginx
tail -f /var/log/nginx/openred_error.log

# Logs système
sudo journalctl -u openred-api --since "1 hour ago"
```

---

Ce guide couvre tous les aspects du déploiement de l'OpenRed Central API v2.0, du développement local à la production Kubernetes. Adaptez les configurations selon vos besoins spécifiques ! 🚀
