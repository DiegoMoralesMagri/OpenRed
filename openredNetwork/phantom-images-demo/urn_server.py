#!/usr/bin/env python3
"""
Serveur URN dédié - OpenRed
Ce serveur permet d'exposer les urns existantes sans générer de nouvelles urns à chaque lancement.
"""

# Copie du contenu original de phantom_urn_system.py
import os
import json
import hashlib
import secrets
from typing import Dict, List, Tuple, Optional, Any
from PIL import Image
import numpy as np
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64
import time
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

@dataclass
class AshFragment:
    color_rgb: Tuple[int, int, int]
    position: Tuple[int, int]
    next_fragment_name: str
    next_decrypt_key: bytes
    creation_timestamp: float

@dataclass
class UrnConfig:
    image_hash: str
    total_fragments: int
    image_dimensions: Tuple[int, int]
    creation_time: float
    authorized_node: str
    burn_after_reads: int = 1

class PhantomUrn:
    def __init__(self, urn_directory: str):
        self.urn_dir = Path(urn_directory)
        self.urn_dir.mkdir(exist_ok=True)
        self.activation_private_key = None
        self.activation_public_key = None
        self.config: Optional[UrnConfig] = None
        self.fragments_map: Dict[str, str] = {}
        self.is_active = False
        self.phoenix_matrix: Optional[np.ndarray] = None
        self.current_session_key: Optional[bytes] = None
        self._generate_activation_keys()
    def _generate_activation_keys(self):
        try:
            self.activation_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.activation_public_key = self.activation_private_key.public_key()
            logger.info("🔑 Clés d'activation URN générées")
        except Exception as e:
            logger.error(f"❌ Erreur génération clés: {e}")
    # ... (toutes les autres méthodes de PhantomUrn inchangées)

class PhantomAshSystem:
    """
    Système de gestion des urnes Phantom
    Interface principale pour burn & resurrection
    """
    def __init__(self, urns_root_dir: str = "./phantom_urns"):
        self.urns_root = Path(urns_root_dir)
        self.urns_root.mkdir(exist_ok=True)
        self.active_urns: Dict[str, PhantomUrn] = {}
    # SUPPRESSION de la méthode create_urn pour ne pas générer de nouvelles urns
    def activate_and_resurrect(self, urn_id: str, activation_key: bytes, first_fragment_info: Dict[str, str]) -> Optional[Image.Image]:
        try:
            if urn_id not in self.active_urns:
                urn_dir = self.urns_root / urn_id
                if not urn_dir.exists():
                    logger.error(f"❌ URN {urn_id} non trouvée")
                    return None
                urn = PhantomUrn(str(urn_dir))
                self._reload_urn_config(urn)
                self.active_urns[urn_id] = urn
            urn = self.active_urns[urn_id]
            if not urn.activate_urn(activation_key, first_fragment_info):
                return None
            phoenix_matrix = urn.resurrect_phoenix(first_fragment_info["name"])
            if phoenix_matrix is not None:
                return urn.get_phoenix_stream()
            return None
        except Exception as e:
            logger.error(f"❌ Erreur activation/résurrection: {e}")
            return None
    def _reload_urn_config(self, urn: PhantomUrn):
        config_path = urn.urn_dir / "urn_config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
                urn.config = UrnConfig(**config_dict)
    def cleanup_urn(self, urn_id: str):
        if urn_id in self.active_urns:
            self.active_urns[urn_id].burn_after_use()
            del self.active_urns[urn_id]

if __name__ == "__main__":

    import threading
    from flask import Flask, jsonify, request
    from schrodinger_phoenix_system import SchrodingerEngine

    logging.basicConfig(level=logging.INFO)
    print("🌀 Serveur URN Schrödinger Phoenix lancé.")

    app = Flask(__name__)
    ash_system = PhantomAshSystem("urns")
    schrodinger_engine = SchrodingerEngine("NodeB")

    @app.route("/phantom_matrix/<urn_id>", methods=["GET"])
    def get_phantom_matrix(urn_id):
        """🌀🦅 RÉSURRECTION SCHRÖDINGER PHOENIX ULTRA-RAPIDE"""
        try:
            logger.info(f"🌀 Demande matrice Phoenix: {urn_id}")
            
            # Vérifier si Schrödinger existe en cache
            status = schrodinger_engine.get_schrodinger_status(urn_id)
            
            if status["status"] == "not_found":
                # Générer Schrödinger depuis cendres (première fois)
                urn_dir = Path("urns") / urn_id
                if not urn_dir.exists():
                    return jsonify({"error": "URN not found"}), 404
                
                logger.info(f"🔥 Génération Schrödinger Phoenix: {urn_id}")
                schrodinger = schrodinger_engine.generate_schrodinger_from_ashes(urn_dir)
                if not schrodinger:
                    return jsonify({"error": "Schrödinger generation failed"}), 500
            
            # Résurrection Phoenix autorisée (ultra-rapide)
            phoenix_matrix = schrodinger_engine.request_phoenix_resurrection(urn_id, "http://NodeA")
            
            if phoenix_matrix is not None:
                # Encoder matrice Phoenix pour transmission
                matrix_json = {
                    "urn_id": urn_id,
                    "shape": phoenix_matrix.shape,
                    "dtype": str(phoenix_matrix.dtype),
                    "data": phoenix_matrix.flatten().tolist(),
                    "phoenix_status": "resurrected_quantum",
                    "method": "schrodinger_ultra_fast"
                }
                
                logger.info(f"✅ Phoenix ressuscité instantanément: {urn_id}")
                return jsonify(matrix_json)
            else:
                return jsonify({"error": "Phoenix resurrection unauthorized"}), 403
                
        except Exception as e:
            logger.error(f"❌ Erreur Schrödinger Phoenix {urn_id}: {e}")
            return jsonify({"error": f"Schrödinger error: {str(e)}"}), 500

    @app.route("/debug/schrodinger_cache", methods=["GET"])
    def debug_schrodinger_cache():
        """🌀 DEBUG: État du cache Schrödinger Phoenix"""
        cache_info = {}
        for urn_id, schrodinger in schrodinger_engine.phoenix_cache.items():
            cache_info[urn_id] = {
                "dimensions": schrodinger.dimensions,
                "encrypted_size_bytes": len(schrodinger.encrypted_matrix),
                "burn_after_reads": schrodinger.burn_after_reads,
                "creation_time": schrodinger.creation_timestamp,
                "status": "quantum_state"
            }
        return jsonify({
            "cache_count": len(cache_info),
            "schrodinger_phoenixes": cache_info
        })

    @app.route("/status", methods=["GET"])
    def status():
        urns = [d.name for d in Path("urns").iterdir() if d.is_dir()]
        return jsonify({
            "urn_count": len(urns),
            "urns": urns,
            "status": "active"
        })

    @app.route("/validate_urn_access", methods=["POST"])
    def validate_urn_access():
        data = request.get_json(force=True)
        urn_id = data.get("urn_id")
        filename = data.get("filename")
        urn_dir = Path("urns") / urn_id
        urn_config_path = urn_dir / "urn_config.json"
        if urn_config_path.exists():
            return jsonify({
                "validation_status": "success",
                "urn_id": urn_id,
                "filename": filename
            })
        else:
            return jsonify({
                "validation_status": "not_found",
                "urn_id": urn_id,
                "filename": filename
            }), 404


    @app.route("/phantom/<urn_id>", methods=["GET"])
    def get_phantom_image(urn_id):
        urn_dir = Path("urns") / urn_id
        urn_config_path = urn_dir / "urn_config.json"
        if not urn_config_path.exists():
            return jsonify({"error": "URN not found"}), 404

        # --- Simulation de reconstitution d'image ---
        # Si une image existe, retourne-la, sinon retourne une image factice
        image_path = urn_dir / "image.jpg"
        if image_path.exists():
            from flask import send_file
            return send_file(str(image_path), mimetype="image/jpeg")
        else:
            # Image factice: tableau numpy rempli d'une couleur
            import numpy as np
            from PIL import Image
            config = json.load(open(urn_config_path, 'r'))
            width, height = config.get('image_dimensions', [400, 300])
            dummy = np.full((height, width, 3), 200, dtype=np.uint8)  # gris clair
            img = Image.fromarray(dummy)
            import io
            buf = io.BytesIO()
            img.save(buf, format='JPEG')
            buf.seek(0)
            from flask import send_file
            return send_file(buf, mimetype="image/jpeg")

    def run_flask():
        app.run(host="0.0.0.0", port=9300)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Boucle passive pour garder le serveur en vie
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Arrêt du serveur URN.")
