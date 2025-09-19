# Arquitectura Técnica de O-Red

## Visión General del Sistema

O-Red se compone de tres capas principales que interactúan para crear una red social descentralizada:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Servidor A    │    │   Servidor B    │    │   Servidor C    │
│  (Usuario)      │    │  (Usuario)      │    │  (Usuario)      │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │Node Client│  │◄──►│  │Node Client│  │◄──►│  │Node Client│  │
│  │    +DB    │  │    │  │    +DB    │  │    │  │    +DB    │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      API Central          │
                    │   (Servicio de Registro)  │
                    │                           │
                    │  ┌─────────────────────┐  │
                    │  │   Directorio Nodes  │  │
                    │  │   Descubrimiento    │  │
                    │  │   Enrutamiento      │  │
                    │  └─────────────────────┘  │
                    └───────────────────────────┘
```

## Componentes Detallados

### 1. API Central (Registro Central)

Responsabilidades:
- Registrar y validar nuevos nodos
- Mantener un directorio de nodos activos
- Proveer servicio de descubrimiento para localizar usuarios
- Enrutar mensajes entre nodos
- Gestionar certificados y seguridad

Tecnologías:
- Backend: FastAPI (Python) o Express.js (Node.js)
- Base de datos: PostgreSQL para persistencia
- Cache: Redis para rendimiento
- Seguridad: JWT para autenticación, TLS para cifrado

Endpoints principales:

```
POST /api/v1/nodes/register     # Registrar un nuevo nodo
GET  /api/v1/nodes/discover     # Descubrir nodos por criterios
POST /api/v1/messages/route     # Enrutar mensajes entre nodos
GET  /api/v1/nodes/{id}/status  # Estado de un nodo
```

### 2. Node Client (Aplicación de Usuario)

Responsabilidades:
- Interfaz de usuario completa (SPA)
- Gestionar datos locales del usuario
- Comunicarse con la API Central
- Comunicarse directamente con otros nodos
- Auto-instalación y configuración

Tecnologías:
- Frontend: React o Vue.js con capacidades PWA
- Backend local: Node.js con Express o Python con Flask
- Base de datos: SQLite para portabilidad, PostgreSQL opcional
- Instalador: scripts shell/batch para despliegue automático

Esquema de datos locales:

```sql
-- Perfil de usuario
CREATE TABLE user_profile (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    email VARCHAR(255),
    display_name VARCHAR(255),
    bio TEXT,
    avatar_url VARCHAR(255),
    node_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP
);

-- Publicaciones
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    content TEXT,
    media_urls JSON,
    visibility VARCHAR(50), -- public, friends, private
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Conexiones (amigos/seguidores)
CREATE TABLE connections (
    id INTEGER PRIMARY KEY,
    target_node_id VARCHAR(255),
    target_username VARCHAR(255),
    target_server_url VARCHAR(255),
    relationship_type VARCHAR(50), -- friend, follower, blocked
    status VARCHAR(50), -- pending, accepted, rejected
    created_at TIMESTAMP
);
```

### 3. Protocolos de Comunicación

**OpenRed Federation (ORF):**

```json
{
  "version": "1.0",
  "type": "message_type",
  "from": {
    "node_id": "unique_node_identifier",
    "server_url": "https://user-server.com",
    "username": "john_doe"
  },
  "to": {
    "node_id": "target_node_identifier",
    "server_url": "https://target-server.com",
    "username": "jane_smith"
  },
  "timestamp": "2025-09-19T10:30:00Z",
  "payload": {
    // Contenido específico al tipo de mensaje
  },
  "signature": "cryptographic_signature"
}
```

Tipos de mensajes:
- `friend_request` : Solicitud de amistad/seguimiento
- `post_share` : Compartir una publicación
- `direct_message` : Mensaje privado
- `activity_update` : Actualización de actividad
- `content_sync` : Sincronización de contenido

## Flujos de Datos

### 1. Registro de un nuevo nodo

```
1. El usuario instala Node Client en su servidor
2. Node Client genera claves criptográficas
3. Node Client contacta a la API Central para registrar
4. La API Central valida y asigna un node_id único
5. Node Client almacena node_id y actualiza su estado
6. El nodo se vuelve detectable por otros usuarios
```

### 2. Comunicación entre usuarios

```
1. El Usuario A busca al Usuario B mediante la API Central
2. La API Central devuelve la información de conexión para el Nodo B
3. El Usuario A envía un mensaje directamente al Nodo B
4. El Nodo B verifica la firma y procesa el mensaje
5. El Nodo B puede responder directamente al Usuario A
```

### 3. Compartir contenido

```
1. El Usuario A publica nuevo contenido en su Nodo
2. El Nodo A notifica a la API Central sobre la nueva publicación
3. Los amigos del Usuario A reciben notificaciones a través de sus Nodos
4. El contenido permanece almacenado en el Nodo A; solo se comparten metadatos
5. Otros usuarios pueden solicitar acceso al contenido completo
```

## Seguridad y Privacidad

### Cifrado
- En tránsito: TLS 1.3 para todas las comunicaciones
- En reposo: Cifrado AES-256 para datos sensibles
- End-to-end: Mensajes privados cifrados con claves públicas

### Autenticación
- Inter-nodos: Firmas criptográficas con claves públicas/privadas
- Usuario: Tokens JWT con rotación automática
- API Central: OAuth2 para autenticación de nodos

### Validación
- Verificación de integridad de mensajes
- Protección contra ataques de repetición (replay)
- Limitación de tasa para prevenir spam y DoS

## Despliegue y Mantenimiento

### Auto-instalación

```bash
# Script de instalación automática
curl -sSL https://o-red.org/install.sh | bash

# O descarga manual
wget https://o-red.org/releases/latest/ored-installer.tar.gz
tar -xzf ored-installer.tar.gz
./install.sh
```

### Configuración automática
- Detección del entorno del servidor
- Configuración automática de la base de datos
- Generación de certificados SSL
- Configuración del proxy web (nginx/apache)

### Actualizaciones
- Sistema de actualizaciones automáticas
- Versionado semántico
- Migraciones automáticas de datos
- Rollback en caso de fallo
