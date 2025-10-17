# 🌐 Protocole ORP (OpenRed Protocol)

## Vue d'ensemble

Le protocole **orp://** est le protocole personnalisé d'OpenRed Network qui permet de créer des liens directs vers les forts, projections et services du réseau. Une fois installé, ce protocole rend OpenRed Network accessible directement depuis votre navigateur ou toute application supportant les URLs personnalisées.

## Format des URLs

Le protocole utilise le format suivant :
```
orp://fort_[16_caracteres_hexadecimaux].openred/[chemin]?[parametres]
```

### Exemples d'URLs

- **Fort racine** : `orp://fort_1234567890abcdef.openred/`
- **Fenêtre publique** : `orp://fort_abcdef1234567890.openred/fenetre`
- **Projection spécifique** : `orp://fort_fedcba0987654321.openred/projection/demo123`
- **Avec paramètres** : `orp://fort_1234567890abcdef.openred/projection/test?mode=view&lang=fr`

## Installation

### Installation automatique

Exécutez l'installateur depuis le répertoire OpenRed Network :

```bash
python installer_protocole_orp.py
```

### Vérification

Testez que le protocole fonctionne :

```bash
python installer_protocole_orp.py test
```

### Désinstallation

Pour supprimer le protocole du système :

```bash
python installer_protocole_orp.py remove
```

## Fonctionnalités

### 🔍 Résolution d'adresses

Le système de résolution utilise plusieurs stratégies pour localiser un fort :

1. **Cache local** : Vérification des adresses récemment résolues
2. **Découverte réseau** : Scan du réseau local pour trouver le fort
3. **Diffusion** : Broadcast pour localiser le fort sur le réseau
4. **Distribution** : Utilisation du réseau distribué OpenRed

### 🎯 Types de connexions

- **Accès racine** (`/`) : Connexion directe au fort
- **Fenêtre publique** (`/fenetre`) : Accès à l'interface publique
- **Projections** (`/projection/[id]`) : Accès aux projections spécifiques

### 🛡️ Sécurité

- Validation stricte des identifiants de fort (16 caractères hexadécimaux)
- Vérification de l'intégrité des URLs
- Protection contre les URLs malformées

## Utilisation

### Depuis Python

```python
from modules.protocole import GestionnaireProtocole

# Traitement d'une URL
gestionnaire = GestionnaireProtocole()
resultat = gestionnaire.traiter_url("orp://fort_1234567890abcdef.openred/")

# Statistiques
stats = gestionnaire.obtenir_statistiques()
print(f"URLs traitées : {stats['urls_traitees']}")
```

### Depuis le navigateur

Une fois installé, vous pouvez :

1. Cliquer sur les liens orp:// dans les pages web
2. Taper des URLs orp:// dans la barre d'adresse
3. Utiliser les liens dans des emails ou documents

### Intégration système

Le protocole s'intègre automatiquement avec :

- **Windows** : Enregistrement dans la registry
- **Linux** : Fichiers .desktop
- **Navigateurs** : Reconnaissance automatique du protocole

## Résolution de problèmes

### Le protocole ne fonctionne pas

1. Vérifiez l'installation :
   ```bash
   python installer_protocole_orp.py test
   ```

2. Relancez l'installation :
   ```bash
   python installer_protocole_orp.py
   ```

### Permissions Windows

Sur Windows, vous pourriez avoir besoin de droits administrateur pour modifier la registry.

### Fort introuvable

Si un fort n'est pas trouvable :
- Vérifiez que le fort est en ligne
- Contrôlez la connectivité réseau
- Assurez-vous que l'ID du fort est correct

## Architecture technique

### Composants principaux

- **AdresseORP** : Parsing et validation des URLs
- **ResolveurORP** : Résolution des forts vers adresses IP
- **GestionnaireProtocole** : Traitement des actions sur les URLs
- **EnregistreurProtocole** : Installation système du protocole

### Flux de traitement

1. **Parsing** : Décomposition de l'URL orp://
2. **Validation** : Vérification format et intégrité
3. **Résolution** : Localisation du fort sur le réseau
4. **Connexion** : Établissement de la connexion
5. **Action** : Exécution de l'action demandée

## Exemples d'intégration

### Page web

```html
<a href="orp://fort_1234567890abcdef.openred/">Accéder au Fort Alpha</a>
<a href="orp://fort_abcdef1234567890.openred/fenetre">Fenêtre publique</a>
```

### Email

```
Visitez notre fort : orp://fort_1234567890abcdef.openred/
Projection demo : orp://fort_1234567890abcdef.openred/projection/demo
```

### Applications

Les applications peuvent utiliser les APIs système pour ouvrir des URLs orp:// et déclencher automatiquement OpenRed Network.

## Développement

### Tests

Exécutez la suite de tests complète :

```bash
python test_protocole_orp_clean.py
```

### Extension

Pour ajouter de nouveaux types de chemins, modifiez `GestionnaireProtocole` dans `modules/protocole/gestionnaire.py`.

## Support

Pour tout problème ou question :

1. Vérifiez les logs d'OpenRed Network
2. Testez avec l'outil de diagnostic intégré
3. Consultez la documentation technique complète

---

**OpenRed Network v1.0.0** - Protocole ORP intégré