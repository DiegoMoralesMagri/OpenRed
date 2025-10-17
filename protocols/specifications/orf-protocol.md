🌐 **Navigation Multilingue** | **Multilingual Navigation**
- [🇫🇷 Français](#français) | [🇺🇸 English](#english) | [🇪🇸 Español](#español) | [🇨🇳 中文](#中文)

---

## Français

# OpenRed Federation Protocol (ORF) v3.0

## Introduction

Le protocole OpenRed Federation (ORF) v3.0 est le protocole révolutionnaire de communication entre les nœuds OpenRed utilisant un système de **tokens asymétriques** pour la validation croisée sans révélation de données. Il permet des communications P2P directes après découverte via l'API centrale ultra-minimale.

## Principes Révolutionnaires v3.0

1. **Ultra-Décentralisation** : Communications P2P directes après découverte initiale
2. **Tokens Asymétriques** : Système révolutionnaire de validation croisée
3. **Sécurité Maximale** : Validation sans révélation de données sensibles
4. **Autonomie Complète** : Nœuds fonctionnels sans dépendance centrale
5. **Scalabilité Infinie** : Architecture distribuée sans goulots d'étranglement

## Architecture Révolutionnaire v3.0

### Phase 1 : Découverte via API Centrale
- **Endpoint** : `/api/v3/nodes/discover`
- **Fonction** : Annuaire de nœuds uniquement
- **Données** : Aucun stockage permanent
- **Réponse** : Liste des nœuds actifs avec endpoints P2P

### Phase 2 : Établissement de Tokens Asymétriques
```json
{
  "orf_version": "3.0",
  "phase": "token_establishment",
  "node_a": {
    "id": "node-a-uuid",
    "endpoint": "https://node-a.example.com:8080",
    "token_a": "generated-by-node-a",
    "public_key": "node-a-public-key"
  },
  "node_b": {
    "id": "node-b-uuid", 
    "endpoint": "https://node-b.example.com:8080",
    "token_b": "generated-by-central-api",
    "validation_hash": "mathematical-link-proof"
  },
  "crypto_proof": {
    "algorithm": "asymmetric-validation-v3",
    "proof": "mathematical-relationship-proof",
    "timestamp": "2025-09-22T10:30:00.000Z"
  }
}
```

### Phase 3 : Communications P2P Directes
Une fois les tokens établis, les nœuds communiquent directement :

```json
{
  "orf_version": "3.0",
  "phase": "direct_p2p",
  "message_id": "unique-p2p-message-id",
  "timestamp": "2025-09-22T10:35:00.000Z",
  "from": "node-a-uuid",
  "to": "node-b-uuid",
  "validation": {
    "token_a_proof": "cryptographic-proof-a",
    "token_b_proof": "cryptographic-proof-b",
    "cross_validation": "success"
  },
  "payload": {
    "type": "message|file|notification",
    "content": "encrypted-payload",
    "metadata": {...}
  }
}
```

---

## English

# OpenRed Federation Protocol (ORF) v3.0

## Introduction

The OpenRed Federation Protocol (ORF) v3.0 is the revolutionary communication protocol between OpenRed nodes using an **asymmetric tokens** system for cross-validation without data revelation. It enables direct P2P communications after discovery via the ultra-minimal central API.

## Revolutionary v3.0 Principles

1. **Ultra-Decentralization**: Direct P2P communications after initial discovery
2. **Asymmetric Tokens**: Revolutionary cross-validation system
3. **Maximum Security**: Validation without sensitive data revelation
4. **Complete Autonomy**: Functional nodes without central dependency
5. **Infinite Scalability**: Distributed architecture without bottlenecks

## Revolutionary v3.0 Architecture

### Phase 1: Discovery via Central API
- **Endpoint**: `/api/v3/nodes/discover`
- **Function**: Node directory only
- **Data**: No permanent storage
- **Response**: List of active nodes with P2P endpoints

### Phase 2: Asymmetric Token Establishment
```json
{
  "orf_version": "3.0",
  "phase": "token_establishment",
  "node_a": {
    "id": "node-a-uuid",
    "endpoint": "https://node-a.example.com:8080",
    "token_a": "generated-by-node-a",
    "public_key": "node-a-public-key"
  },
  "node_b": {
    "id": "node-b-uuid", 
    "endpoint": "https://node-b.example.com:8080",
    "token_b": "generated-by-central-api",
    "validation_hash": "mathematical-link-proof"
  },
  "crypto_proof": {
    "algorithm": "asymmetric-validation-v3",
    "proof": "mathematical-relationship-proof",
    "timestamp": "2025-09-22T10:30:00.000Z"
  }
}
```

### Phase 3: Direct P2P Communications
Once tokens are established, nodes communicate directly:

```json
{
  "orf_version": "3.0",
  "phase": "direct_p2p",
  "message_id": "unique-p2p-message-id",
  "timestamp": "2025-09-22T10:35:00.000Z",
  "from": "node-a-uuid",
  "to": "node-b-uuid",
  "validation": {
    "token_a_proof": "cryptographic-proof-a",
    "token_b_proof": "cryptographic-proof-b",
    "cross_validation": "success"
  },
  "payload": {
    "type": "message|file|notification",
    "content": "encrypted-payload",
    "metadata": {...}
  }
}
```

---

## Español

# Protocolo de Federación OpenRed (ORF) v3.0

## Introducción

El Protocolo de Federación OpenRed (ORF) v3.0 es el protocolo revolucionario de comunicación entre nodos OpenRed utilizando un sistema de **tokens asimétricos** para validación cruzada sin revelación de datos. Permite comunicaciones P2P directas después del descubrimiento a través de la API central ultra-mínima.

## Principios Revolucionarios v3.0

1. **Ultra-Descentralización**: Comunicaciones P2P directas después del descubrimiento inicial
2. **Tokens Asimétricos**: Sistema revolucionario de validación cruzada
3. **Seguridad Máxima**: Validación sin revelación de datos sensibles
4. **Autonomía Completa**: Nodos funcionales sin dependencia central
5. **Escalabilidad Infinita**: Arquitectura distribuida sin cuellos de botella

---

## 中文

# OpenRed联邦协议 (ORF) v3.0

## 介绍

OpenRed联邦协议(ORF) v3.0是OpenRed节点间的革命性通信协议，使用**非对称令牌**系统进行交叉验证而不泄露数据。它通过超精简中央API发现后实现直接P2P通信。

## 革命性v3.0原则

1. **超去中心化**：初始发现后的直接P2P通信
2. **非对称令牌**：革命性交叉验证系统
3. **最大安全性**：无敏感数据泄露的验证
4. **完全自主**：无中央依赖的功能节点
5. **无限可扩展性**：无瓶颈的分布式架构

---

🌐 **Navigation** | **导航**
- [🇫🇷 Français](#français) | [🇺🇸 English](#english) | [🇪🇸 Español](#español) | [🇨🇳 中文](#中文)

**ORF v3.0** - Protocole révolutionnaire | Revolutionary protocol | Protocolo revolucionario | 革命性协议
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