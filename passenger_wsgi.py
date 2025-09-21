#!/usr/bin/env python3
"""
WSGI Configuration for O2Switch Deployment
Point d'entrée WSGI pour le déploiement O2Switch
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire de l'application au PATH
app_path = Path(__file__).parent / "central-api"
sys.path.insert(0, str(app_path))

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv(app_path / '.env')

# Importer l'application FastAPI
from main_new import app

# Point d'entrée WSGI
application = app

if __name__ == "__main__":
    # Pour les tests locaux
    import uvicorn
    uvicorn.run(application, host="0.0.0.0", port=8000)
