# Deployment Guide - OpenRed Central API v2.0

## Executive Summary

This guide provides complete instructions for deploying OpenRed Central API v2.0 from local development to enterprise production. It covers multiple deployment scenarios including Docker, Kubernetes, bare metal, and cloud services.

## Table of Contents

1. [System Prerequisites](#system-prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Ubuntu/Debian Server Deployment](#ubuntudebian-server-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Database Configuration](#database-configuration)
7. [Nginx Configuration](#nginx-configuration)
8. [SSL/TLS Configuration](#ssltls-configuration)
9. [Production Monitoring](#production-monitoring)
10. [Backup and Recovery](#backup-and-recovery)
11. [Troubleshooting](#troubleshooting)

## System Prerequisites

### Minimum Requirements
- **OS**: Ubuntu 20.04+, Debian 11+, CentOS 8+, or Windows Server 2019+
- **CPU**: 2 cores (4 cores recommended for production)
- **RAM**: 4GB (8GB recommended for production)
- **Disk**: 20GB (SSD recommended)
- **Python**: 3.8 or higher
- **Network**: Ports 80, 443, 8000 accessible

### Required Software
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql redis-server

# CentOS/RHEL
sudo dnf install -y python3 python3-pip git nginx postgresql-server redis

# Verify installations
python3 --version  # Should be >= 3.8
nginx -v
psql --version
redis-server --version
```

## Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/DiegoMoralesMagri/OpenRed.git
cd OpenRed/central-api
```

### 2. Setup Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Create .env file
cat > .env << EOF
DATABASE_URL=sqlite:///openred_dev.db
SECRET_KEY=your-development-secret-key
JWT_SECRET=your-jwt-development-secret
LOG_LEVEL=DEBUG
CORS_ENABLED=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
```

### 5. Run in Development Mode
```bash
python main_new.py
```

The API will be available at `http://localhost:8000`

## Ubuntu/Debian Server Deployment

### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql postgresql-contrib redis-server

# Create system user
sudo useradd -m -s /bin/bash openred
sudo usermod -aG sudo openred
```

### 2. Configure PostgreSQL
```bash
# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Configure database
sudo -u postgres psql << EOF
CREATE DATABASE openred_prod;
CREATE USER openred WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE openred_prod TO openred;
ALTER USER openred CREATEDB;
\q
EOF
```

### 3. Configure Redis
```bash
# Configure Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Set Redis password
sudo sed -i 's/# requirepass foobared/requirepass your_redis_password/' /etc/redis/redis.conf
sudo systemctl restart redis-server
```

### 4. Deploy Application
```bash
# Switch to openred user
sudo su - openred

# Clone repository
git clone https://github.com/DiegoMoralesMagri/OpenRed.git
cd OpenRed/central-api

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure production environment variables
cat > .env << EOF
DATABASE_URL=postgresql://openred:your_secure_password@localhost/openred_prod
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
REDIS_URL=redis://:your_redis_password@localhost:6379/0
LOG_LEVEL=INFO
LOG_FORMAT=json
CORS_ENABLED=false
HOST=0.0.0.0
PORT=8000
WORKERS=4
EOF
```

### 5. Configure Systemd Service
```bash
# Create service file
sudo tee /etc/systemd/system/openred-api.service << EOF
[Unit]
Description=OpenRed Central API v2.0
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=openred
Group=openred
WorkingDirectory=/home/openred/OpenRed/central-api
Environment=PATH=/home/openred/OpenRed/central-api/.venv/bin
ExecStart=/home/openred/OpenRed/central-api/.venv/bin/python main_new.py
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable openred-api
sudo systemctl start openred-api
sudo systemctl status openred-api
```

## Docker Deployment

### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-privileged user
RUN useradd -m -u 1000 openred && chown -R openred:openred /app
USER openred

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "main_new.py"]
```

### 2. Create docker-compose.yml
```yaml
version: '3.8'

services:
  openred-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://openred:password@postgres:5432/openred_prod
      - SECRET_KEY=your-production-secret-key
      - JWT_SECRET=your-jwt-production-secret
      - REDIS_URL=redis://:redis_password@redis:6379/0
      - LOG_LEVEL=INFO
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=openred_prod
      - POSTGRES_USER=openred
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    command: redis-server --requirepass redis_password
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - openred-api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 3. Run with Docker Compose
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f openred-api

# Stop services
docker-compose down
```

## Kubernetes Deployment

### 1. Create Namespace
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: openred
```

### 2. Configure Secrets
```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: openred-secrets
  namespace: openred
type: Opaque
data:
  database-url: cG9zdGdyZXNxbDovL29wZW5yZWQ6cGFzc3dvcmRAcG9zdGdyZXM6NTQzMi9vcGVucmVkX3Byb2Q=
  secret-key: eW91ci1wcm9kdWN0aW9uLXNlY3JldC1rZXk=
  jwt-secret: eW91ci1qd3QtcHJvZHVjdGlvbi1zZWNyZXQ=
  redis-url: cmVkaXM6Ly86cmVkaXNfcGFzc3dvcmRAcmVkaXM6NjM3OS8w
```

### 3. API Deployment
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openred-api
  namespace: openred
spec:
  replicas: 3
  selector:
    matchLabels:
      app: openred-api
  template:
    metadata:
      labels:
        app: openred-api
    spec:
      containers:
      - name: openred-api
        image: openred/central-api:v2.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: openred-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: openred-secrets
              key: secret-key
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: openred-secrets
              key: jwt-secret
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: openred-secrets
              key: redis-url
        - name: LOG_LEVEL
          value: "INFO"
        - name: HOST
          value: "0.0.0.0"
        - name: PORT
          value: "8000"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 4. Service and Ingress
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: openred-api-service
  namespace: openred
spec:
  selector:
    app: openred-api
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
  name: openred-api-ingress
  namespace: openred
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.openred.your-domain.com
    secretName: openred-tls
  rules:
  - host: api.openred.your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: openred-api-service
            port:
              number: 80
```

### 5. Apply Configuration
```bash
kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Verify deployment
kubectl get pods -n openred
kubectl get services -n openred
kubectl get ingress -n openred
```

## Nginx Configuration

### 1. Basic Configuration
```nginx
# /etc/nginx/sites-available/openred
server {
    listen 80;
    server_name api.openred.your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.openred.your-domain.com;
    
    # SSL certificates
    ssl_certificate /etc/nginx/ssl/openred.crt;
    ssl_certificate_key /etc/nginx/ssl/openred.key;
    
    # Secure SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Proxy configuration
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # Buffers
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
    
    # Logs
    access_log /var/log/nginx/openred_access.log;
    error_log /var/log/nginx/openred_error.log;
}
```

### 2. Enable Configuration
```bash
# Link configuration
sudo ln -s /etc/nginx/sites-available/openred /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## SSL/TLS Configuration

### 1. Using Let's Encrypt (Certbot)
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.openred.your-domain.com

# Verify automatic renewal
sudo certbot renew --dry-run
```

### 2. Using Custom Certificates
```bash
# Create directory for certificates
sudo mkdir -p /etc/nginx/ssl

# Copy certificates
sudo cp your-certificate.crt /etc/nginx/ssl/openred.crt
sudo cp your-private-key.key /etc/nginx/ssl/openred.key

# Set permissions
sudo chmod 600 /etc/nginx/ssl/openred.key
sudo chmod 644 /etc/nginx/ssl/openred.crt
```

## Production Monitoring

### 1. Configure Logs
```bash
# Create logs directory
sudo mkdir -p /var/log/openred
sudo chown openred:openred /var/log/openred

# Configure log rotation
sudo tee /etc/logrotate.d/openred << EOF
/var/log/openred/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF
```

### 2. Configure Monitoring with Prometheus
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'openred-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### 3. Health Check Script
```bash
#!/bin/bash
# health_check.sh

API_URL="https://api.openred.your-domain.com/health"
NOTIFICATION_EMAIL="admin@your-domain.com"

# Check API health
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL")

if [ "$response" != "200" ]; then
    echo "OpenRed API not responding correctly. Code: $response" | \
    mail -s "Alert: OpenRed API Down" "$NOTIFICATION_EMAIL"
fi
```

## Backup and Recovery

### 1. Database Backup Script
```bash
#!/bin/bash
# backup_db.sh

DB_NAME="openred_prod"
DB_USER="openred"
BACKUP_DIR="/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# PostgreSQL backup
PGPASSWORD=your_secure_password pg_dump -h localhost -U "$DB_USER" "$DB_NAME" > \
    "$BACKUP_DIR/openred_backup_$DATE.sql"

# Compress backup
gzip "$BACKUP_DIR/openred_backup_$DATE.sql"

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: openred_backup_$DATE.sql.gz"
```

### 2. Restore Script
```bash
#!/bin/bash
# restore_db.sh

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    exit 1
fi

BACKUP_FILE="$1"
DB_NAME="openred_prod"
DB_USER="openred"

# Decompress backup
gunzip -c "$BACKUP_FILE" > /tmp/restore.sql

# Restore database
PGPASSWORD=your_secure_password psql -h localhost -U "$DB_USER" "$DB_NAME" < /tmp/restore.sql

# Clean temporary file
rm /tmp/restore.sql

echo "Restore completed from: $BACKUP_FILE"
```

### 3. Configure Cron for Automatic Backups
```bash
# Add to openred user's crontab
crontab -e

# Daily backup at 2:00 AM
0 2 * * * /home/openred/scripts/backup_db.sh

# Health check every 5 minutes
*/5 * * * * /home/openred/scripts/health_check.sh
```

## Troubleshooting

### 1. Common Configuration Issues

#### Error: "Permission denied" when starting service
```bash
# Check permissions
sudo chown -R openred:openred /home/openred/OpenRed
sudo chmod +x /home/openred/OpenRed/central-api/main_new.py
```

#### Error: "Database connection failed"
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Verify database connection
sudo -u openred psql -h localhost -U openred openred_prod -c "SELECT 1;"
```

#### Error: "Redis connection refused"
```bash
# Check Redis status
sudo systemctl status redis-server

# Test Redis connection
redis-cli -a your_redis_password ping
```

### 2. Diagnostic Logs

#### View service logs
```bash
# Systemd service logs
sudo journalctl -u openred-api -f

# Application logs
tail -f /var/log/openred/openred_api.log

# Nginx logs
sudo tail -f /var/log/nginx/openred_error.log
```

#### Verify configuration
```bash
# Test Nginx configuration
sudo nginx -t

# Check ports in use
sudo netstat -tlnp | grep :8000

# Check processes
ps aux | grep python
```

### 3. Useful Diagnostic Commands

```bash
# Check status of all services
sudo systemctl status openred-api postgresql redis-server nginx

# Verify network connectivity
curl -I http://localhost:8000/health

# Check resource usage
htop
df -h
free -h

# Check recent error logs
sudo journalctl --since "1 hour ago" -p err
```

## Production Updates

### 1. Zero-Downtime Update Process
```bash
#!/bin/bash
# update_production.sh

# 1. Create backup
/home/openred/scripts/backup_db.sh

# 2. Update code
cd /home/openred/OpenRed
git fetch origin
git checkout main
git pull origin main

# 3. Update dependencies
source central-api/.venv/bin/activate
pip install -r central-api/requirements.txt

# 4. Run database migrations (if any)
# python migrate.py

# 5. Reload service
sudo systemctl reload openred-api

# 6. Verify health
sleep 10
curl -f http://localhost:8000/health || {
    echo "Update failed, rolling back..."
    sudo systemctl restart openred-api
    exit 1
}

echo "Update completed successfully"
```

---

**OpenRed Central API v2.0** - Complete deployment guide for production environments
*Documentation updated: September 21, 2025*
