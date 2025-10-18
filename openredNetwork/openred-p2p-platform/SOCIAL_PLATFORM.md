# === OpenRed P2P Social Platform - Deployment Guide ===
# Système social complet avec amitié, messagerie et partage URN

## 🎉 Nouveau : Système Social P2P !

La plateforme OpenRed P2P intègre maintenant un **système social complet** permettant de :
- 👥 Gérer des amitiés P2P avec autorisations granulaires
- 💬 Échanger des messages chiffrés entre amis
- 🔱 Partager sélectivement des URN Phantom selon les permissions
- 🎯 Contrôler précisément qui peut accéder à quoi

## 🚀 Démarrage avec le Système Social

### Lancement Standard
```bash
cd web/backend
python web_api.py
```

### Accès aux Interfaces Sociales
- **Interface principale** : http://localhost:8000/
- **Gestion des amis** : http://localhost:8000/friends
- **Dashboard avancé** : http://localhost:8000/dashboard
- **API sociale** : http://localhost:8000/api/docs

## 👥 Système d'Amitié P2P

### Fonctionnalités
- **Demandes d'amitié** avec message personnalisé
- **Autorisations granulaires** : 5 niveaux de permissions
- **Acceptation/refus** avec permissions personnalisées
- **Blocage d'utilisateurs** indésirables
- **Score de confiance** évolutif

### Niveaux de Permissions
```
0. NONE         - Aucune permission
1. BASIC        - Messages uniquement
2. MEDIUM       - Messages + URN publics
3. HIGH         - Messages + URN + Photos
4. FULL         - Accès complet
```

### API Endpoints Amitié
```http
GET    /api/social/friends              # Liste des amis
GET    /api/social/friend-requests      # Demandes en attente
POST   /api/social/send-friend-request  # Envoyer demande
POST   /api/social/accept-friend-request/{id}  # Accepter
POST   /api/social/reject-friend-request/{id}  # Rejeter
```

## 💬 Messagerie P2P Chiffrée

### Capacités
- **Messages texte** chiffrés end-to-end
- **Partage de photos** avec permissions
- **Partage URN Phantom** conditionnel
- **Historique persistant** des conversations
- **Notifications** temps réel via WebSocket

### Types de Messages Supportés
- `TEXT` - Messages texte simples
- `URN_SHARE` - Partage d'URN Phantom
- `PHOTO_SHARE` - Partage de photos
- `FILE_SHARE` - Partage de fichiers
- `SYSTEM` - Messages système

### API Endpoints Messagerie
```http
GET    /api/social/conversations        # Liste conversations
GET    /api/social/conversation/{fp}    # Messages d'une conversation
POST   /api/social/send-message         # Envoyer message
```

## 🔱 Partage URN Conditionnel

### Contrôle d'Accès Granulaire
- **5 niveaux d'accès** : PRIVATE, FRIENDS_ONLY, FRIENDS_URN, FRIENDS_PHOTOS, PUBLIC
- **Listes d'autorisation** explicites par URN
- **Expiration temporelle** des accès
- **Limite d'usage** par URN
- **Journalisation** complète des partages

### Règles d'Accès
```python
# Exemples de règles
PRIVATE        # Propriétaire uniquement
FRIENDS_ONLY   # Tous les amis
FRIENDS_URN    # Amis avec permission URN
FRIENDS_PHOTOS # Amis avec permission photos
PUBLIC         # Accès libre
```

### API Endpoints Partage URN
```http
GET    /api/social/shared-urns          # URN partagés/reçus
POST   /api/social/share-urn            # Partager avec ami
POST   /api/social/create-urn-rule      # Créer règle d'accès
```

## 🏗️ Architecture Technique

### Composants Principaux
```
openred-p2p-platform/
├── friendship_protocol.py      # Système d'amitié P2P
├── social_messaging.py         # Messagerie chiffrée
├── conditional_urn_sharing.py  # Partage URN conditionnel
└── web/
    ├── backend/web_api.py      # API REST étendue
    └── frontend/friends.html   # Interface gestion amis
```

### Intégration avec P2P Core
- **Lighthouse Protocol** : Découverte d'amis potentiels
- **Security Protocol** : Chiffrement messages et signatures
- **Phantom URN Engine** : Partage intelligent des URN
- **P2P Connection** : Transport des messages sociaux

## 📊 Stockage et Persistance

### Données Stockées Localement
```
friendship_data_{node_id}/
├── friendships.json       # Relations d'amitié
└── access_rules.json      # Règles URN

messages_{node_id}/
├── conversations.json     # Historique messages
└── received_photos/       # Photos reçues

urn_sharing_{node_id}/
├── access_rules.json      # Règles d'accès URN
├── share_logs.json        # Journal partages
└── received_urns.json     # URN reçus d'amis
```

## 🔐 Sécurité et Confidentialité

### Mécanismes de Protection
- **RSA 2048** pour signatures et authentification
- **Chiffrement hybride** RSA+AES pour messages (en développement)
- **Fingerprints cryptographiques** pour identification unique
- **Sessions sécurisées** via 3-Phase Protocol
- **Validation des permissions** à chaque action

### Contrôles d'Accès
- Vérification amitié avant toute interaction
- Validation permissions granulaires
- Journalisation tous accès URN
- Blocage utilisateurs indésirables
- Expiration automatique des accès temporaires

## 🎯 Utilisation Pratique

### Scénario Typique
1. **Découverte** : Trouver des nœuds via lighthouse
2. **Demande d'amitié** : Envoyer avec permissions souhaitées
3. **Acceptation** : Accorder permissions personnalisées
4. **Messagerie** : Échanger messages chiffrés
5. **Partage URN** : Partager photos/URN selon permissions

### Exemple de Workflow
```javascript
// 1. Envoyer demande d'amitié
POST /api/social/send-friend-request
{
    "target_fingerprint": "abc123...",
    "target_node_id": "friend_node",
    "message": "Salut ! Veux-tu être ami ?",
    "permission_level": 2  // MEDIUM
}

// 2. Accepter avec permissions personnalisées
POST /api/social/accept-friend-request/req_123
{
    "permission_level": 3  // HIGH
}

// 3. Envoyer message
POST /api/social/send-message
{
    "recipient_fingerprint": "abc123...",
    "content": "Salut mon ami ! 👋"
}

// 4. Partager URN
POST /api/social/share-urn
{
    "urn_id": "urn_photo_123",
    "friend_fingerprint": "abc123...",
    "message": "Regarde cette photo !"
}
```

## 🌟 Fonctionnalités Avancées

### Métriques et Statistiques
- Nombre total d'amis par statut
- Messages envoyés/reçus par conversation
- URN partagés avec succès/refusés
- Score de confiance évolutif par ami
- Logs détaillés des interactions

### Interface Web Moderne
- **Dashboard temps réel** avec WebSocket
- **Gestion visuelle** des amis et permissions
- **Conversations** avec historique complet
- **Partage URN** avec interface glisser-déposer
- **Découverte P2P** interactive

## 🔧 Configuration Avancée

### Variables d'Environnement
```bash
OPENRED_NODE_ID=my_social_node     # ID unique du nœud
OPENRED_SECTOR=social              # Secteur spécialisé
OPENRED_P2P_PORT=8080             # Port réseau P2P
OPENRED_WEB_PORT=8000             # Port interface web
```

### Personnalisation Permissions
```python
# Permissions personnalisées
custom_permissions = {
    "streaming_access": True,      # Accès streaming
    "ai_collaboration": False,     # Collaboration IA
    "research_data": True          # Données recherche
}
```

## 🚀 Prochaines Évolutions

### Roadmap Sociale
- [ ] **Chiffrement E2E** complet (RSA+AES hybride)
- [ ] **Groupes d'amis** avec permissions collectives
- [ ] **Statuts de présence** (en ligne, occupé, invisible)
- [ ] **Appels vocaux P2P** chiffrés
- [ ] **Streaming URN** en temps réel
- [ ] **Synchronisation multi-device** des conversations
- [ ] **Marketplace URN** entre amis
- [ ] **Réputation distribuée** et web of trust

## 🎯 Impact sur l'Écosystème

Le système social P2P d'OpenRed révolutionne la façon dont les utilisateurs interagissent dans un environnement décentralisé :

### Avantages Clés
- **Zéro dépendance** serveurs centraux
- **Contrôle total** des données personnelles  
- **Permissions granulaires** par relation
- **Chiffrement bout-en-bout** natif
- **Évolutivité P2P** infinie

### Cas d'Usage
- **Réseaux sociaux** décentralisés
- **Collaboration** créative P2P
- **Partage de contenu** privé
- **Communautés** spécialisées
- **Échange de ressources** entre pairs

---

**La plateforme OpenRed P2P devient maintenant un véritable réseau social décentralisé avec des capacités sociales avancées ! 🚀👥💬🔱**