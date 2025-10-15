#!/usr/bin/env python3
"""
🚀 OpenRed Quick Demo
Démo rapide du système de déploiement
"""

import os
import time
import subprocess
import sys

def print_banner():
    """Affichage du banner OpenRed"""
    banner = """
    ╭─────────────────────────────────────────╮
    │           🚀 OpenRed Demo               │
    │    Système de déploiement universel     │
    ╰─────────────────────────────────────────╯
    """
    print(banner)

def check_environment():
    """Vérifier l'environnement"""
    print("🔍 Vérification de l'environnement...")
    
    # Vérifier Python
    python_version = sys.version_info
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Vérifier les fichiers de déploiement
    required_files = [
        "universal_installer.py",
        "create_simple_package.py", 
        "install_o2switch.py",
        "install.sh",
        "INSTALLATION_GUIDE.md"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} manquant")
            missing_files.append(file)
    
    return len(missing_files) == 0

def generate_package():
    """Générer un package de déploiement"""
    print("\n📦 Génération du package de déploiement...")
    
    try:
        result = subprocess.run([sys.executable, "create_simple_package.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Package généré avec succès !")
            print(result.stdout)
            
            # Chercher le fichier généré
            for file in os.listdir("."):
                if file.startswith("openred_simple_") and file.endswith(".zip"):
                    size = os.path.getsize(file) / 1024
                    print(f"📁 Fichier : {file} ({size:.1f} KB)")
                    return file
        else:
            print("❌ Erreur lors de la génération :")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
    
    return None

def show_deployment_options():
    """Afficher les options de déploiement"""
    print("\n🚀 OPTIONS DE DÉPLOIEMENT DISPONIBLES :")
    print("=" * 50)
    
    options = [
        ("1", "Package ZIP", "Upload via FTP/cPanel (Recommandé)"),
        ("2", "Script Bash", "Installation automatique Linux"),
        ("3", "O2Switch", "Installation spécialisée O2Switch"),
        ("4", "Universel", "Auto-détection hébergeur"),
        ("5", "Documentation", "Guide complet d'installation")
    ]
    
    for num, name, desc in options:
        print(f"{num}. 🎯 {name:12} : {desc}")

def show_hosting_compatibility():
    """Afficher la compatibilité hébergeurs"""
    print("\n🌐 COMPATIBILITÉ HÉBERGEURS :")
    print("=" * 40)
    
    hosts = [
        ("O2Switch", "✅ Support natif"),
        ("OVH", "✅ Configuration automatique"),
        ("Hostinger", "✅ Compatible"),
        ("1&1/IONOS", "✅ Support standard"),
        ("Gandi", "✅ Configuration personnalisée"),
        ("VPS/Dédiés", "✅ Apache + Nginx"),
        ("Autres", "✅ Détection automatique")
    ]
    
    for host, status in hosts:
        print(f"🏢 {host:12} : {status}")

def main():
    """Fonction principale"""
    print_banner()
    
    # Vérifier l'environnement
    if not check_environment():
        print("\n❌ Environnement incomplet")
        print("🔧 Vérifiez que tous les fichiers sont présents")
        return
    
    print("\n✅ Environnement validé !")
    
    # Générer un package de démonstration
    package_file = generate_package()
    
    # Afficher les options
    show_deployment_options()
    show_hosting_compatibility()
    
    print("\n🎉 SYSTÈME PRÊT POUR DÉPLOIEMENT !")
    print("=" * 50)
    
    if package_file:
        print(f"📦 Package prêt : {package_file}")
        print("🌐 Uploadez ce fichier sur votre hébergeur")
        print("✅ Décompressez dans le répertoire web")
        print("🚀 Accédez à http://votre-domaine.com/openred")
    
    print("\n📚 Documentation complète : INSTALLATION_GUIDE.md")
    print("🧪 Tests disponibles : bash test_deployment.sh")

if __name__ == "__main__":
    main()