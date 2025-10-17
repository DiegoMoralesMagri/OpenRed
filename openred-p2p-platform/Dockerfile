# === OpenRed P2P Platform - Dockerfile Révolutionnaire ===
# Container optimisé pour nœud P2P autonome
# Support UDP multicast pour découverte "Phare dans la Nuit"

FROM python:3.11-slim

# Métadonnées du container
LABEL maintainer="OpenRed Team"
LABEL description="OpenRed P2P Platform - Revolutionary Decentralized Node"
LABEL version="1.0.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OPENRED_NODE_ID=""
ENV OPENRED_SECTOR="general"
ENV OPENRED_P2P_PORT=8080
ENV OPENRED_WEB_PORT=8000

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    curl \
    net-tools \
    iputils-ping \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

# Création utilisateur non-privilégié
RUN useradd -m -u 1000 openred && \
    mkdir -p /app /data/phantom_urn_cache /data/urn-files && \
    chown -R openred:openred /app /data

# Répertoire de travail
WORKDIR /app

# Copie des requirements d'abord (optimisation cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY core/ ./core/
COPY *.py ./
COPY README.md .

# Création des répertoires necessaires
RUN mkdir -p \
    ./core/udp_discovery \
    ./core/p2p_security \
    ./core/schrodinger_phoenix \
    ./logs \
    ./config

# Script d'initialisation
COPY docker/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Configuration réseau pour UDP multicast
# Exposition des ports
EXPOSE 8080/tcp 8000/tcp 5354/udp

# Volumes pour persistance
VOLUME ["/data"]

# Changement vers utilisateur non-privilégié
USER openred

# Répertoire de données
WORKDIR /data

# Sanity check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Point d'entrée
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Commande par défaut
CMD ["start-node"]