# Documentación Técnica - OpenRed Central API v2.0

## Resumen Ejecutivo

OpenRed Central API v2.0 es una API REST moderna construida con FastAPI que proporciona servicios centralizados para el ecosistema OpenRed. Esta API gestiona el descubrimiento de nodos, la comunicación inter-servicios y el registro de auditoría con arquitectura asíncrona y logging estructurado multilingüe.

## Arquitectura del Sistema

### Visión General
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cliente Web   │    │  API OpenRed    │    │  Base de Datos  │
│                 │◄──►│   Central v2.0  │◄──►│    SQLite       │
│   (Frontend)    │    │   (FastAPI)     │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Redis Cache    │
                       │   (Opcional)    │
                       └─────────────────┘
```

### Componentes Principales

1. **Servidor API FastAPI**: Núcleo de la aplicación con endpoints REST
2. **Motor de Base de Datos**: SQLAlchemy ORM con soporte SQLite/PostgreSQL
3. **Sistema de Logging**: Logging estructurado JSON multilingüe
4. **Servicios de Criptografía**: Manejo seguro de tokens y autenticación
5. **Sistema de Auditoría**: Registro completo de acciones administrativas

## Endpoints de la API

### Endpoints de Salud del Sistema

#### GET /health
**Descripción**: Verifica el estado de salud de la API y sus componentes

**Respuesta de Ejemplo**:
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
**Descripción**: Página de inicio con información del proyecto

**Respuesta**: Página HTML con documentación básica y estado del sistema

### Gestión de Nodos

#### GET /api/discover
**Descripción**: Descubre todos los nodos activos en la red OpenRed

**Parámetros de Consulta**:
- `status` (opcional): Filtrar por estado del nodo (active, inactive, maintenance)
- `service` (opcional): Filtrar por tipo de servicio

**Respuesta de Ejemplo**:
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
**Descripción**: Registra un nuevo nodo en la red

**Cuerpo de la Solicitud**:
```json
{
    "node_id": "nuevo-nodo-001",
    "host": "192.168.1.200",
    "port": 8002,
    "status": "active",
    "services": ["api", "storage"],
    "metadata": {
        "version": "2.0.0",
        "description": "Nodo de almacenamiento principal"
    }
}
```

**Respuesta de Éxito**:
```json
{
    "success": true,
    "message": "Nodo registrado exitosamente",
    "node_id": "nuevo-nodo-001",
    "registered_at": "2025-09-21T02:04:52Z"
}
```

#### GET /nodes
**Descripción**: Interfaz web para gestión de nodos

**Respuesta**: Página HTML con lista interactiva de nodos

## Esquema de Base de Datos

### Tabla: nodes
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

### Tabla: messages
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

### Tabla: auth_sessions
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

### Tabla: audit_logs
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

## Variables de Configuración

### Variables de Entorno
```bash
# Configuración de Base de Datos
DATABASE_URL="sqlite:///openred_prod.db"
# o para PostgreSQL:
# DATABASE_URL="postgresql://usuario:password@localhost/openred"

# Configuración del Servidor
HOST="0.0.0.0"
PORT="8000"
WORKERS="4"

# Configuración de Seguridad
SECRET_KEY="tu-clave-secreta-super-segura"
JWT_SECRET="tu-jwt-secret-key"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS="24"

# Configuración de Redis (Opcional)
REDIS_URL="redis://localhost:6379/0"
REDIS_PASSWORD="tu-redis-password"

# Configuración de Logging
LOG_LEVEL="INFO"
LOG_FORMAT="json"
LOG_FILE="openred_api.log"

# Configuración CORS
CORS_ENABLED="false"
CORS_ORIGINS="http://localhost:3000,https://tu-dominio.com"

# Configuración de Monitoreo
METRICS_ENABLED="true"
HEALTH_CHECK_INTERVAL="30"
```

### Archivo de Configuración (config.json)
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
        "multilingue": true,
        "file": "logs/openred_api.log"
    }
}
```

## Sistema de Logging

### Formato de Log Estructurado
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

### Categorías de Logs
- **INFO**: Eventos operacionales normales
- **WARNING**: Situaciones anómalas pero no críticas
- **ERROR**: Errores que requieren atención
- **CRITICAL**: Errores críticos que afectan la operación

## Sistema de Seguridad

### Autenticación JWT
```python
# Generación de Token
token = jwt.encode({
    "node_id": "nodo-001",
    "exp": datetime.utcnow() + timedelta(hours=24),
    "iat": datetime.utcnow(),
    "iss": "openred-central-api"
}, secret_key, algorithm="HS256")
```

### Cifrado de Datos Sensibles
```python
# Uso del servicio de criptografía
crypto_service = CryptoService()
encrypted_data = crypto_service.encrypt("datos_sensibles")
decrypted_data = crypto_service.decrypt(encrypted_data)
```

## Monitoreo y Métricas

### Métricas del Sistema
- **CPU**: Porcentaje de uso del procesador
- **Memoria**: Uso de RAM en MB y porcentaje
- **Disco**: Espacio utilizado y disponible
- **Red**: Bytes enviados/recibidos

### Métricas de la API
- **Tiempo de Respuesta**: Latencia promedio por endpoint
- **Tasa de Éxito**: Porcentaje de respuestas exitosas
- **Throughput**: Requests per second (RPS)
- **Errores**: Conteo y categorización de errores

### Métricas de Base de Datos
- **Conexiones**: Conexiones activas y pool
- **Consultas**: Tiempo de ejecución promedio
- **Tamaño**: Espacio utilizado por tablas

## Manejo de Errores

### Códigos de Estado HTTP
- **200**: Operación exitosa
- **201**: Recurso creado exitosamente
- **400**: Solicitud incorrecta
- **401**: No autenticado
- **403**: Acceso prohibido
- **404**: Recurso no encontrado
- **409**: Conflicto (ej: nodo ya existe)
- **422**: Error de validación
- **500**: Error interno del servidor

### Formato de Respuesta de Error
```json
{
    "error": {
        "code": "NODE_ALREADY_EXISTS",
        "message": "Un nodo con este ID ya existe",
        "details": {
            "node_id": "nodo-duplicado",
            "existing_since": "2025-09-20T10:00:00Z"
        },
        "timestamp": "2025-09-21T02:04:52Z",
        "request_id": "req_123456789"
    }
}
```

## Desarrollo y Testing

### Configuración del Entorno de Desarrollo
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar en modo desarrollo
python main_new.py
```

### Ejecutar Tests
```bash
# Tests de integración
python test_integration_live.py

# Tests de rendimiento
python performance_optimizer.py

# Monitoreo en tiempo real
python monitoring.py
```

## Escalabilidad

### Configuración Multi-Worker
```bash
# Usando Uvicorn con múltiples workers
uvicorn main_new:app --host 0.0.0.0 --port 8000 --workers 4

# Usando Gunicorn
gunicorn main_new:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Load Balancing
Para alta disponibilidad, configure múltiples instancias detrás de un load balancer como nginx:

```nginx
upstream openred_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

## Contribución

### Estándares de Código
- **Estilo**: Seguir PEP 8 para Python
- **Documentación**: Docstrings en español para funciones públicas
- **Tests**: Cobertura mínima del 80%
- **Logging**: Usar el sistema de logging estructurado

### Proceso de Desarrollo
1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Desarrollar y testear cambios
4. Crear Pull Request con descripción detallada

## Soporte

### Documentación Adicional
- **Guía de Despliegue**: Ver `DEPLOYMENT_ES.md`
- **Scripts de Monitoreo**: Ver `monitoring.py`
- **Optimización de Rendimiento**: Ver `performance_optimizer.py`

### Contacto
- **Repositorio**: https://github.com/DiegoMoralesMagri/OpenRed
- **Issues**: Reportar bugs y solicitar features via GitHub Issues
- **Documentación**: Disponible en múltiples idiomas (ES/EN/FR/ZH)

---

**OpenRed Central API v2.0** - Sistema de gestión distribuida para el ecosistema OpenRed
*Documentación actualizada: 21 de septiembre de 2025*
