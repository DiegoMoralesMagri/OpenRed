#!/usr/bin/env python3
"""
📝 OpenRed Network - Enregistrement Protocole Système
Enregistrement du protocole orp:// dans le système d'exploitation
"""

import os
import sys
import winreg
import subprocess
from typing import Dict, Optional, Tuple
from pathlib import Path


class EnregistreurProtocole:
    """
    📝 Enregistreur de protocole orp:// dans le système
    """
    
    def __init__(self):
        self.nom_protocole = "orp"
        self.description = "OpenRed Network Protocol"
        self.executable_python = sys.executable
        self.script_handler = self._obtenir_chemin_handler()
    
    def _obtenir_chemin_handler(self) -> str:
        """Obtient le chemin du script handler"""
        # Chemin du script handler dans le même dossier
        dossier_module = Path(__file__).parent
        return str(dossier_module / "orp_handler.py")
    
    def enregistrer_protocole_windows(self) -> bool:
        """
        📝 Enregistre le protocole orp:// dans Windows Registry
        """
        try:
            if not sys.platform.startswith('win'):
                print("❌ Enregistrement Windows uniquement supporté sur Windows")
                return False
            
            print("📝 Enregistrement protocole orp:// dans Windows...")
            
            # Clé racine du protocole
            cle_protocole = f"SOFTWARE\\Classes\\{self.nom_protocole}"
            
            # Création/ouverture clé protocole
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cle_protocole) as key:
                # Description du protocole
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, self.description)
                winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")
            
            # Icône (optionnel)
            cle_icone = f"{cle_protocole}\\DefaultIcon"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cle_icone) as key:
                # Utilise l'icône Python par défaut
                icone_path = f"{self.executable_python},0"
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, icone_path)
            
            # Commande d'ouverture
            cle_commande = f"{cle_protocole}\\shell\\open\\command"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cle_commande) as key:
                # Commande : python handler.py "%1"
                commande = f'"{self.executable_python}" "{self.script_handler}" "%1"'
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, commande)
            
            print("✅ Protocole orp:// enregistré avec succès dans Windows")
            return True
            
        except Exception as e:
            print(f"❌ Erreur enregistrement Windows: {e}")
            return False
    
    def desinscrire_protocole_windows(self) -> bool:
        """
        🗑️ Désinscrit le protocole orp:// de Windows Registry
        """
        try:
            if not sys.platform.startswith('win'):
                return False
            
            print("🗑️ Désinscription protocole orp:// de Windows...")
            
            cle_protocole = f"SOFTWARE\\Classes\\{self.nom_protocole}"
            
            # Suppression récursive de la clé
            self._supprimer_cle_recursive(winreg.HKEY_CURRENT_USER, cle_protocole)
            
            print("✅ Protocole orp:// désinscrit avec succès")
            return True
            
        except Exception as e:
            print(f"❌ Erreur désinscription Windows: {e}")
            return False
    
    def _supprimer_cle_recursive(self, cle_parent, nom_cle: str):
        """Supprime une clé registry et toutes ses sous-clés"""
        try:
            with winreg.OpenKey(cle_parent, nom_cle) as key:
                # Énumération et suppression des sous-clés
                sous_cles = []
                i = 0
                while True:
                    try:
                        sous_cle = winreg.EnumKey(key, i)
                        sous_cles.append(sous_cle)
                        i += 1
                    except WindowsError:
                        break
                
                # Suppression récursive des sous-clés
                for sous_cle in sous_cles:
                    self._supprimer_cle_recursive(key, sous_cle)
            
            # Suppression de la clé elle-même
            winreg.DeleteKey(cle_parent, nom_cle)
            
        except Exception:
            pass  # Clé n'existe peut-être pas
    
    def verifier_enregistrement_windows(self) -> bool:
        """
        ✅ Vérifie si le protocole est enregistré dans Windows
        """
        try:
            if not sys.platform.startswith('win'):
                return False
            
            cle_protocole = f"SOFTWARE\\Classes\\{self.nom_protocole}"
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, cle_protocole) as key:
                # Vérification valeurs essentielles
                description = winreg.QueryValueEx(key, "")[0]
                url_protocol = winreg.QueryValueEx(key, "URL Protocol")[0]
                
                return description == self.description
                
        except Exception:
            return False
    
    def enregistrer_protocole_linux(self) -> bool:
        """
        🐧 Enregistre le protocole orp:// sous Linux
        """
        try:
            if not sys.platform.startswith('linux'):
                print("❌ Enregistrement Linux uniquement supporté sur Linux")
                return False
            
            print("🐧 Enregistrement protocole orp:// sous Linux...")
            
            # Création fichier .desktop
            desktop_content = f"""[Desktop Entry]
Name=OpenRed Network Protocol Handler
Exec={self.executable_python} {self.script_handler} %u
Icon=network-workgroup
StartupNotify=true
NoDisplay=true
MimeType=x-scheme-handler/{self.nom_protocole};
"""
            
            # Chemin fichier .desktop
            home = os.path.expanduser("~")
            desktop_file = f"{home}/.local/share/applications/{self.nom_protocole}-handler.desktop"
            
            # Écriture fichier .desktop
            os.makedirs(os.path.dirname(desktop_file), exist_ok=True)
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
            
            # Rendre exécutable
            os.chmod(desktop_file, 0o755)
            
            # Enregistrement du handler MIME
            subprocess.run([
                'xdg-mime', 'default', 
                f'{self.nom_protocole}-handler.desktop', 
                f'x-scheme-handler/{self.nom_protocole}'
            ], check=True)
            
            print("✅ Protocole orp:// enregistré avec succès sous Linux")
            return True
            
        except Exception as e:
            print(f"❌ Erreur enregistrement Linux: {e}")
            return False
    
    def enregistrer_protocole_macos(self) -> bool:
        """
        🍎 Enregistre le protocole orp:// sous macOS
        """
        try:
            if not sys.platform.startswith('darwin'):
                print("❌ Enregistrement macOS uniquement supporté sur macOS")
                return False
            
            print("🍎 Enregistrement protocole orp:// sous macOS...")
            
            # TODO: Implémentation macOS
            # - Création d'une app bundle
            # - Modification Info.plist
            # - Enregistrement CFBundleURLTypes
            
            print("⚠️ Enregistrement macOS non encore implémenté")
            return False
            
        except Exception as e:
            print(f"❌ Erreur enregistrement macOS: {e}")
            return False
    
    def enregistrer_protocole_auto(self) -> bool:
        """
        🎯 Enregistrement automatique selon la plateforme
        """
        if sys.platform.startswith('win'):
            return self.enregistrer_protocole_windows()
        elif sys.platform.startswith('linux'):
            return self.enregistrer_protocole_linux()
        elif sys.platform.startswith('darwin'):
            return self.enregistrer_protocole_macos()
        else:
            print(f"❌ Plateforme non supportée: {sys.platform}")
            return False
    
    def verifier_enregistrement(self) -> Dict[str, any]:
        """
        🔍 Vérifie l'état d'enregistrement du protocole
        """
        etat = {
            'plateforme': sys.platform,
            'protocole_enregistre': False,
            'handler_existe': os.path.exists(self.script_handler),
            'python_executable': self.executable_python,
            'details': {}
        }
        
        if sys.platform.startswith('win'):
            etat['protocole_enregistre'] = self.verifier_enregistrement_windows()
            etat['details']['registry_key'] = f"HKEY_CURRENT_USER\\SOFTWARE\\Classes\\{self.nom_protocole}"
        
        return etat
    
    def creer_script_handler(self) -> bool:
        """
        📄 Crée le script handler pour URLs orp://
        """
        try:
            handler_content = '''#!/usr/bin/env python3
"""
🎯 OpenRed Network - Handler URL orp://
Script appelé par le système pour traiter les URLs orp://
"""

import sys
import os

# Ajout du chemin du module OpenRed
script_dir = os.path.dirname(os.path.abspath(__file__))
openred_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, openred_dir)


def main():
    """Fonction principale du handler"""
    if len(sys.argv) < 2:
        print("❌ Usage: orp_handler.py <url_orp>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    try:
        # Import du gestionnaire de protocole
        from modules.protocole import GestionnaireProtocole
        
        print(f"🌐 Handler orp:// appelé avec: {url}")
        
        # Traitement de l'URL
        gestionnaire = GestionnaireProtocole()
        resultat = gestionnaire.traiter_url(url)
        
        if resultat:
            print("✅ URL traitée avec succès")
            sys.exit(0)
        else:
            print("❌ Échec traitement URL")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erreur handler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
            
            # Écriture du script handler
            with open(self.script_handler, 'w', encoding='utf-8') as f:
                f.write(handler_content)
            
            # Rendre exécutable sur Unix
            if not sys.platform.startswith('win'):
                os.chmod(self.script_handler, 0o755)
            
            print(f"✅ Script handler créé: {self.script_handler}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur création handler: {e}")
            return False
    
    def installation_complete(self) -> bool:
        """
        🎯 Installation complète du protocole orp://
        """
        print("🚀 Installation complète du protocole orp://")
        print("=" * 50)
        
        # 1. Création du script handler
        if not self.creer_script_handler():
            return False
        
        # 2. Enregistrement du protocole
        if not self.enregistrer_protocole_auto():
            return False
        
        # 3. Vérification
        etat = self.verifier_enregistrement()
        if etat['protocole_enregistre']:
            print("🎉 Installation protocole orp:// terminée avec succès !")
            print(f"🔗 Testez avec: orp://fort_1234567890abcdef.openred/")
            return True
        else:
            print("❌ Échec installation protocole")
            return False
    
    def obtenir_chemin_handler(self) -> str:
        """
        Retourne le chemin complet vers le script handler
        
        Returns:
            Chemin absolu vers orp_handler.py
        """
        return self.script_handler


def installer_protocole_orp() -> bool:
    """
    🎯 Fonction helper pour installation simple
    """
    enregistreur = EnregistreurProtocole()
    return enregistreur.installation_complete()


def tester_protocole_orp() -> bool:
    """
    🧪 Test du protocole orp:// installé
    """
    try:
        from .gestionnaire import traiter_url_orp
        
        # URL de test
        url_test = "orp://fort_1234567890abcdef.openred/"
        
        print(f"🧪 Test protocole avec: {url_test}")
        resultat = traiter_url_orp(url_test)
        
        if resultat:
            print("✅ Test protocole réussi")
        else:
            print("❌ Test protocole échoué")
        
        return resultat
        
    except Exception as e:
        print(f"❌ Erreur test protocole: {e}")
        return False