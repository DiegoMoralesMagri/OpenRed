# Exemples d'utilisation - OpenRed Central API v2.0

## 🔐 Authentification et Enregistrement

### 1. Enregistrement d'un nouveau node

```bash
# Génération d'une paire de clés RSA pour le node
openssl genrsa -out node_private.pem 2048
openssl rsa -in node_private.pem -outform PEM -pubout -out node_public.pem

# Enregistrement du node
curl -X POST "https://central-api.openred.org/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": "my-awesome-node",
    "display_name": "Mon Node OpenRed",
    "server_url": "https://mon-node.example.com",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqh...\n-----END PUBLIC KEY-----",
    "version": "2.0.0",
    "capabilities": ["messaging", "file_sharing", "ai_assistant"]
  }'
```

**Réponse :**
```json
{
  "success": true,
  "node_id": "my-awesome-node",
  "tokens": {
    "access_token": "eyJhbGciOiJSUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 900
  },
  "message": "Node registered successfully"
}
```

### 2. Authentification avec signature cryptographique

```python
import time
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import requests

def authenticate_node(node_id, private_key_path):
    # Chargement de la clé privée
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    
    # Génération du nonce et du message à signer
    nonce = base64.urlsafe_b64encode(os.urandom(32)).decode()
    timestamp = time.time()
    message = f"{node_id}:{nonce}:{timestamp}"
    
    # Signature du message
    signature = private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    signature_b64 = base64.b64encode(signature).decode()
    
    # Requête d'authentification
    response = requests.post("https://central-api.openred.org/api/v1/auth/login", json={
        "node_id": node_id,
        "nonce": nonce,
        "signature": signature_b64,
        "timestamp": timestamp
    })
    
    return response.json()
```

## 🌐 Découverte de Nodes

### 1. Recherche de nodes par capacités

```bash
curl -X GET "https://central-api.openred.org/api/v1/nodes/discover" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -G \
  -d "capabilities=ai_assistant,file_sharing" \
  -d "limit=20" \
  -d "status=active"
```

**Réponse :**
```json
{
  "nodes": [
    {
      "node_id": "ai-powerhouse-node",
      "display_name": "IA Powerhouse",
      "server_url": "https://ai-node.example.com",
      "capabilities": ["ai_assistant", "image_generation", "nlp"],
      "version": "2.1.0",
      "status": "active",
      "last_heartbeat": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

### 2. Découverte géographique

```python
import requests

def discover_nearby_nodes(latitude, longitude, radius_km=50):
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "geo_lat": latitude,
        "geo_lng": longitude,
        "geo_radius": radius_km,
        "capabilities": "messaging,social"
    }
    
    response = requests.get(
        "https://central-api.openred.org/api/v1/nodes/discover",
        headers=headers,
        params=params
    )
    
    return response.json()

# Exemple : nodes près de Paris
paris_nodes = discover_nearby_nodes(48.8566, 2.3522, 100)
```

## 💬 Routage de Messages

### 1. Envoi de message chiffré

```python
import json
from cryptography.fernet import Fernet

def send_encrypted_message(from_node, to_node, content, encryption_key):
    # Chiffrement du contenu
    cipher = Fernet(encryption_key)
    encrypted_content = cipher.encrypt(content.encode()).decode()
    
    # Métadonnées du message
    message_data = {
        "from_node_id": from_node,
        "to_node_id": to_node,
        "content_type": "text/plain",
        "encrypted_content": encrypted_content,
        "priority": "normal",
        "ttl_hours": 72
    }
    
    # Envoi via l'API
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(
        "https://central-api.openred.org/api/v1/messages/send",
        headers=headers,
        json=message_data
    )
    
    return response.json()

# Exemple d'utilisation
result = send_encrypted_message(
    "my-node",
    "friend-node", 
    "Salut ! Comment ça va ?",
    encryption_key
)
```

### 2. Réception et déchiffrement

```python
def receive_messages(node_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"https://central-api.openred.org/api/v1/messages/receive",
        headers=headers,
        params={"node_id": node_id, "limit": 50}
    )
    
    messages = response.json()["messages"]
    
    # Déchiffrement des messages
    for message in messages:
        if message["content_type"] == "text/plain":
            cipher = Fernet(encryption_key)
            decrypted = cipher.decrypt(message["encrypted_content"].encode())
            message["content"] = decrypted.decode()
    
    return messages
```

## 📊 Monitoring et Heartbeat

### 1. Envoi de heartbeat régulier

```python
import schedule
import time

def send_heartbeat(node_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "node_id": node_id,
        "status": "active",
        "load": get_system_load(),
        "capabilities": ["messaging", "ai_assistant"],
        "metadata": {
            "uptime": get_uptime(),
            "connected_users": get_user_count()
        }
    }
    
    response = requests.post(
        "https://central-api.openred.org/api/v1/nodes/heartbeat",
        headers=headers,
        json=data
    )
    
    return response.status_code == 200

# Heartbeat toutes les 5 minutes
schedule.every(5).minutes.do(lambda: send_heartbeat("my-node"))

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 2. Surveillance des métriques

```bash
# Métriques Prometheus
curl "https://central-api.openred.org/metrics"

# Health check
curl "https://central-api.openred.org/health"
```

## 🔄 Gestion des Tokens

### 1. Renouvellement automatique des tokens

```python
import time
import jwt
from datetime import datetime

class TokenManager:
    def __init__(self, refresh_token):
        self.refresh_token = refresh_token
        self.access_token = None
        self.token_expires = None
    
    def get_valid_token(self):
        # Vérifie si le token est encore valide
        if self.access_token and self.token_expires > datetime.now():
            return self.access_token
        
        # Renouvelle le token
        return self.refresh_access_token()
    
    def refresh_access_token(self):
        response = requests.post(
            "https://central-api.openred.org/api/v1/auth/refresh",
            json={"refresh_token": self.refresh_token}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            self.token_expires = datetime.now() + timedelta(minutes=15)
            return self.access_token
        
        raise Exception("Token refresh failed")

# Utilisation
token_manager = TokenManager(initial_refresh_token)
headers = {"Authorization": f"Bearer {token_manager.get_valid_token()}"}
```

## 🚀 Intégration Complète

### Node Client Complet

```python
class OpenRedNodeClient:
    def __init__(self, node_id, private_key_path, api_base="https://central-api.openred.org"):
        self.node_id = node_id
        self.private_key_path = private_key_path
        self.api_base = api_base
        self.token_manager = None
        
    async def register(self, display_name, server_url, capabilities):
        """Enregistrement initial du node"""
        # Code d'enregistrement ici
        pass
    
    async def authenticate(self):
        """Authentification avec signature crypto"""
        # Code d'authentification ici
        pass
    
    async def discover_nodes(self, **filters):
        """Découverte de nodes"""
        # Code de découverte ici
        pass
    
    async def send_message(self, to_node, content, content_type="text/plain"):
        """Envoi de message chiffré"""
        # Code d'envoi ici
        pass
    
    async def receive_messages(self):
        """Réception de messages"""
        # Code de réception ici
        pass
    
    async def start_heartbeat(self, interval=300):
        """Démarre le heartbeat automatique"""
        # Code de heartbeat ici
        pass

# Utilisation
async def main():
    client = OpenRedNodeClient("my-node", "keys/private.pem")
    
    # Enregistrement
    await client.register(
        display_name="Mon Node OpenRed",
        server_url="https://mon-node.example.com",
        capabilities=["messaging", "ai_assistant"]
    )
    
    # Authentification
    await client.authenticate()
    
    # Démarrage du heartbeat
    await client.start_heartbeat()
    
    # Découverte et communication
    nodes = await client.discover_nodes(capabilities="ai_assistant")
    if nodes:
        await client.send_message(nodes[0]["node_id"], "Salut !")

# Lancement
asyncio.run(main())
```

## 🛠️ SDK et Bibliothèques

### Installation du SDK Python

```bash
pip install openred-sdk
```

### Exemple avec le SDK

```python
from openred_sdk import OpenRedClient, Config

# Configuration
config = Config(
    api_base="https://central-api.openred.org",
    node_id="my-awesome-node",
    private_key_path="keys/private.pem"
)

# Client
client = OpenRedClient(config)

# Utilisation simplifiée
await client.connect()
nodes = await client.discover(capabilities=["ai_assistant"])
await client.send_message(nodes[0].node_id, "Hello OpenRed!")
```

---

Ces exemples montrent l'utilisation complète de l'API centrale OpenRed v2.0 pour construire un écosystème décentralisé robuste et sécurisé.
