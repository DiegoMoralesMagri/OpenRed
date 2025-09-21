# API Central OpenRed v2.0 - Documentación Completa

## 🚀 Visión General

La **API Central OpenRed v2.0** es un rediseño completo de la API central para el ecosistema descentralizado OpenRed. Esta versión aporta una arquitectura segura, escalable y eficiente para gestionar el registro, descubrimiento y comunicación entre nodos de la red.

## ✨ Nuevas Características v2.0

### 🔐 Seguridad Mejorada
- **Autenticación criptográfica** con firmas RSA
- **JWT con rotación automática** (tokens cortos + refresh)
- **Limitación de tasa adaptativa** por endpoint e IP
- **Cifrado extremo a extremo** de datos sensibles
- **Registro de auditoría completo** con anonimización

### ⚡ Rendimiento y Escalabilidad
- **Arquitectura sin estado** para escalado horizontal
- **Caché Redis distribuida** para rendimiento
- **Base de datos optimizada** con índices compuestos
- **Monitoreo y métricas** en tiempo real
- **Balanceado de carga inteligente**

### 🛡️ Protección Avanzada
- **Cabeceras de seguridad OWASP**
- **Protección CSRF/XSS**
- **Validación estricta de datos**
- **Detección de anomalías**
- **Patrón circuit breaker**

## 📁 Arquitectura del Proyecto

```
central-api/
├── SECURITY_REQUIREMENTS_*.md    # Requisitos de seguridad detallados
├── ARCHITECTURE_*.md            # Documentación técnica completa
├── main_new.py                  # Punto de entrada principal optimizado
├── requirements.txt             # Dependencias actualizadas
├── src/
│   ├── core/                    # Configuración y servicios centrales
│   │   ├── config.py           # Configuración centralizada
│   │   ├── security.py         # Servicios criptográficos
│   │   └── logging.py          # Registro estructurado seguro
│   ├── models/
│   │   ├── database.py         # Modelos SQLAlchemy optimizados
│   │   └── schemas.py          # Esquemas de validación Pydantic
│   ├── services/
│   │   ├── auth_service.py     # Servicio de autenticación completo
│   │   ├── node_service.py     # Gestión de nodos
│   │   └── message_service.py  # Enrutamiento de mensajes
│   ├── middleware/
│   │   ├── rate_limiting.py    # Limitación de tasa avanzada
│   │   ├── security_headers.py # Cabeceras de seguridad
│   │   └── request_logging.py  # Registro de peticiones
│   ├── api/v1/                 # Rutas API versionadas
│   └── utils/                  # Utilidades y helpers
└── docs/                       # Documentación detallada
```

## 🔧 Instalación y Configuración

### 1. Instalar Dependencias

```bash
cd central-api
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Crear `.env` con la configuración requerida:

```bash
# Configuración de Base de Datos
DATABASE_URL=postgresql://user:password@localhost/openred_central
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Configuración de Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# Configuración JWT
JWT_SECRET_KEY=your-secure-jwt-secret-256-bits
JWT_ALGORITHM=RS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Configuración de Seguridad
ENCRYPTION_KEY=your-32-byte-encryption-key
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Configuración de Red
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000","https://openred.io"]

# Configuración de Monitoreo
MONITORING_ENABLED=true
METRICS_PORT=9090
LOG_LEVEL=INFO
```

### 3. Configurar Base de Datos

```bash
# Instalar PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Crear base de datos
sudo -u postgres createdb openred_central
sudo -u postgres createuser openred_user

# Ejecutar migraciones
alembic upgrade head
```

### 4. Configurar Redis

```bash
# Instalar Redis
# Ubuntu/Debian  
sudo apt-get install redis-server

# Configurar Redis (opcional)
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## 🚀 Ejecución

### Desarrollo

```bash
# Modo desarrollo con recarga automática
python main_new.py --env development

# O usando uvicorn directamente
uvicorn main_new:app --reload --host 0.0.0.0 --port 8000
```

### Producción

```bash
# Modo producción optimizado
python main_new.py --env production

# O usando gunicorn
gunicorn main_new:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 API Endpoints

### 🔐 Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Registrar nuevo nodo |
| POST | `/api/v1/auth/login` | Iniciar sesión |
| POST | `/api/v1/auth/refresh` | Renovar token JWT |
| POST | `/api/v1/auth/logout` | Cerrar sesión |
| GET | `/api/v1/auth/verify` | Verificar token válido |

### 🌐 Gestión de Nodos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/nodes` | Listar todos los nodos |
| GET | `/api/v1/nodes/{node_id}` | Obtener nodo específico |
| PUT | `/api/v1/nodes/{node_id}` | Actualizar información de nodo |
| DELETE | `/api/v1/nodes/{node_id}` | Desregistrar nodo |
| POST | `/api/v1/nodes/{node_id}/heartbeat` | Heartbeat de nodo |

### 💬 Mensajería

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/messages/send` | Enviar mensaje entre nodos |
| GET | `/api/v1/messages/pending/{node_id}` | Obtener mensajes pendientes |
| PUT | `/api/v1/messages/{message_id}/read` | Marcar mensaje como leído |
| GET | `/api/v1/messages/history` | Historial de mensajes |

### 📊 Monitoreo

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/health` | Estado de salud de la API |
| GET | `/api/v1/metrics` | Métricas de rendimiento |
| GET | `/api/v1/status` | Estado del sistema |
| GET | `/docs` | Documentación interactiva Swagger |
| GET | `/redoc` | Documentación ReDoc |

## 🔒 Seguridad

### Flujo de Autenticación

1. **Registro**: El nodo envía certificado público RSA
2. **Challenge**: El servidor envía desafío aleatorio
3. **Response**: El nodo firma el desafío con clave privada  
4. **Verificación**: El servidor verifica la firma
5. **Token**: Se emite JWT con acceso + refresh tokens

### Características de Seguridad

- ✅ **Autenticación criptográfica** basada en RSA-2048
- ✅ **Tokens JWT con rotación** automática cada 15 minutos
- ✅ **Limitación de tasa** adaptativa con Redis
- ✅ **Cifrado de datos** sensibles con AES-256
- ✅ **Protección CSRF/XSS** con cabeceras seguras
- ✅ **Registro de auditoría** completo con anonimización
- ✅ **Validación estricta** de todos los datos de entrada

## 📈 Monitoreo y Métricas

### Métricas Disponibles

- **Rendimiento**: Latencia, throughput, tasa de errores
- **Seguridad**: Intentos de autenticación, violaciones de tasa
- **Sistema**: Uso de CPU, memoria, conexiones de BD
- **Negocio**: Nodos activos, mensajes procesados, uptime

### Dashboards

- **Prometheus**: Colección de métricas en `/api/v1/metrics`
- **Grafana**: Visualización de métricas y alertas
- **Health Check**: Endpoint `/api/v1/health` para monitoreo

## 🐳 Despliegue

### Docker

```bash
# Construir imagen
docker build -t openred-central-api .

# Ejecutar contenedor
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

### Tests Unitarios

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=src

# Tests específicos
pytest tests/test_auth.py
```

### Tests de Integración

```bash
# Tests de API completos
pytest tests/integration/

# Tests de carga
locust -f tests/load/locustfile.py
```

### Tests de Seguridad

```bash
# Análisis de vulnerabilidades
bandit -r src/

# Tests de penetración
python tests/security/security_tests.py
```

## 📖 Documentación Adicional

- [**SECURITY_REQUIREMENTS.md**](SECURITY_REQUIREMENTS_ES.md) - Requisitos de seguridad detallados
- [**ARCHITECTURE.md**](ARCHITECTURE_ES.md) - Documentación técnica completa  
- [**EXAMPLES.md**](EXAMPLES_ES.md) - Ejemplos de uso y integración
- [**API_REFERENCE.md**](docs/API_REFERENCE_ES.md) - Referencia completa de la API

## 🤝 Contribuir

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/openred/central-api/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/openred/central-api/discussions)
- **Email**: support@openred.io
- **Documentación**: [docs.openred.io](https://docs.openred.io)

---

**OpenRed Central API v2.0** - Construyendo el futuro de las redes descentralizadas seguras 🚀

## Endpoints

- `POST /api/v1/nodes/register` - Registrar un nodo
- `GET /api/v1/nodes/discover` - Descubrir nodos
- `POST /api/v1/messages/route` - Enrutar mensajes
- `GET /api/v1/nodes/{id}/status` - Estado de un nodo
