# API Documentation - OpenRed Central-API v3.0

## Base URL
```
http://localhost:8000
```

## Authentication
Most endpoints require no authentication. Token endpoints require valid node registration.

## Content Type
All POST requests should use `Content-Type: application/json`

---

## Endpoints

### 🏠 Server Information

#### `GET /`

Returns basic server information and available endpoints.

**Response:**
```json
{
  "service": "OpenRed Central-API",
  "version": "3.0",
  "description": "Ultra-minimalist P2P node directory with maximum empathy",
  "philosophy": "Code maison whenever possible",
  "engine": "OpenRed Micro-Engine",
  "endpoints": {
    "register": "POST /register - Register a new node",
    "discover": "GET /discover - Discover available nodes",
    "heartbeat": "POST /heartbeat/{node_id} - Node heartbeat",
    "stats": "GET /stats - Server statistics",
    "security": "POST /security/token - Generate security token"
  },
  "empathy_level": "maximum",
  "max_nodes": 100000,
  "node_tolerance": "6 months between heartbeats"
}
```

---

### 📝 Node Registration

#### `POST /register`

Register a new P2P node in the directory.

**Request Body:**
```json
{
  "node_id": "unique_node_identifier",
  "address": "192.168.1.100",
  "port": 8080,
  "public_key": "base64_encoded_public_key",
  "services": ["file_sharing", "messaging", "backup"],
  "metadata": {
    "name": "My Node",
    "description": "File sharing node",
    "version": "1.0.0"
  }
}
```

**Successful Response (201):**
```json
{
  "status": "registered",
  "node_id": "unique_node_identifier",
  "registered_at": "2025-09-23T10:30:00Z",
  "expires_at": "2026-09-23T10:30:00Z",
  "state": "ACTIVE",
  "message": "Node registered with maximum empathy",
  "next_heartbeat_due": "2026-03-23T10:30:00Z"
}
```

**Error Response (400):**
```json
{
  "error": "registration_failed",
  "message": "Invalid node_id format",
  "details": "node_id must be alphanumeric string"
}
```

---

### 🔍 Node Discovery

#### `GET /discover`

Discover available P2P nodes based on services and criteria.

**Query Parameters:**
- `services` (optional): Comma-separated list of required services
- `max_results` (optional): Maximum number of nodes to return (default: 50, max: 100)
- `exclude_states` (optional): Comma-separated list of states to exclude (default: "DEAD")
- `min_last_seen` (optional): ISO date, only nodes seen after this date

**Examples:**
```http
GET /discover
GET /discover?services=file_sharing,messaging&max_results=10
GET /discover?exclude_states=COMA,DEAD&min_last_seen=2025-09-01T00:00:00Z
```

**Response:**
```json
{
  "nodes": [
    {
      "node_id": "node_001",
      "address": "192.168.1.100",
      "port": 8080,
      "services": ["file_sharing", "messaging"],
      "state": "ACTIVE",
      "last_seen": "2025-09-23T10:15:00Z",
      "metadata": {
        "name": "Node 1",
        "version": "1.0.0"
      }
    },
    {
      "node_id": "node_002",
      "address": "10.0.0.50",
      "port": 8080,
      "services": ["file_sharing"],
      "state": "PENDING_1ST",
      "last_seen": "2025-09-22T15:30:00Z"
    }
  ],
  "total_found": 2,
  "query_time_ms": 15
}
```

---

### 💓 Heartbeat

#### `POST /heartbeat/{node_id}`

Send a heartbeat for a registered node to maintain its active status.

**URL Parameters:**
- `node_id`: The unique identifier of the node

**Request Body (optional):**
```json
{
  "services": ["file_sharing", "messaging"],
  "metadata": {
    "load": "low",
    "available_storage": "500GB"
  }
}
```

**Successful Response (200):**
```json
{
  "status": "heartbeat_received",
  "node_id": "node_001",
  "current_state": "ACTIVE",
  "last_heartbeat": "2025-09-23T10:30:00Z",
  "next_heartbeat_due": "2026-03-23T10:30:00Z",
  "empathy_message": "Your node is alive and well! Thank you for staying connected."
}
```

**Node Not Found (404):**
```json
{
  "error": "node_not_found",
  "message": "Node not registered in directory",
  "suggestion": "Please register your node first using POST /register"
}
```

---

### 📊 Server Statistics

#### `GET /stats`

Get real-time server statistics and directory information.

**Response:**
```json
{
  "server": {
    "name": "OpenRed Central-API",
    "version": "3.0.0",
    "uptime_seconds": 86400,
    "engine": "OpenRed Micro-Engine"
  },
  "directory": {
    "total_nodes": 1250,
    "active_nodes": 980,
    "nodes_by_state": {
      "ACTIVE": 980,
      "PENDING_1ST": 45,
      "RETRY_48H": 12,
      "RETRY_2W": 8,
      "RETRY_2M": 3,
      "COMA": 2,
      "DEAD": 0
    },
    "capacity_used_percent": 1.25,
    "max_capacity": 100000
  },
  "performance": {
    "requests_per_second": 125.5,
    "average_response_time_ms": 12.3,
    "memory_usage_mb": 45.2
  },
  "empathy": {
    "nodes_revived_from_coma": 15,
    "total_empathy_extensions": 234,
    "longest_tolerance_days": 180
  }
}
```

---

### 🔐 Security Token

#### `POST /security/token`

Generate a temporary security token for P2P authentication.

**Request Body:**
```json
{
  "node_id": "requesting_node_id",
  "purpose": "peer_authentication",
  "lifetime_seconds": 300
}
```

**Successful Response (200):**
```json
{
  "token_id": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2025-09-23T10:35:00Z",
  "public_verification_key": "LS0tLS1CRUdJTi...",
  "mathematical_link": "a1b2c3d4e5f6...",
  "usage": "Include token_id in Authorization header for P2P requests"
}
```

**Error Response (403):**
```json
{
  "error": "token_generation_failed",
  "message": "Node not found or not in ACTIVE state",
  "current_state": "PENDING_1ST"
}
```

---

## Error Codes

| HTTP Code | Error Type | Description |
|-----------|------------|-------------|
| 400 | `bad_request` | Invalid request format or parameters |
| 404 | `not_found` | Resource not found (node, endpoint) |
| 403 | `forbidden` | Operation not allowed for current node state |
| 429 | `rate_limited` | Too many requests, slow down |
| 500 | `internal_error` | Server error, empathic retry recommended |
| 503 | `service_unavailable` | Server overloaded, try again later |

---

## Node States Lifecycle

```
REGISTRATION → ACTIVE → [HEARTBEAT MISSED] → PENDING_1ST
                ↑                                ↓
                └─── [HEARTBEAT RECEIVED] ←─── FAILED_1ST
                                                ↓
                                           RETRY_48H
                                                ↓
                                           RETRY_2W
                                                ↓
                                           RETRY_2M
                                                ↓
                                             COMA
                                                ↓
                                             DEAD
```

## Rate Limiting

- Registration: 10 requests per minute per IP
- Heartbeat: 1 request per minute per node
- Discovery: 60 requests per minute per IP
- Token generation: 5 requests per minute per node

## Best Practices

1. **Registration**: Include comprehensive metadata for better discovery
2. **Heartbeat**: Send heartbeats regularly, but respect the 6-month tolerance
3. **Discovery**: Use specific service filters to reduce response size
4. **Tokens**: Cache tokens until expiration to avoid unnecessary requests
5. **Error Handling**: Implement exponential backoff for empathic retry logic

---

**OpenRed Central-API v3.0** - *Maximum empathy for decentralized P2P networks*