# OpenRed Node Client

Self-deployable client for OpenRed users. This application installs automatically on the user's server along with its local database.

## Structure

```
node-client/
├── backend/             # Local backend API
│   ├── src/
│   │   ├── models/      # Data models
│   │   ├── routes/      # API endpoints
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities
│   ├── requirements.txt
│   └── main.py
├── frontend/            # React user interface
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Application pages
│   │   ├── services/    # API services
│   │   └── utils/       # Utilities
│   ├── package.json
│   └── public/
├── installer/           # Auto-install scripts
│   ├── install.sh       # Linux/macOS install script
│   ├── install.bat      # Windows install script
│   └── docker/          # Docker configuration
├── config/              # Configuration
│   ├── database.sql     # Database schema
│   └── nginx.conf       # Web proxy configuration
└── README.md
```

## Installation

```bash
# Automatic installation
curl -sSL https://openred.org/install.sh | bash

# Or manual
./installer/install.sh
```

## Features

- Full user interface (profile, posts, friends)
- Local backend API for data management
- Communication with the central OpenRed API
- Direct peer-to-peer communication with other nodes
- Automatic installation and configuration
