"""
 FR: Fichier: main.py — Entrypoint FastAPI de l'API centrale
 EN: File: main.py — FastAPI entrypoint for the central API
 ES: Archivo: main.py — Punto de entrada FastAPI para la API central
 ZH: 文件: main.py — 中央 API 的 FastAPI 入口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.routes import nodes, messages
from src.config.settings import settings
import uvicorn

app = FastAPI(
    title="OpenRed Central API",
    description="API centrale pour l'enregistrement et la découverte des nodes OpenRed",
    version="1.0.0"
)

# Comments translations:
# FR: Configuration CORS
# EN: CORS configuration
# ES: Configuración de CORS
# ZH: CORS 配置

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(nodes.router, prefix="/api/v1/nodes", tags=["nodes"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["messages"])

@app.get("/")
async def root():
    return {
        "message": "OpenRed Central API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "central-api"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )