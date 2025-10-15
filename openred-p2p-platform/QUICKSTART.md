# 🚀 Test Rapide OpenRed - 2 Minutes

## ✅ Étape 1: Démarrage (30 secondes)

### Windows
```cmd
start_openred.bat
```

### Linux/macOS  
```bash
./start_openred.sh
```

**Attendez le message :** `Uvicorn running on http://0.0.0.0:8000`

## ✅ Étape 2: Interface Web (1 minute)

1. **Ouvrir** http://localhost:8000
2. **Créer votre profil** :
   - Cliquer "👤 Profil Utilisateur" → "Gérer le Profil"
   - Nom : `Test User`
   - Bio : `Demo OpenRed P2P`
   - **Ajouter une photo** (important !)
   - Sauvegarder

## ✅ Étape 3: Découverte P2P (30 secondes)

1. **Retour accueil** → "👥 Gestion des Amis" → "Gérer les Amis"
2. **Observer** :
   - 🟢 Votre statut en ligne
   - 📡 Nœuds découverts en temps réel
   - 🕷️ Internet Spider en action

## 🎯 Test Multi-Nœuds (Optionnel)

### Même Machine
```bash
# Terminal 2
OPENRED_WEB_PORT=8001 OPENRED_DATA_DIR=./user_data_2 ./start_openred.sh
```

**Puis** :
- http://localhost:8000 (Nœud 1)  
- http://localhost:8001 (Nœud 2)
- Créer profils différents
- **Voir découverte mutuelle !**

## 🔍 Que Vérifier

### ✅ Logs Serveur
```
📡 Multicast broadcaster using interface: [VOTRE_IP]
📡 Beacon broadcasted - Fingerprint: [HASH]
🕷️ Spider scanning: [IPs]
```

### ✅ Interface Web
- Status "🟢 Connecté" 
- Nœuds apparaissent dans "Constellation P2P"
- Photos profils visibles
- Demandes d'amitié fonctionnent

### ✅ Réseau P2P  
- UDP multicast sur port 5354
- Beacons toutes les 30 secondes
- Découverte automatique < 1 minute

## 🐛 Si Problème

### Pas de nœuds découverts
```bash
# Vérifier firewall Windows
# Autoriser Python et ports 8000, 8080, 5354
```

### Interface inaccessible
```bash
# Changer de port si occupé
OPENRED_WEB_PORT=8001 ./start_openred.sh
```

### Photos ne s'affichent pas
```bash
# Vérifier PIL installé
pip install pillow
```

## 🎉 Succès !

Si vous voyez :
- ✅ Interface web moderne
- ✅ Profil avec photo 
- ✅ Découverte P2P automatique
- ✅ Logs de Spider Internet

**OpenRed fonctionne parfaitement !** 🌟

---

**🤝 Contribuer** : [GitHub Issues](https://github.com/your-repo/issues)  
**💬 Discussion** : [Discord](discord-link)