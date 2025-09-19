# OpenRed Communication Protocols

This folder contains the specifications and implementations of the communication protocols between OpenRed nodes.

## Structure

```
protocols/
├── specifications/      # Protocol specifications
│   ├── orf-protocol.md  # OpenRed Federation Protocol
│   ├── security.md      # Security specifications
│   └── message-types.md # Supported message types
├── implementations/     # Protocol implementations
│   ├── python/          # Python implementation
│   ├── javascript/      # JavaScript/Node.js implementation
│   └── rust/            # Rust implementation (performance)
├── examples/            # Usage examples
└── tests/               # Conformance tests
```

## Main Protocols

### 1. OpenRed Federation Protocol (ORF)
Primary protocol for node-to-node communication, based on JSON over HTTP/HTTPS.

### 2. Security and Cryptography
- Authentication via cryptographic signatures
- End-to-end encryption for private messages
- Message integrity validation

### 3. Message Types
- Service messages (heartbeat, discovery)
- Social messages (posts, comments, reactions)
- Encrypted private messages
- Notifications and updates
