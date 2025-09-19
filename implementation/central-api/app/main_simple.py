# FR: Version simplifiée pour diagnostic O2Switch
# EN: Simplified version for O2Switch diagnostic
# ES: Versión simplificada para diagnóstico O2Switch
# ZH: O2Switch诊断的简化版本

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

# Configuration basique
app = FastAPI(
    title="O-Red Central API - Test",
    description="Version de test pour O2Switch",
    version="0.1.0"
)

# CORS simple
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporaire pour les tests
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Test de base"""
    return {
        "message": "O-Red API Test",
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "python_version": os.sys.version,
        "environment": os.environ.get("ENVIRONMENT", "unknown")
    }

@app.get("/health")
async def health():
    """Health check simple"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/test")
async def test_endpoint():
    """Endpoint de test"""
    return {
        "test": "success",
        "message": "L'API fonctionne correctement sur O2Switch",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)