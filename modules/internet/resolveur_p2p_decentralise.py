#!/usr/bin/env python3
"""
RÉSOLVEUR P2P DÉCENTRALISÉ - CONFORME MANIFESTE OPENRED
======================================================

Remplace COMPLÈTEMENT les dépendances centralisées :
❌ GitHub Registry (Microsoft)
❌ DNS géants (Google, Cloudflare)
❌ Serveurs centralisés

✅ DHT P2P distribué
✅ Seeds communautaires
✅ Protocole gossip
✅ DNS communautaire
✅ Résistance à la censure

Conformité Manifeste OpenRed :
✅ Article III - Décentralisation irréversible
✅ Article III - Absence de point central
✅ Article III - Architecture P2P obligatoire
✅ Article III - Résistance à la censure
"""

import os
import sys
import json
import time
import socket
import threading
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Import du DHT P2P
from modules.internet.dht_p2p import DecouverteP2P, FortInfo


class ResolveurP2PDecentralise:
    """
    Résolveur 100% P2P pour protocole orp://
    
    ZÉRO DÉPENDANCE vers les géants technologiques
    """
    
    def __init__(self):
        self.decouverte_p2p = DecouverteP2P()
        self.cache_local = {}
        self.cache_ttl = 3600  # 1 heure
        self.seeds_communautaires = self._load_community_seeds()
        self.running = False
        
    def _load_community_seeds(self) -> List[Dict]:
        """
        Charge les seeds communautaires (pas de géants)
        
        Ces seeds sont des serveurs volontaires de la communauté OpenRed,
        pas des infrastructures contrôlées par des monopoles.
        """
        seeds = [
            {
                "nom": "OpenRed Community Seed 1",
                "ip": "openred-seed1.community",
                "port": 7777,
                "maintenu_par": "Communauté OpenRed",
                "type": "bénévole"
            },
            {
                "nom": "OpenRed Community Seed 2", 
                "ip": "openred-seed2.community",
                "port": 7777,
                "maintenu_par": "Communauté OpenRed",
                "type": "bénévole"
            },
            {
                "nom": "OpenRed Community Seed 3",
                "ip": "openred-seed3.community",
                "port": 7777,
                "maintenu_par": "Communauté OpenRed",
                "type": "bénévole"
            },
            {
                "nom": "Bootstrap Local",
                "ip": "127.0.0.1",
                "port": 7777,
                "maintenu_par": "Local",
                "type": "bootstrap"
            }
        ]
        
        # Charge depuis fichier local si disponible
        seeds_file = "seeds_communautaires.json"
        if os.path.exists(seeds_file):
            try:
                with open(seeds_file, 'r', encoding='utf-8') as f:
                    file_seeds = json.load(f)
                    seeds.extend(file_seeds)
            except:
                pass
        
        return seeds
    
    def demarrer(self):
        """Démarre le résolveur P2P"""
        print("🌐 === RÉSOLVEUR P2P DÉCENTRALISÉ ===")
        print("✅ Conforme au Manifeste OpenRed")
        print("❌ ZÉRO dépendance vers Microsoft/Google/Amazon")
        print("🔄 DHT + Gossip + Communauté")
        print("=" * 45)
        
        self.running = True
        self.decouverte_p2p.demarrer()
        
        # Thread de maintenance du cache
        maintenance_thread = threading.Thread(target=self._maintenance_loop)
        maintenance_thread.daemon = True
        maintenance_thread.start()
        
        print("✅ Résolveur P2P décentralisé démarré")
    
    def arreter(self):
        """Arrête le résolveur"""
        self.running = False
        self.decouverte_p2p.arreter()
        print("🛑 Résolveur P2P arrêté")
    
    def resoudre_orp(self, url_orp: str) -> Optional[Dict]:
        """
        Résout une URL orp:// via le réseau P2P décentralisé
        
        Stratégies de résolution (dans l'ordre) :
        1. Cache local
        2. DHT P2P distribué
        3. Seeds communautaires
        4. Broadcast local
        5. Fichiers distribués P2P
        """
        print(f"🔍 Résolution P2P de: {url_orp}")
        
        # Parse l'URL
        parsed = urlparse(url_orp)
        if parsed.scheme != "orp":
            print(f"❌ Protocole non supporté: {parsed.scheme}")
            return None
        
        fort_identifier = parsed.netloc
        chemin = parsed.path or "/"
        
        # 1. Vérification cache local
        resultat = self._check_cache_local(fort_identifier)
        if resultat:
            print(f"💾 Résolu depuis cache local")
            return self._format_resultat(resultat, chemin)
        
        # 2. Recherche DHT P2P
        resultat = self._recherche_dht_p2p(fort_identifier)
        if resultat:
            print(f"🌐 Résolu via DHT P2P")
            self._cache_result(fort_identifier, resultat)
            return self._format_resultat(resultat, chemin)
        
        # 3. Interrogation seeds communautaires
        resultat = self._interroge_seeds_communautaires(fort_identifier)
        if resultat:
            print(f"🌱 Résolu via seeds communautaires")
            self._cache_result(fort_identifier, resultat)
            return self._format_resultat(resultat, chemin)
        
        # 4. Broadcast réseau local
        resultat = self._broadcast_local(fort_identifier)
        if resultat:
            print(f"📡 Résolu via broadcast local")
            self._cache_result(fort_identifier, resultat)
            return self._format_resultat(resultat, chemin)
        
        # 5. Fichiers distribués (dernière chance)
        resultat = self._recherche_fichiers_distribues(fort_identifier)
        if resultat:
            print(f"📂 Résolu via fichiers distribués")
            self._cache_result(fort_identifier, resultat)
            return self._format_resultat(resultat, chemin)
        
        print(f"❌ Fort {fort_identifier} introuvable dans le réseau P2P")
        return None
    
    def _check_cache_local(self, fort_id: str) -> Optional[Dict]:
        """Vérifie le cache local"""
        if fort_id in self.cache_local:
            entry = self.cache_local[fort_id]
            if time.time() - entry["timestamp"] < self.cache_ttl:
                return entry["data"]
            else:
                del self.cache_local[fort_id]
        return None
    
    def _recherche_dht_p2p(self, fort_id: str) -> Optional[Dict]:
        """Recherche dans le DHT P2P"""
        try:
            return self.decouverte_p2p.rechercher_fort(fort_id)
        except Exception as e:
            print(f"⚠️  Erreur DHT P2P: {e}")
            return None
    
    def _interroge_seeds_communautaires(self, fort_id: str) -> Optional[Dict]:
        """Interroge les seeds communautaires"""
        for seed in self.seeds_communautaires:
            if seed.get("type") == "transition":
                continue  # Évite les géants autant que possible
                
            try:
                resultat = self._query_seed(seed, fort_id)
                if resultat:
                    return resultat
            except Exception as e:
                print(f"⚠️  Seed {seed['nom']} injoignable: {e}")
                continue
        
        return None
    
    def _query_seed(self, seed: Dict, fort_id: str) -> Optional[Dict]:
        """Interroge un seed spécifique"""
        try:
            # Protocole simple pour interroger les seeds
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            
            query = json.dumps({
                "type": "find_fort",
                "fort_id": fort_id,
                "protocol": "orp_p2p"
            }).encode()
            
            sock.sendto(query, (seed["ip"], seed["port"]))
            response, _ = sock.recvfrom(4096)
            
            data = json.loads(response.decode())
            if data.get("found"):
                return data.get("fort_info")
                
        except Exception as e:
            print(f"❌ Erreur query seed {seed['nom']}: {e}")
        finally:
            sock.close()
        
        return None
    
    def _broadcast_local(self, fort_id: str) -> Optional[Dict]:
        """Broadcast sur le réseau local"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(2)
            
            query = json.dumps({
                "type": "find_fort_broadcast",
                "fort_id": fort_id
            }).encode()
            
            # Broadcast sur port standard OpenRed
            sock.sendto(query, ("255.255.255.255", 7777))
            
            # Écoute les réponses
            try:
                response, addr = sock.recvfrom(4096)
                data = json.loads(response.decode())
                if data.get("found"):
                    return data.get("fort_info")
            except socket.timeout:
                pass
                
        except Exception as e:
            print(f"❌ Erreur broadcast: {e}")
        finally:
            sock.close()
        
        return None
    
    def _recherche_fichiers_distribues(self, fort_id: str) -> Optional[Dict]:
        """Recherche dans les fichiers distribués"""
        # Vérifie les fichiers distribués locaux
        fichiers_distribues = [
            "forts_registry_p2p.json",
            "forts_communautaires.json",
            os.path.expanduser("~/.openred/forts_distribues.json")
        ]
        
        for fichier in fichiers_distribues:
            if os.path.exists(fichier):
                try:
                    with open(fichier, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    for fort in data.get("forts", []):
                        if fort.get("fort_id") == fort_id:
                            return fort
                            
                except Exception as e:
                    print(f"⚠️  Erreur lecture {fichier}: {e}")
                    continue
        
        return None
    
    def _cache_result(self, fort_id: str, data: Dict):
        """Met en cache un résultat"""
        self.cache_local[fort_id] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def _format_resultat(self, fort_info: Dict, chemin: str) -> Dict:
        """Formate le résultat final"""
        return {
            "fort_id": fort_info["fort_id"],
            "nom": fort_info["nom"],
            "ip_publique": fort_info["ip_publique"],
            "port": fort_info["port"],
            "chemin": chemin,
            "url_complete": f"http://{fort_info['ip_publique']}:{fort_info['port']}{chemin}",
            "cle_publique": fort_info.get("cle_publique"),
            "timestamp": fort_info.get("timestamp"),
            "source_resolution": "p2p_decentralise"
        }
    
    def _maintenance_loop(self):
        """Maintenance périodique"""
        while self.running:
            try:
                # Nettoie le cache expiré
                now = time.time()
                expired = []
                
                for fort_id, entry in self.cache_local.items():
                    if now - entry["timestamp"] > self.cache_ttl:
                        expired.append(fort_id)
                
                for fort_id in expired:
                    del self.cache_local[fort_id]
                
                if expired:
                    print(f"🧹 Cache nettoyé: {len(expired)} entrées expirées")
                
                # Met à jour les seeds communautaires
                self._update_community_seeds()
                
            except Exception as e:
                print(f"❌ Erreur maintenance: {e}")
            
            time.sleep(300)  # 5 minutes
    
    def _update_community_seeds(self):
        """Met à jour la liste des seeds communautaires"""
        try:
            # Dans une vraie implémentation, on pourrait récupérer
            # la liste depuis d'autres nœuds P2P
            pass
        except:
            pass
    
    def publier_fort_local(self, fort_info: Dict):
        """Publie un fort local dans le réseau P2P"""
        print(f"📡 Publication fort {fort_info['nom']} dans réseau P2P décentralisé")
        
        # Publie dans le DHT P2P
        self.decouverte_p2p.publier_fort(fort_info)
        
        # Sauvegarde locale
        self._sauvegarder_fort_local(fort_info)
        
        print(f"✅ Fort {fort_info['nom']} publié avec succès")
    
    def _sauvegarder_fort_local(self, fort_info: Dict):
        """Sauvegarde un fort dans le registry local"""
        fichier_local = "forts_registry_p2p.json"
        
        # Charge le registry existant
        registry = {"forts": []}
        if os.path.exists(fichier_local):
            try:
                with open(fichier_local, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
            except:
                pass
        
        # Ajoute ou met à jour le fort
        found = False
        for i, fort in enumerate(registry["forts"]):
            if fort["fort_id"] == fort_info["fort_id"]:
                registry["forts"][i] = fort_info
                found = True
                break
        
        if not found:
            registry["forts"].append(fort_info)
        
        # Sauvegarde
        try:
            with open(fichier_local, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erreur sauvegarde locale: {e}")
    
    def get_statistiques(self) -> Dict:
        """Statistiques du résolveur P2P"""
        stats_p2p = self.decouverte_p2p.get_statistiques()
        
        return {
            "type_resolveur": "P2P_DECENTRALISE",
            "conformite_manifeste": True,
            "dependances_geants": False,
            "cache_local": len(self.cache_local),
            "seeds_communautaires": len(self.seeds_communautaires),
            "p2p_stats": stats_p2p,
            "running": self.running
        }
    
    def lister_forts_connus(self) -> List[Dict]:
        """Liste tous les forts connus"""
        forts = []
        
        # Forts du DHT P2P
        forts_p2p = self.decouverte_p2p.lister_forts_actifs()
        forts.extend(forts_p2p)
        
        # Forts du cache local
        for fort_id, entry in self.cache_local.items():
            fort_data = entry["data"]
            if fort_data not in forts:
                forts.append(fort_data)
        
        return forts


# Interface globale pour compatibilité
resolveur_global = None

def initialiser_resolveur_p2p():
    """Initialise le résolveur P2P décentralisé"""
    global resolveur_global
    
    if resolveur_global is None:
        print("🚀 Initialisation du résolveur P2P décentralisé...")
        resolveur_global = ResolveurP2PDecentralise()
        resolveur_global.demarrer()
    
    return resolveur_global

def resoudre_url_orp(url: str) -> Optional[Dict]:
    """Résout une URL orp:// via P2P"""
    resolveur = initialiser_resolveur_p2p()
    return resolveur.resoudre_orp(url)

def publier_fort(fort_info: Dict):
    """Publie un fort dans le réseau P2P"""
    resolveur = initialiser_resolveur_p2p()
    resolveur.publier_fort_local(fort_info)


if __name__ == "__main__":
    # Test du résolveur P2P
    print("🧪 === TEST RÉSOLVEUR P2P DÉCENTRALISÉ ===")
    
    resolveur = ResolveurP2PDecentralise()
    resolveur.demarrer()
    
    # Test de résolution
    test_url = "orp://test.fort/page"
    resultat = resolveur.resoudre_orp(test_url)
    
    if resultat:
        print(f"✅ URL résolue: {resultat['url_complete']}")
    else:
        print(f"❌ URL non résolue")
    
    # Statistiques
    stats = resolveur.get_statistiques()
    print(f"\n📊 Statistiques:")
    print(f"   Type: {stats['type_resolveur']}")
    print(f"   Conforme manifeste: {stats['conformite_manifeste']}")
    print(f"   Dépendances géants: {stats['dependances_geants']}")
    print(f"   Cache local: {stats['cache_local']} entrées")
    print(f"   Seeds communautaires: {stats['seeds_communautaires']}")
    
    try:
        print("\n⏳ Résolveur actif (Ctrl+C pour arrêter)")
        while True:
            time.sleep(30)
            stats = resolveur.get_statistiques()
            print(f"🔄 P2P: {stats['p2p_stats']['dht']['routing_table_size']} nœuds, "
                  f"{stats['p2p_stats']['forts_actifs']} forts actifs")
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du résolveur P2P")
        resolveur.arreter()