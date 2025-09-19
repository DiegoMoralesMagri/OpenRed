# 🤝 Contribution Guide - O-Red

Thank you for your interest in contributing to O-Red! This project thrives because of its community of passionate contributors who share our vision for a decentralized and ethical web.

## 🌟 How to Contribute

There are many ways to contribute to O-Red, whatever your experience level:

### 🔧 Development
- Fix bugs
- Add new features
- Improve performance
- Refactor existing code
- Create tests

### 📚 Documentation
- Improve existing documentation
- Write tutorials
- Translate into other languages
- Fix typos
- Add code examples

### 🎨 Design & UX
- Improve the user interface
- Create mockups
- Optimize user experience
- Design icons and visuals

### 🔒 Security
- Identify vulnerabilities
- Conduct security audits
- Propose security improvements
- Test system robustness

### 🌍 Community
- Help new users
- Answer questions on forums
- Organize events
- Promote the project

## 🚀 Quick Start

### 1. Fork & Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/O-Red.git
cd O-Red

# Add the original repository as a remote
git remote add upstream https://github.com/OriginalOwner/O-Red.git
```

### 2. Set Up Your Environment

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
git checkout -b fix/bug-fix
# OR
git checkout -b docs/improve-documentation
```

## 📋 Types of Contributions

### 🐛 Report a Bug

Before reporting a bug:
1. Check whether it has already been reported in the [Issues](https://github.com/[USERNAME]/O-Red/issues)
2. Test with the latest code
3. Prepare a reproducible example

**Bug report template:**

```markdown
## Bug Description
A clear and concise description of the problem.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll to '...'
4. See the error

## Expected Behavior
A clear description of what should happen.

## Screenshots
If applicable, add screenshots.

## Environment
- OS: [e.g. Ubuntu 20.04]
- Browser: [e.g. Chrome 94]
- Python version: [e.g. 3.9.7]
- Node.js version: [e.g. 16.14.0]

## Additional Information
Any other information about the problem.
```

### ✨ Propose a Feature

**Feature request template:**

```markdown
## Feature Summary
A clear and concise description of the requested feature.

## Motivation
Why is this feature useful? What problem does it solve?

## Detailed Description
A detailed description of the proposed feature.

## Alternatives Considered
What alternatives did you consider?

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

# Stage and commit
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

### 3. Code Formatting

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

We follow the [Conventional Commits](https://www.conventionalcommits.org/) convention:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: new feature
- `fix`: bug fix
- `docs`: documentation changes
- `style`: changes that do not affect code (whitespace, formatting, etc.)
- `refactor`: code change that neither fixes a bug nor adds a feature
- `perf`: code change that improves performance
- `test`: adding missing tests or correcting existing tests
- `chore`: changes to build tools or auxiliary libraries

**Examples:**
```bash
git commit -m "feat(api): add node management endpoint"
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
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes do not generate new warnings
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
- Document with JSDoc when appropriate
- Test with Jest and React Testing Library

### Documentation
- Use Markdown
- Include code examples
- Keep consistency with existing style

## 🏗️ Project Structure

```
O-Red/
├── docs/                    # Documentation
├── implementation/          # Core code
│   ├── central-api/         # FastAPI API
│   ├── node-client/         # P2P client
│   ├── web-interface/       # React interface
│   └── tests/               # Integration tests
├── scripts/                 # Utility scripts
├── .github/                 # GitHub templates
├── CONTRIBUTING.md         # This file
├── LICENSE                 # MIT License
└── README.md               # Main documentation
```

## 🎯 Development Priorities

### High Priority
- P2P network stability and robustness
- Security and cryptography
- Performance and scalability
- Testing and documentation

### Medium Priority
- New O-RedMind features
- Advanced UI
- Integrations with external services

### Low Priority
- Cosmetic optimizations
- Experimental features

## 🏆 Recognition

Contributors are recognized in several ways:
- Mention in the main README
- Contributor badge
- Access to the contributors' Discord channel
- Invitations to community events

## 🤔 Need Help?

- **[💬 GitHub Discussions](https://github.com/[USERNAME]/O-Red/discussions)** - For general questions
- **[🐛 Issues](https://github.com/[USERNAME]/O-Red/issues)** - For bugs and features
- **[💬 Discord](https://discord.gg/ored)** - For real-time chat
- **[📧 Email](mailto:community@ored.org)** - For sensitive questions

## 📜 Code of Conduct

By participating in this project you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). We are committed to maintaining an open and welcoming environment for everyone.

---

**Thanks for contributing to O-Red! Together, let's build the future of the decentralized web. 🌟**
