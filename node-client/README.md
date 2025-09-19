# OpenRed Node Client

Client auto-déployable pour les utilisateurs OpenRed. Cette application s'installe automatiquement sur le serveur de l'utilisateur avec sa base de données.

## Structure

```
node-client/
├── backend/             # API backend locale
│   ├── src/
│   │   ├── models/      # Modèles de données
│   │   ├── routes/      # Endpoints API
│   │   ├── services/    # Logique métier
│   │   └── utils/       # Utilitaires
│   ├── requirements.txt
│   └── main.py
├── frontend/            # Interface utilisateur React
│   ├── src/
│   │   ├── components/  # Composants React
│   │   ├── pages/       # Pages de l'application
│   │   ├── services/    # Services API
│   │   └── utils/       # Utilitaires
│   ├── package.json
│   └── public/
├── installer/           # Scripts d'installation automatique
│   ├── install.sh       # Script d'installation Linux/macOS
│   ├── install.bat      # Script d'installation Windows
│   └── docker/          # Configuration Docker
├── config/              # Configuration
│   ├── database.sql     # Schema de base de données
│   └── nginx.conf       # Configuration proxy web
└── README.md
```

## Installation

```bash
# Installation automatique
curl -sSL https://openred.org/install.sh | bash

# Ou manuel
./installer/install.sh
```

## Fonctionnalités

- Interface utilisateur complète (profil, posts, amis)
- API backend pour gestion des données locales
- Communication avec l'API centrale OpenRed
- Communication directe avec d'autres nodes
- Installation et configuration automatiques