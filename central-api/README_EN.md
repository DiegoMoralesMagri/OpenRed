# OpenRed Central API

Central API for node registration and discovery in the OpenRed ecosystem.

## Structure

```
central-api/
├── src/
│   ├── models/          # Data models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── utils/           # Utilities
│   └── config/          # Configuration
├── tests/               # Unit tests
├── requirements.txt     # Python dependencies
├── main.py              # Entry point
└── README.md            # Documentation
```

## Installation

```bash
cd central-api
pip install -r requirements.txt
python main.py
```

## Endpoints

- `POST /api/v1/nodes/register` - Register a node
- `GET /api/v1/nodes/discover` - Discover nodes
- `POST /api/v1/messages/route` - Route messages
- `GET /api/v1/nodes/{id}/status` - Node status
