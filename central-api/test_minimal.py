#!/usr/bin/env python3
"""
Test minimal ultra-rapide
Ultra-quick minimal test
"""

import sys
import os

# Ajout du répertoire src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI
from src.api.v1.endpoints import health

app = FastAPI(title="OpenRed Test Minimal")
app.include_router(health.router, prefix="/health", tags=["Health"])

@app.get("/")
async def root():
    return {"message": "OpenRed Central API Test", "status": "running"}

@app.get("/ping")
async def ping():
    return {"status": "pong"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage du serveur de test minimal...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
