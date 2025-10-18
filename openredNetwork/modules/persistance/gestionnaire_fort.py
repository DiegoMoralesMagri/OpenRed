#!/usr/bin/env python3
"""
🔄 GESTIONNAIRE DE PERSISTANCE FORT - OPENRED P2P
===============================================

Assure la persistance de l'identité et des connexions d'un fort
entre les redémarrages pour maintenir la continuité P2P.

Fonctionnalités :
- Sauvegarde identité fort (ID, clés crypto)
- Restauration connexions P2P
- Maintien position DHT
- Continuité service réseau
- Historique connexions

Conformité Manifeste :
✅ Données locales uniquement
✅ Aucune dépendance centralisée
✅ Chiffrement des données sensibles
"""

import os
import json
import time
import hashlib
import threading
from typing import Dict, List, Optional, Set
from datetime import datetime
from cryptography.fernet import Fernet
from dataclasses import dataclass, asdict


@dataclass
class IdentiteFort:
    """Identité persistante d'un fort"""
    fort_id: str
    nom: str
    cle_privee: str
    cle_publique: str
    port: int
    creation_timestamp: float
    derniere_activite: float
    adresse_ip_connue: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'IdentiteFort':
        return cls(**data)


@dataclass
class ConnexionP2P:
    """Connexion persistante avec un autre fort"""
    fort_distant_id: str
    fort_distant_nom: str
    ip_distante: str
    port_distant: int
    etablie_timestamp: float
    derniere_communication: float
    statut: str = "active"  # active, inactive, suspendue
    qualite_connexion: float = 1.0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConnexionP2P':
        return cls(**data)


class GestionnairePersistanceFort:
    """
    Gestionnaire de persistance pour forts OpenRed
    
    Maintient l'identité et les connexions entre redémarrages
    """
    
    def __init__(self, dossier_donnees: str = ".openred_fort"):
        self.dossier_donnees = dossier_donnees
        self.fichier_identite = os.path.join(dossier_donnees, "identite_fort.json")
        self.fichier_connexions = os.path.join(dossier_donnees, "connexions_p2p.json")
        self.fichier_etat_dht = os.path.join(dossier_donnees, "etat_dht.json")
        self.fichier_historique = os.path.join(dossier_donnees, "historique.json")
        
        # Clé de chiffrement (stockée localement)
        self.cle_chiffrement = self._obtenir_cle_chiffrement()
        
        # État en mémoire
        self.identite: Optional[IdentiteFort] = None
        self.connexions: Dict[str, ConnexionP2P] = {}
        self.etat_dht: Dict = {}
        self.historique: List[Dict] = []
        
        # Thread de sauvegarde automatique
        self.thread_sauvegarde = None
        self.actif = False
        
        self._initialiser_dossiers()
    
    def _initialiser_dossiers(self):
        """Crée les dossiers nécessaires"""
        if not os.path.exists(self.dossier_donnees):
            os.makedirs(self.dossier_donnees)
            print(f"📁 Dossier de persistance créé: {self.dossier_donnees}")
    
    def _obtenir_cle_chiffrement(self) -> bytes:
        """Obtient ou crée la clé de chiffrement locale"""
        fichier_cle = os.path.join(self.dossier_donnees, ".cle_locale")
        
        if os.path.exists(fichier_cle):
            try:
                with open(fichier_cle, 'rb') as f:
                    return f.read()
            except:
                pass
        
        # Génère nouvelle clé
        cle = Fernet.generate_key()
        try:
            self._initialiser_dossiers()
            with open(fichier_cle, 'wb') as f:
                f.write(cle)
            
            # Permissions restrictives sur Unix
            if hasattr(os, 'chmod'):
                os.chmod(fichier_cle, 0o600)
                
        except Exception as e:
            print(f"⚠️  Erreur sauvegarde clé: {e}")
        
        return cle
    
    def _chiffrer_donnees(self, data: Dict) -> bytes:
        """Chiffre les données sensibles"""
        try:
            fernet = Fernet(self.cle_chiffrement)
            json_str = json.dumps(data, separators=(',', ':'))
            return fernet.encrypt(json_str.encode())
        except Exception as e:
            print(f"❌ Erreur chiffrement: {e}")
            return json.dumps(data).encode()
    
    def _dechiffrer_donnees(self, data_chiffree: bytes) -> Dict:
        """Déchiffre les données"""
        try:
            fernet = Fernet(self.cle_chiffrement)
            json_str = fernet.decrypt(data_chiffree).decode()
            return json.loads(json_str)
        except:
            # Fallback données non chiffrées
            try:
                return json.loads(data_chiffree.decode())
            except:
                return {}
    
    def creer_ou_charger_identite(self, nom_fort: str, port: int = 8080) -> IdentiteFort:
        """
        Crée une nouvelle identité ou charge l'identité existante
        
        GARANTIT la persistance de l'identité entre redémarrages
        """
        print(f"🔍 Recherche identité fort '{nom_fort}'...")
        
        # Tente de charger l'identité existante
        identite_existante = self.charger_identite()
        
        if identite_existante and identite_existante.nom == nom_fort:
            print(f"✅ Identité existante trouvée: {identite_existante.fort_id}")
            self.identite = identite_existante
            
            # Met à jour l'activité
            self.identite.derniere_activite = time.time()
            self.identite.port = port  # Peut changer entre redémarrages
            
            self.sauvegarder_identite()
            self._ajouter_historique("identite_restauree", {"fort_id": identite_existante.fort_id})
            
            return self.identite
        
        # Crée nouvelle identité
        print(f"🆕 Création nouvelle identité pour '{nom_fort}'")
        
        # Génère ID unique ET persistant
        seed = f"{nom_fort}:{time.time()}:{os.urandom(16).hex()}"
        fort_id = "fort_" + hashlib.sha256(seed.encode()).hexdigest()[:16]
        
        # Génère clés cryptographiques (simplifiées pour demo)
        cle_privee = self._generer_cle_privee()
        cle_publique = self._generer_cle_publique(cle_privee)
        
        self.identite = IdentiteFort(
            fort_id=fort_id,
            nom=nom_fort,
            cle_privee=cle_privee,
            cle_publique=cle_publique,
            port=port,
            creation_timestamp=time.time(),
            derniere_activite=time.time()
        )
        
        # Sauvegarde immédiate
        self.sauvegarder_identite()
        self._ajouter_historique("identite_creee", {"fort_id": fort_id, "nom": nom_fort})
        
        print(f"✅ Nouvelle identité créée: {fort_id}")
        
        return self.identite
    
    def _generer_cle_privee(self) -> str:
        """Génère une clé privée (démo - utiliser cryptographie robuste en prod)"""
        return hashlib.sha256(f"private_key_{time.time()}_{os.urandom(32).hex()}".encode()).hexdigest()
    
    def _generer_cle_publique(self, cle_privee: str) -> str:
        """Génère la clé publique correspondante"""
        return hashlib.sha256(f"public_{cle_privee}".encode()).hexdigest()
    
    def charger_identite(self) -> Optional[IdentiteFort]:
        """Charge l'identité depuis le disque"""
        if not os.path.exists(self.fichier_identite):
            return None
        
        try:
            with open(self.fichier_identite, 'rb') as f:
                data_chiffree = f.read()
            
            data = self._dechiffrer_donnees(data_chiffree)
            return IdentiteFort.from_dict(data)
            
        except Exception as e:
            print(f"❌ Erreur chargement identité: {e}")
            return None
    
    def sauvegarder_identite(self):
        """Sauvegarde l'identité sur disque (chiffrée)"""
        if not self.identite:
            return
        
        try:
            data_chiffree = self._chiffrer_donnees(self.identite.to_dict())
            
            with open(self.fichier_identite, 'wb') as f:
                f.write(data_chiffree)
            
            print(f"💾 Identité sauvegardée: {self.identite.fort_id}")
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde identité: {e}")
    
    def ajouter_connexion_p2p(self, fort_distant_id: str, fort_distant_nom: str, 
                             ip: str, port: int):
        """Ajoute une connexion P2P persistante"""
        connexion = ConnexionP2P(
            fort_distant_id=fort_distant_id,
            fort_distant_nom=fort_distant_nom,
            ip_distante=ip,
            port_distant=port,
            etablie_timestamp=time.time(),
            derniere_communication=time.time()
        )
        
        self.connexions[fort_distant_id] = connexion
        self.sauvegarder_connexions()
        
        self._ajouter_historique("connexion_etablie", {
            "fort_distant": fort_distant_id,
            "ip": ip,
            "port": port
        })
        
        print(f"🔗 Connexion ajoutée: {fort_distant_nom} ({fort_distant_id})")
    
    def restaurer_connexions_p2p(self) -> Dict[str, ConnexionP2P]:
        """Restaure les connexions P2P depuis le disque"""
        print("🔄 Restauration connexions P2P...")
        
        if not os.path.exists(self.fichier_connexions):
            print("📋 Aucune connexion existante")
            return {}
        
        try:
            with open(self.fichier_connexions, 'rb') as f:
                data_chiffree = f.read()
            
            data = self._dechiffrer_donnees(data_chiffree)
            
            self.connexions = {}
            for fort_id, connexion_data in data.items():
                self.connexions[fort_id] = ConnexionP2P.from_dict(connexion_data)
            
            # Filtre les connexions anciennes
            self._nettoyer_connexions_anciennes()
            
            print(f"✅ {len(self.connexions)} connexions restaurées")
            
            return self.connexions
            
        except Exception as e:
            print(f"❌ Erreur restauration connexions: {e}")
            return {}
    
    def sauvegarder_connexions(self):
        """Sauvegarde les connexions sur disque"""
        try:
            data = {}
            for fort_id, connexion in self.connexions.items():
                data[fort_id] = connexion.to_dict()
            
            data_chiffree = self._chiffrer_donnees(data)
            
            with open(self.fichier_connexions, 'wb') as f:
                f.write(data_chiffree)
            
            print(f"💾 {len(self.connexions)} connexions sauvegardées")
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde connexions: {e}")
    
    def _nettoyer_connexions_anciennes(self):
        """Nettoie les connexions trop anciennes"""
        maintenant = time.time()
        seuil_ancien = 7 * 24 * 3600  # 7 jours
        
        connexions_a_supprimer = []
        
        for fort_id, connexion in self.connexions.items():
            age = maintenant - connexion.derniere_communication
            if age > seuil_ancien:
                connexions_a_supprimer.append(fort_id)
        
        for fort_id in connexions_a_supprimer:
            del self.connexions[fort_id]
            print(f"🧹 Connexion ancienne supprimée: {fort_id}")
    
    def mettre_a_jour_activite_connexion(self, fort_distant_id: str):
        """Met à jour l'activité d'une connexion"""
        if fort_distant_id in self.connexions:
            self.connexions[fort_distant_id].derniere_communication = time.time()
    
    def sauvegarder_etat_dht(self, etat: Dict):
        """Sauvegarde l'état du DHT"""
        self.etat_dht = etat
        
        try:
            data_chiffree = self._chiffrer_donnees(etat)
            
            with open(self.fichier_etat_dht, 'wb') as f:
                f.write(data_chiffree)
            
            print("💾 État DHT sauvegardé")
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde DHT: {e}")
    
    def restaurer_etat_dht(self) -> Dict:
        """Restaure l'état du DHT"""
        if not os.path.exists(self.fichier_etat_dht):
            return {}
        
        try:
            with open(self.fichier_etat_dht, 'rb') as f:
                data_chiffree = f.read()
            
            etat = self._dechiffrer_donnees(data_chiffree)
            self.etat_dht = etat
            
            print("✅ État DHT restauré")
            return etat
            
        except Exception as e:
            print(f"❌ Erreur restauration DHT: {e}")
            return {}
    
    def _ajouter_historique(self, action: str, details: Dict):
        """Ajoute une entrée à l'historique"""
        entree = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        
        self.historique.append(entree)
        
        # Limite la taille de l'historique
        if len(self.historique) > 1000:
            self.historique = self.historique[-500:]
        
        # Sauvegarde asynchrone
        threading.Thread(target=self._sauvegarder_historique, daemon=True).start()
    
    def _sauvegarder_historique(self):
        """Sauvegarde l'historique"""
        try:
            with open(self.fichier_historique, 'w', encoding='utf-8') as f:
                json.dump(self.historique, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def demarrer_sauvegarde_auto(self, intervalle: int = 300):
        """Démarre la sauvegarde automatique (5 minutes par défaut)"""
        if self.actif:
            return
        
        self.actif = True
        
        def boucle_sauvegarde():
            while self.actif:
                time.sleep(intervalle)
                if self.actif:
                    self.sauvegarder_identite()
                    self.sauvegarder_connexions()
                    print("🔄 Sauvegarde automatique effectuée")
        
        self.thread_sauvegarde = threading.Thread(target=boucle_sauvegarde, daemon=True)
        self.thread_sauvegarde.start()
        
        print(f"⏰ Sauvegarde automatique démarrée (toutes les {intervalle}s)")
    
    def arreter_sauvegarde_auto(self):
        """Arrête la sauvegarde automatique"""
        self.actif = False
        
        # Sauvegarde finale
        self.sauvegarder_identite()
        self.sauvegarder_connexions()
        
        print("🛑 Sauvegarde automatique arrêtée")
    
    def obtenir_statistiques(self) -> Dict:
        """Statistiques de persistance"""
        stats = {
            "fort_id": self.identite.fort_id if self.identite else None,
            "nom_fort": self.identite.nom if self.identite else None,
            "creation": datetime.fromtimestamp(self.identite.creation_timestamp).isoformat() if self.identite else None,
            "derniere_activite": datetime.fromtimestamp(self.identite.derniere_activite).isoformat() if self.identite else None,
            "connexions_actives": len([c for c in self.connexions.values() if c.statut == "active"]),
            "connexions_totales": len(self.connexions),
            "entrees_historique": len(self.historique),
            "taille_etat_dht": len(self.etat_dht),
            "dossier_donnees": self.dossier_donnees,
            "fichiers_existants": {
                "identite": os.path.exists(self.fichier_identite),
                "connexions": os.path.exists(self.fichier_connexions),
                "etat_dht": os.path.exists(self.fichier_etat_dht),
                "historique": os.path.exists(self.fichier_historique)
            }
        }
        
        return stats


if __name__ == "__main__":
    # Test de persistance
    print("🧪 === TEST GESTIONNAIRE PERSISTANCE ===")
    
    gestionnaire = GestionnairePersistanceFort()
    
    # Test création/restauration identité
    identite = gestionnaire.creer_ou_charger_identite("Fort Test Persistance")
    
    print(f"\n📋 Identité:")
    print(f"   ID: {identite.fort_id}")
    print(f"   Nom: {identite.nom}")
    print(f"   Port: {identite.port}")
    print(f"   Création: {datetime.fromtimestamp(identite.creation_timestamp)}")
    
    # Test connexions
    gestionnaire.ajouter_connexion_p2p(
        "fort_test123456789",
        "Fort Distant Test",
        "192.168.1.50",
        8081
    )
    
    # Restauration
    connexions = gestionnaire.restaurer_connexions_p2p()
    print(f"\n🔗 Connexions restaurées: {len(connexions)}")
    
    # Statistiques
    stats = gestionnaire.obtenir_statistiques()
    print(f"\n📊 Statistiques:")
    for cle, valeur in stats.items():
        if cle != "fichiers_existants":
            print(f"   {cle}: {valeur}")
    
    print("\n✅ Test persistance terminé")
    print("🔄 Redémarrez le script pour tester la restauration !")