#!/bin/bash
# 🌐 OpenRed Social Platform - Installation pour Hébergement Mutualisé
# Installe la plateforme sociale complète avec login, profils, amis, chat

echo "🌐 OpenRed Social Platform - Installation"
echo "======================================="

# Variables
URL="https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/openred-social-hosting.zip"
ZIP="openred-social.zip"

echo "📥 Téléchargement de la plateforme sociale..."
if curl -L -o "$ZIP" "$URL" 2>/dev/null || wget -O "$ZIP" "$URL" 2>/dev/null; then
    echo "✅ Téléchargement réussi ($(du -h "$ZIP" | cut -f1))"
else
    echo "❌ Échec du téléchargement"
    exit 1
fi

echo "📦 Extraction de la plateforme..."
if unzip -q "$ZIP" 2>/dev/null; then
    echo "✅ Extraction réussie"
    rm -f "$ZIP"
else
    echo "❌ Échec de l'extraction"
    exit 1
fi

echo "🔧 Configuration des permissions..."
# Créer le dossier data pour les utilisateurs
mkdir -p data
chmod 755 data
chmod 644 *.html *.php 2>/dev/null
chmod 755 api/ 2>/dev/null
chmod 644 api/*.php 2>/dev/null

echo ""
echo "🎉 OpenRed Social Platform installé avec succès !"
echo "================================================"
echo ""
echo "🌐 Fonctionnalités disponibles :"
echo "  🔐 Système de connexion sécurisé"
echo "  👤 Profils utilisateurs personnalisables"
echo "  👥 Gestion d'amis et demandes"
echo "  💬 Chat en temps réel P2P"
echo "  🌐 Découverte de nœuds du réseau"
echo ""
echo "🚀 Accédez à votre plateforme :"
echo "   http://votre-domaine.com$(pwd | sed 's|'$HOME'||')"
echo ""
echo "📋 Première utilisation :"
echo "   1. Visitez votre site"
echo "   2. Créez un compte utilisateur"
echo "   3. Explorez les fonctionnalités sociales"
echo ""
echo "📖 Documentation complète :"
echo "   https://github.com/DiegoMoralesMagri/OpenRed"