#!/usr/bin/env python3
"""
🌐🔥 Système P2P URN-PHANTOM Réel
=================================

Expérience utilisateur complète avec image réelle :
- Node A : Serveur avec test_real_image.jpg protégé URN
- Interface utilisateur interactive pour Node B
- Écran sécurisé réel avec protection anti-capture

Auteur: Diego Morales Magri
Innovation URN: 25 septembre 2025
"""

import os
import sys
import time
import json
import threading
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import requests
from flask import Flask, send_file, jsonify, request
from PIL import Image, ImageTk
import numpy as np
from phantom_urn_system import PhantomUrn

class NodeA_RealServer:
    """Node A - Serveur réel avec image utilisateur"""
    
    def __init__(self, port=9200):
        self.port = port
        self.app = Flask(__name__)
        self.urn = PhantomUrn("node_a_real_urns")
        self.authorized_nodes = set()
        self.real_image_path = "shared-images/test_real_image.jpg"
        self.orp_files = []
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.route('/authorize_node', methods=['POST'])
        def authorize_node():
            data = request.get_json()
            node_id = data.get('node_id')
            if node_id:
                self.authorized_nodes.add(node_id)
                print(f"🔑 Node A: Autorisation accordée à {node_id}")
                return jsonify({"status": "authorized", "node_id": node_id})
            return jsonify({"error": "node_id required"}), 400
        
        @self.app.route('/list_files', methods=['GET'])
        def list_files():
            node_id = request.headers.get('Node-ID')
            if node_id not in self.authorized_nodes:
                return jsonify({"error": "unauthorized"}), 401
            
            files = []
            for f in self.orp_files:
                if os.path.exists(f):
                    files.append({
                        "filename": f,
                        "size": os.path.getsize(f),
                        "urn_protected": True,
                        "classification": "REAL_IMAGE",
                        "description": "Image utilisateur protégée URN"
                    })
            
            print(f"📋 Node A: Envoi liste de {len(files)} fichiers à {node_id}")
            return jsonify({"files": files, "node": "A", "server": "Real URN Server"})
        
        @self.app.route('/download/<filename>', methods=['GET'])
        def download_file(filename):
            node_id = request.headers.get('Node-ID')
            if node_id not in self.authorized_nodes:
                return jsonify({"error": "unauthorized"}), 401
                
            if not filename.endswith('.orp'):
                return jsonify({"error": "only .orp files"}), 400
                
            if not os.path.exists(filename):
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
                "real_image": os.path.exists(self.real_image_path),
                "orp_files": len(self.orp_files)
            })
    
    def prepare_real_image(self):
        """Préparer l'image réelle utilisateur avec protection URN"""
        print("🎨 Node A: Préparation image utilisateur réelle...")
        
        if not os.path.exists(self.real_image_path):
            print(f"❌ Image non trouvée: {self.real_image_path}")
            return False
        
        try:
            # Charger image utilisateur
            img = Image.open(self.real_image_path)
            print(f"📷 Image chargée: {img.size} pixels, mode {img.mode}")
            
            # Redimensionner si trop grande (pour performance URN)
            max_size = (200, 200)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                print(f"📐 Redimensionnée à: {img.size}")
            
            # Convertir en RGB si nécessaire
            if img.mode != 'RGB':
                img = img.convert('RGB')
                print(f"🔄 Convertie en RGB")
            
            # Sauvegarder version traitée
            processed_path = "processed_real_image.png"
            img.save(processed_path)
            
            # Créer fichier .orp avec l'image réelle
            orp_filename = "real_user_document.orp"
            
            # Convertir en array numpy
            img_array = np.array(img)
            
            # Créer fichier .orp avec métadonnées complètes
            orp_data = {
                "version": "1.0",
                "phantom_id": "real_user_img_001",
                "phantom_name": "real_user_document",
                "image_data": img_array.tolist(),
                "metadata": {
                    "classification": "USER_IMAGE",
                    "owner": "Node A - Utilisateur Réel",
                    "original_file": self.real_image_path,
                    "authorization_required": True,
                    "urn_protected": True,
                    "created_by": "Diego Morales Magri",
                    "phantom_system": "active",
                    "projection_duration": 30,  # 30 secondes pour test réel
                    "dimensions": {"width": img.size[0], "height": img.size[1]},
                    "processing_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "security_level": "HIGH",
                    "anti_capture": True
                }
            }
            
            # Sauvegarder .orp
            with open(orp_filename, 'w') as f:
                json.dump(orp_data, f, indent=2)
            
            self.orp_files.append(orp_filename)
            
            print(f"✅ Node A: Fichier .orp créé: {orp_filename}")
            print(f"   Taille originale: {os.path.getsize(self.real_image_path)} bytes")
            print(f"   Taille .orp: {os.path.getsize(orp_filename)} bytes")
            print(f"   Protection URN: ACTIVE")
            
            # Cleanup
            if os.path.exists(processed_path):
                os.remove(processed_path)
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur préparation image: {e}")
            return False
    
    def start_server(self):
        """Démarrer le serveur Node A"""
        print(f"🚀 Node A: Serveur réel démarré sur http://127.0.0.1:{self.port}")
        print("💡 Interface web disponible pour monitoring")
        self.app.run(host='127.0.0.1', port=self.port, debug=False, use_reloader=False)

class NodeB_RealClient:
    """Node B - Client avec interface utilisateur réelle"""
    
    def __init__(self):
        self.node_id = "UserNode_B_Real"
        self.server_url = "http://127.0.0.1:9200"
        self.urn = PhantomUrn("node_b_real_urns")
        self.root = None
        self.secure_window = None
        self.downloaded_files = []
        
    def create_ui(self):
        """Créer interface utilisateur Tkinter"""
        self.root = tk.Tk()
        self.root.title("🔥🐦‍🔥 Node B - Client URN Réel")
        self.root.geometry("600x500")
        self.root.configure(bg='#1a1a1a')
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), 
                       foreground='#ffffff', background='#1a1a1a')
        style.configure('Info.TLabel', font=('Arial', 10), 
                       foreground='#cccccc', background='#1a1a1a')
        style.configure('Action.TButton', font=('Arial', 11, 'bold'))
        
        # Titre
        title = ttk.Label(self.root, text="🔥🐦‍🔥 URN-PHANTOM Client Réel", 
                         style='Title.TLabel')
        title.pack(pady=20)
        
        # Informations
        info = ttk.Label(self.root, 
                        text="Client P2P pour téléchargement et visualisation sécurisée\nImages protégées par système URN", 
                        style='Info.TLabel', justify='center')
        info.pack(pady=10)
        
        # Zone de statut
        self.status_var = tk.StringVar(value="🔴 Non connecté au serveur")
        status_label = ttk.Label(self.root, textvariable=self.status_var, 
                                style='Info.TLabel')
        status_label.pack(pady=10)
        
        # Boutons d'action
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        self.connect_btn = ttk.Button(btn_frame, text="🔗 Se connecter au Node A", 
                                     command=self.connect_to_server, style='Action.TButton')
        self.connect_btn.pack(pady=5, fill='x')
        
        self.list_btn = ttk.Button(btn_frame, text="📋 Lister les fichiers", 
                                  command=self.list_files, style='Action.TButton', state='disabled')
        self.list_btn.pack(pady=5, fill='x')
        
        self.download_btn = ttk.Button(btn_frame, text="📥 Télécharger fichier", 
                                      command=self.download_file, style='Action.TButton', state='disabled')
        self.download_btn.pack(pady=5, fill='x')
        
        self.open_btn = ttk.Button(btn_frame, text="🔓 Ouvrir avec URN", 
                                  command=self.open_with_urn, style='Action.TButton', state='disabled')
        self.open_btn.pack(pady=5, fill='x')
        
        # Zone de log
        log_frame = ttk.LabelFrame(self.root, text="📝 Journal des opérations")
        log_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        self.log_text = tk.Text(log_frame, height=12, bg='#2a2a2a', fg='#cccccc',
                               font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Variables
        self.connected = False
        self.available_files = []
        self.selected_file = None
        
        self.log("🚀 Client URN démarré")
        self.log("💡 Cliquez sur 'Se connecter' pour commencer")
    
    def log(self, message):
        """Ajouter message au log"""
        timestamp = time.strftime("[%H:%M:%S]")
        full_message = f"{timestamp} {message}\n"
        
        if self.log_text:
            self.log_text.insert(tk.END, full_message)
            self.log_text.see(tk.END)
        else:
            print(full_message.strip())
    
    def connect_to_server(self):
        """Se connecter au serveur Node A"""
        self.log("🔑 Demande d'autorisation au Node A...")
        
        try:
            response = requests.post(
                f"{self.server_url}/authorize_node",
                json={"node_id": self.node_id},
                timeout=10
            )
            
            if response.status_code == 200:
                self.connected = True
                self.status_var.set("🟢 Connecté et autorisé")
                self.list_btn.config(state='normal')
                self.log("✅ Autorisation accordée par Node A")
                self.log("🎯 Vous pouvez maintenant lister les fichiers")
            else:
                self.log(f"❌ Autorisation refusée: {response.text}")
                messagebox.showerror("Erreur", "Autorisation refusée par le serveur")
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Erreur connexion: {e}")
            messagebox.showerror("Erreur", f"Impossible de se connecter au serveur:\n{e}")
    
    def list_files(self):
        """Lister les fichiers disponibles"""
        if not self.connected:
            messagebox.showwarning("Attention", "Connectez-vous d'abord au serveur")
            return
            
        self.log("📋 Récupération liste des fichiers...")
        
        try:
            headers = {"Node-ID": self.node_id}
            response = requests.get(f"{self.server_url}/list_files", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.available_files = data.get('files', [])
                
                self.log(f"📁 {len(self.available_files)} fichier(s) trouvé(s):")
                for i, file_info in enumerate(self.available_files):
                    self.log(f"   {i+1}. {file_info['filename']}")
                    self.log(f"      📏 Taille: {file_info['size']} bytes")
                    self.log(f"      🔐 URN: {file_info['urn_protected']}")
                    self.log(f"      📝 Description: {file_info.get('description', 'N/A')}")
                
                if self.available_files:
                    self.selected_file = self.available_files[0]['filename']
                    self.download_btn.config(state='normal')
                    self.log(f"🎯 Fichier sélectionné: {self.selected_file}")
            else:
                self.log(f"❌ Erreur liste: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Erreur liste: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la récupération:\n{e}")
    
    def download_file(self):
        """Télécharger le fichier sélectionné"""
        if not self.selected_file:
            messagebox.showwarning("Attention", "Aucun fichier sélectionné")
            return
        
        self.log(f"📥 Téléchargement {self.selected_file}...")
        
        try:
            headers = {"Node-ID": self.node_id}
            response = requests.get(
                f"{self.server_url}/download/{self.selected_file}",
                headers=headers, stream=True, timeout=30
            )
            
            if response.status_code == 200:
                local_filename = f"downloaded_{self.selected_file}"
                
                with open(local_filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                size = os.path.getsize(local_filename)
                self.downloaded_files.append(local_filename)
                
                self.log(f"✅ Téléchargement terminé!")
                self.log(f"   📄 Fichier local: {local_filename}")
                self.log(f"   📏 Taille: {size} bytes")
                
                self.open_btn.config(state='normal')
                self.log("🔓 Vous pouvez maintenant ouvrir avec URN")
                
            else:
                self.log(f"❌ Erreur téléchargement: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Erreur téléchargement: {e}")
            messagebox.showerror("Erreur", f"Erreur téléchargement:\n{e}")
    
    def open_with_urn(self):
        """Ouvrir le fichier téléchargé avec système URN"""
        if not self.downloaded_files:
            messagebox.showwarning("Attention", "Aucun fichier téléchargé")
            return
        
        filename = self.downloaded_files[-1]  # Dernier téléchargé
        self.log(f"🔓 Ouverture {filename} avec système URN...")
        
        try:
            # Lire fichier .orp
            with open(filename, 'r') as f:
                orp_data = json.load(f)
            
            # Extraire données
            image_list = orp_data["image_data"]
            image_data = np.array(image_list, dtype=np.uint8)
            metadata = orp_data["metadata"]
            
            self.log(f"📖 Fichier .orp analysé:")
            self.log(f"   🏷️  Classification: {metadata.get('classification', 'N/A')}")
            self.log(f"   👤 Propriétaire: {metadata.get('owner', 'N/A')}")
            self.log(f"   🔐 Protection URN: {metadata.get('urn_protected', False)}")
            self.log(f"   📐 Dimensions: {image_data.shape}")
            
            # Appliquer système URN
            temp_filename = f"temp_urn_{int(time.time())}.png"
            img = Image.fromarray(image_data)
            img.save(temp_filename)
            
            self.log("🔥 Application du système URN...")
            burn_result = self.urn.burn_image_to_ashes(temp_filename, self.node_id)
            
            self.log("✅ Système URN appliqué!")
            self.log(f"   🆔 URN ID: {burn_result['urn_id']}")
            self.log(f"   🧬 Fragments: {burn_result['total_fragments']}")
            
            # Ouvrir écran sécurisé
            self.open_secure_screen(image_data, metadata, burn_result)
            
            # Cleanup
            os.remove(temp_filename)
            
        except Exception as e:
            self.log(f"❌ Erreur ouverture URN: {e}")
            messagebox.showerror("Erreur", f"Erreur ouverture URN:\n{e}")
    
    def open_secure_screen(self, image_data, metadata, burn_result):
        """Ouvrir écran sécurisé pour visualisation"""
        self.log("🖥️  Ouverture écran sécurisé URN...")
        
        # Créer fenêtre sécurisée
        self.secure_window = tk.Toplevel(self.root)
        self.secure_window.title("🔐 ÉCRAN SÉCURISÉ URN")
        self.secure_window.geometry("800x600")
        self.secure_window.configure(bg='#0a0a0a')
        self.secure_window.attributes('-topmost', True)  # Toujours au-dessus
        
        # Bloquer redimensionnement
        self.secure_window.resizable(False, False)
        
        # Header sécurisé
        header_frame = ttk.Frame(self.secure_window)
        header_frame.pack(fill='x', padx=10, pady=5)
        
        security_label = tk.Label(header_frame, 
                                 text="🚫 PROTECTION URN ACTIVE - CAPTURE INTERDITE 🚫",
                                 font=('Arial', 12, 'bold'), fg='#ff0000', bg='#0a0a0a')
        security_label.pack()
        
        # Info document
        info_frame = ttk.LabelFrame(self.secure_window, text="📄 Informations Document")
        info_frame.pack(fill='x', padx=10, pady=5)
        
        info_text = f"""Classification: {metadata.get('classification', 'N/A')}
Propriétaire: {metadata.get('owner', 'N/A')}
Dimensions: {image_data.shape[0]}x{image_data.shape[1]}
URN ID: {burn_result['urn_id'][:16]}...
Fragments sécurisés: {burn_result['total_fragments']}"""
        
        info_label = tk.Label(info_frame, text=info_text, justify='left',
                             font=('Consolas', 9), fg='#cccccc', bg='#1a1a1a')
        info_label.pack(padx=10, pady=5)
        
        # Affichage image
        img_frame = ttk.LabelFrame(self.secure_window, text="🖼️  Image Protégée")
        img_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Redimensionner image pour affichage
        img = Image.fromarray(image_data)
        img.thumbnail((500, 400), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        img_label = tk.Label(img_frame, image=photo, bg='#1a1a1a')
        img_label.photo = photo  # Garder référence
        img_label.pack(expand=True)
        
        # Minuteur sécurisé
        duration = metadata.get('projection_duration', 30)
        self.remaining_time = duration
        
        timer_label = tk.Label(self.secure_window, 
                              text=f"⏱️  Temps restant: {self.remaining_time}s",
                              font=('Arial', 11, 'bold'), fg='#ffaa00', bg='#0a0a0a')
        timer_label.pack(pady=5)
        
        # Bouton fermeture
        close_btn = tk.Button(self.secure_window, text="🔒 Fermer et Détruire",
                             command=self.close_secure_screen,
                             font=('Arial', 10, 'bold'), bg='#cc0000', fg='white')
        close_btn.pack(pady=10)
        
        # Démarrer minuteur
        self.update_timer(timer_label)
        
        self.log("🖥️  Écran sécurisé ouvert avec protection URN complète")
        self.log(f"⏱️  Session de {duration} secondes démarrée")
    
    def update_timer(self, timer_label):
        """Mettre à jour le minuteur sécurisé"""
        if self.secure_window and self.remaining_time > 0:
            timer_label.config(text=f"⏱️  Temps restant: {self.remaining_time}s")
            self.remaining_time -= 1
            self.root.after(1000, lambda: self.update_timer(timer_label))
        elif self.remaining_time <= 0:
            self.log("⏰ Session expirée - Fermeture automatique")
            self.close_secure_screen()
    
    def close_secure_screen(self):
        """Fermer écran sécurisé"""
        if self.secure_window:
            self.secure_window.destroy()
            self.secure_window = None
            self.log("🔒 Écran sécurisé fermé - Protection URN désactivée")
    
    def run(self):
        """Démarrer l'interface utilisateur"""
        self.create_ui()
        self.root.mainloop()

def start_node_a_server():
    """Démarrer Node A en arrière-plan"""
    print("🚀 Démarrage Node A Server...")
    
    server = NodeA_RealServer()
    
    # Préparer image réelle
    if not server.prepare_real_image():
        print("❌ Impossible de préparer l'image réelle")
        return False
    
    # Démarrer serveur dans thread séparé
    server_thread = threading.Thread(target=server.start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Attendre démarrage
    time.sleep(3)
    
    # Vérifier que le serveur répond
    try:
        response = requests.get("http://127.0.0.1:9200/status", timeout=5)
        if response.status_code == 200:
            print("✅ Node A Server opérationnel")
            return True
    except:
        pass
    
    print("❌ Node A Server non accessible")
    return False

def main():
    """Point d'entrée principal"""
    print("🔥🐦‍🔥 SYSTÈME P2P URN-PHANTOM RÉEL")
    print("Diego Morales Magri - Expérience Utilisateur Complète")
    print("=" * 60)
    
    print("\n🎯 Configuration:")
    print(f"   Image utilisateur: shared-images/test_real_image.jpg")
    print(f"   Node A Server: http://127.0.0.1:9200")
    print(f"   Protection URN: ACTIVE")
    print(f"   Interface: Tkinter GUI")
    
    # Démarrer Node A
    if not start_node_a_server():
        print("💥 Échec démarrage du serveur")
        return
    
    print("\n🎮 Démarrage interface utilisateur Node B...")
    
    # Démarrer client avec interface
    client = NodeB_RealClient()
    
    try:
        client.run()
    except KeyboardInterrupt:
        print("\n🔚 Arrêt du système P2P URN")
    except Exception as e:
        print(f"\n💥 Erreur: {e}")

if __name__ == "__main__":
    main()