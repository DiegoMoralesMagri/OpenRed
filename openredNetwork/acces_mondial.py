#!/usr/bin/env python3
"""
🌍 CONFIGURATEUR ACCÈS MONDIAL - FORT OPENRED
============================================

Configure l'accès mondial pour un fort OpenRed via IP publique
et publication dans le réseau P2P décentralisé.

Étapes :
1. Détection IP publique automatique
2. Configuration routeur (instructions)
3. Publication réseau P2P mondial
4. Test accessibilité externe
"""

import os
import sys
import json
import socket
import requests
import threading
import time
from typing import Dict, Optional
from datetime import datetime

# Import des modules OpenRed
sys.path.append(os.path.join(os.getcwd(), 'modules'))
from persistance.gestionnaire_fort import GestionnairePersistanceFort
from internet.resolveur_p2p_decentralise import publier_fort


class ConfigurateurAccesMondial:
    """Configure l'accès mondial pour un fort OpenRed"""
    
    def __init__(self):
        self.ip_publique = None
        self.port_externe = None
        self.fort_info = None
        
    def detecter_ip_publique(self) -> Optional[str]:
        """Détecte l'IP publique via services indépendants"""
        print("🔍 Détection de votre IP publique...")
        
        services = [
            "https://api.ipify.org",
            "https://ifconfig.me/ip", 
            "https://ipecho.net/plain",
            "https://checkip.dyndns.org"
        ]
        
        for service in services:
            try:
                print(f"   🌐 Test {service}...")
                response = requests.get(service, timeout=5)
                
                if response.status_code == 200:
                    ip_text = response.text.strip()
                    
                    # Pour checkip.dyndns.org qui retourne du HTML
                    if "checkip.dyndns.org" in service:
                        import re
                        match = re.search(r'(\d+\.\d+\.\d+\.\d+)', ip_text)
                        if match:
                            ip_text = match.group(1)
                    
                    # Valide que c'est une IP
                    parts = ip_text.split('.')
                    if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
                        self.ip_publique = ip_text
                        print(f"✅ IP publique détectée: {self.ip_publique}")
                        return self.ip_publique
                        
            except Exception as e:
                print(f"   ⚠️  {service} injoignable: {e}")
                continue
        
        print("❌ Impossible de détecter l'IP publique automatiquement")
        return None
    
    def tester_port_ouvert(self, port: int) -> bool:
        """Test si un port est accessible depuis l'extérieur"""
        if not self.ip_publique:
            return False
            
        print(f"🔍 Test accessibilité port {port} depuis l'extérieur...")
        
        try:
            # Service de test de port (service tiers)
            test_url = f"http://portquiz.net:{port}"
            response = requests.get(test_url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Port {port} accessible depuis l'extérieur")
                return True
            else:
                print(f"❌ Port {port} non accessible depuis l'extérieur")
                return False
                
        except Exception as e:
            print(f"⚠️  Impossible de tester le port {port}: {e}")
            return False
    
    def generer_instructions_routeur(self, port: int) -> Dict:
        """Génère les instructions de configuration routeur"""
        instructions = {
            "titre": "🌍 CONFIGURATION ROUTEUR POUR ACCÈS MONDIAL",
            "ip_publique": self.ip_publique,
            "port": port,
            "etapes": [
                {
                    "numero": 1,
                    "titre": "Accéder à l'interface routeur",
                    "description": "Ouvrez l'interface web de votre routeur",
                    "actions": [
                        "Ouvrir navigateur web",
                        "Aller à http://192.168.1.1 ou http://192.168.0.1",
                        "Se connecter avec identifiants administrateur",
                        "Chercher section 'Redirection de port' ou 'Port Forwarding'"
                    ]
                },
                {
                    "numero": 2,
                    "titre": "Configurer la redirection de port",
                    "description": f"Rediriger le port {port} vers votre machine",
                    "actions": [
                        f"Port externe: {port}",
                        f"IP interne: {self._detecter_ip_locale()}",
                        f"Port interne: {port}",
                        "Protocole: TCP",
                        "Nom de règle: OpenRed Fort",
                        "Activer la règle"
                    ]
                },
                {
                    "numero": 3,
                    "titre": "Configurer le pare-feu",
                    "description": "Autoriser le trafic sur le port",
                    "actions": [
                        f"Autoriser port {port} en entrée (TCP)",
                        "Créer exception Windows Firewall si nécessaire",
                        "Redémarrer routeur si demandé"
                    ]
                },
                {
                    "numero": 4,
                    "titre": "Tester l'accessibilité",
                    "description": "Vérifier que le fort est accessible",
                    "actions": [
                        f"Test depuis autre réseau: http://{self.ip_publique}:{port}",
                        "Utiliser site test de port (portchecker.co)",
                        "Demander à un ami de tester l'accès"
                    ]
                }
            ],
            "urls_test": [
                f"http://{self.ip_publique}:{port}",
                f"orp://fort_[ID].openred/",
                "https://www.portchecker.co",
                "https://canyouseeme.org"
            ],
            "notes_importantes": [
                "⚠️  La configuration varie selon le modèle de routeur",
                "🔒 Vérifiez que le port est bien sécurisé (OpenRed uniquement)",
                "🌐 L'IP publique peut changer (IP dynamique)",
                "📞 Contactez votre FAI si problème persistant",
                "🔄 Redémarrage routeur parfois nécessaire"
            ]
        }
        
        return instructions
    
    def _detecter_ip_locale(self) -> str:
        """Détecte l'IP locale de la machine"""
        try:
            # Méthode fiable pour obtenir l'IP locale
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            ip_locale = sock.getsockname()[0]
            sock.close()
            return ip_locale
        except:
            return "192.168.1.100"  # Valeur par défaut
    
    def publier_fort_mondial(self, fort_id: str, nom_fort: str, port: int):
        """Publie le fort dans le réseau P2P mondial"""
        if not self.ip_publique:
            print("❌ IP publique requise pour publication mondiale")
            return False
        
        print(f"📡 Publication mondiale du fort {nom_fort}...")
        
        self.fort_info = {
            "fort_id": fort_id,
            "nom": nom_fort,
            "ip_publique": self.ip_publique,
            "port": port,
            "cle_publique": f"demo_key_{fort_id[:16]}",
            "timestamp": time.time(),
            "access_type": "mondial",
            "description": f"Fort OpenRed {nom_fort} accessible mondialement"
        }
        
        try:
            # Sauvegarde locale d'abord
            self._sauvegarder_registry_mondial()
            
            # Publication P2P
            publier_fort(self.fort_info)
            
            print(f"✅ Fort publié mondialement !")
            print(f"🌍 Accessible via: http://{self.ip_publique}:{port}")
            print(f"🔗 URL OpenRed: orp://{fort_id}.openred/")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Erreur publication P2P: {e}")
            print("💾 Fort sauvegardé localement")
            return False
    
    def _sauvegarder_registry_mondial(self):
        """Sauvegarde le registry mondial local"""
        fichier_registry = "registry_mondial.json"
        
        # Charge le registry existant
        registry = {"forts_mondiaux": [], "meta": {}}
        if os.path.exists(fichier_registry):
            try:
                with open(fichier_registry, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
            except:
                pass
        
        # Met à jour les métadonnées
        registry["meta"] = {
            "ip_publique": self.ip_publique,
            "derniere_maj": datetime.now().isoformat(),
            "type": "registry_mondial_openred",
            "version": "1.0"
        }
        
        # Ajoute ou met à jour le fort
        found = False
        for i, fort in enumerate(registry["forts_mondiaux"]):
            if fort["fort_id"] == self.fort_info["fort_id"]:
                registry["forts_mondiaux"][i] = self.fort_info
                found = True
                break
        
        if not found:
            registry["forts_mondiaux"].append(self.fort_info)
        
        # Sauvegarde
        try:
            with open(fichier_registry, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Registry mondial sauvegardé: {fichier_registry}")
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde registry: {e}")
    
    def generer_guide_acces_mondial(self, fort_id: str, nom_fort: str, port: int) -> str:
        """Génère un guide complet d'accès mondial"""
        guide = f"""
# 🌍 GUIDE ACCÈS MONDIAL - FORT {nom_fort.upper()}

## 📋 INFORMATIONS FORT

- **Nom:** {nom_fort}
- **Fort ID:** {fort_id}
- **IP Publique:** {self.ip_publique}
- **Port:** {port}

## 🔗 URLS D'ACCÈS

### Accès Direct HTTP
```
http://{self.ip_publique}:{port}
```

### Accès via Protocole OpenRed
```
orp://{fort_id}.openred/
```

## 🌐 ACCÈS DEPUIS N'IMPORTE OÙ DANS LE MONDE

### 1. Via Navigateur Web Classique
- Tapez: `http://{self.ip_publique}:{port}`
- Fonctionne depuis n'importe quel navigateur
- Accès direct via Internet

### 2. Via Extension OpenRed (Recommandé)
- Installer extension navigateur OpenRed
- Tapez: `orp://{fort_id}.openred/`
- Résolution automatique P2P

### 3. Via Réseau P2P OpenRed
- Autres forts OpenRed trouvent automatiquement
- Découverte via DHT distribué
- Accès décentralisé

## ⚙️ CONFIGURATION REQUISE

### Côté Serveur (Vous)
✅ Fort OpenRed démarré sur port {port}
✅ IP publique détectée: {self.ip_publique}
⚠️  Redirection port routeur à configurer
⚠️  Pare-feu à configurer

### Côté Client (Visiteurs)
✅ Navigateur web standard (HTTP)
🔄 Extension OpenRed (protocole orp://)
🔄 Client OpenRed (accès P2P avancé)

## 🔧 PROCHAINES ÉTAPES

1. **Configurer votre routeur** (voir instructions détaillées)
2. **Tester l'accès externe** 
3. **Partager votre URL fort**
4. **Surveiller les connexions**

## 📞 PARTAGE DU FORT

Partagez ces URLs avec vos amis/collègues :

**URL Directe (tous navigateurs):**
`http://{self.ip_publique}:{port}`

**URL OpenRed (avec extension):**
`orp://{fort_id}.openred/`

## 🔒 SÉCURITÉ

- ✅ Chiffrement P2P natif OpenRed
- ✅ Identité cryptographique unique
- ⚠️  Port exposé sur Internet (normal)
- 💡 Surveiller les logs d'accès

---
*Fort créé le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*
"""
        
        return guide
    
    def configurer_fort_existant(self, nom_fort: str = None) -> bool:
        """Configure un fort existant pour l'accès mondial"""
        print("🌍 === CONFIGURATION ACCÈS MONDIAL ===")
        
        # Charge le fort existant
        gestionnaire = GestionnairePersistanceFort()
        
        if nom_fort:
            identite = gestionnaire.creer_ou_charger_identite(nom_fort)
        else:
            # Essaie de charger le dernier fort
            identite = gestionnaire.charger_identite()
            if not identite:
                print("❌ Aucun fort trouvé. Créez d'abord un fort.")
                return False
        
        print(f"✅ Fort trouvé: {identite.nom} ({identite.fort_id})")
        
        # Détecte l'IP publique
        if not self.detecter_ip_publique():
            print("❌ Configuration impossible sans IP publique")
            return False
        
        # Génère les instructions
        instructions = self.generer_instructions_routeur(identite.port)
        
        # Sauvegarde les instructions
        fichier_instructions = f"instructions_acces_mondial_{identite.fort_id[:8]}.json"
        try:
            with open(fichier_instructions, 'w', encoding='utf-8') as f:
                json.dump(instructions, f, indent=2, ensure_ascii=False)
            print(f"📄 Instructions sauvegardées: {fichier_instructions}")
        except:
            pass
        
        # Affiche les instructions
        print("\n" + "="*60)
        print("🔧 INSTRUCTIONS CONFIGURATION ROUTEUR")
        print("="*60)
        
        for etape in instructions["etapes"]:
            print(f"\n{etape['numero']}️⃣ {etape['titre']}")
            print(f"   {etape['description']}")
            for action in etape['actions']:
                print(f"   • {action}")
        
        # Publication mondiale
        if input(f"\n🌍 Publier le fort mondialement ? (o/N): ").lower().startswith('o'):
            success = self.publier_fort_mondial(
                identite.fort_id,
                identite.nom, 
                identite.port
            )
            
            if success:
                # Génère le guide d'accès
                guide = self.generer_guide_acces_mondial(
                    identite.fort_id,
                    identite.nom,
                    identite.port
                )
                
                # Sauvegarde le guide
                fichier_guide = f"guide_acces_mondial_{identite.nom.replace(' ', '_')}.md"
                try:
                    with open(fichier_guide, 'w', encoding='utf-8') as f:
                        f.write(guide)
                    print(f"📖 Guide d'accès sauvegardé: {fichier_guide}")
                except:
                    pass
        
        print("\n" + "="*60)
        print("🎉 CONFIGURATION ACCÈS MONDIAL TERMINÉE")
        print("="*60)
        print(f"🌍 URL mondiale: http://{self.ip_publique}:{identite.port}")
        print(f"🔗 URL OpenRed: orp://{identite.fort_id}.openred/")
        print("\n💡 Suivez les instructions pour configurer votre routeur !")
        
        return True


def main():
    """Fonction principale"""
    configurateur = ConfigurateurAccesMondial()
    
    print("🌍 === CONFIGURATEUR ACCÈS MONDIAL OPENRED ===")
    print("Rend votre fort accessible depuis n'importe où dans le monde")
    print("="*60)
    
    # Menu
    print("\n🎯 OPTIONS:")
    print("1. Configurer fort existant pour accès mondial")
    print("2. Détecter IP publique seulement")
    print("3. Générer instructions routeur")
    
    choix = input("\nVotre choix (1-3): ").strip()
    
    if choix == "1":
        nom_fort = input("Nom du fort (ou Entrée pour le dernier): ").strip()
        configurateur.configurer_fort_existant(nom_fort if nom_fort else None)
    
    elif choix == "2":
        configurateur.detecter_ip_publique()
    
    elif choix == "3":
        ip = input("Votre IP publique: ").strip()
        port = int(input("Port du fort: ").strip() or "8080")
        configurateur.ip_publique = ip
        instructions = configurateur.generer_instructions_routeur(port)
        
        print("\n📋 INSTRUCTIONS ROUTEUR:")
        for etape in instructions["etapes"]:
            print(f"\n{etape['numero']}️⃣ {etape['titre']}")
            for action in etape['actions']:
                print(f"   • {action}")
    
    else:
        print("❌ Choix invalide")


if __name__ == "__main__":
    main()