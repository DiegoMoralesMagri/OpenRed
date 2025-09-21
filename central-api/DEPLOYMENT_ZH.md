# 部署指南 - OpenRed Central API v2.0

## 执行摘要

本指南提供从本地开发到企业级生产环境部署 OpenRed Central API v2.0 的完整说明。涵盖多种部署场景，包括 Docker、Kubernetes、裸机和云服务。

## 目录

1. [系统先决条件](#系统先决条件)
2. [本地开发环境设置](#本地开发环境设置)
3. [Ubuntu/Debian 服务器部署](#ubuntudebian-服务器部署)
4. [Docker 部署](#docker-部署)
5. [Kubernetes 部署](#kubernetes-部署)
6. [数据库配置](#数据库配置)
7. [Nginx 配置](#nginx-配置)
8. [SSL/TLS 配置](#ssltls-配置)
9. [生产环境监控](#生产环境监控)
10. [备份与恢复](#备份与恢复)
11. [故障排除](#故障排除)

## 系统先决条件

### 最低要求
- **操作系统**: Ubuntu 20.04+、Debian 11+、CentOS 8+ 或 Windows Server 2019+
- **CPU**: 2 核心（生产环境推荐 4 核心）
- **内存**: 4GB（生产环境推荐 8GB）
- **磁盘**: 20GB（推荐 SSD）
- **Python**: 3.8 或更高版本
- **网络**: 端口 80、443、8000 可访问

### 必需软件
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql redis-server

# CentOS/RHEL
sudo dnf install -y python3 python3-pip git nginx postgresql-server redis

# 验证安装
python3 --version  # 应该 >= 3.8
nginx -v
psql --version
redis-server --version
```

## 本地开发环境设置

### 1. 克隆仓库
```bash
git clone https://github.com/DiegoMoralesMagri/OpenRed.git
cd OpenRed/central-api
```

### 2. 设置虚拟环境
```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### 3. 安装依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 配置环境变量
```bash
# 创建 .env 文件
cat > .env << EOF
DATABASE_URL=sqlite:///openred_dev.db
SECRET_KEY=你的开发密钥
JWT_SECRET=你的jwt开发密钥
LOG_LEVEL=DEBUG
CORS_ENABLED=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
```

### 5. 以开发模式运行
```bash
python main_new.py
```

API 将在 `http://localhost:8000` 可用

## Ubuntu/Debian 服务器部署

### 1. 服务器准备
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装系统依赖
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql postgresql-contrib redis-server

# 创建系统用户
sudo useradd -m -s /bin/bash openred
sudo usermod -aG sudo openred
```

### 2. 配置 PostgreSQL
```bash
# 启动并启用 PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 配置数据库
sudo -u postgres psql << EOF
CREATE DATABASE openred_prod;
CREATE USER openred WITH ENCRYPTED PASSWORD '你的安全密码';
GRANT ALL PRIVILEGES ON DATABASE openred_prod TO openred;
ALTER USER openred CREATEDB;
\q
EOF
```

### 3. 配置 Redis
```bash
# 配置 Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 设置 Redis 密码
sudo sed -i 's/# requirepass foobared/requirepass 你的redis密码/' /etc/redis/redis.conf
sudo systemctl restart redis-server
```

### 4. 部署应用程序
```bash
# 切换到 openred 用户
sudo su - openred

# 克隆仓库
git clone https://github.com/DiegoMoralesMagri/OpenRed.git
cd OpenRed/central-api

# 设置虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 配置生产环境变量
cat > .env << EOF
DATABASE_URL=postgresql://openred:你的安全密码@localhost/openred_prod
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
REDIS_URL=redis://:你的redis密码@localhost:6379/0
LOG_LEVEL=INFO
LOG_FORMAT=json
CORS_ENABLED=false
HOST=0.0.0.0
PORT=8000
WORKERS=4
EOF
```

### 5. 配置 Systemd 服务
```bash
# 创建服务文件
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

# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable openred-api
sudo systemctl start openred-api
sudo systemctl status openred-api
```

## Docker 部署

### 1. 创建 Dockerfile
```dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 创建应用目录
WORKDIR /app

# 复制并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非特权用户
RUN useradd -m -u 1000 openred && chown -R openred:openred /app
USER openred

# 暴露端口
EXPOSE 8000

# 默认命令
CMD ["python", "main_new.py"]
```

### 2. 创建 docker-compose.yml
```yaml
version: '3.8'

services:
  openred-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://openred:password@postgres:5432/openred_prod
      - SECRET_KEY=你的生产密钥
      - JWT_SECRET=你的jwt生产密钥
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

### 3. 使用 Docker Compose 运行
```bash
# 构建并运行
docker-compose up -d

# 查看日志
docker-compose logs -f openred-api

# 停止服务
docker-compose down
```

## Kubernetes 部署

### 1. 创建命名空间
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: openred
```

### 2. 配置机密
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
  secret-key: 你的生产密钥的base64编码
  jwt-secret: 你的jwt生产密钥的base64编码
  redis-url: cmVkaXM6Ly86cmVkaXNfcGFzc3dvcmRAcmVkaXM6NjM3OS8w
```

### 3. API 部署
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

### 4. 服务和 Ingress
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
    - api.openred.你的域名.com
    secretName: openred-tls
  rules:
  - host: api.openred.你的域名.com
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

### 5. 应用配置
```bash
kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# 验证部署
kubectl get pods -n openred
kubectl get services -n openred
kubectl get ingress -n openred
```

## Nginx 配置

### 1. 基本配置
```nginx
# /etc/nginx/sites-available/openred
server {
    listen 80;
    server_name api.openred.你的域名.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.openred.你的域名.com;
    
    # SSL 证书
    ssl_certificate /etc/nginx/ssl/openred.crt;
    ssl_certificate_key /etc/nginx/ssl/openred.key;
    
    # 安全的 SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全头部
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # 代理配置
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # 缓冲区
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
    
    # 日志
    access_log /var/log/nginx/openred_access.log;
    error_log /var/log/nginx/openred_error.log;
}
```

### 2. 启用配置
```bash
# 链接配置
sudo ln -s /etc/nginx/sites-available/openred /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重新加载 Nginx
sudo systemctl reload nginx
```

## SSL/TLS 配置

### 1. 使用 Let's Encrypt (Certbot)
```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d api.openred.你的域名.com

# 验证自动续期
sudo certbot renew --dry-run
```

### 2. 使用自定义证书
```bash
# 创建证书目录
sudo mkdir -p /etc/nginx/ssl

# 复制证书
sudo cp 你的证书.crt /etc/nginx/ssl/openred.crt
sudo cp 你的私钥.key /etc/nginx/ssl/openred.key

# 设置权限
sudo chmod 600 /etc/nginx/ssl/openred.key
sudo chmod 644 /etc/nginx/ssl/openred.crt
```

## 生产环境监控

### 1. 配置日志
```bash
# 创建日志目录
sudo mkdir -p /var/log/openred
sudo chown openred:openred /var/log/openred

# 配置日志轮转
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

### 2. 使用 Prometheus 配置监控
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

### 3. 健康检查脚本
```bash
#!/bin/bash
# health_check.sh

API_URL="https://api.openred.你的域名.com/health"
NOTIFICATION_EMAIL="admin@你的域名.com"

# 检查 API 健康状态
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL")

if [ "$response" != "200" ]; then
    echo "OpenRed API 响应异常。状态码: $response" | \
    mail -s "警报: OpenRed API 宕机" "$NOTIFICATION_EMAIL"
fi
```

## 备份与恢复

### 1. 数据库备份脚本
```bash
#!/bin/bash
# backup_db.sh

DB_NAME="openred_prod"
DB_USER="openred"
BACKUP_DIR="/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# PostgreSQL 备份
PGPASSWORD=你的安全密码 pg_dump -h localhost -U "$DB_USER" "$DB_NAME" > \
    "$BACKUP_DIR/openred_backup_$DATE.sql"

# 压缩备份
gzip "$BACKUP_DIR/openred_backup_$DATE.sql"

# 清理旧备份（保留30天）
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

echo "备份完成: openred_backup_$DATE.sql.gz"
```

### 2. 恢复脚本
```bash
#!/bin/bash
# restore_db.sh

if [ -z "$1" ]; then
    echo "用法: $0 <备份文件.sql.gz>"
    exit 1
fi

BACKUP_FILE="$1"
DB_NAME="openred_prod"
DB_USER="openred"

# 解压备份
gunzip -c "$BACKUP_FILE" > /tmp/restore.sql

# 恢复数据库
PGPASSWORD=你的安全密码 psql -h localhost -U "$DB_USER" "$DB_NAME" < /tmp/restore.sql

# 清理临时文件
rm /tmp/restore.sql

echo "从以下文件恢复完成: $BACKUP_FILE"
```

### 3. 配置自动备份的 Cron
```bash
# 添加到 openred 用户的 crontab
crontab -e

# 每日凌晨 2:00 备份
0 2 * * * /home/openred/scripts/backup_db.sh

# 每 5 分钟健康检查
*/5 * * * * /home/openred/scripts/health_check.sh
```

## 故障排除

### 1. 常见配置问题

#### 错误: 启动服务时"权限被拒绝"
```bash
# 检查权限
sudo chown -R openred:openred /home/openred/OpenRed
sudo chmod +x /home/openred/OpenRed/central-api/main_new.py
```

#### 错误: "数据库连接失败"
```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 验证数据库连接
sudo -u openred psql -h localhost -U openred openred_prod -c "SELECT 1;"
```

#### 错误: "Redis 连接被拒绝"
```bash
# 检查 Redis 状态
sudo systemctl status redis-server

# 测试 Redis 连接
redis-cli -a 你的redis密码 ping
```

### 2. 诊断日志

#### 查看服务日志
```bash
# Systemd 服务日志
sudo journalctl -u openred-api -f

# 应用程序日志
tail -f /var/log/openred/openred_api.log

# Nginx 日志
sudo tail -f /var/log/nginx/openred_error.log
```

#### 验证配置
```bash
# 测试 Nginx 配置
sudo nginx -t

# 检查正在使用的端口
sudo netstat -tlnp | grep :8000

# 检查进程
ps aux | grep python
```

### 3. 有用的诊断命令

```bash
# 检查所有服务状态
sudo systemctl status openred-api postgresql redis-server nginx

# 验证网络连接
curl -I http://localhost:8000/health

# 检查资源使用
htop
df -h
free -h

# 检查最近的错误日志
sudo journalctl --since "1 hour ago" -p err
```

## 生产更新

### 1. 零停机更新流程
```bash
#!/bin/bash
# update_production.sh

# 1. 创建备份
/home/openred/scripts/backup_db.sh

# 2. 更新代码
cd /home/openred/OpenRed
git fetch origin
git checkout main
git pull origin main

# 3. 更新依赖
source central-api/.venv/bin/activate
pip install -r central-api/requirements.txt

# 4. 运行数据库迁移（如果有）
# python migrate.py

# 5. 重新加载服务
sudo systemctl reload openred-api

# 6. 验证健康状态
sleep 10
curl -f http://localhost:8000/health || {
    echo "更新失败，正在回滚..."
    sudo systemctl restart openred-api
    exit 1
}

echo "更新成功完成"
```

---

**OpenRed Central API v2.0** - 生产环境完整部署指南
*文档更新时间: 2025年9月21日*
