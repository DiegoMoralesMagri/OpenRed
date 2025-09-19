````markdown
[![FR](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/fr.svg) Français](README.md) | [![EN](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/gb.svg) English](README_EN.md) | [![ES](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/es.svg) Español](README_ES.md) | [![ZH](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/cn.svg) 中文](README_ZH.md)

````markdown
# OpenRed Central API

API centrale pour l'enregistrement et la découverte des nodes OpenRed.

## Structure

```
central-api/
├── src/
│   ├── models/          # Modèles de données
│   ├── routes/          # Endpoints API
│   ├── services/        # Logique métier
│   ├── utils/           # Utilitaires
│   └── config/          # Configuration
├── tests/               # Tests unitaires
├── requirements.txt     # Dépendances Python
├── main.py             # Point d'entrée
└── README.md           # Documentation
```

## Installation

```bash
cd central-api
pip install -r requirements.txt
python main.py
```

## Endpoints

- `POST /api/v1/nodes/register` - Enregistrement d'un node
- `GET /api/v1/nodes/discover` - Découverte de nodes
- `POST /api/v1/messages/route` - Routage de messages
- `GET /api/v1/nodes/{id}/status` - Statut d'un node