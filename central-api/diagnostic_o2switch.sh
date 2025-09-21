#!/bin/bash
# Script de diagnostic et installation pour O2Switch
# Diagnostic and installation script for O2Switch

echo "🔍 Diagnostic Python/Pip sur O2Switch"
echo "🔍 Python/Pip diagnostic on O2Switch"

echo ""
echo "=== 1. RECHERCHE DES VERSIONS PYTHON DISPONIBLES ==="
echo "Looking for available Python versions..."

# Test différentes versions de Python
for python_cmd in python3.11 python3.10 python3.9 python3.8 python3 python python2.7; do
    if command -v $python_cmd &> /dev/null; then
        version=$($python_cmd --version 2>&1)
        echo "✅ $python_cmd trouvé: $version"
        echo "   Chemin: $(which $python_cmd)"
    fi
done

echo ""
echo "=== 2. RECHERCHE DES VERSIONS PIP DISPONIBLES ==="
echo "Looking for available Pip versions..."

# Test différentes versions de pip
for pip_cmd in pip3.11 pip3.10 pip3.9 pip3.8 pip3 pip pip2.7; do
    if command -v $pip_cmd &> /dev/null; then
        version=$($pip_cmd --version 2>&1)
        echo "✅ $pip_cmd trouvé: $version"
        echo "   Chemin: $(which $pip_cmd)"
    fi
done

echo ""
echo "=== 3. RECHERCHE DANS LES CHEMINS COURANTS O2SWITCH ==="
echo "Looking in common O2Switch paths..."

# Chemins courants sur O2Switch
common_paths=(
    "/usr/bin"
    "/usr/local/bin"
    "/opt/cpanel/ea-python311/bin"
    "/opt/cpanel/ea-python310/bin"
    "/opt/cpanel/ea-python39/bin"
    "/opt/cpanel/ea-python38/bin"
    "/home/$(whoami)/bin"
    "/home/$(whoami)/.local/bin"
)

for path in "${common_paths[@]}"; do
    if [ -d "$path" ]; then
        echo "📁 Contenu de $path:"
        ls -la "$path" | grep -E "(python|pip)" || echo "   Aucun python/pip trouvé"
    fi
done

echo ""
echo "=== 4. VARIABLES D'ENVIRONNEMENT ==="
echo "Environment variables..."
echo "PATH: $PATH"
echo "USER: $(whoami)"
echo "HOME: $HOME"
echo "PWD: $(pwd)"

echo ""
echo "=== 5. TENTATIVES D'INSTALLATION ALTERNATIVE ==="
echo "Alternative installation attempts..."

# Essayer d'installer pip via ensurepip
echo "Tentative 1: Installation via ensurepip..."
python3 -m ensurepip --user 2>/dev/null && echo "✅ ensurepip réussi" || echo "❌ ensurepip échoué"

# Essayer de télécharger get-pip.py
echo "Tentative 2: Téléchargement de get-pip.py..."
if command -v wget &> /dev/null; then
    wget -q https://bootstrap.pypa.io/get-pip.py -O get-pip.py
    if [ -f "get-pip.py" ]; then
        echo "✅ get-pip.py téléchargé"
        python3 get-pip.py --user 2>/dev/null && echo "✅ Installation pip réussie" || echo "❌ Installation pip échouée"
    fi
elif command -v curl &> /dev/null; then
    curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    if [ -f "get-pip.py" ]; then
        echo "✅ get-pip.py téléchargé via curl"
        python3 get-pip.py --user 2>/dev/null && echo "✅ Installation pip réussie" || echo "❌ Installation pip échouée"
    fi
else
    echo "❌ Ni wget ni curl disponible"
fi

echo ""
echo "=== 6. TEST DES MODULES PYTHON INTÉGRÉS ==="
echo "Testing built-in Python modules..."

python3 -c "
import sys
print('Python executable:', sys.executable)
print('Python version:', sys.version)
print('Python path:', sys.path)

# Test des modules disponibles
modules_to_test = ['os', 'sys', 'json', 'urllib', 'sqlite3', 'http.server']
for module in modules_to_test:
    try:
        __import__(module)
        print(f'✅ Module {module} disponible')
    except ImportError:
        print(f'❌ Module {module} non disponible')
"

echo ""
echo "=== 7. RECOMMANDATIONS ==="
echo "Recommendations..."

echo "Si aucun pip n'est trouvé, contactez O2Switch pour:"
echo "1. Activer Python dans votre cPanel"
echo "2. Installer pip dans votre environnement"
echo "3. Ou utilisez leur interface Python App"
echo ""
echo "Alternatives sans pip:"
echo "- Utiliser uniquement les modules Python intégrés"
echo "- Télécharger les packages manuellement"
echo "- Demander l'installation à O2Switch"
