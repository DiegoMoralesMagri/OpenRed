# 🔐 OpenRed Authentication System

## Vue d'ensemble

Le système d'authentification OpenRed sécurise l'interface web pour empêcher l'accès non autorisé à votre nœud P2P. **Seul le propriétaire du serveur peut accéder à l'interface.**

## ✨ Fonctionnalités

- 🔐 **Authentification forte** avec PBKDF2 + SHA256
- 🍪 **Sessions sécurisées** avec cookies HTTPOnly
- ⏰ **Expiration automatique** des sessions (24h)
- 🔑 **Changement de mot de passe** intégré
- 🚀 **Installation simple** en première utilisation

## 🚀 Première Utilisation

### 1. Accès Initial
Quand vous visitez votre OpenRed pour la première fois :
```
http://votre-serveur:8000
```
Vous serez redirigé vers : `http://votre-serveur:8000/login`

### 2. Configuration du Compte
1. Cliquez sur l'onglet **"Première Installation"**
2. Choisissez un nom d'utilisateur (min 3 caractères)
3. Créez un mot de passe fort (min 6 caractères)
4. Confirmez le mot de passe
5. Cliquez **"Créer le Compte"**

### 3. Connexion
1. Basculez vers l'onglet **"Connexion"**
2. Entrez vos identifiants
3. Cliquez **"Se Connecter"**
4. Vous êtes redirigé vers l'interface OpenRed

## 🛡️ Sécurité

### Protection des Endpoints
Tous les endpoints sensibles sont protégés :
- ✅ `/api/status` - Statut du nœud P2P
- ✅ `/api/constellation` - Vue de la constellation
- ✅ `/api/social/*` - Système d'amitié et messagerie
- ✅ `/api/profile/*` - Gestion du profil
- ✅ Toutes les pages HTML principales

### Endpoints Publics
Seuls ces endpoints restent publics :
- `/api/health` - Check basique de santé
- `/api/auth/*` - Système d'authentification
- `/login` - Page de connexion

### Sessions
- **Durée** : 24 heures
- **Stockage** : Cookie HTTPOnly sécurisé
- **Renouvellement** : Automatique à chaque utilisation
- **Révocation** : Logout ou changement de mot de passe

## 🔧 Configuration Avancée

### Variables d'Environnement
```bash
# Répertoire de données (contient auth.json)
OPENRED_DATA_DIR=./user_data

# Timeout des sessions (en secondes)
OPENRED_SESSION_TIMEOUT=86400  # 24h par défaut
```

### Fichiers Créés
```
user_data/
├── auth.json          # Données d'authentification chiffrées
├── user_profile.json  # Profil utilisateur
└── ...               # Autres données P2P
```

## 📡 API d'Authentification

### Statut du Système
```bash
GET /api/auth/status
```
Retourne si un utilisateur est configuré.

### Configuration Initiale
```bash
POST /api/auth/setup
Content-Type: application/json

{
  "username": "admin",
  "password": "motdepassefort"
}
```

### Connexion
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin", 
  "password": "motdepassefort"
}
```
Retourne un token et configure un cookie sécurisé.

### Déconnexion
```bash
POST /api/auth/logout
Authorization: Bearer <token>
```

### Changement de Mot de Passe
```bash
POST /api/auth/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "old_password": "ancienmdp",
  "new_password": "nouveaumdp"
}
```

## 🧪 Tests

### Test Manuel de l'Authentification
```bash
# Tester le système d'auth
python test_auth.py

# Tester toutes les fonctionnalités
python test_complete.py
```

### Test Automatique
```bash
# Dans votre script de déploiement
python test_auth.py && echo "Auth OK" || echo "Auth FAIL"
```

## 🚨 Troubleshooting

### "Auth system not initialized"
- Le serveur n'a pas démarré correctement
- Vérifier les logs de démarrage
- Redémarrer le serveur

### "No user configured"
- Première installation pas faite
- Aller sur `/login` et utiliser l'onglet "Première Installation"

### "Invalid credentials"
- Vérifier nom d'utilisateur et mot de passe
- Les mots de passe sont sensibles à la casse

### Sessions expirées
- Se reconnecter sur `/login`
- Les sessions durent 24h par défaut

### Accès refusé après mise à jour
- Le token peut être invalidé
- Se déconnecter et se reconnecter

## 🔄 Migration et Sauvegarde

### Sauvegarder l'Authentification
```bash
# Sauvegarder le fichier d'auth
cp user_data/auth.json user_data/auth.json.backup
```

### Réinitialiser l'Authentification
```bash
# ATTENTION : Ceci supprime l'utilisateur configuré
rm user_data/auth.json
# Redémarrer le serveur et reconfigurer
```

### Changer l'Emplacement des Données
```bash
# Déplacer le répertoire
mv user_data /nouveau/path/
export OPENRED_DATA_DIR=/nouveau/path/user_data
```

## 🌐 Déploiement Sécurisé

### VPS/Serveur Dédié
```bash
# Avec HTTPS (recommandé en production)
# Configurer reverse proxy (nginx/apache)
# Les cookies sécurisés fonctionneront correctement
```

### Hébergement Mutualisé
```bash
# Adapter le port si nécessaire
OPENRED_WEB_PORT=8080 python web/backend/web_api.py
```

### Docker (Futur)
```dockerfile
# Monter le volume de données pour persistance
-v ./user_data:/app/user_data
```

---

**🔐 Votre OpenRed est maintenant sécurisé !**

Seul le propriétaire du serveur (vous) peut accéder à l'interface. Les autres utilisateurs du réseau P2P ne peuvent que découvrir votre nœud et interagir via les protocoles P2P, mais pas accéder à votre interface de gestion.