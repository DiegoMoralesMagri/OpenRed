🌐 **Navigation Multilingue** | **Multilingual Navigation**
- [🇫🇷 Français](#français) | [🇺🇸 English](#english) | [🇪🇸 Español](#español) | [🇨🇳 中文](#中文)

---

## Français

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
git clone https://github.com/VOTRE_USERNAME/OpenRed.git
cd O-Red

# Ajouter le repository original comme remote
git remote add upstream https://github.com/DiegoMoralesMagri/OpenRed.git
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
1. Vérifiez qu'il n'a pas déjà été signalé dans les [Issues](https://github.com/DiegoMoralesMagri/OpenRed/issues)
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

- **[💬 Discussions GitHub](https://github.com/DiegoMoralesMagri/OpenRed/discussions)** - Pour les questions générales
- **[🐛 Issues](https://github.com/DiegoMoralesMagri/OpenRed/issues)** - Pour les bugs et fonctionnalités
- **[💬 Discord](https://discord.gg/dEJ2eaU4)** - Pour le chat en temps réel
- **[📧 Email](mailto:community@o-red.org)** - Pour les questions sensibles

## 📜 Code de Conduite

En participant à ce projet, vous acceptez de respecter notre [Code de Conduite](CODE_OF_CONDUCT.md). Nous nous engageons à maintenir un environnement ouvert et accueillant pour tous.

---

**Merci de contribuer à O-Red ! Ensemble, construisons l'avenir du web décentralisé. 🌟**

---

## English

# 🤝 Contributing Guide - O-Red

Thank you for your interest in contributing to O-Red! This project thrives thanks to its community of passionate contributors who share our vision of a decentralized and ethical web.

## 🌟 How to Contribute

There are many ways to contribute to O-Red, regardless of your experience level:

### 🔧 Development
- Fix bugs
- Add new features
- Improve performance
- Optimize existing code
- Create tests

### 📚 Documentation
- Improve existing documentation
- Create tutorials
- Translate to other languages
- Fix typos
- Add code examples

### 🎨 Design and UX
- Improve user interface
- Create mockups
- Optimize user experience
- Design icons and visuals

### 🔒 Security
- Identify vulnerabilities
- Perform security audits
- Propose security improvements
- Test system robustness

### 🌍 Community
- Help new users
- Answer questions on forums
- Organize events
- Promote the project

## 🚀 Quick Start

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/OpenRed.git
cd O-Red

# Add the original repository as remote
git remote add upstream https://github.com/DiegoMoralesMagri/OpenRed.git
```

### 2. Environment Setup

```bash
# Follow the installation guide
cd implementation
# See GUIDE_TEST_LOCAL.md for detailed instructions
```

### 3. Create a Branch

```bash
# Create a branch for your contribution
git checkout -b feature/my-new-feature
# OR
git checkout -b fix/bug-correction
# OR
git checkout -b docs/documentation-improvement
```

## 📋 Types of Contributions

### 🐛 Report a Bug

Before reporting a bug:
1. Check that it hasn't already been reported in [Issues](https://github.com/DiegoMoralesMagri/OpenRed/issues)
2. Test with the latest version of the code
3. Prepare a reproducible example

**Bug report template:**

```markdown
## Bug Description
Clear and concise description of the problem.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
Clear description of what should happen.

## Screenshots
If applicable, add screenshots.

## Environment
- OS: [e.g. Ubuntu 20.04]
- Browser: [e.g. Chrome 94]
- Python Version: [e.g. 3.9.7]
- Node.js Version: [e.g. 16.14.0]

## Additional Information
Any other information about the problem.
```

### ✨ Propose a Feature

**Feature proposal template:**

```markdown
## Feature Summary
Clear and concise description of the desired feature.

## Motivation
Why would this feature be useful? What problem does it solve?

## Detailed Description
Detailed description of the proposed feature.

## Considered Alternatives
What alternatives have you considered?

## Suggested Implementation
If you have ideas about implementation, share them here.
```

## 🔄 Contribution Process

### 1. Development

```bash
# Keep your branch up to date
git fetch upstream
git checkout main
git merge upstream/main
git checkout feature/my-new-feature
git rebase main

# Make your changes
# ...

# Add and commit
git add .
git commit -m "feat: add new feature X"
```

### 2. Tests

Make sure all tests pass:

```bash
# API tests
cd central-api
python -m pytest app/tests/ -v

# Frontend tests
cd ../web-interface
npm test

# P2P tests
cd ../node-client
python -m pytest tests/ -v
```

### 3. Code Format

We use automatic formatting tools:

```bash
# Python (API and Node Client)
pip install black isort
black .
isort .

# JavaScript/TypeScript (Web Interface)
npm run lint
npm run format
```

### 4. Commit Convention

We use the [Conventional Commits](https://www.conventionalcommits.org/) convention:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: new feature
- `fix`: bug fix
- `docs`: documentation changes
- `style`: changes that don't affect code (spaces, formatting, etc.)
- `refactor`: code change that neither fixes a bug nor adds a feature
- `perf`: code change that improves performance
- `test`: adding missing tests or correcting existing tests
- `chore`: changes to build tools or auxiliary libraries

**Examples:**
```bash
git commit -m "feat(api): add endpoint for node management"
git commit -m "fix(ui): fix mobile display bug"
git commit -m "docs: update installation guide"
git commit -m "test(p2p): add tests for peer discovery"
```

### 5. Pull Request

```bash
# Push your branch
git push origin feature/my-new-feature

# Open a Pull Request on GitHub
```

**Pull Request template:**

```markdown
## Description
Clear description of what this PR does.

## Type of Change
- [ ] Bug fix (change that fixes an issue)
- [ ] New feature (change that adds functionality)
- [ ] Breaking change (fix or feature that would break existing functionality)
- [ ] This change requires a documentation update

## Tests
- [ ] I have tested my changes locally
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Checklist
- [ ] My code follows the style conventions of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
```

## 📐 Code Standards

### Python
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints
- Document functions with docstrings
- Test with pytest

### JavaScript/TypeScript
- Use ESLint and Prettier
- Follow React/TypeScript conventions
- Document with JSDoc when necessary
- Test with Jest and React Testing Library

### Documentation
- Use Markdown
- Include code examples
- Maintain consistency with existing style

## 🏗️ Project Structure

```
O-Red/
├── docs/                    # Documentation
├── implementation/          # Main code
│   ├── central-api/        # FastAPI API
│   ├── node-client/        # P2P Client
│   ├── web-interface/      # React Interface
│   └── tests/              # Integration tests
├── scripts/                # Utility scripts
├── .github/                # GitHub templates
├── CONTRIBUTING.md         # This file
├── LICENSE                 # MIT License
└── README.md              # Main documentation
```

## 🎯 Development Priorities

### High Priority
- P2P network stability and robustness
- Security and cryptography
- Performance and scalability
- Tests and documentation

### Medium Priority
- New O-RedMind features
- Advanced user interface
- External service integrations

### Low Priority
- Cosmetic optimizations
- Experimental features

## 🏆 Recognition

Contributors are recognized in several ways:
- Mention in main README
- Contributor badge
- Access to contributors Discord channel
- Invitation to community events

## 🤔 Need Help?

- **[💬 GitHub Discussions](https://github.com/DiegoMoralesMagri/OpenRed/discussions)** - For general questions
- **[🐛 Issues](https://github.com/DiegoMoralesMagri/OpenRed/issues)** - For bugs and features
- **[💬 Discord](https://discord.gg/dEJ2eaU4)** - For real-time chat
- **[📧 Email](mailto:community@o-red.org)** - For sensitive questions

## 📜 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). We are committed to maintaining an open and welcoming environment for everyone.

---

**Thank you for contributing to O-Red! Together, let's build the future of the decentralized web. 🌟**

---

## Español

# 🤝 Guía de Contribución - O-Red

¡Gracias por tu interés en contribuir a O-Red! Este proyecto prospera gracias a su comunidad de contribuyentes apasionados que comparten nuestra visión de una web descentralizada y ética.

## 🌟 Cómo Contribuir

Hay muchas formas de contribuir a O-Red, sin importar tu nivel de experiencia:

### 🔧 Desarrollo
- Corregir bugs
- Añadir nuevas funcionalidades
- Mejorar el rendimiento
- Optimizar código existente
- Crear pruebas

### 📚 Documentación
- Mejorar la documentación existente
- Crear tutoriales
- Traducir a otros idiomas
- Corregir errores tipográficos
- Añadir ejemplos de código

### 🎨 Diseño y UX
- Mejorar la interfaz de usuario
- Crear mockups
- Optimizar la experiencia del usuario
- Diseñar iconos y visuales

### 🔒 Seguridad
- Identificar vulnerabilidades
- Realizar auditorías de seguridad
- Proponer mejoras de seguridad
- Probar la robustez del sistema

### 🌍 Comunidad
- Ayudar a nuevos usuarios
- Responder preguntas en los foros
- Organizar eventos
- Promover el proyecto

## 🚀 Inicio Rápido

### 1. Fork y Clonar

```bash
# Hacer fork del repositorio en GitHub, luego clonar tu fork
git clone https://github.com/TU_USUARIO/OpenRed.git
cd O-Red

# Añadir el repositorio original como remoto
git remote add upstream https://github.com/DiegoMoralesMagri/OpenRed.git
```

### 2. Configuración del Entorno

```bash
# Seguir la guía de instalación
cd implementation
# Ver GUIDE_TEST_LOCAL.md para instrucciones detalladas
```

### 3. Crear una Rama

```bash
# Crear una rama para tu contribución
git checkout -b feature/mi-nueva-funcionalidad
# O
git checkout -b fix/correccion-del-bug
# O
git checkout -b docs/mejora-documentacion
```

## 📋 Tipos de Contribuciones

### 🐛 Reportar un Bug

Antes de reportar un bug:
1. Verifica que no haya sido reportado ya en [Issues](https://github.com/DiegoMoralesMagri/OpenRed/issues)
2. Prueba con la última versión del código
3. Prepara un ejemplo reproducible

**Plantilla para reportar un bug:**

```markdown
## Descripción del Bug
Descripción clara y concisa del problema.

## Pasos para Reproducir
1. Ir a '...'
2. Hacer clic en '...'
3. Desplazarse hasta '...'
4. Ver el error

## Comportamiento Esperado
Descripción clara de lo que debería suceder.

## Capturas de Pantalla
Si aplica, añade capturas de pantalla.

## Entorno
- SO: [ej. Ubuntu 20.04]
- Navegador: [ej. Chrome 94]
- Versión de Python: [ej. 3.9.7]
- Versión de Node.js: [ej. 16.14.0]

## Información Adicional
Cualquier otra información sobre el problema.
```

### ✨ Proponer una Funcionalidad

**Plantilla para proponer una funcionalidad:**

```markdown
## Resumen de la Funcionalidad
Descripción clara y concisa de la funcionalidad deseada.

## Motivación
¿Por qué sería útil esta funcionalidad? ¿Qué problema resuelve?

## Descripción Detallada
Descripción detallada de la funcionalidad propuesta.

## Alternativas Consideradas
¿Qué alternativas has considerado?

## Implementación Sugerida
Si tienes ideas sobre la implementación, compártelas aquí.
```

## 🔄 Proceso de Contribución

### 1. Desarrollo

```bash
# Mantener tu rama actualizada
git fetch upstream
git checkout main
git merge upstream/main
git checkout feature/mi-nueva-funcionalidad
git rebase main

# Hacer tus cambios
# ...

# Añadir y hacer commit
git add .
git commit -m "feat: añadir nueva funcionalidad X"
```

### 2. Pruebas

Asegúrate de que todas las pruebas pasen:

```bash
# Pruebas de API
cd central-api
python -m pytest app/tests/ -v

# Pruebas de Frontend
cd ../web-interface
npm test

# Pruebas P2P
cd ../node-client
python -m pytest tests/ -v
```

### 3. Formato del Código

Utilizamos herramientas de formateo automático:

```bash
# Python (API y Node Client)
pip install black isort
black .
isort .

# JavaScript/TypeScript (Interfaz Web)
npm run lint
npm run format
```

### 4. Convención de Commits

Utilizamos la convención [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>[ámbito opcional]: <descripción>

[cuerpo opcional]

[pie(s) opcional(es)]
```

**Tipos:**
- `feat`: nueva funcionalidad
- `fix`: corrección de bug
- `docs`: cambios en documentación
- `style`: cambios que no afectan el código (espacios, formateo, etc.)
- `refactor`: cambio de código que ni corrige un bug ni añade funcionalidad
- `perf`: cambio de código que mejora el rendimiento
- `test`: añadir pruebas faltantes o corregir pruebas existentes
- `chore`: cambios a herramientas de build o librerías auxiliares

**Ejemplos:**
```bash
git commit -m "feat(api): añadir endpoint para gestión de nodos"
git commit -m "fix(ui): corregir bug de visualización en móvil"
git commit -m "docs: actualizar guía de instalación"
git commit -m "test(p2p): añadir pruebas para descubrimiento de pares"
```

### 5. Pull Request

```bash
# Empujar tu rama
git push origin feature/mi-nueva-funcionalidad

# Abrir un Pull Request en GitHub
```

**Plantilla de Pull Request:**

```markdown
## Descripción
Descripción clara de lo que hace este PR.

## Tipo de Cambio
- [ ] Corrección de bug (cambio que soluciona un problema)
- [ ] Nueva funcionalidad (cambio que añade funcionalidad)
- [ ] Cambio disruptivo (corrección o funcionalidad que rompería funcionalidad existente)
- [ ] Este cambio requiere una actualización de documentación

## Pruebas
- [ ] He probado mis cambios localmente
- [ ] He añadido pruebas que demuestran que mi corrección es efectiva o que mi funcionalidad funciona
- [ ] Las pruebas unitarias nuevas y existentes pasan localmente con mis cambios

## Lista de Verificación
- [ ] Mi código sigue las convenciones de estilo de este proyecto
- [ ] He realizado una auto-revisión de mi propio código
- [ ] He comentado mi código, particularmente en áreas difíciles de entender
- [ ] He realizado los cambios correspondientes a la documentación
- [ ] Mis cambios no generan nuevas advertencias
```

## 📐 Estándares de Código

### Python
- Seguir [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Usar type hints
- Documentar funciones con docstrings
- Probar con pytest

### JavaScript/TypeScript
- Usar ESLint y Prettier
- Seguir convenciones React/TypeScript
- Documentar con JSDoc cuando sea necesario
- Probar con Jest y React Testing Library

### Documentación
- Usar Markdown
- Incluir ejemplos de código
- Mantener consistencia con el estilo existente

## 🏗️ Estructura del Proyecto

```
O-Red/
├── docs/                    # Documentación
├── implementation/          # Código principal
│   ├── central-api/        # API FastAPI
│   ├── node-client/        # Cliente P2P
│   ├── web-interface/      # Interfaz React
│   └── tests/              # Pruebas de integración
├── scripts/                # Scripts utilitarios
├── .github/                # Plantillas GitHub
├── CONTRIBUTING.md         # Este archivo
├── LICENSE                 # Licencia MIT
└── README.md              # Documentación principal
```

## 🎯 Prioridades de Desarrollo

### Alta Prioridad
- Estabilidad y robustez de la red P2P
- Seguridad y criptografía
- Rendimiento y escalabilidad
- Pruebas y documentación

### Prioridad Media
- Nuevas funcionalidades O-RedMind
- Interfaz de usuario avanzada
- Integraciones con servicios externos

### Baja Prioridad
- Optimizaciones cosméticas
- Funcionalidades experimentales

## 🏆 Reconocimiento

Los contribuyentes son reconocidos de varias maneras:
- Mención en el README principal
- Insignia de contribuyente
- Acceso al canal Discord de contribuyentes
- Invitación a eventos de la comunidad

## 🤔 ¿Necesitas Ayuda?

- **[💬 Discusiones GitHub](https://github.com/DiegoMoralesMagri/OpenRed/discussions)** - Para preguntas generales
- **[🐛 Issues](https://github.com/DiegoMoralesMagri/OpenRed/issues)** - Para bugs y funcionalidades
- **[💬 Discord](https://discord.gg/dEJ2eaU4)** - Para chat en tiempo real
- **[📧 Email](mailto:community@o-red.org)** - Para preguntas sensibles

## 📜 Código de Conducta

Al participar en este proyecto, aceptas cumplir con nuestro [Código de Conducta](CODE_OF_CONDUCT.md). Nos comprometemos a mantener un ambiente abierto y acogedor para todos.

---

**¡Gracias por contribuir a O-Red! Juntos, construyamos el futuro de la web descentralizada. 🌟**

---

## 中文

# 🤝 贡献指南 - O-Red

感谢您对为O-Red做出贡献的兴趣！这个项目因其充满激情的贡献者社区而蓬勃发展，他们分享我们对去中心化和道德网络的愿景。

## 🌟 如何贡献

无论您的经验水平如何，都有很多方式可以为O-Red做出贡献：

### 🔧 开发
- 修复错误
- 添加新功能
- 提高性能
- 优化现有代码
- 创建测试

### 📚 文档
- 改进现有文档
- 创建教程
- 翻译成其他语言
- 修正拼写错误
- 添加代码示例

### 🎨 设计和用户体验
- 改进用户界面
- 创建模型
- 优化用户体验
- 设计图标和视觉效果

### 🔒 安全
- 识别漏洞
- 执行安全审核
- 提出安全改进建议
- 测试系统稳健性

### 🌍 社区
- 帮助新用户
- 在论坛上回答问题
- 组织活动
- 推广项目

## 🚀 快速开始

### 1. 分叉和克隆

```bash
# 在GitHub上分叉仓库，然后克隆您的分叉
git clone https://github.com/您的用户名/OpenRed.git
cd O-Red

# 添加原始仓库作为远程
git remote add upstream https://github.com/DiegoMoralesMagri/OpenRed.git
```

### 2. 环境设置

```bash
# 遵循安装指南
cd implementation
# 查看GUIDE_TEST_LOCAL.md获取详细说明
```

### 3. 创建分支

```bash
# 为您的贡献创建一个分支
git checkout -b feature/我的新功能
# 或者
git checkout -b fix/错误修正
# 或者
git checkout -b docs/文档改进
```

## 📋 贡献类型

### 🐛 报告错误

在报告错误之前：
1. 检查是否已在[Issues](https://github.com/DiegoMoralesMagri/OpenRed/issues)中报告
2. 使用最新版本的代码进行测试
3. 准备一个可重现的示例

**错误报告模板：**

```markdown
## 错误描述
问题的清晰简洁描述。

## 重现步骤
1. 转到'...'
2. 点击'...'
3. 滚动到'...'
4. 看到错误

## 预期行为
应该发生什么的清晰描述。

## 屏幕截图
如果适用，添加屏幕截图。

## 环境
- 操作系统：[例如Ubuntu 20.04]
- 浏览器：[例如Chrome 94]
- Python版本：[例如3.9.7]
- Node.js版本：[例如16.14.0]

## 附加信息
关于问题的任何其他信息。
```

### ✨ 提出功能

**功能提案模板：**

```markdown
## 功能摘要
所需功能的清晰简洁描述。

## 动机
为什么这个功能会有用？它解决了什么问题？

## 详细描述
提议功能的详细描述。

## 考虑的替代方案
您考虑过哪些替代方案？

## 建议的实现
如果您对实现有想法，请在此分享。
```

## 🔄 贡献流程

### 1. 开发

```bash
# 保持您的分支更新
git fetch upstream
git checkout main
git merge upstream/main
git checkout feature/我的新功能
git rebase main

# 进行更改
# ...

# 添加和提交
git add .
git commit -m "feat: 添加新功能X"
```

### 2. 测试

确保所有测试通过：

```bash
# API测试
cd central-api
python -m pytest app/tests/ -v

# 前端测试
cd ../web-interface
npm test

# P2P测试
cd ../node-client
python -m pytest tests/ -v
```

### 3. 代码格式

我们使用自动格式化工具：

```bash
# Python（API和Node Client）
pip install black isort
black .
isort .

# JavaScript/TypeScript（Web界面）
npm run lint
npm run format
```

### 4. 提交约定

我们使用[Conventional Commits](https://www.conventionalcommits.org/)约定：

```
<类型>[可选范围]: <描述>

[可选正文]

[可选页脚]
```

**类型：**
- `feat`：新功能
- `fix`：错误修复
- `docs`：文档更改
- `style`：不影响代码的更改（空格、格式等）
- `refactor`：既不修复错误也不添加功能的代码更改
- `perf`：提高性能的代码更改
- `test`：添加缺失的测试或更正现有测试
- `chore`：构建工具或辅助库的更改

**示例：**
```bash
git commit -m "feat(api): 添加节点管理端点"
git commit -m "fix(ui): 修复移动端显示错误"
git commit -m "docs: 更新安装指南"
git commit -m "test(p2p): 添加对等发现测试"
```

### 5. 拉取请求

```bash
# 推送您的分支
git push origin feature/我的新功能

# 在GitHub上开启拉取请求
```

**拉取请求模板：**

```markdown
## 描述
此PR做什么的清晰描述。

## 更改类型
- [ ] 错误修复（修复问题的更改）
- [ ] 新功能（添加功能的更改）
- [ ] 破坏性更改（会破坏现有功能的修复或功能）
- [ ] 此更改需要文档更新

## 测试
- [ ] 我已在本地测试了我的更改
- [ ] 我已添加证明我的修复有效或我的功能工作的测试
- [ ] 新的和现有的单元测试在我的更改下本地通过

## 检查清单
- [ ] 我的代码遵循此项目的样式约定
- [ ] 我已对我自己的代码进行了自我审查
- [ ] 我已注释了我的代码，特别是在难以理解的区域
- [ ] 我已对文档进行了相应更改
- [ ] 我的更改不产生新的警告
```

## 📐 代码标准

### Python
- 遵循[PEP 8](https://www.python.org/dev/peps/pep-0008/)
- 使用类型提示
- 使用docstrings记录函数
- 使用pytest测试

### JavaScript/TypeScript
- 使用ESLint和Prettier
- 遵循React/TypeScript约定
- 必要时使用JSDoc记录
- 使用Jest和React Testing Library测试

### 文档
- 使用Markdown
- 包含代码示例
- 保持与现有样式的一致性

## 🏗️ 项目结构

```
O-Red/
├── docs/                    # 文档
├── implementation/          # 主要代码
│   ├── central-api/        # FastAPI API
│   ├── node-client/        # P2P客户端
│   ├── web-interface/      # React界面
│   └── tests/              # 集成测试
├── scripts/                # 实用脚本
├── .github/                # GitHub模板
├── CONTRIBUTING.md         # 此文件
├── LICENSE                 # MIT许可证
└── README.md              # 主要文档
```

## 🎯 开发优先级

### 高优先级
- P2P网络稳定性和稳健性
- 安全和密码学
- 性能和可扩展性
- 测试和文档

### 中等优先级
- 新的O-RedMind功能
- 高级用户界面
- 外部服务集成

### 低优先级
- 外观优化
- 实验性功能

## 🏆 认可

贡献者会通过以下几种方式得到认可：
- 在主README中提及
- 贡献者徽章
- 访问贡献者Discord频道
- 邀请参加社区活动

## 🤔 需要帮助？

- **[💬 GitHub讨论](https://github.com/DiegoMoralesMagri/OpenRed/discussions)** - 用于一般问题
- **[🐛 Issues](https://github.com/DiegoMoralesMagri/OpenRed/issues)** - 用于错误和功能
- **[💬 Discord](https://discord.gg/dEJ2eaU4)** - 用于实时聊天
- **[📧 邮箱](mailto:community@o-red.org)** - 用于敏感问题

## 📜 行为准则

通过参与此项目，您同意遵守我们的[行为准则](CODE_OF_CONDUCT.md)。我们致力于为每个人维护一个开放和欢迎的环境。

---

**感谢您为O-Red做出贡献！让我们一起构建去中心化网络的未来。🌟**

---

🌐 **Navigation Multilingue** | **Multilingual Navigation**
- [🇫🇷 Français](#français) | [🇺🇸 English](#english) | [🇪🇸 Español](#español) | [🇨🇳 中文](#中文)

**O-Red Contributing Guide** - Ensemble pour contribuer | Together to contribute | Juntos para contribuir | 一起贡献
