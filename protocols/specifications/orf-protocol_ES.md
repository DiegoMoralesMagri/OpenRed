# Protocolo de Federación OpenRed (ORF) v1.0

## Introducción

El Protocolo de Federación OpenRed (ORF) es el protocolo de comunicación estándar entre nodos OpenRed. Permite el intercambio de datos seguro y descentralizado entre servidores de usuarios, manteniendo la soberanía de los datos.

## Principios fundamentales

1. Descentralización: sin un punto de control central para las comunicaciones
2. Seguridad: autenticación criptográfica y cifrado
3. Interoperabilidad: compatible con múltiples implementaciones
4. Escalabilidad: soporte de versiones y extensibilidad
5. Resiliencia: tolerancia a fallos y reintentos automáticos

## Arquitectura del Protocolo

### Capa de Transporte
- Protocolo: HTTP/HTTPS
- Formato: JSON
- Compresión: gzip (opcional)
- Timeout: 30 segundos por defecto

### Estructura del Mensaje

Todos los mensajes ORF siguen esta estructura básica:

```json
{
  "orf_version": "1.0",
  "message_id": "unique-message-identifier",
  "timestamp": "2025-09-19T10:30:00.000Z",
  "type": "message_type",
  "from": {
    "node_id": "sender-node-id",
    "server_url": "https://sender-server.com",
    "username": "sender_username"
  },
  "to": {
    "node_id": "recipient-node-id", 
    "server_url": "https://recipient-server.com",
    "username": "recipient_username"
  },
  "payload": {
    // Contenido específico del tipo de mensaje
  },
  "security": {
    "signature": "cryptographic-signature",
    "public_key_fingerprint": "key-fingerprint",
    "encryption": "none|aes256"
  }
}
```

### Campos Requeridos

- `orf_version`: versión del protocolo ORF en uso
- `message_id`: identificador único del mensaje (UUID v4)
- `timestamp`: marca de tiempo ISO 8601 UTC
- `type`: tipo de mensaje (ver sección Tipos de Mensajes)
- `from`: información del remitente
- `to`: información del destinatario
- `payload`: contenido del mensaje
- `security`: información de seguridad y firma

## Tipos de Mensajes

### 1. Mensajes de Servicio

#### node_discovery
Descubrimiento e intercambio de información entre nodos.

```json
{
  "type": "node_discovery",
  "payload": {
    "action": "ping|pong|info_request|info_response",
    "capabilities": ["posts", "messages", "groups", "files"],
    "version": "1.0.0",
    "public_key": "-----BEGIN PUBLIC KEY-----...",
    "last_seen": "2025-09-19T10:30:00.000Z"
  }
}
```

#### heartbeat
Señalización de actividad/presencia del nodo.

```json
{
  "type": "heartbeat",
  "payload": {
    "status": "online|away|busy|offline",
    "capabilities": ["posts", "messages"],
    "load": 0.75,
    "peers_connected": 42
  }
}
```

### 2. Mensajes Sociales

#### post_share
Compartir una publicación.

```json
{
  "type": "post_share",
  "payload": {
    "post_id": "unique-post-id",
    "content": "Contenido de la publicación",
    "content_type": "text|html|markdown",
    "visibility": "public|friends|private",
    "media": [
      {
        "type": "image|video|audio|document",
        "url": "https://node-server.com/media/file.jpg",
        "thumbnail_url": "https://node-server.com/media/thumb.jpg",
        "size": 1024000,
        "metadata": {
          "width": 1920,
          "height": 1080,
          "duration": 30
        }
      }
    ],
    "tags": ["#openred", "#decentralized"],
    "location": {
      "latitude": 48.8566,
      "longitude": 2.3522,
      "name": "Paris, France"
    },
    "created_at": "2025-09-19T10:30:00.000Z"
  }
}
```

#### post_reaction
Reacción a una publicación (like, etc.).

```json
{
  "type": "post_reaction",
  "payload": {
    "post_id": "target-post-id",
    "post_author_node_id": "original-author-node-id",
    "reaction_type": "like|love|laugh|angry|sad",
    "action": "add|remove"
  }
}
```

#### comment
Comentario en una publicación.

```json
{
  "type": "comment",
  "payload": {
    "comment_id": "unique-comment-id",
    "post_id": "target-post-id",
    "parent_comment_id": "parent-comment-id", // Para respuestas
    "content": "Contenido del comentario",
    "content_type": "text|html|markdown",
    "created_at": "2025-09-19T10:30:00.000Z"
  }
}
```

### 3. Mensajes Relacionales

#### connection_request
Solicitud de conexión (amigo, follow).

```json
{
  "type": "connection_request",
  "payload": {
    "request_id": "unique-request-id",
    "connection_type": "friend|follow",
    "message": "Mensaje personal opcional",
    "public_profile": {
      "display_name": "John Doe",
      "bio": "Descripción pública",
      "avatar_url": "https://node-server.com/avatar.jpg"
    }
  }
}
```

#### connection_response
Respuesta a una solicitud de conexión.

```json
{
  "type": "connection_response",
  "payload": {
    "request_id": "original-request-id",
    "action": "accept|reject|block",
    "message": "Mensaje de respuesta opcional"
  }
}
```

### 4. Mensajes Privados

#### private_message
Mensaje privado cifrado.

```json
{
  "type": "private_message",
  "payload": {
    "conversation_id": "unique-conversation-id",
    "message_id": "unique-message-id",
    "content": "encrypted-content",
    "content_type": "text|image|file",
    "encryption_method": "aes256-gcm",
    "encryption_key_ref": "key-reference",
    "media_url": "https://node-server.com/encrypted-file",
    "created_at": "2025-09-19T10:30:00.000Z"
  }
}
```

#### message_status
Estado de entrega/lectura de mensajes.

```json
{
  "type": "message_status",
  "payload": {
    "message_ids": ["msg-id-1", "msg-id-2"],
    "status": "delivered|read",
    "timestamp": "2025-09-19T10:30:00.000Z"
  }
}
```

## Seguridad y Autenticación

### Firma de Mensajes

Todos los mensajes DEBEN estar firmados criptográficamente:

1. Generación de la firma:
   - Serialización canónica del payload
   - Hash SHA-256 del contenido
   - Firma RSA-2048 o Ed25519 del hash

2. Verificación:
   - Recuperar la clave pública del remitente
   - Verificar la firma
   - Validar el timestamp (tolerancia de 5 minutos)

### Cifrado de Mensajes Privados

1. Intercambio de claves: Diffie-Hellman efímero (ECDHE)
2. Cifrado simétrico: AES-256-GCM
3. Autenticación: HMAC-SHA256

## Manejo de Errores

### Códigos de Respuesta HTTP

- 200 OK: mensaje procesado con éxito
- 400 Bad Request: formato de mensaje inválido
- 401 Unauthorized: firma inválida
- 403 Forbidden: acceso denegado
- 404 Not Found: destinatario desconocido
- 429 Too Many Requests: limitación de tasa
- 500 Internal Server Error: error del servidor

### Formato de Errores

```json
{
  "orf_version": "1.0",
  "error": {
    "code": "INVALID_SIGNATURE",
    "message": "La verificación de la firma del mensaje falló",
    "details": {
      "expected_signature": "...",
      "received_signature": "..."
    },
    "timestamp": "2025-09-19T10:30:00.000Z"
  }
}
```

## Limitación de Tasa

Para prevenir spam y ataques DoS:

- Mensajes por minuto por nodo: 60
- Mensajes privados por minuto: 30
- Reacciones por minuto: 120
- Descubrimiento por minuto: 10

## Descubrimiento y Enrutamiento

### Descubrimiento de Nodos

1. Via API central: consulta a la API central de OpenRed
2. Via DHT: Tabla Hash Distribuida para descubrimiento P2P
3. Via Webfinger: soporte para el protocolo Webfinger

### Enrutamiento de Mensajes

1. Directo: comunicación directa entre nodos
2. Via Relay: uso de nodos relé para atravesar NAT/firewalls
3. Store-and-Forward: almacenamiento temporal para nodos offline

## Implementación

### Endpoints Requeridos

Cada nodo DEBE exponer estos endpoints:

- `POST /.well-known/openred/inbox`: recibir mensajes
- `GET /.well-known/openred/nodeinfo`: información del nodo
- `GET /.well-known/openred/public-key`: clave pública del nodo

### Ejemplo de Implementación (Python)

```python
import json
import hmac
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

class ORFMessage:
    def __init__(self, message_type, payload, from_node, to_node):
        self.orf_version = "1.0"
        self.message_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.type = message_type
        self.from_node = from_node
        self.to_node = to_node
        self.payload = payload
    
    def sign(self, private_key):
        # Crear firma
        payload_json = json.dumps(self.payload, sort_keys=True)
        message_hash = hashlib.sha256(payload_json.encode()).digest()
        
        signature = private_key.sign(
            message_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        self.security = {
            "signature": base64.b64encode(signature).decode(),
            "public_key_fingerprint": self.get_public_key_fingerprint(private_key.public_key())
        }
    
    def verify(self, public_key):
        # Verificación de firma
        # Implementación...
        pass
```

## Versionado y Evolución

- Versión actual: 1.0
- Compatibilidad hacia atrás: 2 versiones menores
- Negociación de versión: vía el campo `orf_version`
- Extensiones: soporta campos personalizados con prefijo `x_`

## Conformidad

Para ser conforme con ORF 1.0, una implementación DEBE:

1. Soportar todos los tipos de mensajes base
2. Implementar la firma y verificación criptográfica
3. Respetar timeouts y limitación de tasa
4. Manejar errores según la especificación
5. Exponer los endpoints requeridos

## Pruebas de Conformidad

Pruebas automatizadas están disponibles en la carpeta `tests/` para validar la conformidad de una implementación.
