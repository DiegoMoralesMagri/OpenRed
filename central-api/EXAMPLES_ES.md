# Ejemplos de Uso - API Central OpenRed v2.0

Este documento proporciona ejemplos completos de uso de la API Central OpenRed v2.0, incluyendo integración SDK, autenticación, gestión de nodos y mensajería.

## 🚀 Inicio Rápido

### Configuración Inicial

```python
import asyncio
import aiohttp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import jwt
import json

class OpenRedClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.access_token = None
        self.refresh_token = None
        self.private_key = None
        self.public_key = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
```

## 🔐 Autenticación y Seguridad

### 1. Generación de Claves RSA

```python
def generate_rsa_keypair():
    """Genera un par de claves RSA para autenticación."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    
    # Serialización PEM
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem, public_pem

# Ejemplo de uso
private_key_pem, public_key_pem = generate_rsa_keypair()
print("Clave privada generada y almacenada de forma segura")
```

### 2. Registro de Nodo

```python
async def register_node(client: OpenRedClient, node_info: dict):
    """Registra un nuevo nodo en la red OpenRed."""
    
    # Cargar clave privada
    private_key = serialization.load_pem_private_key(
        private_key_pem, password=None
    )
    client.private_key = private_key
    
    # Datos de registro
    registration_data = {
        "node_id": node_info["node_id"],
        "name": node_info["name"],
        "type": node_info["type"],
        "capabilities": node_info["capabilities"],
        "public_key": public_key_pem.decode('utf-8'),
        "endpoint": node_info["endpoint"],
        "metadata": node_info.get("metadata", {})
    }
    
    async with client.session.post(
        f"{client.base_url}/api/v1/auth/register",
        json=registration_data
    ) as response:
        if response.status == 201:
            result = await response.json()
            print(f"Nodo registrado exitosamente: {result['node_id']}")
            return result
        else:
            error = await response.text()
            raise Exception(f"Error de registro: {error}")

# Ejemplo de uso
node_config = {
    "node_id": "node-001",
    "name": "Nodo Principal",
    "type": "gateway",
    "capabilities": ["routing", "storage", "compute"],
    "endpoint": "https://node001.openred.io:8443",
    "metadata": {
        "region": "eu-west-1",
        "version": "2.0.0"
    }
}

async with OpenRedClient() as client:
    await register_node(client, node_config)
```

### 3. Autenticación Challenge/Response

```python
async def authenticate_node(client: OpenRedClient, node_id: str):
    """Autentica un nodo usando el sistema challenge/response."""
    
    # Paso 1: Solicitar challenge
    async with client.session.post(
        f"{client.base_url}/api/v1/auth/login",
        json={"node_id": node_id}
    ) as response:
        if response.status == 200:
            challenge_data = await response.json()
            challenge = challenge_data["challenge"]
        else:
            raise Exception("No se puede obtener el challenge")
    
    # Paso 2: Firmar challenge
    signature = client.private_key.sign(
        challenge.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    # Paso 3: Enviar respuesta firmada
    auth_response = {
        "node_id": node_id,
        "challenge": challenge,
        "signature": signature.hex()
    }
    
    async with client.session.post(
        f"{client.base_url}/api/v1/auth/verify",
        json=auth_response
    ) as response:
        if response.status == 200:
            tokens = await response.json()
            client.access_token = tokens["access_token"]
            client.refresh_token = tokens["refresh_token"]
            print("Autenticación exitosa")
            return tokens
        else:
            raise Exception("Fallo en la autenticación")

# Ejemplo de uso
async with OpenRedClient() as client:
    client.private_key = serialization.load_pem_private_key(
        private_key_pem, password=None
    )
    await authenticate_node(client, "node-001")
```

## 🌐 Gestión de Nodos

### 1. Descubrimiento de Nodos

```python
async def discover_nodes(client: OpenRedClient, filters: dict = None):
    """Descubre nodos disponibles en la red."""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    params = {}
    
    if filters:
        if "type" in filters:
            params["type"] = filters["type"]
        if "capabilities" in filters:
            params["capabilities"] = ",".join(filters["capabilities"])
        if "region" in filters:
            params["region"] = filters["region"]
    
    async with client.session.get(
        f"{client.base_url}/api/v1/nodes",
        headers=headers,
        params=params
    ) as response:
        if response.status == 200:
            nodes = await response.json()
            print(f"Descubiertos {len(nodes['nodes'])} nodos")
            return nodes["nodes"]
        else:
            raise Exception("Error durante el descubrimiento de nodos")

# Ejemplo de uso
async with OpenRedClient() as client:
    # Autenticación previa requerida
    await authenticate_node(client, "node-001")
    
    # Descubrir todos los nodos
    all_nodes = await discover_nodes(client)
    
    # Descubrir solo nodos de almacenamiento
    storage_nodes = await discover_nodes(client, {
        "type": "storage",
        "capabilities": ["storage"]
    })
```

### 2. Actualización de Estado de Nodo

```python
async def update_node_status(client: OpenRedClient, node_id: str, status_data: dict):
    """Actualiza el estado y metadatos de un nodo."""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    update_data = {
        "status": status_data["status"],
        "load": status_data.get("load", 0),
        "available_resources": status_data.get("available_resources", {}),
        "metadata": status_data.get("metadata", {}),
        "last_seen": status_data.get("last_seen")
    }
    
    async with client.session.put(
        f"{client.base_url}/api/v1/nodes/{node_id}",
        headers=headers,
        json=update_data
    ) as response:
        if response.status == 200:
            result = await response.json()
            print(f"Estado del nodo {node_id} actualizado")
            return result
        else:
            error = await response.text()
            raise Exception(f"Error de actualización: {error}")

# Ejemplo de uso
status_update = {
    "status": "active",
    "load": 0.65,
    "available_resources": {
        "cpu": 75,
        "memory": 80,
        "storage": 90
    },
    "metadata": {
        "version": "2.0.1",
        "uptime": "72h",
        "connections": 150
    }
}

await update_node_status(client, "node-001", status_update)
```

### 3. Heartbeat Automático

```python
import asyncio
from datetime import datetime

async def heartbeat_loop(client: OpenRedClient, node_id: str, interval: int = 30):
    """Mantiene conexión heartbeat con la API central."""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    while True:
        try:
            heartbeat_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "healthy",
                "metrics": {
                    "cpu_usage": 45.2,
                    "memory_usage": 67.8,
                    "disk_usage": 23.4,
                    "network_in": 1024,
                    "network_out": 2048
                }
            }
            
            async with client.session.post(
                f"{client.base_url}/api/v1/nodes/{node_id}/heartbeat",
                headers=headers,
                json=heartbeat_data
            ) as response:
                if response.status == 200:
                    print(f"Heartbeat enviado para {node_id}")
                else:
                    print(f"Fallo en heartbeat: {response.status}")
            
            await asyncio.sleep(interval)
            
        except Exception as e:
            print(f"Error en heartbeat: {e}")
            await asyncio.sleep(interval)

# Iniciar heartbeat en segundo plano
asyncio.create_task(heartbeat_loop(client, "node-001"))
```

## 💬 Mensajería Inter-Nodos

### 1. Envío de Mensajes

```python
async def send_message(client: OpenRedClient, message_data: dict):
    """Envía mensaje a uno o más nodos."""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    # Cifrar contenido sensible
    if message_data.get("encrypt", False):
        # Aquí implementarías cifrado E2E
        pass
    
    message_payload = {
        "from_node": message_data["from_node"],
        "to_nodes": message_data["to_nodes"],
        "message_type": message_data["message_type"],
        "content": message_data["content"],
        "priority": message_data.get("priority", "normal"),
        "ttl": message_data.get("ttl", 3600),
        "metadata": message_data.get("metadata", {})
    }
    
    async with client.session.post(
        f"{client.base_url}/api/v1/messages/send",
        headers=headers,
        json=message_payload
    ) as response:
        if response.status == 200:
            result = await response.json()
            print(f"Mensaje enviado: {result['message_id']}")
            return result
        else:
            error = await response.text()
            raise Exception(f"Error de envío: {error}")

# Ejemplo de uso
message = {
    "from_node": "node-001",
    "to_nodes": ["node-002", "node-003"],
    "message_type": "data_sync",
    "content": {
        "action": "sync_request",
        "data_hash": "abc123...",
        "timestamp": datetime.utcnow().isoformat()
    },
    "priority": "high",
    "ttl": 1800,
    "metadata": {
        "correlation_id": "sync-001",
        "retry_count": 0
    }
}

await send_message(client, message)
```

### 2. Recepción de Mensajes

```python
async def get_pending_messages(client: OpenRedClient, node_id: str):
    """Recupera mensajes pendientes para un nodo."""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    async with client.session.get(
        f"{client.base_url}/api/v1/messages/pending/{node_id}",
        headers=headers
    ) as response:
        if response.status == 200:
            messages = await response.json()
            print(f"Recuperados {len(messages['messages'])} mensajes")
            return messages["messages"]
        else:
            raise Exception("Error al recuperar mensajes")

async def mark_message_read(client: OpenRedClient, message_id: str):
    """Marca mensaje como leído."""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    async with client.session.put(
        f"{client.base_url}/api/v1/messages/{message_id}/read",
        headers=headers
    ) as response:
        if response.status == 200:
            print(f"Mensaje {message_id} marcado como leído")
        else:
            raise Exception("Error al marcar mensaje como leído")

# Bucle de procesamiento de mensajes
async def message_processing_loop(client: OpenRedClient, node_id: str):
    """Procesa continuamente mensajes entrantes."""
    
    while True:
        try:
            messages = await get_pending_messages(client, node_id)
            
            for message in messages:
                print(f"Procesando mensaje: {message['id']}")
                
                # Procesar mensaje según su tipo
                if message["message_type"] == "data_sync":
                    await handle_data_sync(message)
                elif message["message_type"] == "command":
                    await handle_command(message)
                
                # Marcar como leído
                await mark_message_read(client, message["id"])
            
            await asyncio.sleep(5)  # Esperar 5 segundos
            
        except Exception as e:
            print(f"Error procesando mensajes: {e}")
            await asyncio.sleep(10)
```

## 📊 Monitoreo y Métricas

### 1. Recolección de Métricas

```python
async def get_system_metrics(client: OpenRedClient):
    """Recupera métricas del sistema de la API."""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    async with client.session.get(
        f"{client.base_url}/api/v1/metrics",
        headers=headers
    ) as response:
        if response.status == 200:
            metrics = await response.text()
            return metrics
        else:
            raise Exception("Error al recuperar métricas")

async def check_health(client: OpenRedClient):
    """Verifica el estado de salud de la API."""
    
    async with client.session.get(
        f"{client.base_url}/api/v1/health"
    ) as response:
        if response.status == 200:
            health = await response.json()
            return health
        else:
            raise Exception("Servicio no disponible")

# Ejemplo de monitoreo
async def monitoring_dashboard():
    """Panel de monitoreo simple."""
    
    async with OpenRedClient() as client:
        await authenticate_node(client, "node-001")
        
        # Verificar salud
        health = await check_health(client)
        print(f"Estado API: {health['status']}")
        print(f"Tiempo activo: {health['uptime']}")
        
        # Obtener métricas
        metrics = await get_system_metrics(client)
        print("Métricas del sistema recuperadas")
        
        # Descubrir nodos
        nodes = await discover_nodes(client)
        active_nodes = [n for n in nodes if n['status'] == 'active']
        print(f"Nodos activos: {len(active_nodes)}")

await monitoring_dashboard()
```

## 🔄 Gestión Avanzada de Tokens

### 1. Rotación Automática de Tokens

```python
import time
import jwt

async def refresh_access_token(client: OpenRedClient):
    """Renueva automáticamente el token de acceso."""
    
    if not client.refresh_token:
        raise Exception("No hay token de renovación disponible")
    
    headers = {"Authorization": f"Bearer {client.refresh_token}"}
    
    async with client.session.post(
        f"{client.base_url}/api/v1/auth/refresh",
        headers=headers
    ) as response:
        if response.status == 200:
            tokens = await response.json()
            client.access_token = tokens["access_token"]
            if "refresh_token" in tokens:
                client.refresh_token = tokens["refresh_token"]
            print("Token renovado exitosamente")
            return True
        else:
            print("Fallo en la renovación del token")
            return False

def is_token_expired(token: str) -> bool:
    """Verifica si un token JWT está expirado."""
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp = decoded.get("exp")
        if exp:
            return time.time() > exp
        return False
    except:
        return True

async def ensure_valid_token(client: OpenRedClient):
    """Asegura que un token válido esté disponible."""
    
    if not client.access_token or is_token_expired(client.access_token):
        success = await refresh_access_token(client)
        if not success:
            raise Exception("No se puede renovar el token")
```

## 🛠️ Utilidades y Helpers

### 1. Cliente Completo con Manejo de Errores

```python
class OpenRedAPIError(Exception):
    """Excepción personalizada para errores de API."""
    def __init__(self, message, status_code=None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class EnhancedOpenRedClient(OpenRedClient):
    """Cliente OpenRed con características avanzadas."""
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 retry_attempts: int = 3, timeout: int = 30):
        super().__init__(base_url)
        self.retry_attempts = retry_attempts
        self.timeout = timeout
    
    async def _make_request(self, method: str, endpoint: str, 
                           data: dict = None, headers: dict = None):
        """Realiza petición con retry y manejo de errores."""
        
        url = f"{self.base_url}{endpoint}"
        headers = headers or {}
        
        # Agregar token si está disponible
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        for attempt in range(self.retry_attempts):
            try:
                async with self.session.request(
                    method, url, json=data, headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status < 400:
                        if response.content_type == 'application/json':
                            return await response.json()
                        else:
                            return await response.text()
                    elif response.status == 401:
                        # Token expirado, intentar renovar
                        if await refresh_access_token(self):
                            continue
                        else:
                            raise OpenRedAPIError("Fallo en autenticación", 401)
                    else:
                        error_text = await response.text()
                        raise OpenRedAPIError(f"Error API: {error_text}", response.status)
            
            except asyncio.TimeoutError:
                if attempt == self.retry_attempts - 1:
                    raise OpenRedAPIError("Timeout de petición")
                await asyncio.sleep(2 ** attempt)  # Backoff exponencial
            
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    raise OpenRedAPIError(f"Error de red: {str(e)}")
                await asyncio.sleep(2 ** attempt)
    
    async def register_and_authenticate(self, node_config: dict):
        """Registra y autentica nodo en una operación."""
        
        # Generar claves RSA
        private_key_pem, public_key_pem = generate_rsa_keypair()
        self.private_key = serialization.load_pem_private_key(
            private_key_pem, password=None
        )
        
        # Agregar clave pública a la configuración
        node_config["public_key"] = public_key_pem.decode('utf-8')
        
        # Registrar nodo
        registration_result = await self._make_request(
            "POST", "/api/v1/auth/register", node_config
        )
        
        # Autenticar nodo
        await authenticate_node(self, node_config["node_id"])
        
        return registration_result
```

### 2. Configuración y Logging

```python
import logging
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class NodeConfig:
    """Configuración de nodo OpenRed."""
    node_id: str
    name: str
    type: str
    capabilities: List[str]
    endpoint: str
    api_url: str = "http://localhost:8000"
    log_level: str = "INFO"
    heartbeat_interval: int = 30
    message_poll_interval: int = 5
    metadata: Optional[dict] = None

def setup_logging(level: str = "INFO"):
    """Configura logging para aplicaciones OpenRed."""
    
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('openred_client.log')
        ]
    )
    
    return logging.getLogger('openred_client')

# Aplicación de ejemplo completa
async def main():
    """Aplicación de ejemplo usando API OpenRed."""
    
    logger = setup_logging("INFO")
    
    config = NodeConfig(
        node_id="example-node-001",
        name="Nodo de Ejemplo",
        type="compute",
        capabilities=["processing", "storage"],
        endpoint="https://example-node.openred.io:8443",
        api_url="http://localhost:8000"
    )
    
    async with EnhancedOpenRedClient(config.api_url) as client:
        try:
            # Registro y autenticación
            logger.info("Registrando nodo...")
            await client.register_and_authenticate(config.__dict__)
            
            # Iniciar tareas en segundo plano
            heartbeat_task = asyncio.create_task(
                heartbeat_loop(client, config.node_id, config.heartbeat_interval)
            )
            message_task = asyncio.create_task(
                message_processing_loop(client, config.node_id)
            )
            
            logger.info("Nodo operacional")
            
            # Mantener tareas en ejecución
            await asyncio.gather(heartbeat_task, message_task)
            
        except Exception as e:
            logger.error(f"Error en aplicación: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(main())
```

## 📝 Resumen

Estos ejemplos cubren todos los aspectos esenciales para usar la API Central OpenRed v2.0:

1. **Autenticación segura** con RSA y JWT
2. **Gestión completa de nodos** (registro, descubrimiento, actualizaciones)
3. **Mensajería inter-nodos** confiable y segura
4. **Monitoreo y métricas** en tiempo real
5. **Gestión avanzada de tokens** con rotación automática
6. **Cliente robusto** con manejo de errores y lógica de retry

Para una integración exitosa, asegúrate de:
- Implementar gestión adecuada de claves privadas
- Manejar errores de red y timeouts
- Mantener logs detallados para debugging
- Probar todos los escenarios de error
- Monitorear métricas de rendimiento

La API OpenRed v2.0 proporciona una base sólida para construir aplicaciones descentralizadas seguras y performantes.
