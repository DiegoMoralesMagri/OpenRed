# Protocoles de Communication OpenRed

Ce dossier contient les spécifications et implémentations des protocoles de communication entre les nodes OpenRed.

## Structure

```
protocols/
├── specifications/      # Spécifications des protocoles
│   ├── orf-protocol.md  # OpenRed Federation Protocol
│   ├── security.md      # Spécifications de sécurité
│   └── message-types.md # Types de messages supportés
├── implementations/     # Implémentations des protocoles
│   ├── python/         # Implémentation Python
│   ├── javascript/     # Implémentation JavaScript/Node.js
│   └── rust/           # Implémentation Rust (performance)
├── examples/           # Exemples d'utilisation
└── tests/              # Tests de conformité
```

## Protocoles Principaux

### 1. OpenRed Federation Protocol (ORF)
Protocole principal pour la communication entre nodes, basé sur JSON et HTTP/HTTPS.

### 2. Sécurité et Cryptographie
- Authentification par signatures cryptographiques
- Chiffrement end-to-end pour les messages privés
- Validation d'intégrité des messages

### 3. Types de Messages
- Messages de service (heartbeat, découverte)
- Messages sociaux (posts, commentaires, réactions)
- Messages privés chiffrés
- Notifications et mises à jour