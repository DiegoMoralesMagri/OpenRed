# [![FR](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/fr.svg) Français](DEPLOYMENT.md) | [![EN](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/gb.svg) English](DEPLOYMENT_EN.md) | [![ES](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/es.svg) Español](DEPLOYMENT_ES.md) | [![ZH](https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/cn.svg) 中文](DEPLOYMENT_ZH.md)

# 🚀 Guide de Déploiement - Écosystème O-Red

Ce guide vous accompagne dans le déploiement de l'écosystème O-Red décentralisé.

## 📋 Prérequis

### Logiciels Requis
- **Docker** (version 20.10+)
- **Docker Compose** (version 1.29+)
- **Node.js** (version 16+)
- **Python** (version 3.9+)
- **Git**

### Configuration Système
- **RAM**: Minimum 4GB, recommandé 8GB+
- **Stockage**: Minimum 10GB d'espace libre
- **Réseau**: Accès Internet pour télécharger les dépendances

## 🛠️ Installation Rapide

### Windows
```batch
# Cloner le projet (si pas déjà fait)
git clone https://github.com/O-Red/implementation.git
cd implementation

# Exécuter le script de déploiement
deploy.bat development
```

### Linux/macOS
```bash
# Cloner le projet (si pas déjà fait)
git clone https://github.com/O-Red/implementation.git
cd implementation

# Rendre le script exécutable
chmod +x deploy.sh

# Exécuter le script de déploiement
./deploy.sh development
```

## 🔧 Configuration Manuelle

### 1. Configuration de l'environnement

Créer le fichier `.env` dans `central-api/`:
```env
# Configuration O-Red API Centrale
DEBUG=false
SECRET_KEY=your_very_secure_secret_key_here
DATABASE_URL=postgresql+asyncpg://ored:ored_secure_password@postgres:5432/ored_central
REDIS_URL=redis://redis:6379/0
LOG_LEVEL=INFO

# Configuration P2P
P2P_PORT=8001
P2P_MAX_CONNECTIONS=100

# Configuration IA
AI_DISTRIBUTED_COMPUTING_ENABLED=true
AI_PRIVACY_LEVEL=maximum

# Configuration sécurité
POST_QUANTUM_ENABLED=true
RATE_LIMIT_ENABLED=true
```

### 2. Installation des dépendances

#### API Centrale
```bash
cd central-api
pip install -r requirements.txt
```

#### Interface Web
```bash
cd web-interface
npm install
```

#### Client Nœud
```bash
cd node-client
pip install -r requirements.txt
```

### 3. Démarrage des services

```bash
cd central-api
docker-compose up -d
```

## 🌐 Accès aux Services

Une fois le déploiement terminé, vous pouvez accéder aux services :

| Service | URL | Description |
|---------|-----|-------------|
| **Interface Web** | http://localhost:3000 | Interface utilisateur principale |
| **API Centrale** | http://localhost:8000 | API REST pour l'écosystème |
| **Documentation API** | http://localhost:8000/docs | Documentation Swagger interactive |
| **Prometheus** | http://localhost:9090 | Monitoring des métriques |
| **Grafana** | http://localhost:3001 | Tableaux de bord (admin/ored_admin_password) |

## 📊 Monitoring et Logs

### Consulter les logs
```bash
# Logs de tous les services
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f ored-api
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Statut des services
```bash
# Voir l'état des conteneurs
docker-compose ps

# Statistiques en temps réel
docker stats
```

## 🔍 Tests et Validation

### Tests automatisés
```bash
# Tests de l'API
cd central-api
python -m pytest app/tests/ -v

# Tests de l'interface web
cd web-interface
npm test
```

### Tests manuels
```bash
# Test de santé de l'API
curl http://localhost:8000/health

# Test de l'authentification
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"testpassword"}'
```

## 🐛 Dépannage

### Problèmes courants

#### Port déjà utilisé
```bash
# Vérifier les ports utilisés
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# Arrêter les services
docker-compose down
```

#### Erreurs de base de données
```bash
# Réinitialiser la base de données
docker-compose down -v
docker-compose up -d postgres
# Attendre 30 secondes
docker-compose up -d
```

#### Problèmes de permissions
```bash
# Linux/macOS
sudo chown -R $USER:$USER storage/ logs/

# Windows (en tant qu'administrateur)
icacls storage /grant %USERNAME%:F /T
icacls logs /grant %USERNAME%:F /T
```

### Logs de débogage
```bash
# Activer le mode debug
echo "DEBUG=true" >> central-api/.env
docker-compose restart ored-api

# Consulter les logs détaillés
docker-compose logs -f ored-api
```

## 🚀 Déploiement en Production

### Configuration pour la production
```env
# central-api/.env.production
DEBUG=false
SECRET_KEY=your_super_secure_production_key
DATABASE_URL=postgresql+asyncpg://ored:secure_prod_password@postgres:5432/ored_central
LOG_LEVEL=WARNING
RATE_LIMIT_ENABLED=true
```

### Sécurisation
1. **Changez tous les mots de passe par défaut**
2. **Configurez SSL/TLS avec des certificats valides**
3. **Activez le pare-feu et limitez les accès**
4. **Configurez la sauvegarde automatique**
5. **Activez la surveillance des logs**

### Script de déploiement production
```bash
./deploy.sh production
```

## 📈 Scaling et Performance

### Scaling horizontal
```yaml
# docker-compose.yml
services:
  ored-api:
    deploy:
      replicas: 3
    
  ored-node:
    deploy:
      replicas: 5
```

### Optimisation base de données
```sql
-- Configuration PostgreSQL pour la production
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
```

## 🔄 Mise à Jour

### Mise à jour vers une nouvelle version
```bash
# Sauvegarder les données
docker-compose exec postgres pg_dump -U ored ored_central > backup.sql

# Mettre à jour le code
git pull origin main

# Redéployer
./deploy.sh production
```

## 📞 Support

- **Documentation**: [docs.o-red.org](https://docs.o-red.org)
- **GitHub Issues**: [github.com/O-Red/implementation/issues](https://github.com/O-Red/implementation/issues)
- **Forum Communauté**: [forum.o-red.org](https://forum.o-red.org)
- **Chat Discord**: [discord.gg/ored](https://discord.gg/ored)

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](../LICENSE) pour plus de détails.

---

**Bienvenue dans l'écosystème O-Red ! 🌟**