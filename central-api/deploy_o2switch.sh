#!/bin/bash
# Script de déploiement pour O2Switch
# Deployment script for O2Switch

echo "🚀 Déploiement OpenRed Central API sur O2Switch"
echo "🚀 Deploying OpenRed Central API on O2Switch"

# Vérifier Python
echo "📍 Vérification de Python..."
python3 --version
which python3

# Solution 1: Utiliser virtualenv
echo "📦 Installation de virtualenv..."
pip3 install --user virtualenv

# Créer l'environnement virtuel avec virtualenv
echo "🔧 Création de l'environnement virtuel..."
python3 -m virtualenv venv

# Ou bien, utiliser cette alternative si la première ne marche pas:
# virtualenv -p python3 venv

echo "✅ Environnement virtuel créé avec succès"
