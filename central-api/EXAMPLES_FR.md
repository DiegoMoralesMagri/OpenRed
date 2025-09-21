# Exemples d'utilisation - API Central OpenRed v2.0

Ce document fournit des exemples complets d'utilisation de l'API Central OpenRed v2.0, incluant l'intégration SDK, l'authentification, la gestion des nœuds et la messagerie.

## 🚀 Démarrage rapide

### Configuration initiale

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

## 🔐 Authentification et sécurité

### 1. Génération de clés RSA

```python
def generate_rsa_keypair():
    """Génère une paire de clés RSA pour l'authentification."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    
    # Sérialisation en PEM
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

# Exemple d'utilisation
private_key_pem, public_key_pem = generate_rsa_keypair()
print("Clé privée générée et stockée de manière sécurisée")
```

### 2. Enregistrement de nœud

```python
async def register_node(client: OpenRedClient, node_info: dict):
    """Enregistre un nouveau nœud dans le réseau OpenRed."""
    
    # Charger la clé privée
    private_key = serialization.load_pem_private_key(
        private_key_pem, password=None
    )
    client.private_key = private_key
    
    # Données d'enregistrement
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
            print(f"Nœud enregistré avec succès: {result['node_id']}")
            return result
        else:
            error = await response.text()
            raise Exception(f"Erreur d'enregistrement: {error}")

# Exemple d'utilisation
node_config = {
    "node_id": "node-001",
    "name": "Nœud Principal",
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

### 3. Authentification avec challenge/response

```python
async def authenticate_node(client: OpenRedClient, node_id: str):
    """Authentifie un nœud avec le système challenge/response."""
    
    # Étape 1: Demander un challenge
    async with client.session.post(
        f"{client.base_url}/api/v1/auth/login",
        json={"node_id": node_id}
    ) as response:
        if response.status == 200:
            challenge_data = await response.json()
            challenge = challenge_data["challenge"]
        else:
            raise Exception("Impossible d'obtenir le challenge")
    
    # Étape 2: Signer le challenge
    signature = client.private_key.sign(
        challenge.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    # Étape 3: Envoyer la réponse signée
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
            print("Authentification réussie")
            return tokens
        else:
            raise Exception("Échec de l'authentification")

# Exemple d'utilisation
async with OpenRedClient() as client:
    client.private_key = serialization.load_pem_private_key(
        private_key_pem, password=None
    )
    await authenticate_node(client, "node-001")
```

## 🌐 Gestion des nœuds

### 1. Découverte de nœuds

```python
async def discover_nodes(client: OpenRedClient, filters: dict = None):
    """Découvre les nœuds disponibles dans le réseau."""
    
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
            print(f"Découvert {len(nodes['nodes'])} nœuds")
            return nodes["nodes"]
        else:
            raise Exception("Erreur lors de la découverte des nœuds")

# Exemple d'utilisation
async with OpenRedClient() as client:
    # Authentification préalable requise
    await authenticate_node(client, "node-001")
    
    # Découvrir tous les nœuds
    all_nodes = await discover_nodes(client)
    
    # Découvrir uniquement les nœuds de stockage
    storage_nodes = await discover_nodes(client, {
        "type": "storage",
        "capabilities": ["storage"]
    })
```

### 2. Mise à jour du statut de nœud

```python
async def update_node_status(client: OpenRedClient, node_id: str, status_data: dict):
    """Met à jour le statut et les métadonnées d'un nœud."""
    
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
            print(f"Statut du nœud {node_id} mis à jour")
            return result
        else:
            error = await response.text()
            raise Exception(f"Erreur de mise à jour: {error}")

# Exemple d'utilisation
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

### 3. Heartbeat automatique

```python
import asyncio
from datetime import datetime

async def heartbeat_loop(client: OpenRedClient, node_id: str, interval: int = 30):
    """Maintient une connexion heartbeat avec l'API centrale."""
    
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
                    print(f"Heartbeat envoyé pour {node_id}")
                else:
                    print(f"Échec heartbeat: {response.status}")
            
            await asyncio.sleep(interval)
            
        except Exception as e:
            print(f"Erreur heartbeat: {e}")
            await asyncio.sleep(interval)

# Lancer le heartbeat en arrière-plan
asyncio.create_task(heartbeat_loop(client, "node-001"))
```

## 💬 Messagerie inter-nœuds

### 1. Envoi de messages

```python
async def send_message(client: OpenRedClient, message_data: dict):
    """Envoie un message à un ou plusieurs nœuds."""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    # Chiffrement du contenu sensible
    if message_data.get("encrypt", False):
        # Ici vous implémenteriez le chiffrement E2E
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
            print(f"Message envoyé: {result['message_id']}")
            return result
        else:
            error = await response.text()
            raise Exception(f"Erreur d'envoi: {error}")

# Exemple d'utilisation
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

### 2. Réception de messages

```python
async def get_pending_messages(client: OpenRedClient, node_id: str):
    """Récupère les messages en attente pour un nœud."""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    async with client.session.get(
        f"{client.base_url}/api/v1/messages/pending/{node_id}",
        headers=headers
    ) as response:
        if response.status == 200:
            messages = await response.json()
            print(f"Récupéré {len(messages['messages'])} messages")
            return messages["messages"]
        else:
            raise Exception("Erreur lors de la récupération des messages")

async def mark_message_read(client: OpenRedClient, message_id: str):
    """Marque un message comme lu."""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    async with client.session.put(
        f"{client.base_url}/api/v1/messages/{message_id}/read",
        headers=headers
    ) as response:
        if response.status == 200:
            print(f"Message {message_id} marqué comme lu")
        else:
            raise Exception("Erreur lors du marquage du message")

# Boucle de traitement des messages
async def message_processing_loop(client: OpenRedClient, node_id: str):
    """Traite continuellement les messages entrants."""
    
    while True:
        try:
            messages = await get_pending_messages(client, node_id)
            
            for message in messages:
                print(f"Traitement du message: {message['id']}")
                
                # Traiter le message selon son type
                if message["message_type"] == "data_sync":
                    await handle_data_sync(message)
                elif message["message_type"] == "command":
                    await handle_command(message)
                
                # Marquer comme lu
                await mark_message_read(client, message["id"])
            
            await asyncio.sleep(5)  # Attendre 5 secondes
            
        except Exception as e:
            print(f"Erreur traitement messages: {e}")
            await asyncio.sleep(10)
```

## 📊 Monitoring et métriques

### 1. Collecte de métriques

```python
async def get_system_metrics(client: OpenRedClient):
    """Récupère les métriques système de l'API."""
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    async with client.session.get(
        f"{client.base_url}/api/v1/metrics",
        headers=headers
    ) as response:
        if response.status == 200:
            metrics = await response.text()
            return metrics
        else:
            raise Exception("Erreur lors de la récupération des métriques")

async def check_health(client: OpenRedClient):
    """Vérifie l'état de santé de l'API."""
    
    async with client.session.get(
        f"{client.base_url}/api/v1/health"
    ) as response:
        if response.status == 200:
            health = await response.json()
            return health
        else:
            raise Exception("Service non disponible")

# Exemple de monitoring
async def monitoring_dashboard():
    """Tableau de bord de monitoring simple."""
    
    async with OpenRedClient() as client:
        await authenticate_node(client, "node-001")
        
        # Vérifier la santé
        health = await check_health(client)
        print(f"Statut API: {health['status']}")
        print(f"Uptime: {health['uptime']}")
        
        # Récupérer les métriques
        metrics = await get_system_metrics(client)
        print("Métriques système récupérées")
        
        # Découvrir les nœuds
        nodes = await discover_nodes(client)
        active_nodes = [n for n in nodes if n['status'] == 'active']
        print(f"Nœuds actifs: {len(active_nodes)}")

await monitoring_dashboard()
```

## 🔄 Gestion avancée des tokens

### 1. Rotation automatique des tokens

```python
import time
import jwt

async def refresh_access_token(client: OpenRedClient):
    """Rafraîchit automatiquement le token d'accès."""
    
    if not client.refresh_token:
        raise Exception("Aucun refresh token disponible")
    
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
            print("Token rafraîchi avec succès")
            return True
        else:
            print("Échec du rafraîchissement du token")
            return False

def is_token_expired(token: str) -> bool:
    """Vérifie si un token JWT est expiré."""
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp = decoded.get("exp")
        if exp:
            return time.time() > exp
        return False
    except:
        return True

async def ensure_valid_token(client: OpenRedClient):
    """S'assure qu'un token valide est disponible."""
    
    if not client.access_token or is_token_expired(client.access_token):
        success = await refresh_access_token(client)
        if not success:
            raise Exception("Impossible de renouveler le token")
```

## 🛠️ Utilitaires et helpers

### 1. Client complet avec gestion d'erreurs

```python
class OpenRedAPIError(Exception):
    """Exception personnalisée pour les erreurs API."""
    def __init__(self, message, status_code=None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class EnhancedOpenRedClient(OpenRedClient):
    """Client OpenRed avec fonctionnalités avancées."""
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 retry_attempts: int = 3, timeout: int = 30):
        super().__init__(base_url)
        self.retry_attempts = retry_attempts
        self.timeout = timeout
    
    async def _make_request(self, method: str, endpoint: str, 
                           data: dict = None, headers: dict = None):
        """Effectue une requête avec retry et gestion d'erreurs."""
        
        url = f"{self.base_url}{endpoint}"
        headers = headers or {}
        
        # Ajouter le token si disponible
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
                        # Token expiré, essayer de le rafraîchir
                        if await refresh_access_token(self):
                            continue
                        else:
                            raise OpenRedAPIError("Authentification échouée", 401)
                    else:
                        error_text = await response.text()
                        raise OpenRedAPIError(f"Erreur API: {error_text}", response.status)
            
            except asyncio.TimeoutError:
                if attempt == self.retry_attempts - 1:
                    raise OpenRedAPIError("Timeout de la requête")
                await asyncio.sleep(2 ** attempt)  # Backoff exponentiel
            
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    raise OpenRedAPIError(f"Erreur réseau: {str(e)}")
                await asyncio.sleep(2 ** attempt)
    
    async def register_and_authenticate(self, node_config: dict):
        """Enregistre et authentifie un nœud en une opération."""
        
        # Générer les clés RSA
        private_key_pem, public_key_pem = generate_rsa_keypair()
        self.private_key = serialization.load_pem_private_key(
            private_key_pem, password=None
        )
        
        # Ajouter la clé publique à la configuration
        node_config["public_key"] = public_key_pem.decode('utf-8')
        
        # Enregistrer le nœud
        registration_result = await self._make_request(
            "POST", "/api/v1/auth/register", node_config
        )
        
        # Authentifier le nœud
        await authenticate_node(self, node_config["node_id"])
        
        return registration_result
```

### 2. Configuration et logging

```python
import logging
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class NodeConfig:
    """Configuration d'un nœud OpenRed."""
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
    """Configure le logging pour les applications OpenRed."""
    
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('openred_client.log')
        ]
    )
    
    return logging.getLogger('openred_client')

# Exemple d'application complète
async def main():
    """Application exemple utilisant l'API OpenRed."""
    
    logger = setup_logging("INFO")
    
    config = NodeConfig(
        node_id="example-node-001",
        name="Nœud d'exemple",
        type="compute",
        capabilities=["processing", "storage"],
        endpoint="https://example-node.openred.io:8443",
        api_url="http://localhost:8000"
    )
    
    async with EnhancedOpenRedClient(config.api_url) as client:
        try:
            # Enregistrement et authentification
            logger.info("Enregistrement du nœud...")
            await client.register_and_authenticate(config.__dict__)
            
            # Démarrer les tâches en arrière-plan
            heartbeat_task = asyncio.create_task(
                heartbeat_loop(client, config.node_id, config.heartbeat_interval)
            )
            message_task = asyncio.create_task(
                message_processing_loop(client, config.node_id)
            )
            
            logger.info("Nœud opérationnel")
            
            # Maintenir les tâches actives
            await asyncio.gather(heartbeat_task, message_task)
            
        except Exception as e:
            logger.error(f"Erreur dans l'application: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(main())
```

## 📝 Résumé

Ces exemples couvrent tous les aspects essentiels de l'utilisation de l'API Central OpenRed v2.0 :

1. **Authentification sécurisée** avec RSA et JWT
2. **Gestion complète des nœuds** (enregistrement, découverte, mise à jour)
3. **Messagerie inter-nœuds** fiable et sécurisée
4. **Monitoring et métriques** en temps réel
5. **Gestion avancée des tokens** avec rotation automatique
6. **Client robuste** avec gestion d'erreurs et retry logic

Pour une intégration réussie, assurez-vous de :
- Implémenter une gestion appropriée des clés privées
- Gérer les erreurs réseau et les timeouts
- Maintenir des logs détaillés pour le debugging
- Tester tous les scénarios d'erreur
- Surveiller les métriques de performance

L'API OpenRed v2.0 offre une base solide pour construire des applications décentralisées sécurisées et performantes.
