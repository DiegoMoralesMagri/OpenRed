# O-Red Technical Architecture

## System Overview

O-Red consists of three main layers that interact to create a decentralized social network:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Server A      │    │   Server B      │    │   Server C      │
│  (User)         │    │  (User)         │    │  (User)         │
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
                    │      Central API          │
                    │   (Registry Service)      │
                    │                           │
                    │  ┌─────────────────────┐  │
                    │  │   Node Directory    │  │
                    │  │   Service Discovery │  │
                    │  │   Message Routing   │  │
                    │  └─────────────────────┘  │
                    └───────────────────────────┘
```

## Detailed Components

### 1. Central API (Central Registry)

Responsibilities:
- Register and validate new nodes
- Maintain a directory of active nodes
- Provide discovery service to locate users
- Route messages between nodes
- Manage certificates and security

Technologies:
- Backend: FastAPI (Python) or Express.js (Node.js)
- Database: PostgreSQL for persistence
- Cache: Redis for performance
- Security: JWT for authentication, TLS for encryption

Main endpoints:

```
POST /api/v1/nodes/register     # Register a new node
GET  /api/v1/nodes/discover     # Discover nodes by criteria
POST /api/v1/messages/route     # Route messages between nodes
GET  /api/v1/nodes/{id}/status  # Node status
```

### 2. Node Client (User Application)

Responsibilities:
- Full user interface (SPA)
- Manage user's local data
- Communicate with the Central API
- Communicate directly with other nodes
- Auto-installation and configuration

Technologies:
- Frontend: React or Vue.js with PWA capabilities
- Local backend: Node.js with Express or Python with Flask
- Database: SQLite for portability, PostgreSQL optional
- Installer: shell/batch scripts for auto-deployment

Local data schema:

```sql
-- User profile
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

-- Posts
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    content TEXT,
    media_urls JSON,
    visibility VARCHAR(50), -- public, friends, private
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Connections (friends/followers)
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

### 3. Communication Protocols

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
    // Content specific to the message type
  },
  "signature": "cryptographic_signature"
}
```

Message types:
- `friend_request` : Friend/follow request
- `post_share` : Share a post
- `direct_message` : Private message
- `activity_update` : Activity update
- `content_sync` : Content synchronization

## Data Flows

### 1. Registering a new node

```
1. User installs Node Client on their server
2. Node Client generates cryptographic keys
3. Node Client contacts Central API to register
4. Central API validates and assigns a unique node_id
5. Node Client stores node_id and updates status
6. Node becomes discoverable by other users
```

### 2. Communication between users

```
1. User A looks up User B via Central API
2. Central API returns connection info for Node B
3. User A sends a message directly to Node B
4. Node B verifies signature and processes message
5. Node B may respond directly to Node A
```

### 3. Content sharing

```
1. User A publishes new content on their Node
2. Node A notifies Central API of the new post
3. Friends of User A receive notifications via their Nodes
4. Content remains stored on Node A; only metadata is shared
5. Other users may request access to the full content
```

## Security and Privacy

### Encryption
- In transit: TLS 1.3 for all communications
- At rest: AES-256 encryption for sensitive data
- End-to-end: Private messages encrypted with public keys

### Authentication
- Inter-node: Cryptographic signatures with public/private keys
- User: JWT tokens with automatic rotation
- Central API: OAuth2 for node authentication

### Validation
- Message integrity verification
- Protection against replay attacks
- Rate limiting to prevent spam and DoS

## Deployment and Maintenance

### Auto-installation

```bash
# Automatic install script
curl -sSL https://o-red.org/install.sh | bash

# Or manual download
wget https://o-red.org/releases/latest/ored-installer.tar.gz
tar -xzf ored-installer.tar.gz
./install.sh
```

### Auto configuration
- Server environment detection
- Automatic database configuration
- SSL certificate generation
- Web proxy configuration (nginx/apache)

### Updates
- Automatic update system
- Semantic versioning
- Automatic data migrations
- Rollback on failure
