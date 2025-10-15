#!/bin/bash
# 🌐 OpenRed - Installation SIMPLE pour Hébergement Mutualisé
# Version minimaliste garantie de fonctionner

echo "🌐 OpenRed - Installation Simple"
echo "================================"

# Variables
URL="https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/openred-shared-hosting.zip"
ZIP="openred.zip"

echo "📥 Téléchargement..."
if curl -L -o "$ZIP" "$URL" 2>/dev/null || wget -O "$ZIP" "$URL" 2>/dev/null; then
    echo "✅ Téléchargement réussi"
else
    echo "❌ Échec du téléchargement"
    exit 1
fi

echo "📦 Extraction..."
if unzip -q "$ZIP" 2>/dev/null; then
    echo "✅ Extraction réussie"
    rm -f "$ZIP"
else
    echo "❌ Échec de l'extraction"
    exit 1
fi

echo ""
echo "🎉 OpenRed installé avec succès !"
echo "📁 Répertoire: $(pwd)"
echo "🌐 Testez: http://votre-domaine.com$(pwd | sed 's|'$HOME'||')"
echo ""
echo "📖 Documentation: https://github.com/DiegoMoralesMagri/OpenRed"