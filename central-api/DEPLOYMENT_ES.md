# Guía de Despliegue - OpenRed Central API v2.0

## Resumen Ejecutivo

Esta guía proporciona instrucciones completas para desplegar OpenRed Central API v2.0 desde el desarrollo local hasta la producción enterprise. Cubre múltiples escenarios de despliegue incluyendo Docker, Kubernetes, bare metal y servicios en la nube.

## Tabla de Contenidos

1. [Prerrequisitos del Sistema](#prerrequisitos-del-sistema)
2. [Configuración Local de Desarrollo](#configuración-local-de-desarrollo)
3. [Despliegue en Servidor Ubuntu/Debian](#despliegue-en-servidor-ubuntudebian)
4. [Despliegue con Docker](#despliegue-con-docker)
5. [Despliegue en Kubernetes](#despliegue-en-kubernetes)
6. [Configuración de Base de Datos](#configuración-de-base-de-datos)
7. [Configuración de Nginx](#configuración-de-nginx)
8. [Configuración SSL/TLS](#configuración-ssltls)
9. [Monitoreo de Producción](#monitoreo-de-producción)
10. [Backup y Recuperación](#backup-y-recuperación)
11. [Solución de Problemas](#solución-de-problemas)

## Prerrequisitos del Sistema

### Requerimientos Mínimos
- **OS**: Ubuntu 20.04+, Debian 11+, CentOS 8+, o Windows Server 2019+
- **CPU**: 2 cores (4 cores recomendado para producción)
- **RAM**: 4GB (8GB recomendado para producción)
- **Disco**: 20GB (SSD recomendado)
- **Python**: 3.8 o superior
- **Red**: Puertos 80, 443, 8000 accesibles

### Software Requerido
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql redis-server

# CentOS/RHEL
sudo dnf install -y python3 python3-pip git nginx postgresql-server redis

# Verificar instalaciones
python3 --version  # Debe ser >= 3.8
nginx -v
psql --version
redis-server --version
```

## Configuración Local de Desarrollo

### 1. Clonar el Repositorio
```bash
git clone https://github.com/DiegoMoralesMagri/OpenRed.git
cd OpenRed/central-api
```

### 2. Configurar Entorno Virtual
```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
```bash
# Crear archivo .env
cat > .env << EOF
DATABASE_URL=sqlite:///openred_dev.db
SECRET_KEY=tu-clave-secreta-desarrollo
JWT_SECRET=tu-jwt-secret-desarrollo
LOG_LEVEL=DEBUG
CORS_ENABLED=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
```

### 5. Ejecutar en Modo Desarrollo
```bash
python main_new.py
```

La API estará disponible en `http://localhost:8000`

## Despliegue en Servidor Ubuntu/Debian

### 1. Preparación del Servidor
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql postgresql-contrib redis-server

# Crear usuario del sistema
sudo useradd -m -s /bin/bash openred
sudo usermod -aG sudo openred
```

### 2. Configurar PostgreSQL
```bash
# Iniciar y habilitar PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Configurar base de datos
sudo -u postgres psql << EOF
CREATE DATABASE openred_prod;
CREATE USER openred WITH ENCRYPTED PASSWORD 'tu_password_seguro';
GRANT ALL PRIVILEGES ON DATABASE openred_prod TO openred;
ALTER USER openred CREATEDB;
\q
EOF
```

### 3. Configurar Redis
```bash
# Configurar Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Configurar contraseña Redis
sudo sed -i 's/# requirepass foobared/requirepass tu_redis_password/' /etc/redis/redis.conf
sudo systemctl restart redis-server
```

### 4. Desplegar Aplicación
```bash
# Cambiar al usuario openred
sudo su - openred

# Clonar repositorio
git clone https://github.com/DiegoMoralesMagri/OpenRed.git
cd OpenRed/central-api

# Configurar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Configurar variables de entorno de producción
cat > .env << EOF
DATABASE_URL=postgresql://openred:tu_password_seguro@localhost/openred_prod
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
REDIS_URL=redis://:tu_redis_password@localhost:6379/0
LOG_LEVEL=INFO
LOG_FORMAT=json
CORS_ENABLED=false
HOST=0.0.0.0
PORT=8000
WORKERS=4
EOF
```

### 5. Configurar Servicio Systemd
```bash
# Crear archivo de servicio
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

# Habilitar y iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable openred-api
sudo systemctl start openred-api
sudo systemctl status openred-api
```

## Despliegue con Docker

### 1. Crear Dockerfile
```dockerfile
FROM python:3.9-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de aplicación
WORKDIR /app

# Copiar y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de aplicación
COPY . .

# Crear usuario no privilegiado
RUN useradd -m -u 1000 openred && chown -R openred:openred /app
USER openred

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["python", "main_new.py"]
```

### 2. Crear docker-compose.yml
```yaml
version: '3.8'

services:
  openred-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://openred:password@postgres:5432/openred_prod
      - SECRET_KEY=tu-clave-secreta-produccion
      - JWT_SECRET=tu-jwt-secret-produccion
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

### 3. Ejecutar con Docker Compose
```bash
# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f openred-api

# Parar servicios
docker-compose down
```

## Despliegue en Kubernetes

### 1. Crear Namespace
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: openred
```

### 2. Configurar Secrets
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
  secret-key: dHUtY2xhdmUtc2VjcmV0YS1wcm9kdWNjaW9u
  jwt-secret: dHUtand0LXNlY3JldC1wcm9kdWNjaW9u
  redis-url: cmVkaXM6Ly86cmVkaXNfcGFzc3dvcmRAcmVkaXM6NjM3OS8w
```

### 3. Deployment de la API
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

### 4. Service y Ingress
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
    - api.openred.tu-dominio.com
    secretName: openred-tls
  rules:
  - host: api.openred.tu-dominio.com
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

### 5. Aplicar Configuración
```bash
kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Verificar despliegue
kubectl get pods -n openred
kubectl get services -n openred
kubectl get ingress -n openred
```

## Configuración de Nginx

### 1. Configuración Básica
```nginx
# /etc/nginx/sites-available/openred
server {
    listen 80;
    server_name api.openred.tu-dominio.com;
    
    # Redirección a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.openred.tu-dominio.com;
    
    # Certificados SSL
    ssl_certificate /etc/nginx/ssl/openred.crt;
    ssl_certificate_key /etc/nginx/ssl/openred.key;
    
    # Configuración SSL segura
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Headers de seguridad
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Configuración del proxy
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

### 2. Habilitar Configuración
```bash
# Enlazar configuración
sudo ln -s /etc/nginx/sites-available/openred /etc/nginx/sites-enabled/

# Probar configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx
```

## Configuración SSL/TLS

### 1. Usando Let's Encrypt (Certbot)
```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d api.openred.tu-dominio.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

### 2. Usando Certificados Personalizados
```bash
# Crear directorio para certificados
sudo mkdir -p /etc/nginx/ssl

# Copiar certificados
sudo cp tu-certificado.crt /etc/nginx/ssl/openred.crt
sudo cp tu-clave-privada.key /etc/nginx/ssl/openred.key

# Configurar permisos
sudo chmod 600 /etc/nginx/ssl/openred.key
sudo chmod 644 /etc/nginx/ssl/openred.crt
```

## Monitoreo de Producción

### 1. Configurar Logs
```bash
# Crear directorio de logs
sudo mkdir -p /var/log/openred
sudo chown openred:openred /var/log/openred

# Configurar rotación de logs
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

### 2. Configurar Monitoreo con Prometheus
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

### 3. Script de Monitoreo de Salud
```bash
#!/bin/bash
# health_check.sh

API_URL="https://api.openred.tu-dominio.com/health"
NOTIFICATION_EMAIL="admin@tu-dominio.com"

# Verificar salud de la API
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL")

if [ "$response" != "200" ]; then
    echo "API OpenRed no responde correctamente. Código: $response" | \
    mail -s "Alerta: API OpenRed Down" "$NOTIFICATION_EMAIL"
fi
```

## Backup y Recuperación

### 1. Script de Backup de Base de Datos
```bash
#!/bin/bash
# backup_db.sh

DB_NAME="openred_prod"
DB_USER="openred"
BACKUP_DIR="/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)

# Crear directorio de backup
mkdir -p "$BACKUP_DIR"

# Backup de PostgreSQL
PGPASSWORD=tu_password_seguro pg_dump -h localhost -U "$DB_USER" "$DB_NAME" > \
    "$BACKUP_DIR/openred_backup_$DATE.sql"

# Comprimir backup
gzip "$BACKUP_DIR/openred_backup_$DATE.sql"

# Limpiar backups antiguos (mantener 30 días)
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

echo "Backup completado: openred_backup_$DATE.sql.gz"
```

### 2. Script de Restauración
```bash
#!/bin/bash
# restore_db.sh

if [ -z "$1" ]; then
    echo "Uso: $0 <archivo_backup.sql.gz>"
    exit 1
fi

BACKUP_FILE="$1"
DB_NAME="openred_prod"
DB_USER="openred"

# Descomprimir backup
gunzip -c "$BACKUP_FILE" > /tmp/restore.sql

# Restaurar base de datos
PGPASSWORD=tu_password_seguro psql -h localhost -U "$DB_USER" "$DB_NAME" < /tmp/restore.sql

# Limpiar archivo temporal
rm /tmp/restore.sql

echo "Restauración completada desde: $BACKUP_FILE"
```

### 3. Configurar Cron para Backups Automáticos
```bash
# Agregar a crontab del usuario openred
crontab -e

# Backup diario a las 2:00 AM
0 2 * * * /home/openred/scripts/backup_db.sh

# Verificación de salud cada 5 minutos
*/5 * * * * /home/openred/scripts/health_check.sh
```

## Solución de Problemas

### 1. Problemas Comunes de Configuración

#### Error: "Permission denied" al iniciar el servicio
```bash
# Verificar permisos
sudo chown -R openred:openred /home/openred/OpenRed
sudo chmod +x /home/openred/OpenRed/central-api/main_new.py
```

#### Error: "Database connection failed"
```bash
# Verificar estado de PostgreSQL
sudo systemctl status postgresql

# Verificar conexión de base de datos
sudo -u openred psql -h localhost -U openred openred_prod -c "SELECT 1;"
```

#### Error: "Redis connection refused"
```bash
# Verificar estado de Redis
sudo systemctl status redis-server

# Probar conexión Redis
redis-cli -a tu_redis_password ping
```

### 2. Logs de Diagnóstico

#### Ver logs del servicio
```bash
# Logs del servicio systemd
sudo journalctl -u openred-api -f

# Logs de la aplicación
tail -f /var/log/openred/openred_api.log

# Logs de Nginx
sudo tail -f /var/log/nginx/openred_error.log
```

#### Verificar configuración
```bash
# Probar configuración de Nginx
sudo nginx -t

# Verificar puertos en uso
sudo netstat -tlnp | grep :8000

# Verificar procesos
ps aux | grep python
```

### 3. Comandos de Diagnóstico Útiles

```bash
# Verificar estado de todos los servicios
sudo systemctl status openred-api postgresql redis-server nginx

# Verificar conectividad de red
curl -I http://localhost:8000/health

# Verificar uso de recursos
htop
df -h
free -h

# Verificar logs de errores recientes
sudo journalctl --since "1 hour ago" -p err
```

## Actualizaciones de Producción

### 1. Proceso de Actualización con Zero-Downtime
```bash
#!/bin/bash
# update_production.sh

# 1. Hacer backup
/home/openred/scripts/backup_db.sh

# 2. Actualizar código
cd /home/openred/OpenRed
git fetch origin
git checkout main
git pull origin main

# 3. Actualizar dependencias
source central-api/.venv/bin/activate
pip install -r central-api/requirements.txt

# 4. Ejecutar migraciones de BD (si existen)
# python migrate.py

# 5. Recargar servicio
sudo systemctl reload openred-api

# 6. Verificar salud
sleep 10
curl -f http://localhost:8000/health || {
    echo "Error en la actualización, restaurando..."
    sudo systemctl restart openred-api
    exit 1
}

echo "Actualización completada exitosamente"
```

---

**OpenRed Central API v2.0** - Guía completa de despliegue para entornos de producción
*Documentación actualizada: 21 de septiembre de 2025*
