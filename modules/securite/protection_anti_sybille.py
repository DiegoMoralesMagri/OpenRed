#!/usr/bin/env python3
"""
🛡️ PROTECTION ANTI-SYBILLE OPENRED
=================================

Système de protection avancé contre les attaques Sybilles
et renforcement de la liaison cryptographique profils-fort.

Mécanismes de protection :
- Proof of Work pour création de fort
- Liaison cryptographique fort ↔ profils
- Validation de réputation P2P
- Détection de comportements suspects
- Blacklist distribuée

Conformité Manifeste OpenRed :
✅ Pas de serveur central de validation
✅ Validation distribuée P2P
✅ Coût computationnel pour création
✅ Réputation basée sur comportement
"""

import os
import json
import time
import hashlib
import secrets
import threading
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64


@dataclass
class ProofOfWork:
    """Preuve de travail pour création de fort légitime"""
    fort_id: str
    nonce: int
    difficulte: int
    hash_resultat: str
    timestamp: float
    temps_calcul: float  # Temps en secondes pour calculer
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProofOfWork':
        return cls(**data)


@dataclass
class SignatureFortProfil:
    """Signature cryptographique liant un profil à son fort"""
    fort_id: str
    profil_id: str
    cle_publique_fort: str
    timestamp_creation: float
    signature_liaison: str  # Signature fort_id + profil_id + timestamp
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SignatureFortProfil':
        return cls(**data)


@dataclass
class ReputationFort:
    """Réputation d'un fort dans le réseau P2P"""
    fort_id: str
    score_reputation: float  # 0.0 à 1.0
    validations_positives: int
    validations_negatives: int
    comportements_suspects: List[str]
    temps_activite: float  # Temps total d'activité en secondes
    connexions_legitimites: Set[str]  # Forts qui valident celui-ci
    derniere_activite: float
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'connexions_legitimites': list(self.connexions_legitimites)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ReputationFort':
        data['connexions_legitimites'] = set(data['connexions_legitimites'])
        return cls(**data)


class ProtectionAntiSybille:
    """
    Système de protection contre les attaques Sybilles
    
    Utilise plusieurs mécanismes complémentaires :
    1. Proof of Work pour création de fort
    2. Liaison cryptographique fort-profils
    3. Réputation distribuée P2P
    4. Détection de patterns suspects
    """
    
    def __init__(self, fort_id: str, cle_privee, cle_publique, dossier_donnees: str = ".openred_fort"):
        self.fort_id = fort_id
        self.cle_privee = cle_privee
        self.cle_publique = cle_publique
        self.dossier_donnees = dossier_donnees
        self.dossier_securite = os.path.join(dossier_donnees, "securite")
        
        # État en mémoire
        self.reputations: Dict[str, ReputationFort] = {}
        self.blacklist: Set[str] = set()
        self.forts_suspects: Dict[str, List[str]] = {}  # fort_id -> raisons
        self.signatures_profils: Dict[str, SignatureFortProfil] = {}
        
        # Configuration
        self.difficulte_pow = 4  # Nombre de zéros requis en début de hash
        self.seuil_reputation_minimum = 0.3
        self.max_connexions_par_ip = 5
        
        self._initialiser_securite()
        self._charger_donnees_securite()
    
    def _initialiser_securite(self):
        """Initialise la structure de sécurité"""
        os.makedirs(self.dossier_securite, exist_ok=True)
        
        # Fichiers de sécurité
        fichiers = ["reputations.json", "blacklist.json", "signatures_profils.json", "incidents.json"]
        for fichier in fichiers:
            chemin = os.path.join(self.dossier_securite, fichier)
            if not os.path.exists(chemin):
                with open(chemin, 'w') as f:
                    json.dump({}, f)
    
    def _charger_donnees_securite(self):
        """Charge les données de sécurité existantes"""
        try:
            # Charge les réputations
            fichier_reputations = os.path.join(self.dossier_securite, "reputations.json")
            if os.path.exists(fichier_reputations):
                with open(fichier_reputations, 'r') as f:
                    data = json.load(f)
                    for fort_id, rep_data in data.items():
                        self.reputations[fort_id] = ReputationFort.from_dict(rep_data)
            
            # Charge la blacklist
            fichier_blacklist = os.path.join(self.dossier_securite, "blacklist.json")
            if os.path.exists(fichier_blacklist):
                with open(fichier_blacklist, 'r') as f:
                    self.blacklist = set(json.load(f))
            
            # Charge les signatures profils
            fichier_signatures = os.path.join(self.dossier_securite, "signatures_profils.json")
            if os.path.exists(fichier_signatures):
                with open(fichier_signatures, 'r') as f:
                    data = json.load(f)
                    for profil_id, sig_data in data.items():
                        self.signatures_profils[profil_id] = SignatureFortProfil.from_dict(sig_data)
            
            print(f"🔐 Sécurité chargée: {len(self.reputations)} réputations, {len(self.blacklist)} blacklistés")
            
        except Exception as e:
            print(f"⚠️  Erreur chargement sécurité: {e}")
    
    def _sauvegarder_donnees_securite(self):
        """Sauvegarde les données de sécurité"""
        try:
            # Sauvegarde réputations
            fichier_reputations = os.path.join(self.dossier_securite, "reputations.json")
            data_reputations = {fort_id: rep.to_dict() for fort_id, rep in self.reputations.items()}
            with open(fichier_reputations, 'w') as f:
                json.dump(data_reputations, f, indent=2)
            
            # Sauvegarde blacklist
            fichier_blacklist = os.path.join(self.dossier_securite, "blacklist.json")
            with open(fichier_blacklist, 'w') as f:
                json.dump(list(self.blacklist), f, indent=2)
            
            # Sauvegarde signatures
            fichier_signatures = os.path.join(self.dossier_securite, "signatures_profils.json")
            data_signatures = {profil_id: sig.to_dict() for profil_id, sig in self.signatures_profils.items()}
            with open(fichier_signatures, 'w') as f:
                json.dump(data_signatures, f, indent=2)
                
        except Exception as e:
            print(f"❌ Erreur sauvegarde sécurité: {e}")
    
    def generer_proof_of_work(self, difficulte: Optional[int] = None) -> ProofOfWork:
        """
        Génère une preuve de travail pour le fort
        
        Augmente le coût de création d'identités multiples
        """
        if difficulte is None:
            difficulte = self.difficulte_pow
        
        print(f"⚡ Génération Proof of Work (difficulté: {difficulte} zéros)...")
        debut = time.time()
        
        nonce = 0
        cible = "0" * difficulte
        
        while True:
            # Données à hasher
            donnees = f"{self.fort_id}:{nonce}:{time.time()}"
            hash_resultat = hashlib.sha256(donnees.encode()).hexdigest()
            
            if hash_resultat.startswith(cible):
                temps_calcul = time.time() - debut
                
                pow_resultat = ProofOfWork(
                    fort_id=self.fort_id,
                    nonce=nonce,
                    difficulte=difficulte,
                    hash_resultat=hash_resultat,
                    timestamp=time.time(),
                    temps_calcul=temps_calcul
                )
                
                print(f"✅ Proof of Work généré en {temps_calcul:.2f}s")
                print(f"   Hash: {hash_resultat}")
                print(f"   Nonce: {nonce}")
                
                return pow_resultat
            
            nonce += 1
            
            # Affiche le progrès tous les 100000 essais
            if nonce % 100000 == 0:
                print(f"   🔄 Essai {nonce}...")
    
    def verifier_proof_of_work(self, pow_data: ProofOfWork) -> bool:
        """Vérifie une preuve de travail"""
        try:
            # Reconstitue les données
            donnees = f"{pow_data.fort_id}:{pow_data.nonce}:{pow_data.timestamp}"
            hash_calcule = hashlib.sha256(donnees.encode()).hexdigest()
            
            # Vérifie le hash
            cible = "0" * pow_data.difficulte
            
            valid = (
                hash_calcule == pow_data.hash_resultat and
                hash_calcule.startswith(cible) and
                pow_data.temps_calcul > 0.1  # Minimum 0.1 seconde
            )
            
            if valid:
                print(f"✅ Proof of Work valide pour {pow_data.fort_id}")
            else:
                print(f"❌ Proof of Work invalide pour {pow_data.fort_id}")
            
            return valid
            
        except Exception as e:
            print(f"❌ Erreur vérification PoW: {e}")
            return False
    
    def lier_profil_fort(self, profil_id: str) -> SignatureFortProfil:
        """
        Crée une liaison cryptographique entre profil et fort
        
        Empêche la copie/transfert de profils entre forts
        """
        print(f"🔗 Liaison cryptographique profil {profil_id} ↔ fort {self.fort_id}")
        
        # Données à signer
        timestamp = time.time()
        donnees_liaison = f"{self.fort_id}:{profil_id}:{timestamp}"
        donnees_bytes = donnees_liaison.encode('utf-8')
        
        # Signature avec clé privée du fort
        signature = self.cle_privee.sign(
            donnees_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Encodage de la signature
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        # Clé publique du fort (pour vérification)
        cle_publique_pem = self.cle_publique.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        # Crée la signature de liaison
        signature_liaison = SignatureFortProfil(
            fort_id=self.fort_id,
            profil_id=profil_id,
            cle_publique_fort=cle_publique_pem,
            timestamp_creation=timestamp,
            signature_liaison=signature_b64
        )
        
        # Stocke la signature
        self.signatures_profils[profil_id] = signature_liaison
        self._sauvegarder_donnees_securite()
        
        print(f"✅ Profil {profil_id} lié cryptographiquement au fort {self.fort_id}")
        
        return signature_liaison
    
    def verifier_liaison_profil_fort(self, profil_id: str, fort_id_suppose: str, 
                                   signature_liaison: SignatureFortProfil) -> bool:
        """
        Vérifie qu'un profil appartient bien au fort revendiqué
        """
        try:
            # Vérifie les IDs
            if (signature_liaison.fort_id != fort_id_suppose or
                signature_liaison.profil_id != profil_id):
                print(f"❌ IDs ne correspondent pas")
                return False
            
            # Reconstitue les données signées
            donnees_liaison = f"{signature_liaison.fort_id}:{signature_liaison.profil_id}:{signature_liaison.timestamp_creation}"
            donnees_bytes = donnees_liaison.encode('utf-8')
            
            # Charge la clé publique
            cle_publique = serialization.load_pem_public_key(
                signature_liaison.cle_publique_fort.encode('utf-8')
            )
            
            # Décode la signature
            signature_bytes = base64.b64decode(signature_liaison.signature_liaison)
            
            # Vérifie la signature
            cle_publique.verify(
                signature_bytes,
                donnees_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            print(f"✅ Liaison profil-fort vérifiée: {profil_id} ↔ {fort_id_suppose}")
            return True
            
        except Exception as e:
            print(f"❌ Liaison profil-fort invalide: {e}")
            return False
    
    def calculer_reputation(self, fort_id: str) -> float:
        """Calcule le score de réputation d'un fort"""
        if fort_id in self.blacklist:
            return 0.0
        
        if fort_id not in self.reputations:
            # Nouveau fort = réputation neutre
            return 0.5
        
        rep = self.reputations[fort_id]
        
        # Calcul basé sur plusieurs facteurs
        facteurs = []
        
        # 1. Ratio validations positives/négatives
        total_validations = rep.validations_positives + rep.validations_negatives
        if total_validations > 0:
            ratio_positif = rep.validations_positives / total_validations
            facteurs.append(ratio_positif * 0.4)
        
        # 2. Temps d'activité (plus ancien = plus fiable)
        age_jours = (time.time() - rep.derniere_activite) / (24 * 3600)
        if age_jours < 30:  # Moins de 30 jours = nouveau
            facteur_age = min(age_jours / 30, 1.0) * 0.2
        else:
            facteur_age = 0.2
        facteurs.append(facteur_age)
        
        # 3. Nombre de connexions légitimes
        nb_connexions = len(rep.connexions_legitimites)
        facteur_connexions = min(nb_connexions / 10, 1.0) * 0.2
        facteurs.append(facteur_connexions)
        
        # 4. Absence de comportements suspects
        if len(rep.comportements_suspects) == 0:
            facteurs.append(0.2)
        else:
            facteur_suspect = max(0, 0.2 - len(rep.comportements_suspects) * 0.05)
            facteurs.append(facteur_suspect)
        
        score_final = sum(facteurs)
        
        # Met à jour le score
        rep.score_reputation = min(max(score_final, 0.0), 1.0)
        
        return rep.score_reputation
    
    def detecter_comportement_suspect(self, fort_id: str, ip_source: str, 
                                    pattern: str, details: str):
        """Détecte et enregistre un comportement suspect"""
        if fort_id not in self.reputations:
            self.reputations[fort_id] = ReputationFort(
                fort_id=fort_id,
                score_reputation=0.5,
                validations_positives=0,
                validations_negatives=0,
                comportements_suspects=[],
                temps_activite=0.0,
                connexions_legitimites=set(),
                derniere_activite=time.time()
            )
        
        rep = self.reputations[fort_id]
        
        # Enregistre le comportement suspect
        incident = f"{datetime.now().isoformat()}:{pattern}:{details}:{ip_source}"
        rep.comportements_suspects.append(incident)
        
        # Si trop de comportements suspects, blacklist temporaire
        if len(rep.comportements_suspects) > 5:
            self.blacklist.add(fort_id)
            print(f"⚠️  Fort {fort_id} ajouté à la blacklist (trop de comportements suspects)")
        
        self._sauvegarder_donnees_securite()
        print(f"🚨 Comportement suspect détecté: {fort_id} - {pattern}")
    
    def valider_fort_legitime(self, fort_id: str) -> bool:
        """
        Valide qu'un fort est légitime selon tous les critères
        """
        # 1. Pas dans la blacklist
        if fort_id in self.blacklist:
            print(f"❌ Fort {fort_id} blacklisté")
            return False
        
        # 2. Réputation suffisante
        reputation = self.calculer_reputation(fort_id)
        if reputation < self.seuil_reputation_minimum:
            print(f"❌ Fort {fort_id} réputation insuffisante: {reputation}")
            return False
        
        # 3. Pas trop de connexions depuis la même IP (à implémenter avec données réseau)
        
        print(f"✅ Fort {fort_id} validé comme légitime (réputation: {reputation})")
        return True
    
    def obtenir_statistiques_securite(self) -> Dict:
        """Obtient les statistiques de sécurité"""
        stats = {
            "total_reputations": len(self.reputations),
            "blacklist_size": len(self.blacklist),
            "signatures_profils": len(self.signatures_profils),
            "seuil_reputation": self.seuil_reputation_minimum,
            "difficulte_pow": self.difficulte_pow,
            "forts_legitimes": 0,
            "forts_suspects": 0,
            "reputation_moyenne": 0.0
        }
        
        scores = []
        for fort_id, rep in self.reputations.items():
            score = self.calculer_reputation(fort_id)
            scores.append(score)
            
            if score >= self.seuil_reputation_minimum:
                stats["forts_legitimes"] += 1
            else:
                stats["forts_suspects"] += 1
        
        if scores:
            stats["reputation_moyenne"] = sum(scores) / len(scores)
        
        return stats


def demo_protection_anti_sybille():
    """Démonstration du système de protection anti-Sybille"""
    print("🛡️ === DÉMONSTRATION PROTECTION ANTI-SYBILLE ===")
    
    # Simule des clés RSA pour le test
    cle_privee = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    cle_publique = cle_privee.public_key()
    
    # Initialise la protection
    protection = ProtectionAntiSybille(
        fort_id="fort_demo_securise",
        cle_privee=cle_privee,
        cle_publique=cle_publique
    )
    
    print("\n1️⃣ === TEST PROOF OF WORK ===")
    # Génère une preuve de travail
    pow_resultat = protection.generer_proof_of_work(difficulte=3)  # Plus facile pour demo
    
    # Vérifie la preuve
    valid = protection.verifier_proof_of_work(pow_resultat)
    print(f"Validation PoW: {'✅ Valide' if valid else '❌ Invalide'}")
    
    print("\n2️⃣ === TEST LIAISON PROFIL-FORT ===")
    # Lie des profils au fort
    profils_test = ["famille_demo123", "amis_demo456", "pro_demo789"]
    
    for profil_id in profils_test:
        signature = protection.lier_profil_fort(profil_id)
        
        # Vérifie la liaison
        valid = protection.verifier_liaison_profil_fort(
            profil_id, 
            "fort_demo_securise", 
            signature
        )
        print(f"Validation liaison {profil_id}: {'✅ Valide' if valid else '❌ Invalide'}")
    
    print("\n3️⃣ === TEST RÉPUTATION ===")
    # Simule des interactions
    forts_test = ["fort_alice", "fort_bob", "fort_charlie", "fort_suspect"]
    
    for fort_id in forts_test:
        if fort_id == "fort_suspect":
            # Simule comportements suspects
            protection.detecter_comportement_suspect(
                fort_id, 
                "192.168.1.100", 
                "SPAM_CONNECTIONS", 
                "Plus de 100 connexions/minute"
            )
            protection.detecter_comportement_suspect(
                fort_id,
                "192.168.1.100",
                "FAKE_PROFILES",
                "Création massive de profils"
            )
        
        reputation = protection.calculer_reputation(fort_id)
        legitime = protection.valider_fort_legitime(fort_id)
        
        print(f"Fort {fort_id}: Réputation={reputation:.2f}, Légitime={'✅' if legitime else '❌'}")
    
    print("\n4️⃣ === STATISTIQUES SÉCURITÉ ===")
    stats = protection.obtenir_statistiques_securite()
    for cle, valeur in stats.items():
        print(f"   {cle}: {valeur}")
    
    print("\n🎉 Démonstration terminée!")
    return protection


if __name__ == "__main__":
    demo_protection_anti_sybille()