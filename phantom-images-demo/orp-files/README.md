# 📁 Organisation des Fichiers ORP

Ce dossier contient tous les fichiers ORP (O-Red Phantom) organisés par format :

## 🔀 Structure

```
orp-files/
├── BinaryPhantom/     # Fichiers PHANTOM binaires (format legacy)
└── UrnPhantom/        # Fichiers URN modernes (format JSON)
```

## 📱 BinaryPhantom (Format Legacy)

Fichiers au format binaire PHANTOM original avec connexion WebSocket :
- `cosmos_phantom.orp` - Image cosmos avec serveur phantom
- `nature_pixel.orp` - Paysage naturel pixelisé  
- `ocean_virtuel.orp` - Scène océanique virtuelle
- `test_phantom_websocket.orp` - Test WebSocket fonctionnel
- `test_ocean_fixed.orp` - Test océan réparé

**Utilisation :** 
- Double-clic pour ouvrir avec `orp_viewer_websocket_transition.py`
- Nécessite serveur phantom actif sur ws://localhost:8001

## 🔮 UrnPhantom (Format Moderne)

Fichiers au format URN avec fragmentation atomique "Burn & Phoenix" :
- `sunset_landscape.orp` - Paysage coucher de soleil
- `corporate_document.orp` - Document d'entreprise  
- `profile_photo.orp` - Photo de profil utilisateur

**Utilisation :**
- Double-clic pour ouvrir avec `orp_viewer_intelligent.py`
- Validation URN via http://localhost:8000/validate
- Chiffrement Fernet AES-128 avec rotation toutes les 30s

## 🚀 Viewers Disponibles

- `orp_viewer_websocket_transition.py` - Support complet (URN + Binary)
- `orp_viewer_intelligent.py` - Support URN avec détection format
- `orp_viewer.py` - Viewer basique legacy

## 🛠️ Serveurs Requis

- **Phantom Server:** `python phantom_projection_server.py` (port 8001)
- **URN Validator:** `python o_red_search_secure_p2p.py` (port 8000)

---
*Diego Morales Magri - Innovation URN-PHANTOM System*