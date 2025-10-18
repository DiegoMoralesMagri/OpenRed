#!/bin/bash
# 🔧 OpenRed - Correctif .htaccess pour hébergement mutualisé
# Résout les problèmes de permissions 403 Forbidden

echo "🔧 OpenRed - Correctif .htaccess"
echo "================================"

# Sauvegarde de l'ancien .htaccess
if [ -f ".htaccess" ]; then
    cp .htaccess .htaccess.backup
    echo "✅ Sauvegarde créée: .htaccess.backup"
fi

# Création du nouveau .htaccess compatible
cat > .htaccess << 'EOF'
# OpenRed - Configuration compatible hébergement mutualisé
# Version corrigée pour O2Switch

# Page d'accueil
DirectoryIndex index.html

# Configuration MIME
AddType application/json .json
AddType text/html .html

# Protection des fichiers sensibles
<Files "*.json">
    Order Allow,Deny
    Deny from all
</Files>

<Files "*.md">
    Order Allow,Deny
    Deny from all
</Files>

# Accès autorisé aux fichiers web
<Files "index.html">
    Order Allow,Deny
    Allow from all
</Files>

<Files "*.css">
    Order Allow,Deny
    Allow from all
</Files>

<Files "*.js">
    Order Allow,Deny
    Allow from all
</Files>
EOF

echo "✅ Nouveau .htaccess créé"

# Correction des permissions
chmod 644 .htaccess
echo "✅ Permissions .htaccess corrigées (644)"

# Correction des permissions des fichiers
if [ -f "index.html" ]; then
    chmod 644 index.html
    echo "✅ Permissions index.html corrigées"
fi

# Correction du dossier app s'il existe
if [ -d "app" ]; then
    chmod 755 app
    chmod 644 app/*
    echo "✅ Permissions dossier app corrigées"
fi

echo ""
echo "🎉 Correctif appliqué avec succès !"
echo "🌐 Testez maintenant: http://votre-domaine.com"
echo ""
echo "📋 Si le problème persiste:"
echo "   1. Supprimez le .htaccess: rm .htaccess"
echo "   2. Testez sans .htaccess"
echo "   3. Contactez le support O2Switch si nécessaire"