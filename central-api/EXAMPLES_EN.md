# Usage Examples - OpenRed Central API v2.0

This document provides comprehensive usage examples for the OpenRed Central API v2.0, including SDK integration, authentication, node management, and messaging.

## 🚀 Quick Start

### Initial Setup

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

## 🔐 Authentication and Security

### 1. RSA Key Generation

```python
def generate_rsa_keypair():
    """Generate RSA key pair for authentication."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    
    # PEM serialization
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

# Usage example
private_key_pem, public_key_pem = generate_rsa_keypair()
print("Private key generated and stored securely")
```

### 2. Node Registration

```python
async def register_node(client: OpenRedClient, node_info: dict):
    """Register a new node in the OpenRed network."""
    
    # Load private key
    private_key = serialization.load_pem_private_key(
        private_key_pem, password=None
    )
    client.private_key = private_key
    
    # Registration data
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
            print(f"Node registered successfully: {result['node_id']}")
            return result
        else:
            error = await response.text()
            raise Exception(f"Registration error: {error}")

# Usage example
node_config = {
    "node_id": "node-001",
    "name": "Primary Node",
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

### 3. Challenge/Response Authentication

```python
async def authenticate_node(client: OpenRedClient, node_id: str):
    """Authenticate a node using challenge/response system."""
    
    # Step 1: Request challenge
    async with client.session.post(
        f"{client.base_url}/api/v1/auth/login",
        json={"node_id": node_id}
    ) as response:
        if response.status == 200:
            challenge_data = await response.json()
            challenge = challenge_data["challenge"]
        else:
            raise Exception("Cannot obtain challenge")
    
    # Step 2: Sign challenge
    signature = client.private_key.sign(
        challenge.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    # Step 3: Send signed response
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
            print("Authentication successful")
            return tokens
        else:
            raise Exception("Authentication failed")

# Usage example
async with OpenRedClient() as client:
    client.private_key = serialization.load_pem_private_key(
        private_key_pem, password=None
    )
    await authenticate_node(client, "node-001")
```

## 🌐 Node Management

### 1. Node Discovery

```python
async def discover_nodes(client: OpenRedClient, filters: dict = None):
    """Discover available nodes in the network."""
    
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
            print(f"Discovered {len(nodes['nodes'])} nodes")
            return nodes["nodes"]
        else:
            raise Exception("Error during node discovery")

# Usage example
async with OpenRedClient() as client:
    # Prior authentication required
    await authenticate_node(client, "node-001")
    
    # Discover all nodes
    all_nodes = await discover_nodes(client)
    
    # Discover only storage nodes
    storage_nodes = await discover_nodes(client, {
        "type": "storage",
        "capabilities": ["storage"]
    })
```

### 2. Node Status Update

```python
async def update_node_status(client: OpenRedClient, node_id: str, status_data: dict):
    """Update node status and metadata."""
    
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
            print(f"Node {node_id} status updated")
            return result
        else:
            error = await response.text()
            raise Exception(f"Update error: {error}")

# Usage example
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

### 3. Automatic Heartbeat

```python
import asyncio
from datetime import datetime

async def heartbeat_loop(client: OpenRedClient, node_id: str, interval: int = 30):
    """Maintain heartbeat connection with central API."""
    
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
                    print(f"Heartbeat sent for {node_id}")
                else:
                    print(f"Heartbeat failed: {response.status}")
            
            await asyncio.sleep(interval)
            
        except Exception as e:
            print(f"Heartbeat error: {e}")
            await asyncio.sleep(interval)

# Start background heartbeat
asyncio.create_task(heartbeat_loop(client, "node-001"))
```

## 💬 Inter-Node Messaging

### 1. Sending Messages

```python
async def send_message(client: OpenRedClient, message_data: dict):
    """Send message to one or more nodes."""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    # Encrypt sensitive content
    if message_data.get("encrypt", False):
        # Here you would implement E2E encryption
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
            print(f"Message sent: {result['message_id']}")
            return result
        else:
            error = await response.text()
            raise Exception(f"Send error: {error}")

# Usage example
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

### 2. Receiving Messages

```python
async def get_pending_messages(client: OpenRedClient, node_id: str):
    """Retrieve pending messages for a node."""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    async with client.session.get(
        f"{client.base_url}/api/v1/messages/pending/{node_id}",
        headers=headers
    ) as response:
        if response.status == 200:
            messages = await response.json()
            print(f"Retrieved {len(messages['messages'])} messages")
            return messages["messages"]
        else:
            raise Exception("Error retrieving messages")

async def mark_message_read(client: OpenRedClient, message_id: str):
    """Mark message as read."""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    async with client.session.put(
        f"{client.base_url}/api/v1/messages/{message_id}/read",
        headers=headers
    ) as response:
        if response.status == 200:
            print(f"Message {message_id} marked as read")
        else:
            raise Exception("Error marking message as read")

# Message processing loop
async def message_processing_loop(client: OpenRedClient, node_id: str):
    """Continuously process incoming messages."""
    
    while True:
        try:
            messages = await get_pending_messages(client, node_id)
            
            for message in messages:
                print(f"Processing message: {message['id']}")
                
                # Process message based on type
                if message["message_type"] == "data_sync":
                    await handle_data_sync(message)
                elif message["message_type"] == "command":
                    await handle_command(message)
                
                # Mark as read
                await mark_message_read(client, message["id"])
            
            await asyncio.sleep(5)  # Wait 5 seconds
            
        except Exception as e:
            print(f"Message processing error: {e}")
            await asyncio.sleep(10)
```

## 📊 Monitoring and Metrics

### 1. Metrics Collection

```python
async def get_system_metrics(client: OpenRedClient):
    """Retrieve system metrics from the API."""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    async with client.session.get(
        f"{client.base_url}/api/v1/metrics",
        headers=headers
    ) as response:
        if response.status == 200:
            metrics = await response.text()
            return metrics
        else:
            raise Exception("Error retrieving metrics")

async def check_health(client: OpenRedClient):
    """Check API health status."""
    
    async with client.session.get(
        f"{client.base_url}/api/v1/health"
    ) as response:
        if response.status == 200:
            health = await response.json()
            return health
        else:
            raise Exception("Service unavailable")

# Monitoring example
async def monitoring_dashboard():
    """Simple monitoring dashboard."""
    
    async with OpenRedClient() as client:
        await authenticate_node(client, "node-001")
        
        # Check health
        health = await check_health(client)
        print(f"API Status: {health['status']}")
        print(f"Uptime: {health['uptime']}")
        
        # Get metrics
        metrics = await get_system_metrics(client)
        print("System metrics retrieved")
        
        # Discover nodes
        nodes = await discover_nodes(client)
        active_nodes = [n for n in nodes if n['status'] == 'active']
        print(f"Active nodes: {len(active_nodes)}")

await monitoring_dashboard()
```

## 🔄 Advanced Token Management

### 1. Automatic Token Rotation

```python
import time
import jwt

async def refresh_access_token(client: OpenRedClient):
    """Automatically refresh access token."""
    
    if not client.refresh_token:
        raise Exception("No refresh token available")
    
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
            print("Token refreshed successfully")
            return True
        else:
            print("Token refresh failed")
            return False

def is_token_expired(token: str) -> bool:
    """Check if JWT token is expired."""
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp = decoded.get("exp")
        if exp:
            return time.time() > exp
        return False
    except:
        return True

async def ensure_valid_token(client: OpenRedClient):
    """Ensure a valid token is available."""
    
    if not client.access_token or is_token_expired(client.access_token):
        success = await refresh_access_token(client)
        if not success:
            raise Exception("Cannot renew token")
```

## 🛠️ Utilities and Helpers

### 1. Complete Client with Error Handling

```python
class OpenRedAPIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, message, status_code=None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class EnhancedOpenRedClient(OpenRedClient):
    """OpenRed client with advanced features."""
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 retry_attempts: int = 3, timeout: int = 30):
        super().__init__(base_url)
        self.retry_attempts = retry_attempts
        self.timeout = timeout
    
    async def _make_request(self, method: str, endpoint: str, 
                           data: dict = None, headers: dict = None):
        """Make request with retry and error handling."""
        
        url = f"{self.base_url}{endpoint}"
        headers = headers or {}
        
        # Add token if available
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
                        # Token expired, try to refresh
                        if await refresh_access_token(self):
                            continue
                        else:
                            raise OpenRedAPIError("Authentication failed", 401)
                    else:
                        error_text = await response.text()
                        raise OpenRedAPIError(f"API error: {error_text}", response.status)
            
            except asyncio.TimeoutError:
                if attempt == self.retry_attempts - 1:
                    raise OpenRedAPIError("Request timeout")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    raise OpenRedAPIError(f"Network error: {str(e)}")
                await asyncio.sleep(2 ** attempt)
    
    async def register_and_authenticate(self, node_config: dict):
        """Register and authenticate node in one operation."""
        
        # Generate RSA keys
        private_key_pem, public_key_pem = generate_rsa_keypair()
        self.private_key = serialization.load_pem_private_key(
            private_key_pem, password=None
        )
        
        # Add public key to configuration
        node_config["public_key"] = public_key_pem.decode('utf-8')
        
        # Register node
        registration_result = await self._make_request(
            "POST", "/api/v1/auth/register", node_config
        )
        
        # Authenticate node
        await authenticate_node(self, node_config["node_id"])
        
        return registration_result
```

### 2. Configuration and Logging

```python
import logging
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class NodeConfig:
    """OpenRed node configuration."""
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
    """Configure logging for OpenRed applications."""
    
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('openred_client.log')
        ]
    )
    
    return logging.getLogger('openred_client')

# Complete example application
async def main():
    """Example application using OpenRed API."""
    
    logger = setup_logging("INFO")
    
    config = NodeConfig(
        node_id="example-node-001",
        name="Example Node",
        type="compute",
        capabilities=["processing", "storage"],
        endpoint="https://example-node.openred.io:8443",
        api_url="http://localhost:8000"
    )
    
    async with EnhancedOpenRedClient(config.api_url) as client:
        try:
            # Registration and authentication
            logger.info("Registering node...")
            await client.register_and_authenticate(config.__dict__)
            
            # Start background tasks
            heartbeat_task = asyncio.create_task(
                heartbeat_loop(client, config.node_id, config.heartbeat_interval)
            )
            message_task = asyncio.create_task(
                message_processing_loop(client, config.node_id)
            )
            
            logger.info("Node operational")
            
            # Keep tasks running
            await asyncio.gather(heartbeat_task, message_task)
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(main())
```

## 📝 Summary

These examples cover all essential aspects of using the OpenRed Central API v2.0:

1. **Secure authentication** with RSA and JWT
2. **Complete node management** (registration, discovery, updates)
3. **Reliable and secure inter-node messaging**
4. **Real-time monitoring and metrics**
5. **Advanced token management** with automatic rotation
6. **Robust client** with error handling and retry logic

For successful integration, make sure to:
- Implement proper private key management
- Handle network errors and timeouts
- Maintain detailed logs for debugging
- Test all error scenarios
- Monitor performance metrics

The OpenRed API v2.0 provides a solid foundation for building secure and performant decentralized applications.
