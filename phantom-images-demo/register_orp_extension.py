#!/usr/bin/env python3
"""
Association d'Extension OpenRed Phantom (.orp)
==============================================
Script pour associer l'extension .orp au viewer dans Windows.
"""

import os
import sys
import winreg
from pathlib import Path
import subprocess

def register_orp_extension():
    """Enregistre l'extension .orp dans Windows"""
    
    # Chemins
    current_dir = Path(__file__).parent
    viewer_path = current_dir / "orp_viewer.py"  # Viewer principal (ex-WebSocket transition)
    python_exe = sys.executable
    
    if not viewer_path.exists():
        print("❌ Erreur: orp_viewer.py non trouvé")
        return False
    
    try:
        # Clé pour l'extension .orp
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\.orp") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "OpenRedPhantom")
        
        # Clé pour le type de fichier
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OpenRedPhantom") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Fichier OpenRed PHANTOM (URN + WebSocket Support)")
        
        # Icône (optionnel)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OpenRedPhantom\DefaultIcon") as key:
            # Utiliser icône Python par défaut
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f"{python_exe},0")
        
        # Commande d'ouverture
        command = f'"{python_exe}" "{viewer_path}" "%1"'
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OpenRedPhantom\shell\open\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
        
        print("✅ Extension .orp associée avec succès !")
        print(f"📂 Viewer: {viewer_path}")
        print(f"🐍 Python: {python_exe}")
        print(f"💻 Commande: {command}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'association: {e}")
        return False

def unregister_orp_extension():
    """Supprime l'association .orp"""
    try:
        # Supprimer les clés
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\.orp")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OpenRedPhantom\shell\open\command")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OpenRedPhantom\shell\open")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OpenRedPhantom\shell")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OpenRedPhantom\DefaultIcon")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OpenRedPhantom")
        
        print("✅ Association .orp supprimée")
        return True
        
    except FileNotFoundError:
        print("⚠️  Association .orp déjà supprimée")
        return True
    except Exception as e:
        print(f"❌ Erreur suppression: {e}")
        return False

def test_association():
    """Teste l'association en créant un fichier .orp de test"""
    try:
        from orp_format import OrpFormat
        
        # Créer fichier test
        orp = OrpFormat.create_phantom_file(
            phantom_id="test_association",
            phantom_name="Test Association .orp",
            server_url="ws://localhost:8001",
            phantom_size=(300, 200)
        )
        
        test_file = Path("test_association.orp")
        orp.save_to_file(test_file)
        
        print(f"📄 Fichier test créé: {test_file}")
        print("🖱️  Double-cliquez dessus pour tester l'association")
        
        # Optionnel: ouvrir automatiquement
        choice = input("Ouvrir le fichier test maintenant ? (o/n): ")
        if choice.lower() == 'o':
            os.startfile(str(test_file))
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création fichier test: {e}")
        return False

def main():
    """Menu principal"""
    print("🔧 ASSOCIATION EXTENSION .ORP")
    print("=" * 35)
    print("1. Associer l'extension .orp")
    print("2. Supprimer l'association")
    print("3. Tester l'association")
    print("4. Quitter")
    
    while True:
        choice = input("\nChoisissez une option (1-4): ")
        
        if choice == '1':
            if register_orp_extension():
                print("\n🎉 L'extension .orp est maintenant associée !")
                print("Vous pouvez double-cliquer sur les fichiers .orp pour les ouvrir.")
            break
            
        elif choice == '2':
            if unregister_orp_extension():
                print("\n🗑️  Association .orp supprimée")
            break
            
        elif choice == '3':
            test_association()
            break
            
        elif choice == '4':
            print("Au revoir !")
            break
            
        else:
            print("❌ Option invalide")

if __name__ == "__main__":
    # Vérifier Windows
    if os.name != 'nt':
        print("❌ Ce script fonctionne uniquement sous Windows")
        print("💡 Sous Linux/macOS, utilisez les outils système pour associer .orp à orp_viewer.py")
        sys.exit(1)
    
    main()