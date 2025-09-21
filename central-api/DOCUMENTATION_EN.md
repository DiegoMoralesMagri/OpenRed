# Technical Documentation - OpenRed Central API v2.0

## Executive Summary

OpenRed Central API v2.0 is a modern REST API built with FastAPI that provides centralized services for the OpenRed ecosystem. This API manages node discovery, inter-service communication, and audit logging with asynchronous architecture and multilingual structured logging.

## System Architecture

### Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │  OpenRed Central│    │    Database     │
│                 │◄──►│    API v2.0     │◄──►│    SQLite       │
│   (Frontend)    │    │   (FastAPI)     │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Redis Cache    │
                       │   (Optional)    │
                       └─────────────────┘
```

### Core Components

1. **FastAPI Server**: Application core with REST endpoints
2. **Database Engine**: SQLAlchemy ORM with SQLite/PostgreSQL support
3. **Logging System**: Multilingual structured JSON logging
4. **Cryptography Services**: Secure token and authentication handling
5. **Audit System**: Complete administrative action logging

## API Endpoints

### System Health Endpoints

#### GET /health
**Description**: Checks the health status of the API and its components

**Example Response**:
```json
{
    "status": "healthy",
    "version": "2.0.0",
    "timestamp": "2025-09-21T02:04:52Z",
    "uptime_seconds": 1234.56,
    "services": {
        "database": "connected",
        "redis": "connected",
        "crypto": "initialized"
    }
}
```

#### GET /
**Description**: Home page with project information

**Response**: HTML page with basic documentation and system status

### Node Management

#### GET /api/discover
**Description**: Discovers all active nodes in the OpenRed network

**Query Parameters**:
- `status` (optional): Filter by node status (active, inactive, maintenance)
- `service` (optional): Filter by service type

**Example Response**:
```json
{
    "nodes": [
        {
            "node_id": "node-001",
            "host": "192.168.1.100",
            "port": 8001,
            "status": "active",
            "services": ["storage", "processing"],
            "last_seen": "2025-09-21T02:04:52Z",
            "metadata": {
                "version": "1.0.0",
                "capabilities": ["async", "backup"]
            }
        }
    ],
    "total_nodes": 1,
    "active_nodes": 1
}
```

#### POST /api/nodes
**Description**: Registers a new node in the network

**Request Body**:
```json
{
    "node_id": "new-node-001",
    "host": "192.168.1.200",
    "port": 8002,
    "status": "active",
    "services": ["api", "storage"],
    "metadata": {
        "version": "2.0.0",
        "description": "Primary storage node"
    }
}
```

**Success Response**:
```json
{
    "success": true,
    "message": "Node registered successfully",
    "node_id": "new-node-001",
    "registered_at": "2025-09-21T02:04:52Z"
}
```

#### GET /nodes
**Description**: Web interface for node management

**Response**: HTML page with interactive node list

## Database Schema

### Table: nodes
```sql
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id VARCHAR(255) UNIQUE NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    services TEXT, -- JSON array
    metadata TEXT, -- JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table: messages
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node VARCHAR(255) NOT NULL,
    to_node VARCHAR(255),
    message_type VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT, -- JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending'
);
```

### Table: auth_sessions
```sql
CREATE TABLE auth_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    node_id VARCHAR(255) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Table: audit_logs
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    target VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    metadata TEXT, -- JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Configuration Variables

### Environment Variables
```bash
# Database Configuration
DATABASE_URL="sqlite:///openred_prod.db"
# or for PostgreSQL:
# DATABASE_URL="postgresql://user:password@localhost/openred"

# Server Configuration
HOST="0.0.0.0"
PORT="8000"
WORKERS="4"

# Security Configuration
SECRET_KEY="your-super-secure-secret-key"
JWT_SECRET="your-jwt-secret-key"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS="24"

# Redis Configuration (Optional)
REDIS_URL="redis://localhost:6379/0"
REDIS_PASSWORD="your-redis-password"

# Logging Configuration
LOG_LEVEL="INFO"
LOG_FORMAT="json"
LOG_FILE="openred_api.log"

# CORS Configuration
CORS_ENABLED="false"
CORS_ORIGINS="http://localhost:3000,https://your-domain.com"

# Monitoring Configuration
METRICS_ENABLED="true"
HEALTH_CHECK_INTERVAL="30"
```

### Configuration File (config.json)
```json
{
    "database": {
        "type": "sqlite",
        "path": "openred_prod.db",
        "pool_size": 10,
        "max_overflow": 20
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "workers": 4,
        "reload": false
    },
    "security": {
        "cors_enabled": false,
        "https_only": true,
        "max_request_size": "10MB"
    },
    "monitoring": {
        "enabled": true,
        "metrics_endpoint": "/metrics",
        "health_endpoint": "/health"
    },
    "logging": {
        "level": "INFO",
        "format": "json",
        "multilingual": true,
        "file": "logs/openred_api.log"
    }
}
```

## Logging System

### Structured Log Format
```json
{
    "timestamp": "2025-09-21T02:04:52.467203Z",
    "level": "info",
    "logger": "openred.central_api",
    "event": "Logging configured",
    "filename": "main_new.py",
    "lineno": 66,
    "multilingual": {
        "fr": "Configuration du logging terminée",
        "en": "Logging configured",
        "es": "Configuración de logging completada",
        "zh": "日志配置完成"
    }
}
```

### Log Categories
- **INFO**: Normal operational events
- **WARNING**: Anomalous but non-critical situations
- **ERROR**: Errors requiring attention
- **CRITICAL**: Critical errors affecting operation

## Security System

### JWT Authentication
```python
# Token Generation
token = jwt.encode({
    "node_id": "node-001",
    "exp": datetime.utcnow() + timedelta(hours=24),
    "iat": datetime.utcnow(),
    "iss": "openred-central-api"
}, secret_key, algorithm="HS256")
```

### Sensitive Data Encryption
```python
# Using cryptography service
crypto_service = CryptoService()
encrypted_data = crypto_service.encrypt("sensitive_data")
decrypted_data = crypto_service.decrypt(encrypted_data)
```

## Monitoring and Metrics

### System Metrics
- **CPU**: Processor usage percentage
- **Memory**: RAM usage in MB and percentage
- **Disk**: Used and available space
- **Network**: Bytes sent/received

### API Metrics
- **Response Time**: Average latency per endpoint
- **Success Rate**: Percentage of successful responses
- **Throughput**: Requests per second (RPS)
- **Errors**: Error count and categorization

### Database Metrics
- **Connections**: Active connections and pool
- **Queries**: Average execution time
- **Size**: Space used by tables

## Error Handling

### HTTP Status Codes
- **200**: Successful operation
- **201**: Resource created successfully
- **400**: Bad request
- **401**: Unauthenticated
- **403**: Forbidden access
- **404**: Resource not found
- **409**: Conflict (e.g., node already exists)
- **422**: Validation error
- **500**: Internal server error

### Error Response Format
```json
{
    "error": {
        "code": "NODE_ALREADY_EXISTS",
        "message": "A node with this ID already exists",
        "details": {
            "node_id": "duplicate-node",
            "existing_since": "2025-09-20T10:00:00Z"
        },
        "timestamp": "2025-09-21T02:04:52Z",
        "request_id": "req_123456789"
    }
}
```

## Development and Testing

### Development Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python main_new.py
```

### Running Tests
```bash
# Integration tests
python test_integration_live.py

# Performance tests
python performance_optimizer.py

# Real-time monitoring
python monitoring.py
```

## Scalability

### Multi-Worker Configuration
```bash
# Using Uvicorn with multiple workers
uvicorn main_new:app --host 0.0.0.0 --port 8000 --workers 4

# Using Gunicorn
gunicorn main_new:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Load Balancing
For high availability, configure multiple instances behind a load balancer like nginx:

```nginx
upstream openred_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

## Contributing

### Code Standards
- **Style**: Follow PEP 8 for Python
- **Documentation**: English docstrings for public functions
- **Tests**: Minimum 80% coverage
- **Logging**: Use structured logging system

### Development Process
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-functionality`
3. Develop and test changes
4. Create Pull Request with detailed description

## Support

### Additional Documentation
- **Deployment Guide**: See `DEPLOYMENT_EN.md`
- **Monitoring Scripts**: See `monitoring.py`
- **Performance Optimization**: See `performance_optimizer.py`

### Contact
- **Repository**: https://github.com/DiegoMoralesMagri/OpenRed
- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Available in multiple languages (ES/EN/FR/ZH)

---

**OpenRed Central API v2.0** - Distributed management system for the OpenRed ecosystem
*Documentation updated: September 21, 2025*
