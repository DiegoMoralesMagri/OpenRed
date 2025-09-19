# 🤝 Guide de Contribution - O-Red

Merci de votre intérêt pour contribuer à O-Red ! Ce projet vit grâce à sa communauté de contributeurs passionnés qui partagent notre vision d'un web décentralisé et éthique.

## 🌟 Comment Contribuer

Il existe de nombreuses façons de contribuer à O-Red, quel que soit votre niveau d'expérience :

### 🔧 Développement
- Corriger des bugs
- Ajouter de nouvelles fonctionnalités
- Améliorer les performances
- Optimiser le code existant
- Créer des tests

### 📚 Documentation
- Améliorer la documentation existante
- Créer des tutoriels
- Traduire en d'autres langues
- Corriger les erreurs de frappe
- Ajouter des exemples de code

### 🎨 Design et UX
- Améliorer l'interface utilisateur
- Créer des mockups
- Optimiser l'expérience utilisateur
- Concevoir des icônes et visuels

### 🔒 Sécurité
- Identifier des vulnérabilités
- Effectuer des audits de sécurité
- Proposer des améliorations de sécurité
- Tester la robustesse du système

### 🌍 Communauté
- Aider les nouveaux utilisateurs
- Répondre aux questions sur les forums
- Organiser des événements
- Promouvoir le projet

## 🚀 Démarrage Rapide

### 1. Fork et Clone

```bash
# Forker le repository sur GitHub, puis cloner votre fork
git clone https://github.com/VOTRE_USERNAME/O-Red.git
cd O-Red

# Ajouter le repository original comme remote
git remote add upstream https://github.com/OriginalOwner/O-Red.git
```

### 2. Configuration de l'Environnement

```bash
# Suivre le guide d'installation
cd implementation
# Voir GUIDE_TEST_LOCAL.md pour les instructions détaillées
```

### 3. Créer une Branche

```bash
# Créer une branche pour votre contribution
git checkout -b feature/ma-nouvelle-fonctionnalite
# OU
git checkout -b fix/correction-du-bug
# OU
git checkout -b docs/amelioration-documentation
```

## 📋 Types de Contributions

### 🐛 Signaler un Bug

Avant de signaler un bug :
1. Vérifiez qu'il n'a pas déjà été signalé dans les [Issues](https://github.com/[USERNAME]/O-Red/issues)
2. Testez avec la dernière version du code
3. Préparez un exemple reproductible

**Template pour signaler un bug :**

```markdown
## Description du Bug
Description claire et concise du problème.

## Étapes pour Reproduire
1. Aller à '...'
2. Cliquer sur '...'
3. Faire défiler jusqu'à '...'
4. Voir l'erreur

## Comportement Attendu
Description claire de ce qui devrait se passer.

## Captures d'Écran
Si applicable, ajoutez des captures d'écran.

## Environnement
- OS: [ex. Ubuntu 20.04]
- Navigateur: [ex. Chrome 94]
- Version de Python: [ex. 3.9.7]
- Version de Node.js: [ex. 16.14.0]

## Informations Supplémentaires
Toute autre information sur le problème.
```

### ✨ Proposer une Fonctionnalité

**Template pour proposer une fonctionnalité :**

```markdown
## Résumé de la Fonctionnalité
Description claire et concise de la fonctionnalité souhaitée.

## Motivation
Pourquoi cette fonctionnalité serait-elle utile ? Quel problème résout-elle ?

## Description Détaillée
Description détaillée de la fonctionnalité proposée.

## Alternatives Considérées
Quelles alternatives avez-vous envisagées ?

## Implémentation Suggérée
Si vous avez des idées sur l'implémentation, partagez-les ici.
```

## 🔄 Processus de Contribution

### 1. Développement

```bash
# Garder votre branche à jour
git fetch upstream
git checkout main
git merge upstream/main
git checkout feature/ma-nouvelle-fonctionnalite
git rebase main

# Faire vos modifications
# ...

# Ajouter et commiter
git add .
git commit -m "feat: ajouter nouvelle fonctionnalité X"
```

### 2. Tests

Assurez-vous que tous les tests passent :

```bash
# Tests API
cd central-api
python -m pytest app/tests/ -v

# Tests Frontend
cd ../web-interface
npm test

# Tests P2P
cd ../node-client
python -m pytest tests/ -v
```

### 3. Format du Code

Nous utilisons des outils de formatage automatique :

```bash
# Python (API et Node Client)
pip install black isort
black .
isort .

# JavaScript/TypeScript (Interface Web)
npm run lint
npm run format
```

### 4. Convention de Commit

Nous utilisons la convention [Conventional Commits](https://www.conventionalcommits.org/) :

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types :**
- `feat`: nouvelle fonctionnalité
- `fix`: correction de bug
- `docs`: changements de documentation
- `style`: changements qui n'affectent pas le code (espaces, formatage, etc.)
- `refactor`: changement de code qui ne corrige pas un bug ni n'ajoute une fonctionnalité
- `perf`: changement de code qui améliore les performances
- `test`: ajout de tests manquants ou correction de tests existants
- `chore`: changements aux outils de build ou bibliothèques auxiliaires

**Exemples :**
```bash
git commit -m "feat(api): ajouter endpoint pour gestion des nœuds"
git commit -m "fix(ui): corriger bug d'affichage sur mobile"
git commit -m "docs: mettre à jour guide d'installation"
git commit -m "test(p2p): ajouter tests pour découverte de pairs"
```

### 5. Pull Request

```bash
# Pousser votre branche
git push origin feature/ma-nouvelle-fonctionnalite

# Ouvrir une Pull Request sur GitHub
```

**Template de Pull Request :**

```markdown
## Description
Description claire de ce que fait cette PR.

## Type de Changement
- [ ] Bug fix (changement qui corrige un problème)
- [ ] Nouvelle fonctionnalité (changement qui ajoute une fonctionnalité)
- [ ] Breaking change (correction ou fonctionnalité qui casserait la fonctionnalité existante)
- [ ] Cette modification nécessite une mise à jour de la documentation

## Tests
- [ ] J'ai testé mes changements localement
- [ ] J'ai ajouté des tests qui prouvent que ma correction est efficace ou que ma fonctionnalité fonctionne
- [ ] Les tests unitaires nouveaux et existants passent localement avec mes changements

## Checklist
- [ ] Mon code suit les conventions de style de ce projet
- [ ] J'ai effectué une auto-révision de mon propre code
- [ ] J'ai commenté mon code, particulièrement dans les zones difficiles à comprendre
- [ ] J'ai apporté les modifications correspondantes à la documentation
- [ ] Mes changements ne génèrent aucun nouvel avertissement
```

## 📐 Standards de Code

### Python
- Suivre [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Utiliser des type hints
- Documenter les fonctions avec des docstrings
- Tester avec pytest

### JavaScript/TypeScript
- Utiliser ESLint et Prettier
- Suivre les conventions React/TypeScript
- Documenter avec JSDoc quand nécessaire
- Tester avec Jest et React Testing Library

### Documentation
- Utiliser Markdown
- Inclure des exemples de code
- Maintenir la cohérence avec le style existant

## 🏗️ Structure du Projet

```
O-Red/
├── docs/                    # Documentation
├── implementation/          # Code principal
│   ├── central-api/        # API FastAPI
│   ├── node-client/        # Client P2P
│   ├── web-interface/      # Interface React
│   └── tests/              # Tests d'intégration
├── scripts/                # Scripts utilitaires
├── .github/                # Templates GitHub
├── CONTRIBUTING.md         # Ce fichier
├── LICENSE                 # Licence MIT
└── README.md              # Documentation principale
```

## 🎯 Priorités de Développement

### Haute Priorité
- Stabilité et robustesse du réseau P2P
- Sécurité et cryptographie
- Performance et scalabilité
- Tests et documentation

### Moyenne Priorité
- Nouvelles fonctionnalités O-RedMind
- Interface utilisateur avancée
- Intégrations avec services externes

### Basse Priorité
- Optimisations cosmétiques
- Fonctionnalités expérimentales

## 🏆 Reconnaissance

Les contributeurs sont reconnus de plusieurs façons :
- Mention dans le README principal
- Badge de contributeur
- Accès au canal Discord des contributeurs
- Invitation aux événements de la communauté

## 🤔 Besoin d'Aide ?

- **[💬 Discussions GitHub](https://github.com/[USERNAME]/O-Red/discussions)** - Pour les questions générales
- **[🐛 Issues](https://github.com/[USERNAME]/O-Red/issues)** - Pour les bugs et fonctionnalités
- **[💬 Discord](https://discord.gg/ored)** - Pour le chat en temps réel
- **[📧 Email](mailto:community@ored.org)** - Pour les questions sensibles

## 📜 Code de Conduite

En participant à ce projet, vous acceptez de respecter notre [Code de Conduite](CODE_OF_CONDUCT.md). Nous nous engageons à maintenir un environnement ouvert et accueillant pour tous.

---

**Merci de contribuer à O-Red ! Ensemble, construisons l'avenir du web décentralisé. 🌟**