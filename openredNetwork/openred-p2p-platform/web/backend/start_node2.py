# === OpenRed P2P Platform - Lanceur Nœud 2 ===
# Script pour lancer un deuxième nœud sur des ports différents

import os
import uvicorn

# Configuration pour le deuxième nœud
os.environ["OPENRED_NODE_ID"] = "web_node_2"
os.environ["OPENRED_SECTOR"] = "secondary"
os.environ["OPENRED_P2P_PORT"] = "8081"  # Port P2P différent
os.environ["OPENRED_DATA_DIR"] = "./user_data_node2"  # Répertoire de données séparé

# Port web différent
WEB_PORT = 8001

print("🚀 Lancement OpenRed P2P Node 2")
print(f"   Node ID: {os.environ['OPENRED_NODE_ID']}")
print(f"   Secteur: {os.environ['OPENRED_SECTOR']}")
print(f"   Port P2P: {os.environ['OPENRED_P2P_PORT']}")
print(f"   Port Web: {WEB_PORT}")
print(f"   Interface: http://localhost:{WEB_PORT}")

if __name__ == "__main__":
    uvicorn.run(
        "web_api:app",
        host="0.0.0.0",
        port=WEB_PORT,
        reload=False,
        log_level="info"
    )