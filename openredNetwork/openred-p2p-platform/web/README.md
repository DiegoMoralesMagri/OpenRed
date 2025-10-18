# === Instructions de Déploiement Interface Web ===
# OpenRed P2P Platform - Web Interface

## 🚀 Démarrage Rapide

### Option 1: Démarrage Direct (Recommandé)
```bash
cd web/backend
python web_api.py
```

### Option 2: Windows PowerShell
```powershell
cd web/backend
.\start_web.ps1
```

### Option 3: Linux/macOS
```bash
cd web/backend
chmod +x start_web.sh
./start_web.sh
```

## 🌐 Accès Interfaces

- **Interface Simple**: http://localhost:8000/
- **Dashboard Avancé**: http://localhost:8000/dashboard
- **API Documentation**: http://localhost:8000/api/docs
- **Status JSON**: http://localhost:8000/api/status
- **Constellation Map**: http://localhost:8000/constellation

## ⚙️ Configuration

Variables d'environnement disponibles:

```bash
OPENRED_NODE_ID=web_node_123        # ID unique du nœud
OPENRED_SECTOR=general              # Secteur P2P
OPENRED_P2P_PORT=8080              # Port réseau P2P
OPENRED_WEB_PORT=8000              # Port interface web
```

## 🔗 WebSocket en Temps Réel

L'interface utilise WebSocket pour les mises à jour temps réel:
- **Endpoint**: ws://localhost:8000/ws
- **Fréquence**: Mise à jour toutes les 5 secondes
- **Données**: Status nœud, constellation, URN, sécurité

## 📊 Fonctionnalités Disponibles

### Dashboard Principal
- ✅ Status nœud en temps réel
- ✅ Carte constellation P2P interactive
- ✅ Statistiques URN/Phantom System
- ✅ Monitoring sécurité 3-phases
- ✅ Actions de contrôle

### API REST
- ✅ GET /api/health - Santé du service
- ✅ GET /api/status - Status complet nœud
- ✅ GET /api/constellation - Carte P2P
- ✅ GET /api/urn/stats - Stats URN
- ✅ POST /api/urn/{id}/resurrect - Résurrection URN
- ✅ POST /api/urn/test - Test système URN
- ✅ GET /api/security - Status sécurité
- ✅ POST /api/connect/{fingerprint} - Connexion P2P

## 🛠️ Architecture Technique

```
web/
├── backend/
│   ├── web_api.py              # FastAPI principal
│   ├── requirements.txt        # Dépendances Python
│   ├── start_web.sh           # Script Linux/macOS
│   └── start_web.ps1          # Script Windows
└── frontend/
    └── dashboard.html         # Interface moderne
```

## 🔧 Dépendances

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
python-multipart==0.0.6
jinja2==3.1.2
aiofiles==23.2.1
python-dotenv==1.0.0
```

## 🐛 Résolution de Problèmes

### Port déjà utilisé
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8000 | xargs kill -9
```

### Problèmes WebSocket
- Vérifier firewall Windows/Linux
- Confirmer que le port 8000 est accessible
- Tester avec navigateur moderne (Chrome, Firefox, Edge)

### Nœud P2P non détecté
- Vérifier que openred_p2p_node.py fonctionne
- Confirmer UDP multicast autorisé (224.0.1.100:5354)
- Vérifier variables d'environnement

## 🎯 Prochaines Étapes

- [ ] Interface 3D constellation avec Three.js
- [ ] Export logs en temps réel
- [ ] Administration URN avancée
- [ ] Monitoring réseau détaillé
- [ ] Thèmes sombres/clairs
- [ ] Mobile responsive optimization

## 🆘 Support

En cas de problème:
1. Vérifier logs console navigateur (F12)
2. Contrôler logs FastAPI dans terminal
3. Tester endpoints API directement
4. Confirmer nœud P2P opérationnel