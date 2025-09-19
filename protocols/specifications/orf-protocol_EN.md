# OpenRed Federation Protocol (ORF) v1.0

## Introduction

The OpenRed Federation Protocol (ORF) is the standard communication protocol between OpenRed nodes. It enables secure, decentralized data exchange between user servers while preserving data sovereignty.

## Core Principles

1. Decentralization: no central control point for communications
2. Security: cryptographic authentication and encryption
3. Interoperability: compatible with multiple implementations
4. Scalability: versioning and extensibility support
5. Resilience: fault tolerance and automatic retries

## Protocol Architecture

### Transport Layer
- Protocol: HTTP/HTTPS
- Format: JSON
- Compression: gzip (optional)
- Timeout: 30 seconds by default

### Message Structure

All ORF messages follow this basic structure:

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
    // Content specific to the message type
  },
  "security": {
    "signature": "cryptographic-signature",
    "public_key_fingerprint": "key-fingerprint",
    "encryption": "none|aes256"
  }
}
```

### Required Fields

- `orf_version`: ORF protocol version in use
- `message_id`: unique message identifier (UUID v4)
- `timestamp`: ISO 8601 UTC timestamp
- `type`: message type (see Message Types section)
- `from`: sender information
- `to`: recipient information
- `payload`: message content
- `security`: security and signature information

## Message Types

### 1. Service Messages

#### node_discovery
Discovery and exchange of information between nodes.

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
Node activity / presence signaling.

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

### 2. Social Messages

#### post_share
Sharing a post.

```json
{
  "type": "post_share",
  "payload": {
    "post_id": "unique-post-id",
    "content": "Post content",
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
Reaction to a post (like, etc.).

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
Comment on a post.

```json
{
  "type": "comment",
  "payload": {
    "comment_id": "unique-comment-id",
    "post_id": "target-post-id",
    "parent_comment_id": "parent-comment-id", // For replies
    "content": "Comment content",
    "content_type": "text|html|markdown",
    "created_at": "2025-09-19T10:30:00.000Z"
  }
}
```

### 3. Relational Messages

#### connection_request
Connection request (friend, follow).

```json
{
  "type": "connection_request",
  "payload": {
    "request_id": "unique-request-id",
    "connection_type": "friend|follow",
    "message": "Optional personal message",
    "public_profile": {
      "display_name": "John Doe",
      "bio": "Public description",
      "avatar_url": "https://node-server.com/avatar.jpg"
    }
  }
}
```

#### connection_response
Response to a connection request.

```json
{
  "type": "connection_response",
  "payload": {
    "request_id": "original-request-id",
    "action": "accept|reject|block",
    "message": "Optional response message"
  }
}
```

### 4. Private Messages

#### private_message
Encrypted private message.

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
Message delivery/read status.

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

## Security and Authentication

### Message Signing

All messages MUST be cryptographically signed:

1. Signature generation:
   - Canonical serialization of the payload
   - SHA-256 hash of the content
   - RSA-2048 or Ed25519 signature of the hash

2. Verification:
   - Retrieve sender's public key
   - Verify the signature
   - Validate timestamp (5 minute tolerance)

### Private Message Encryption

1. Key exchange: Ephemeral Diffie-Hellman (ECDHE)
2. Symmetric encryption: AES-256-GCM
3. Authentication: HMAC-SHA256

## Error Handling

### HTTP Response Codes

- 200 OK: message processed successfully
- 400 Bad Request: invalid message format
- 401 Unauthorized: invalid signature
- 403 Forbidden: access denied
- 404 Not Found: recipient unknown
- 429 Too Many Requests: rate limiting
- 500 Internal Server Error: server error

### Error Format

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

To prevent spam and DoS attacks:

- Messages per minute per node: 60
- Private messages per minute: 30
- Reactions per minute: 120
- Discovery per minute: 10

## Discovery and Routing

### Node Discovery

1. Via Central API: query the OpenRed central API
2. Via DHT: Distributed Hash Table for P2P discovery
3. Via Webfinger: support for Webfinger protocol

### Message Routing

1. Direct: direct communication between nodes
2. Via Relay: use relay nodes to traverse NAT/firewalls
3. Store-and-Forward: temporary storage for offline nodes

## Implementation

### Required Endpoints

Each node MUST expose these endpoints:

- `POST /.well-known/openred/inbox`: receive messages
- `GET /.well-known/openred/nodeinfo`: node information
- `GET /.well-known/openred/public-key`: node public key

### Implementation Example (Python)

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
        # Create signature
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
        # Signature verification
        # Implementation...
        pass
```

## Versioning and Evolution

- Current version: 1.0
- Backward compatibility: 2 minor versions
- Version negotiation: via the `orf_version` field
- Extensions: support custom fields prefixed with `x_`

## Compliance

To be ORF 1.0 compliant, an implementation MUST:

1. Support all base message types
2. Implement cryptographic signing and verification
3. Respect timeouts and rate limiting
4. Handle errors as specified
5. Expose required endpoints

## Conformance Tests

Automated tests are available in the `tests/` folder to validate an implementation's compliance.
