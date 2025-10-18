#!/usr/bin/env python3
"""
🔐 Système de Validation Continue et Rotation des Clés URN
==========================================================

Extension du système P2P URN-PHANTOM avec :
- Validation continue Node A ↔ Node B
- Rotation automatique des clés d'activation
- Registre des clés par URN
- Vérification des autorisations en temps réel

Auteur: Diego Morales Magri
Innovation URN: 25 septembre 2025
"""

import os
import sys
import time
import json
import threading
import hashlib
import secrets
import base64
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import requests
from flask import Flask, send_file, jsonify, request
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk
from phantom_urn_system import PhantomUrn

class UrnKeyManager:
    """Gestionnaire de clés URN avec rotation automatique"""
    
    def __init__(self):
        self.urn_registry = {}  # urn_id -> key_info
        self.node_sessions = {}  # node_id -> session_info
        
    def register_urn(self, urn_id: str, node_id: str) -> dict:
        """Enregistrer une nouvelle URN avec génération des clés"""
        current_key = self._generate_activation_key()
        next_key = self._generate_activation_key()
        
        key_info = {
            "urn_id": urn_id,
            "owner_node": node_id,
            "current_key": current_key,
            "next_key": next_key,
            "created_at": datetime.now().isoformat(),
            "last_validation": None,
            "validation_count": 0,
            "authorized_nodes": set(),
            "status": "active"
        }
        
        self.urn_registry[urn_id] = key_info
        
        print(f"🔑 URN {urn_id[:8]}... enregistrée avec rotation des clés")
        return key_info
    
    def authorize_node_for_urn(self, urn_id: str, node_id: str) -> bool:
        """Autoriser un nœud pour une URN spécifique"""
        if urn_id not in self.urn_registry:
            return False
        
        self.urn_registry[urn_id]["authorized_nodes"].add(node_id)
        print(f"🔐 Node {node_id} autorisé pour URN {urn_id[:8]}...")
        return True
    
    def validate_and_rotate_key(self, urn_id: str, node_id: str, current_session_key: str = None) -> dict:
        """Valider l'accès et effectuer rotation des clés"""
        if urn_id not in self.urn_registry:
            return {"status": "error", "message": "URN not found"}
        
        urn_info = self.urn_registry[urn_id]
        
        # Vérifier autorisation
        if node_id not in urn_info["authorized_nodes"]:
            return {"status": "error", "message": "Node not authorized"}
        
        # Vérifier statut URN
        if urn_info["status"] != "active":
            return {"status": "error", "message": "URN not active"}
        
        # Effectuer rotation des clés
        old_current = urn_info["current_key"]
        urn_info["current_key"] = urn_info["next_key"]
        urn_info["next_key"] = self._generate_activation_key()
        urn_info["last_validation"] = datetime.now().isoformat()
        urn_info["validation_count"] += 1
        
        # Enregistrer session
        session_id = self._generate_session_id()
        self.node_sessions[node_id] = {
            "session_id": session_id,
            "urn_id": urn_id,
            "current_key": urn_info["current_key"],
            "expires_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
            "validation_count": urn_info["validation_count"]
        }
        
        print(f"🔄 Rotation clés URN {urn_id[:8]}... pour {node_id} (validation #{urn_info['validation_count']})")
        
        return {
            "status": "success",
            "session_id": session_id,
            "activation_key": urn_info["current_key"],
            "next_validation_required": True,
            "validation_count": urn_info["validation_count"],
            "expires_at": self.node_sessions[node_id]["expires_at"]
        }
    
    def get_urn_status(self, urn_id: str) -> dict:
        """Obtenir le statut d'une URN"""
        if urn_id not in self.urn_registry:
            return {"exists": False}
        
        urn_info = self.urn_registry[urn_id]
        return {
            "exists": True,
            "status": urn_info["status"],
            "validation_count": urn_info["validation_count"],
            "last_validation": urn_info["last_validation"],
            "authorized_nodes_count": len(urn_info["authorized_nodes"])
        }
    
    def _generate_activation_key(self) -> str:
        """Générer une nouvelle clé d'activation"""
        key_data = secrets.token_bytes(32)
        return base64.urlsafe_b64encode(key_data).decode()
    
    def _generate_session_id(self) -> str:
        """Générer un ID de session unique"""
        return secrets.token_urlsafe(16)

class NodeA_SecureServer:
    """Node A avec validation continue et rotation des clés"""
    
    def __init__(self, port=9300):
        self.port = port
        self.app = Flask(__name__)
        self.urn = PhantomUrn("node_a_secure_urns")
        self.key_manager = UrnKeyManager()
        self.authorized_nodes = set()
        self.real_image_path = "shared-images/test_real_image.jpg"
        self.orp_files = []
        self.urn_mappings = {}  # filename -> urn_id
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.route('/authorize_node', methods=['POST'])
        def authorize_node():
            data = request.get_json()
            node_id = data.get('node_id')
            if node_id:
                self.authorized_nodes.add(node_id)
                print(f"🔑 Node A: Autorisation initiale accordée à {node_id}")
                return jsonify({"status": "authorized", "node_id": node_id})
            return jsonify({"error": "node_id required"}), 400
        
        @self.app.route('/validate_urn_access', methods=['POST'])
        def validate_urn_access():
            """Validation continue avec rotation des clés"""
            data = request.get_json()
            node_id = request.headers.get('Node-ID')
            urn_id = data.get('urn_id')
            filename = data.get('filename')
            
            if not node_id or not urn_id:
                return jsonify({"error": "missing parameters"}), 400
            
            # Vérifier autorisation de base
            if node_id not in self.authorized_nodes:
                return jsonify({"error": "node not authorized"}), 401
            
            # Vérifier existence fichier (chercher dans tous les mappings)
            file_found = False
            if filename:
                for mapped_file, mapped_urn in self.urn_mappings.items():
                    if mapped_urn == urn_id or filename in mapped_file:
                        file_found = True
                        break
                if not file_found and filename not in self.urn_mappings:
                    print(f"⚠️  Fichier {filename} non trouvé dans mappings, autorisation URN quand même")
                    # Ne pas bloquer - autoriser la validation URN
            
            # Autoriser nœud pour cette URN si pas déjà fait
            if urn_id not in self.key_manager.urn_registry:
                # Première fois - enregistrer URN
                self.key_manager.register_urn(urn_id, "NodeA")
            
            self.key_manager.authorize_node_for_urn(urn_id, node_id)
            
            # Effectuer validation et rotation
            result = self.key_manager.validate_and_rotate_key(urn_id, node_id)
            
            if result["status"] == "success":
                print(f"✅ Validation URN réussie pour {node_id} - Nouvelle clé envoyée")
                return jsonify({
                    "validation_status": "success",
                    "server_status": "online",
                    "urn_exists": True,
                    "authorization_valid": True,
                    **result
                })
            else:
                return jsonify({"validation_status": "failed", **result}), 403
        
        @self.app.route('/list_files', methods=['GET'])
        def list_files():
            node_id = request.headers.get('Node-ID')
            if node_id not in self.authorized_nodes:
                return jsonify({"error": "unauthorized"}), 401
            
            files = []
            for f in self.orp_files:
                if os.path.exists(f):
                    urn_id = self.urn_mappings.get(f, "unknown")
                    urn_status = self.key_manager.get_urn_status(urn_id)
                    
                    files.append({
                        "filename": f,
                        "size": os.path.getsize(f),
                        "urn_protected": True,
                        "urn_id": urn_id,
                        "urn_status": urn_status,
                        "requires_continuous_validation": True,
                        "classification": "USER_IMAGE",
                        "description": "Image utilisateur avec validation continue"
                    })
            
            return jsonify({"files": files, "node": "A", "server": "Secure URN Server with Key Rotation"})
        
        @self.app.route('/download/<filename>', methods=['GET'])
        def download_file(filename):
            node_id = request.headers.get('Node-ID')
            if node_id not in self.authorized_nodes:
                return jsonify({"error": "unauthorized"}), 401
                
            if not filename.endswith('.orp') or not os.path.exists(filename):
                return jsonify({"error": "file not found"}), 404
            
            print(f"📤 Node A: Envoi {filename} vers {node_id}")
            return send_file(filename, as_attachment=True)
        
        @self.app.route('/status', methods=['GET'])
        def status():
            return jsonify({
                "node": "A",
                "port": self.port,
                "authorized_nodes": len(self.authorized_nodes),
                "urn_system": "active",
                "key_rotation": "enabled",
                "registered_urns": len(self.key_manager.urn_registry),
                "active_sessions": len(self.key_manager.node_sessions),
                "validation_system": "continuous"
            })
    
    def prepare_real_image_with_urn(self):
        """Préparer image avec système URN intégré"""
        print("🎨 Node A: Préparation image avec système URN sécurisé...")
        
        if not os.path.exists(self.real_image_path):
            print(f"❌ Image non trouvée: {self.real_image_path}")
            return False
        
        try:
            # Traitement image (identique à avant)
            img = Image.open(self.real_image_path)
            print(f"📷 Image chargée: {img.size} pixels")
            
            max_size = (150, 150)  # Plus petit pour test
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                print(f"📐 Redimensionnée à: {img.size}")
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Créer URN pour cette image
            temp_path = "temp_secure_image.png"
            img.save(temp_path)
            
            burn_result = self.urn.burn_image_to_ashes(temp_path, "NodeA_Secure")
            urn_id = burn_result['urn_id']
            
            # Enregistrer URN dans le gestionnaire de clés
            key_info = self.key_manager.register_urn(urn_id, "NodeA")
            
            # Créer fichier .orp avec URN ID
            orp_filename = "secure_real_document.orp"
            img_array = np.array(img)
            
            orp_data = {
                "version": "1.0",
                "phantom_id": "secure_real_img_001",
                "phantom_name": "secure_real_document",
                "urn_id": urn_id,  # Ajout URN ID
                "image_data": img_array.tolist(),
                "metadata": {
                    "classification": "SECURE_USER_IMAGE",
                    "owner": "Node A - Validation Continue",
                    "urn_protected": True,
                    "urn_id": urn_id,
                    "key_rotation_enabled": True,
                    "continuous_validation": True,
                    "created_by": "Diego Morales Magri",
                    "security_level": "MAXIMUM",
                    "projection_duration": 45,
                    "dimensions": {"width": img.size[0], "height": img.size[1]},
                    "burn_timestamp": burn_result['burn_timestamp'],
                    "fragments_count": burn_result['total_fragments']
                }
            }
            
            with open(orp_filename, 'w') as f:
                json.dump(orp_data, f, indent=2)
            
            self.orp_files.append(orp_filename)
            self.urn_mappings[orp_filename] = urn_id
            
            print(f"✅ Fichier .orp sécurisé créé: {orp_filename}")
            print(f"   URN ID: {urn_id}")
            print(f"   Fragments URN: {burn_result['total_fragments']}")
            print(f"   Rotation des clés: ACTIVE")
            
            # Cleanup
            os.remove(temp_path)
            return True
            
        except Exception as e:
            print(f"❌ Erreur préparation: {e}")
            return False
    
    def start_server(self):
        """Démarrer serveur sécurisé"""
        print(f"🚀 Node A: Serveur sécurisé avec rotation des clés sur port {self.port}")
        self.app.run(host='127.0.0.1', port=self.port, debug=False, use_reloader=False)

class NodeB_SecureClient:
    """Node B avec validation continue"""
    
    def __init__(self):
        self.node_id = "SecureUserNode_B"
        self.server_url = "http://127.0.0.1:9300"
        self.urn = PhantomUrn("node_b_secure_urns")
        self.root = None
        self.current_urn_id = None
        self.current_session = None
        self.validation_timer = None
        
    def create_secure_ui(self):
        """Interface avec validation continue"""
        self.root = tk.Tk()
        self.root.title("🔐 Node B - Client URN Sécurisé avec Validation Continue")
        self.root.geometry("700x600")
        self.root.configure(bg='#0d1117')
        
        # Titre
        title = tk.Label(self.root, 
                        text="🔐🔄 URN-PHANTOM Client avec Rotation des Clés", 
                        font=('Arial', 14, 'bold'), fg='#58a6ff', bg='#0d1117')
        title.pack(pady=15)
        
        # Statut validation continue
        self.validation_status_var = tk.StringVar(value="🔴 Validation continue: Inactive")
        validation_status = tk.Label(self.root, textvariable=self.validation_status_var,
                                   font=('Arial', 10, 'bold'), fg='#f85149', bg='#0d1117')
        validation_status.pack(pady=5)
        
        # Compteur validations
        self.validation_count_var = tk.StringVar(value="Validations: 0")
        validation_count = tk.Label(self.root, textvariable=self.validation_count_var,
                                  font=('Arial', 9), fg='#7d8590', bg='#0d1117')
        validation_count.pack()
        
        # Boutons
        btn_frame = tk.Frame(self.root, bg='#0d1117')
        btn_frame.pack(pady=20)
        
        self.connect_btn = tk.Button(btn_frame, text="🔗 Connexion Sécurisée", 
                                   command=self.secure_connect, font=('Arial', 10, 'bold'),
                                   bg='#238636', fg='white', relief='raised')
        self.connect_btn.pack(pady=5, fill='x')
        
        self.list_btn = tk.Button(btn_frame, text="📋 Lister Fichiers URN", 
                                command=self.list_secure_files, font=('Arial', 10),
                                bg='#0969da', fg='white', state='disabled')
        self.list_btn.pack(pady=5, fill='x')
        
        self.download_btn = tk.Button(btn_frame, text="📥 Téléchargement Sécurisé", 
                                    command=self.secure_download, font=('Arial', 10),
                                    bg='#8957e5', fg='white', state='disabled')
        self.download_btn.pack(pady=5, fill='x')
        
        self.open_btn = tk.Button(btn_frame, text="🔓 Ouverture avec Validation Continue", 
                                command=self.open_with_continuous_validation, font=('Arial', 10),
                                bg='#da3633', fg='white', state='disabled')
        self.open_btn.pack(pady=5, fill='x')
        
        # Log sécurisé
        log_frame = tk.LabelFrame(self.root, text="📝 Journal Sécurisé", fg='#f0f6fc', bg='#0d1117')
        log_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        self.log_text = tk.Text(log_frame, height=15, bg='#161b22', fg='#c9d1d9',
                               font=('Consolas', 8), insertbackground='#58a6ff')
        scrollbar = tk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Variables
        self.connected = False
        self.available_files = []
        self.selected_file = None
        self.downloaded_files = []
        
        self.log("🚀 Client URN sécurisé avec validation continue démarré")
        self.log("🔐 Système de rotation des clés prêt")
    
    def log(self, message):
        """Log avec horodatage"""
        timestamp = time.strftime("[%H:%M:%S]")
        full_message = f"{timestamp} {message}\n"
        
        if self.log_text:
            self.log_text.insert(tk.END, full_message)
            self.log_text.see(tk.END)
        print(full_message.strip())
    
    def secure_connect(self):
        """Connexion sécurisée avec Node A"""
        self.log("🔑 Établissement connexion sécurisée...")
        
        try:
            response = requests.post(
                f"{self.server_url}/authorize_node",
                json={"node_id": self.node_id},
                timeout=10
            )
            
            if response.status_code == 200:
                self.connected = True
                self.list_btn.config(state='normal')
                self.log("✅ Connexion sécurisée établie")
                self.log("🔐 Prêt pour validation continue")
            else:
                self.log(f"❌ Connexion refusée: {response.text}")
                
        except Exception as e:
            self.log(f"❌ Erreur connexion: {e}")
    
    def validate_urn_continuously(self, urn_id: str, filename: str):
        """Validation continue avec Node A"""
        if not self.connected or not urn_id:
            return False
        
        try:
            headers = {"Node-ID": self.node_id}
            data = {"urn_id": urn_id, "filename": filename}
            
            response = requests.post(
                f"{self.server_url}/validate_urn_access",
                json=data, headers=headers, timeout=10
            )
            
            if response.status_code == 200:
                validation_data = response.json()
                
                if validation_data.get("validation_status") == "success":
                    self.current_session = validation_data
                    count = validation_data.get("validation_count", 0)
                    
                    self.validation_status_var.set("🟢 Validation continue: Active")
                    self.validation_count_var.set(f"Validations: {count}")
                    
                    self.log(f"✅ Validation #{count} réussie - Nouvelle clé reçue")
                    self.log(f"🔄 Prochaine validation dans 30s")
                    
                    # Programmer prochaine validation
                    if self.validation_timer:
                        self.root.after_cancel(self.validation_timer)
                    self.validation_timer = self.root.after(30000, 
                        lambda: self.validate_urn_continuously(urn_id, filename))
                    
                    return True
                else:
                    self.log(f"❌ Validation échouée: {validation_data.get('message')}")
                    self.validation_status_var.set("🔴 Validation continue: Échec")
                    return False
            else:
                self.log(f"❌ Erreur serveur validation: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Erreur validation continue: {e}")
            self.validation_status_var.set("🔴 Validation continue: Erreur")
            return False
    
    def list_secure_files(self):
        """Lister fichiers avec info sécurité"""
        if not self.connected:
            return
        
        self.log("📋 Récupération fichiers sécurisés...")
        
        try:
            headers = {"Node-ID": self.node_id}
            response = requests.get(f"{self.server_url}/list_files", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.available_files = data.get('files', [])
                
                self.log(f"📁 {len(self.available_files)} fichier(s) URN trouvé(s):")
                for file_info in self.available_files:
                    self.log(f"   📄 {file_info['filename']}")
                    self.log(f"      🔐 URN ID: {file_info.get('urn_id', 'N/A')[:8]}...")
                    self.log(f"      🔄 Validation continue: {file_info.get('requires_continuous_validation')}")
                
                if self.available_files:
                    self.selected_file = self.available_files[0]
                    self.download_btn.config(state='normal')
                    
        except Exception as e:
            self.log(f"❌ Erreur liste: {e}")
    
    def secure_download(self):
        """Téléchargement sécurisé"""
        if not self.selected_file:
            return
        
        filename = self.selected_file['filename']
        self.log(f"📥 Téléchargement sécurisé {filename}...")
        
        try:
            headers = {"Node-ID": self.node_id}
            response = requests.get(
                f"{self.server_url}/download/{filename}",
                headers=headers, stream=True, timeout=30
            )
            
            if response.status_code == 200:
                local_filename = f"secure_{filename}"
                
                with open(local_filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.downloaded_files.append(local_filename)
                self.current_urn_id = self.selected_file.get('urn_id')
                
                self.log(f"✅ Téléchargement sécurisé terminé")
                self.log(f"🆔 URN ID: {self.current_urn_id[:8]}...")
                
                self.open_btn.config(state='normal')
                
        except Exception as e:
            self.log(f"❌ Erreur téléchargement: {e}")
    
    def open_with_continuous_validation(self):
        """Ouverture avec validation continue active"""
        if not self.downloaded_files or not self.current_urn_id:
            return
        
        filename = self.downloaded_files[-1]
        self.log(f"🔓 Ouverture avec validation continue...")
        
        # Démarrer validation continue
        if self.validate_urn_continuously(self.current_urn_id, filename):
            self.log("🔄 Validation continue démarrée")
            
            # Ouvrir le fichier (logique existante)
            try:
                with open(filename, 'r') as f:
                    orp_data = json.load(f)
                
                image_data = np.array(orp_data["image_data"], dtype=np.uint8)
                metadata = orp_data["metadata"]
                
                self.log("🖥️  Ouverture écran sécurisé avec validation continue...")
                self.open_validated_screen(image_data, metadata)
                
            except Exception as e:
                self.log(f"❌ Erreur ouverture: {e}")
    
    def open_validated_screen(self, image_data, metadata):
        """Écran sécurisé avec validation continue visible"""
        secure_window = tk.Toplevel(self.root)
        secure_window.title("🔐 ÉCRAN SÉCURISÉ - VALIDATION CONTINUE ACTIVE")
        secure_window.geometry("600x500")
        secure_window.configure(bg='#0d1117')
        secure_window.attributes('-topmost', True)
        
        # Header avec statut validation
        header = tk.Frame(secure_window, bg='#0d1117')
        header.pack(fill='x', padx=10, pady=5)
        
        validation_label = tk.Label(header, 
            text="🔄 VALIDATION CONTINUE ACTIVE - CLÉ ROTATION EN COURS",
            font=('Arial', 10, 'bold'), fg='#58a6ff', bg='#0d1117')
        validation_label.pack()
        
        status_label = tk.Label(header, textvariable=self.validation_status_var,
                              font=('Arial', 9), fg='#7d8590', bg='#0d1117')
        status_label.pack()
        
        count_label = tk.Label(header, textvariable=self.validation_count_var,
                             font=('Arial', 8), fg='#7d8590', bg='#0d1117')
        count_label.pack()
        
        # Image
        img_frame = tk.LabelFrame(secure_window, text="🖼️  Image Protégée URN", 
                                 fg='#f0f6fc', bg='#0d1117')
        img_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        img = Image.fromarray(image_data)
        img.thumbnail((400, 300))
        photo = ImageTk.PhotoImage(img)
        
        img_label = tk.Label(img_frame, image=photo, bg='#0d1117')
        img_label.photo = photo
        img_label.pack(expand=True)
        
        # Info sécurité
        info_text = f"""🔐 Protection URN Active
URN ID: {metadata.get('urn_id', 'N/A')[:16]}...
Fragments: {metadata.get('fragments_count', 'N/A')}
Validation Continue: ✅ ACTIVE
Rotation des Clés: ✅ ACTIVE"""
        
        info_label = tk.Label(secure_window, text=info_text, justify='left',
                            font=('Consolas', 8), fg='#c9d1d9', bg='#0d1117')
        info_label.pack(padx=10, pady=5)
        
        self.log("🖥️  Écran sécurisé ouvert avec validation continue")
    
    def run(self):
        """Démarrer client sécurisé"""
        self.create_secure_ui()
        
        # Cleanup à la fermeture
        def on_closing():
            if self.validation_timer:
                self.root.after_cancel(self.validation_timer)
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()

def start_secure_system():
    """Démarrer système P2P sécurisé avec validation continue"""
    print("🔐🔄 SYSTÈME P2P URN SÉCURISÉ - VALIDATION CONTINUE")
    print("Diego Morales Magri - Rotation des Clés URN")
    print("=" * 65)
    
    # Démarrer Node A sécurisé
    print("🚀 Démarrage Node A avec rotation des clés...")
    server = NodeA_SecureServer()
    
    if not server.prepare_real_image_with_urn():
        print("❌ Échec préparation image sécurisée")
        return
    
    # Serveur en thread
    server_thread = threading.Thread(target=server.start_server)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(3)
    
    # Vérifier serveur
    try:
        response = requests.get("http://127.0.0.1:9300/status", timeout=5)
        if response.status_code == 200:
            print("✅ Serveur sécurisé opérationnel")
        else:
            print("❌ Serveur non accessible")
            return
    except:
        print("❌ Erreur connexion serveur")
        return
    
    print("\n🎮 Démarrage client avec validation continue...")
    
    # Client sécurisé
    client = NodeB_SecureClient()
    
    try:
        client.run()
    except KeyboardInterrupt:
        print("\n🔚 Arrêt système sécurisé")
    except Exception as e:
        print(f"\n💥 Erreur: {e}")

if __name__ == "__main__":
    start_secure_system()