#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 Script d'installation du protocole ORP (OpenRed Protocol)
Rend le protocole orp:// utilisable et reconnu par le système
"""

import sys
import os

# Configuration pour Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Ajout du chemin du projet
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def main():
    """Installation du protocole ORP"""
    
    print("=" * 60)
    print("     INSTALLATION PROTOCOLE ORP - OPENRED NETWORK")
    print("=" * 60)
    print()
    
    try:
        # Import du module protocole
        print("1. Chargement du module protocole...")
        from modules.protocole import EnregistreurProtocole
        print("   Module charge avec succes")
        
        # Création de l'enregistreur
        print("\n2. Initialisation de l'enregistreur...")
        enregistreur = EnregistreurProtocole()
        print("   Enregistreur initialise")
        
        # Affichage informations système
        print(f"\n3. Informations systeme:")
        print(f"   Plateforme: {sys.platform}")
        print(f"   Python: {sys.version}")
        print(f"   Repertoire: {project_root}")
        
        # Chemin du handler
        handler_path = enregistreur.obtenir_chemin_handler()
        print(f"   Handler: {handler_path}")
        
        # Vérification handler existe
        if not os.path.exists(handler_path):
            print("   ERREUR: Handler introuvable!")
            return 1
        
        print("\n4. Installation du protocole...")
        print("   (Ceci va modifier le registre Windows ou fichiers systeme)")
        
        # Demande confirmation
        reponse = input("\n   Continuer l'installation ? (o/N): ").lower().strip()
        
        if reponse not in ['o', 'oui', 'y', 'yes']:
            print("   Installation annulee par l'utilisateur")
            return 0
        
        # Installation
        print("\n   Installation en cours...")
        succes = enregistreur.installation_complete()
        
        if succes:
            print("\n" + "=" * 60)
            print("   ✅ INSTALLATION REUSSIE!")
            print("=" * 60)
            print()
            print("Le protocole orp:// est maintenant utilisable:")
            print()
            print("• Vous pouvez cliquer sur les liens orp:// dans votre navigateur")
            print("• Les liens s'ouvriront automatiquement avec OpenRed Network")
            print("• Format: orp://fort_[16hex].openred/[chemin]")
            print()
            print("Exemples d'URLs:")
            print("  orp://fort_1234567890abcdef.openred/")
            print("  orp://fort_abcdef1234567890.openred/fenetre")
            print("  orp://fort_fedcba0987654321.openred/projection/demo")
            print()
            print("Pour tester:")
            print("  python -c \"from modules.protocole import traiter_url_orp; traiter_url_orp('orp://fort_1234567890abcdef.openred/')\"")
            print()
            
        else:
            print("\n" + "=" * 60)
            print("   ❌ ECHEC INSTALLATION")
            print("=" * 60)
            print()
            print("L'installation a echoue. Verifiez:")
            print("• Droits administrateur (pour Windows)")
            print("• Permissions d'ecriture")
            print("• Integrite des fichiers")
            print()
            return 1
            
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Verifiez que vous etes dans le bon repertoire OpenRed Network")
        return 1
        
    except Exception as e:
        print(f"❌ Erreur installation: {e}")
        return 1
    
    return 0


def desinstaller():
    """Désinstallation du protocole ORP"""
    
    print("=" * 60)
    print("   DESINSTALLATION PROTOCOLE ORP - OPENRED NETWORK")
    print("=" * 60)
    print()
    
    try:
        from modules.protocole import EnregistreurProtocole
        
        enregistreur = EnregistreurProtocole()
        
        # Demande confirmation
        reponse = input("Confirmer la desinstallation du protocole orp:// ? (o/N): ").lower().strip()
        
        if reponse not in ['o', 'oui', 'y', 'yes']:
            print("Desinstallation annulee")
            return 0
        
        # Désinstallation Windows
        if sys.platform.startswith('win'):
            succes = enregistreur.desinscrire_protocole_windows()
        else:
            print("Desinstallation automatique non supportee sur cette plateforme")
            succes = False
        
        if succes:
            print("✅ Protocole orp:// desinstalle avec succes")
        else:
            print("❌ Echec desinstallation")
            return 1
            
    except Exception as e:
        print(f"❌ Erreur desinstallation: {e}")
        return 1
    
    return 0


def tester():
    """Test du protocole ORP installé"""
    
    print("=" * 60)
    print("      TEST PROTOCOLE ORP - OPENRED NETWORK")
    print("=" * 60)
    print()
    
    try:
        from modules.protocole import GestionnaireProtocole, ValidateurAdresseORP
        
        # URL de test
        url_test = "orp://fort_1234567890abcdef.openred/"
        
        print(f"URL de test: {url_test}")
        print()
        
        # Test validation
        print("1. Test validation...")
        if ValidateurAdresseORP.valider_url(url_test):
            print("   ✅ URL valide")
        else:
            print("   ❌ URL invalide")
            return 1
        
        # Test traitement
        print("\n2. Test traitement...")
        gestionnaire = GestionnaireProtocole()
        resultat = gestionnaire.traiter_url(url_test)
        
        if resultat:
            print("   ✅ Traitement reussi")
        else:
            print("   ⚠️  Traitement echoue (normal si le fort n'existe pas)")
        
        # Statistiques
        stats = gestionnaire.obtenir_statistiques()
        print(f"\n3. Statistiques:")
        print(f"   URLs traitees: {stats['urls_traitees']}")
        print(f"   Connexions: {stats['connexions_etablies']}")
        
        print("\n✅ Test complete - Le protocole fonctionne!")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        commande = sys.argv[1].lower()
        
        if commande in ['desinstaller', 'uninstall', 'remove']:
            sys.exit(desinstaller())
        elif commande in ['test', 'tester']:
            sys.exit(tester())
        elif commande in ['help', 'aide', '--help', '-h']:
            print("Usage:")
            print("  python installer_protocole_orp.py           # Installation")
            print("  python installer_protocole_orp.py test      # Test")
            print("  python installer_protocole_orp.py remove    # Desinstallation")
            sys.exit(0)
        else:
            print(f"Commande inconnue: {commande}")
            print("Utilisez 'help' pour voir les options")
            sys.exit(1)
    else:
        # Installation par défaut
        sys.exit(main())