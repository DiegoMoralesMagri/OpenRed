# OpenRed Federation Protocol (ORF) v1.0

## Introduction

Le protocole OpenRed Federation (ORF) est le protocole de communication standard entre les nodes OpenRed. Il permet l'échange sécurisé et décentralisé de données entre serveurs utilisateurs tout en maintenant la souveraineté des données.

## Principes Fondamentaux

1. **Décentralisation** : Aucun point central de contrôle des communications
2. **Sécurité** : Authentification cryptographique et chiffrement
3. **Interopérabilité** : Compatible avec différentes implémentations
4. **Évolutivité** : Support de versions et extensibilité
5. **Résilience** : Tolérance aux pannes et retry automatique

## Architecture du Protocole

### Transport Layer
- **Protocole** : HTTP/HTTPS
- **Format** : JSON
- **Compression** : gzip (optionnel)
- **Timeout** : 30 secondes par défaut

### Structure des Messages

Tous les messages ORF suivent cette structure de base :

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
    // Contenu spécifique au type de message
  },
  "security": {
    "signature": "cryptographic-signature",
    "public_key_fingerprint": "key-fingerprint",
    "encryption": "none|aes256"
  }
}
```

### Champs Obligatoires

- **orf_version** : Version du protocole ORF utilisée
- **message_id** : Identifiant unique du message (UUID v4)
- **timestamp** : Horodatage ISO 8601 UTC
- **type** : Type de message (voir section Types de Messages)
- **from** : Informations sur l'expéditeur
- **to** : Informations sur le destinataire
- **payload** : Contenu du message
- **security** : Informations de sécurité et signature

## Types de Messages

### 1. Messages de Service

#### node_discovery
Découverte et échange d'informations entre nodes.

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
Signalisation de l'état d'activité d'un node.

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

### 2. Messages Sociaux

#### post_share
Partage d'une publication.

```json
{
  "type": "post_share",
  "payload": {
    "post_id": "unique-post-id",
    "content": "Contenu de la publication",
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
Réaction à une publication (like, etc.).

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
Commentaire sur une publication.

```json
{
  "type": "comment",
  "payload": {
    "comment_id": "unique-comment-id",
    "post_id": "target-post-id",
    "parent_comment_id": "parent-comment-id", // Pour les réponses
    "content": "Contenu du commentaire",
    "content_type": "text|html|markdown",
    "created_at": "2025-09-19T10:30:00.000Z"
  }
}
```

### 3. Messages Relationnels

#### connection_request
Demande de connexion (ami, follow).

```json
{
  "type": "connection_request",
  "payload": {
    "request_id": "unique-request-id",
    "connection_type": "friend|follow",
    "message": "Message personnel d'accompagnement",
    "public_profile": {
      "display_name": "John Doe",
      "bio": "Description publique",
      "avatar_url": "https://node-server.com/avatar.jpg"
    }
  }
}
```

#### connection_response
Réponse à une demande de connexion.

```json
{
  "type": "connection_response",
  "payload": {
    "request_id": "original-request-id",
    "action": "accept|reject|block",
    "message": "Message de réponse optionnel"
  }
}
```

### 4. Messages Privés

#### private_message
Message privé chiffré.

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
Statut de lecture des messages.

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

## Sécurité et Authentification

### Signature des Messages

Tous les messages doivent être signés cryptographiquement :

1. **Génération de la signature** :
   - Sérialisation canonique du payload
   - Hash SHA-256 du contenu
   - Signature RSA-2048 ou Ed25519 du hash

2. **Vérification** :
   - Récupération de la clé publique de l'expéditeur
   - Vérification de la signature
   - Validation du timestamp (tolérance de 5 minutes)

### Chiffrement des Messages Privés

1. **Échange de clés** : Protocole Diffie-Hellman Ephémère (ECDHE)
2. **Chiffrement symétrique** : AES-256-GCM
3. **Authentification** : HMAC-SHA256

## Gestion des Erreurs

### Codes de Réponse HTTP

- **200 OK** : Message traité avec succès
- **400 Bad Request** : Format de message invalide
- **401 Unauthorized** : Signature invalide
- **403 Forbidden** : Accès refusé
- **404 Not Found** : Destinataire inconnu
- **429 Too Many Requests** : Rate limiting
- **500 Internal Server Error** : Erreur serveur

### Format des Erreurs

```json
{
  "orf_version": "1.0",
  "error": {
    "code": "INVALID_SIGNATURE",
    "message": "Message signature verification failed",
    "details": {
      "expected_signature": "...",
      "received_signature": "..."
    },
    "timestamp": "2025-09-19T10:30:00.000Z"
  }
}
```

## Rate Limiting

Pour prévenir le spam et les attaques DoS :

- **Messages par minute par node** : 60
- **Messages privés par minute** : 30
- **Réactions par minute** : 120
- **Découverte par minute** : 10

## Découverte et Routage

### Découverte de Nodes

1. **Via API Centrale** : Query sur l'API centrale OpenRed
2. **Via DHT** : Distributed Hash Table pour la découverte P2P
3. **Via Webfinger** : Support du protocole Webfinger pour la découverte

### Routage des Messages

1. **Direct** : Communication directe entre nodes
2. **Via Relais** : Utilisation de nodes relais pour traverser les NAT/firewalls
3. **Store-and-Forward** : Stockage temporaire pour les nodes hors ligne

## Implémentation

### Endpoints Requis

Chaque node doit exposer ces endpoints :

- `POST /.well-known/openred/inbox` : Reception des messages
- `GET /.well-known/openred/nodeinfo` : Informations du node
- `GET /.well-known/openred/public-key` : Clé publique du node

### Exemple d'Implémentation (Python)

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
        # Création de la signature
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
        # Vérification de la signature
        # Implementation...
        pass
```

## Versioning et Évolution

- **Version actuelle** : 1.0
- **Backward compatibility** : 2 versions mineures
- **Négociation de version** : Via le champ `orf_version`
- **Extensions** : Support des champs personnalisés avec préfixe `x_`

## Conformité

Pour être conforme au protocole ORF 1.0, une implémentation doit :

1. Supporter tous les types de messages de base
2. Implémenter la signature et vérification cryptographique
3. Respecter les timeouts et rate limiting
4. Gérer les erreurs selon les spécifications
5. Exposer les endpoints requis

## Tests de Conformité

Des tests automatisés sont disponibles dans le dossier `tests/` pour valider la conformité d'une implémentation.