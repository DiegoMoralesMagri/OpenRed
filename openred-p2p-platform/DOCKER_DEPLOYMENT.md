# 🐳 OpenRed P2P Platform - Déploiement Docker

## 🚀 Installation One-Click

### Installation Automatique (Linux/macOS)
```bash
curl -sSL https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/openred-p2p-platform/install.sh | bash
```

### Installation Manuelle

#### 1. Prérequis
- Docker (>= 20.10)
- Docker Compose (>= 2.0)

#### 2. Téléchargement
```bash
git clone https://github.com/DiegoMoralesMagri/OpenRed.git
cd OpenRed/openred-p2p-platform
```

#### 3. Configuration
```bash
# Copier configuration exemple
cp .env.example .env

# Éditer configuration
nano .env
```

#### 4. Démarrage
```bash
# Nœud simple
docker-compose up -d

# Multi-nœuds pour test
docker-compose --profile multi-node up -d

# Avec monitoring
docker-compose --profile monitoring up -d
```

## 🔧 Configuration

### Variables d'Environnement
```bash
# Identification
OPENRED_NODE_ID=mon_noeud_unique
OPENRED_SECTOR=general              # general, tech, health, creative...

# Réseau
OPENRED_P2P_PORT=8080              # Port P2P
OPENRED_WEB_PORT=8000              # Interface web
```

### Configuration Avancée
```json
{
    "lighthouse": {
        "multicast_group": "224.0.1.100",
        "multicast_port": 5354,
        "beacon_interval": 30
    },
    "security": {
        "rsa_key_size": 2048,
        "session_timeout": 3600
    }
}
```

## 🌐 Modes de Déploiement

### 1. Nœud Simple
```bash
docker run -d \
  --name openred-p2p-node \
  --network host \
  -e OPENRED_NODE_ID=mon_noeud \
  -e OPENRED_SECTOR=general \
  -v openred_data:/data \
  openred/p2p-platform:latest
```

### 2. Constellation Multi-Nœuds
```bash
# Nœud principal
docker-compose up -d openred-node

# Nœud secondaire
docker-compose --profile multi-node up -d
```

### 3. Déploiement Hébergeur
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  openred-node:
    image: openred/p2p-platform:latest
    restart: unless-stopped
    network_mode: host
    environment:
      - OPENRED_NODE_ID=${NODE_ID}
      - OPENRED_SECTOR=${SECTOR}
    volumes:
      - /data/openred:/data
```

## 🔍 Monitoring et Maintenance

### Commandes Utiles
```bash
# Statut des services
docker-compose ps

# Logs en temps réel
docker-compose logs -f

# Statut nœud P2P
docker exec openred-p2p-node curl localhost:8000/status

# Constellation P2P
docker exec openred-p2p-node python3 -c "
from openred_p2p_node import *
node = OpenRedP2PNode('monitor', 'monitoring')
node.print_constellation_map()
"

# Santé du container
docker healthcheck openred-p2p-node
```

### Maintenance
```bash
# Redémarrage
docker-compose restart

# Mise à jour
docker-compose pull
docker-compose up -d

# Sauvegarde données
docker run --rm -v openred_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/openred-backup.tar.gz /data

# Restauration
docker run --rm -v openred_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/openred-backup.tar.gz -C /
```

## 🌟 Cas d'Usage

### Hébergeur VPS
```bash
# Installation sur serveur distant
ssh user@vps.example.com
curl -sSL install-url | bash -s -- "vps_node" "general" 8080 8000
```

### Réseau Familial
```bash
# Papa
OPENRED_NODE_ID=papa OPENRED_SECTOR=family docker-compose up -d

# Maman
OPENRED_NODE_ID=maman OPENRED_SECTOR=family docker-compose up -d

# Enfants
OPENRED_NODE_ID=alice OPENRED_SECTOR=family docker-compose up -d
```

### Entreprise
```bash
# Département IT
OPENRED_NODE_ID=dev_team OPENRED_SECTOR=tech docker-compose up -d

# Marketing
OPENRED_NODE_ID=marketing OPENRED_SECTOR=business docker-compose up -d

# Direction
OPENRED_NODE_ID=management OPENRED_SECTOR=business docker-compose up -d
```

## 🔐 Sécurité

### Configuration Réseau
- **UDP Multicast** : 224.0.1.100:5354 (découverte)
- **TCP P2P** : Port configé (communications)
- **HTTP Interface** : Port configuré (administration)

### Pare-feu
```bash
# Autoriser discovery UDP
ufw allow 5354/udp

# Autoriser P2P TCP
ufw allow 8080/tcp

# Autoriser interface web (optionnel)
ufw allow 8000/tcp
```

### Certificats
Les clés RSA 2048 sont générées automatiquement au premier démarrage et stockées dans `/data/keys/`.

## 🚀 Performance

### Optimisations Production
```yaml
# docker-compose.prod.yml
services:
  openred-node:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
    ulimits:
      nofile: 65536
```

### Monitoring Ressources
```bash
# Utilisation ressources
docker stats openred-p2p-node

# Espace disque
docker exec openred-p2p-node df -h /data

# Processus réseau
docker exec openred-p2p-node netstat -tulpn
```

## 🛠️ Dépannage

### Problèmes Courants

**UDP Multicast ne fonctionne pas :**
```bash
# Vérifier support multicast
ip route show | grep 224.0.0.0

# Test manuel
docker run --rm --network host openred/p2p-platform:latest \
  python3 -c "import socket; print('Multicast OK')"
```

**Nœuds ne se découvrent pas :**
```bash
# Vérifier pare-feu
iptables -L | grep 5354

# Test connectivité
docker exec openred-p2p-node ping 224.0.1.100
```

**Port déjà utilisé :**
```bash
# Changer port dans .env
OPENRED_P2P_PORT=8081

# Redémarrer
docker-compose up -d
```

### Logs de Debug
```bash
# Logs détaillés
docker-compose logs -f openred-node

# Debug réseau
docker exec openred-p2p-node tcpdump -i any port 5354

# Test P2P
docker exec openred-p2p-node python3 test_p2p_platform.py
```

---

**🌟 Déploiement One-Click - La Révolution P2P à Portée de Main !**