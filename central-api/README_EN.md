# OpenRed Central API v2.0 - Complete Documentation

## 🚀 Overview

The **OpenRed Central API v2.0** is a complete redesign of the central API for the OpenRed decentralized ecosystem. This version brings secure, scalable, and efficient architecture for managing registration, discovery, and communication between network nodes.

## ✨ New Features v2.0

### 🔐 Enhanced Security
- **Cryptographic authentication** with RSA signatures
- **JWT with automatic rotation** (short tokens + refresh)
- **Adaptive rate limiting** per endpoint and IP
- **End-to-end encryption** of sensitive data
- **Complete audit logging** with anonymization

### ⚡ Performance and Scalability
- **Stateless architecture** for horizontal scaling
- **Distributed Redis cache** for performance
- **Optimized database** with composite indexes
- **Real-time monitoring and metrics**
- **Intelligent load balancing**

### 🛡️ Advanced Protection
- **OWASP security headers**
- **CSRF/XSS protection**
- **Strict data validation**
- **Anomaly detection**
- **Circuit breaker pattern**

## 📁 Project Architecture

```
central-api/
├── SECURITY_REQUIREMENTS_*.md    # Detailed security requirements
├── ARCHITECTURE_*.md            # Complete technical documentation
├── main_new.py                  # Optimized main entry point
├── requirements.txt             # Updated dependencies
├── src/
│   ├── core/                    # Configuration and core services
│   │   ├── config.py           # Centralized configuration
│   │   ├── security.py         # Cryptographic services
│   │   └── logging.py          # Secure structured logging
│   ├── models/
│   │   ├── database.py         # Optimized SQLAlchemy models
│   │   └── schemas.py          # Pydantic validation schemas
│   ├── services/
│   │   ├── auth_service.py     # Complete authentication service
│   │   ├── node_service.py     # Node management
│   │   └── message_service.py  # Message routing
│   ├── middleware/
│   │   ├── rate_limiting.py    # Advanced rate limiting
│   │   ├── security_headers.py # Security headers
│   │   └── request_logging.py  # Request logging
│   ├── api/v1/                 # Versioned API routes
│   └── utils/                  # Utilities and helpers
└── docs/                       # Detailed documentation
```

## 🔧 Installation and Configuration

### 1. Install Dependencies

```bash
cd central-api
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` with required configuration:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/openred_central
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# JWT Configuration
JWT_SECRET_KEY=your-secure-jwt-secret-256-bits
JWT_ALGORITHM=RS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Security Configuration
ENCRYPTION_KEY=your-32-byte-encryption-key
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Network Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000","https://openred.io"]

# Monitoring Configuration
MONITORING_ENABLED=true
METRICS_PORT=9090
LOG_LEVEL=INFO
```

### 3. Setup Database

```bash
# Install PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb openred_central
sudo -u postgres createuser openred_user

# Run migrations
alembic upgrade head
```

### 4. Setup Redis

```bash
# Install Redis
# Ubuntu/Debian  
sudo apt-get install redis-server

# Configure Redis (optional)
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## 🚀 Running

### Development

```bash
# Development mode with auto-reload
python main_new.py --env development

# Or using uvicorn directly
uvicorn main_new:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
# Optimized production mode
python main_new.py --env production

# Or using gunicorn
gunicorn main_new:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 API Endpoints

### 🔐 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new node |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/refresh` | Refresh JWT token |
| POST | `/api/v1/auth/logout` | Logout |
| GET | `/api/v1/auth/verify` | Verify valid token |

### 🌐 Node Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/nodes` | List all nodes |
| GET | `/api/v1/nodes/{node_id}` | Get specific node |
| PUT | `/api/v1/nodes/{node_id}` | Update node information |
| DELETE | `/api/v1/nodes/{node_id}` | Unregister node |
| POST | `/api/v1/nodes/{node_id}/heartbeat` | Node heartbeat |

### 💬 Messaging

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/messages/send` | Send message between nodes |
| GET | `/api/v1/messages/pending/{node_id}` | Get pending messages |
| PUT | `/api/v1/messages/{message_id}/read` | Mark message as read |
| GET | `/api/v1/messages/history` | Message history |

### 📊 Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | API health status |
| GET | `/api/v1/metrics` | Performance metrics |
| GET | `/api/v1/status` | System status |
| GET | `/docs` | Interactive Swagger documentation |
| GET | `/redoc` | ReDoc documentation |

## 🔒 Security

### Authentication Flow

1. **Registration**: Node sends RSA public certificate
2. **Challenge**: Server sends random challenge
3. **Response**: Node signs challenge with private key  
4. **Verification**: Server verifies signature
5. **Token**: JWT is issued with access + refresh tokens

### Security Features

- ✅ **Cryptographic authentication** based on RSA-2048
- ✅ **JWT tokens with automatic rotation** every 15 minutes
- ✅ **Adaptive rate limiting** with Redis
- ✅ **Sensitive data encryption** with AES-256
- ✅ **CSRF/XSS protection** with secure headers
- ✅ **Complete audit logging** with anonymization
- ✅ **Strict validation** of all input data

## 📈 Monitoring and Metrics

### Available Metrics

- **Performance**: Latency, throughput, error rate
- **Security**: Authentication attempts, rate violations
- **System**: CPU usage, memory, DB connections
- **Business**: Active nodes, processed messages, uptime

### Dashboards

- **Prometheus**: Metrics collection at `/api/v1/metrics`
- **Grafana**: Metrics visualization and alerts
- **Health Check**: `/api/v1/health` endpoint for monitoring

## 🐳 Deployment

### Docker

```bash
# Build image
docker build -t openred-central-api .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  openred-central-api
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/openred
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
      
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: openred
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
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
        image: openred-central-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: openred-secrets
              key: database-url
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest

# Tests with coverage
pytest --cov=src

# Specific tests
pytest tests/test_auth.py
```

### Integration Tests

```bash
# Complete API tests
pytest tests/integration/

# Load tests
locust -f tests/load/locustfile.py
```

### Security Tests

```bash
# Vulnerability analysis
bandit -r src/

# Penetration tests
python tests/security/security_tests.py
```

## 📖 Additional Documentation

- [**SECURITY_REQUIREMENTS.md**](SECURITY_REQUIREMENTS_EN.md) - Detailed security requirements
- [**ARCHITECTURE.md**](ARCHITECTURE_EN.md) - Complete technical documentation  
- [**EXAMPLES.md**](EXAMPLES_EN.md) - Usage and integration examples
- [**API_REFERENCE.md**](docs/API_REFERENCE_EN.md) - Complete API reference

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/openred/central-api/issues)
- **Discussions**: [GitHub Discussions](https://github.com/openred/central-api/discussions)
- **Email**: support@openred.io
- **Documentation**: [docs.openred.io](https://docs.openred.io)

---

**OpenRed Central API v2.0** - Building the future of secure decentralized networks 🚀
