# Dockerfile pour l'API centrale O-Red
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="O-Red Community <contact@o-red.org>"
LABEL version="1.0.0"
LABEL description="API centrale pour l'écosystème O-Red décentralisé"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV PORT=8000

# Création de l'utilisateur non-root
RUN groupadd -r ored && useradd -r -g ored ored

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie du code de l'application
COPY app/ ./app/

# Création des dossiers nécessaires
RUN mkdir -p logs storage static templates && \
    chown -R ored:ored /app

# Changement vers l'utilisateur non-root
USER ored

# Port exposé
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Commande par défaut
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]