# OpenRed Central-API v3.0 🚀

**Ultra-minimalist P2P directory server with maximum empathy**

## 🎯 Vision

OpenRed Central-API is an ultra-empathic HTTP directory server for decentralized P2P networks. Designed with the **"Homemade Code"** philosophy for zero critical external dependencies.

## ✨ Features

- 🚀 **OpenRed Micro-Engine** - Custom HTTP server (50KB vs 15MB FastAPI)
- 💖 **Maximum empathy** - 6-month tolerance between heartbeats
- 🔐 **Asymmetric security** - Quantum-ready cryptographic tokens
- 🌍 **100,000 nodes** - Ultra-scalable architecture
- ⚡ **Zero framework** - Only cryptography as dependency
- 🛡️ **Empathic states** - Advanced node lifecycle management

## 🏗️ Architecture

```
OpenRed Central-API (HTTP Directory)
├── P2P node registration
├── Peer discovery 
├── Ultra-empathic heartbeat
├── Secure token generation
└── Real-time statistics
```

**Clear separation:**
- **Central-API** = HTTP directory (this project)
- **Node-API** = Direct P2P communication (separate project)

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Git

### Quick install

```bash
git clone https://github.com/DiegoMoralesMagri/OpenRed.git
cd OpenRed/central-api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install cryptography
python src/main.py
```

## 📡 API Endpoints

### 🏠 Information
```http
GET /
```
Basic server information

### 📝 Registration
```http
POST /register
Content-Type: application/json

{
  "node_id": "unique_node_identifier",
  "address": "192.168.1.100",
  "port": 8080,
  "public_key": "base64_encoded_public_key",
  "services": ["file_sharing", "messaging"]
}
```

### 🔍 Discovery
```http
GET /discover?services=file_sharing&max_results=10
```

### 💓 Heartbeat
```http
POST /heartbeat/{node_id}
```

### 📊 Statistics
```http
GET /stats
```

### 🔐 Tokens
```http
POST /security/token
Content-Type: application/json

{
  "node_id": "requesting_node_id"
}
```

## 💖 Empathy & Node States

| State | Description | Duration |
|-------|-------------|----------|
| `ACTIVE` | Active node | Permanent |
| `PENDING_1ST` | First check pending | 48h |
| `RETRY_48H` | Retry after 48h | 48h |
| `RETRY_2W` | Retry after 2 weeks | 2 weeks |
| `RETRY_2M` | Retry after 2 months | 2 months |
| `COMA` | Node in coma | Up to 2 years |
| `DEAD` | Node declared dead | Permanent |

## ⚙️ Configuration

File: `src/core/config.py`

```python
# Maximum capacity
max_nodes: int = 100000

# Temporal empathy  
heartbeat_check_interval: int = 15552000  # 6 months
initial_registration_lifetime: int = 31536000  # 1 year
max_coma_duration: int = 63072000  # 2 years

# Security
min_key_size: int = 2048
token_lifetime_seconds: int = 300
```

## 🌟 "Homemade Code" Philosophy

- **Custom Micro-Engine** instead of FastAPI (50KB vs 15MB)
- **Zero web framework** - Optimized manual HTTP parsing
- **Pure cryptography** - No complex JWT/OAuth
- **Technical empathy** - Maximum tolerance to network failures
- **Separated architecture** - Central-API vs Node-API

## 📜 License

MIT License - See [LICENSE](LICENSE)

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**OpenRed Central-API v3.0** - *Maximum empathy for decentralized P2P networks*