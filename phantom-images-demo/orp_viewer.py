#!/usr/bin/env python3
"""
🔄 ORP Viewer avec Support WebSocket - Version de Transition
===========================================================

Version expérimentale du viewer avec support complet WebSocket
pour les anciens fichiers PHANTOM binaires.

Fonctionnalités :
- Détection automatique URN vs PHANTOM binaire
- Support WebSocket pour anciens serveurs PHANTOM
- Support HTTP pour nouveaux serveurs URN
- Fenêtre image pure, redimensionnable
- Messages console détaillés

Usage:
    python orp_viewer_websocket_transition.py fichier.orp

Auteur: Diego Morales Magri
Innovation URN-PHANTOM: 25 septembre 2025
"""

import sys
import os
import json
import time
import requests
import tkinter as tk
from tkinter import messagebox
import numpy as np
from PIL import Image, ImageTk
from typing import Dict, Any, Optional, Tuple
import hashlib
import io
import asyncio
import websockets
import base64
import threading
from urllib.parse import urlparse

class WebSocketPhantomClient:
    """Client WebSocket pour anciens serveurs PHANTOM"""
    
    def __init__(self):
        self.connection = None
        self.image_data = None
        self.error_message = None
        
    async def fetch_phantom_image(self, ws_url: str, phantom_id: str, timeout: int = 15):
        """Récupérer une image phantom via WebSocket - Protocole PHANTOM réel"""
        try:
            print(f"🔗 Connexion WebSocket: {ws_url}")
            
            # Connexion WebSocket avec timeout via wait_for
            websocket = await asyncio.wait_for(
                websockets.connect(ws_url),
                timeout=timeout
            )
            
            try:
                print(f"✅ Connexion WebSocket établie")
                print(f"🎭 Attente de la liste des phantoms...")
                
                # Attendre le premier message (liste des phantoms)
                response = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=timeout
                )
                
                try:
                    response_data = json.loads(response)
                    print(f"📄 Message reçu: {response_data.get('type', 'unknown')}")
                    
                    if response_data.get('type') == 'phantom_list':
                        phantoms = response_data.get('phantoms', [])
                        print(f"� {len(phantoms)} phantoms disponibles")
                        
                        # Chercher notre phantom spécifique
                        target_phantom = None
                        for phantom in phantoms:
                            if phantom.get('id') == phantom_id:
                                target_phantom = phantom
                                break
                            # Fallback: chercher par nom partiel
                            elif phantom_id in phantom.get('id', '') or phantom_id in phantom.get('name', ''):
                                target_phantom = phantom
                                break
                        
                        if target_phantom:
                            print(f"🎯 Phantom trouvé: {target_phantom['id']}")
                            print(f"   Nom: {target_phantom.get('name', 'N/A')}")
                            print(f"   Taille: {target_phantom.get('size', 'N/A')} bytes")
                            
                            # Décoder l'image base64
                            if 'data' in target_phantom:
                                image_bytes = base64.b64decode(target_phantom['data'])
                                image_pil = Image.open(io.BytesIO(image_bytes))
                                self.image_data = np.array(image_pil)
                                print(f"✅ Image PHANTOM décodée: {self.image_data.shape}")
                                return True
                            else:
                                self.error_message = "Pas de données image dans le phantom"
                                return False
                        else:
                            # Liste des phantoms disponibles pour debug
                            available_ids = [p.get('id', 'N/A') for p in phantoms]
                            print(f"🔍 Phantoms disponibles: {available_ids}")
                            self.error_message = f"Phantom '{phantom_id}' non trouvé. Disponibles: {available_ids}"
                            return False
                    else:
                        self.error_message = f"Type de message inattendu: {response_data.get('type')}"
                        return False
                        
                except json.JSONDecodeError as e:
                    self.error_message = f"Erreur parsing JSON: {e}"
                    return False
                    
            finally:
                await websocket.close()
                    
        except websockets.exceptions.ConnectionClosed:
            self.error_message = "Connexion WebSocket fermée par le serveur"
            return False
        except websockets.exceptions.InvalidURI:
            self.error_message = "URI WebSocket invalide"
            return False
        except asyncio.TimeoutError:
            self.error_message = "Timeout connexion WebSocket"
            return False
        except ConnectionRefusedError:
            self.error_message = "Connexion refusée - Serveur PHANTOM probablement hors ligne"
            return False
        except Exception as e:
            self.error_message = f"Erreur WebSocket: {e}"
            return False

def run_websocket_client(ws_url: str, phantom_id: str) -> Tuple[Optional[np.ndarray], Optional[str]]:
    """Exécuter le client WebSocket dans un thread séparé"""
    client = WebSocketPhantomClient()
    
    def run_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                client.fetch_phantom_image(ws_url, phantom_id)
            )
        finally:
            loop.close()
    
    # Exécuter dans un thread
    thread = threading.Thread(target=run_async)
    thread.start()
    thread.join(timeout=20)  # Timeout global de 20 secondes
    
    if thread.is_alive():
        return None, "Timeout global WebSocket"
    
    if client.image_data is not None:
        return client.image_data, None
    else:
        return None, client.error_message or "Erreur inconnue"

class URNDetector:
    """Détecteur intelligent avec support WebSocket"""
    
    def __init__(self):
        self.urn_servers = [
            "http://127.0.0.1:9300",
            "http://127.0.0.1:9200", 
            "http://127.0.0.1:9100"
        ]
        self.node_id = "WebSocketViewer_Client"
        self.MAGIC_HEADER = b"ORPHANTOM"
    
    def detect_orp_format(self, filepath: str) -> str:
        """Détecter le format du fichier .orp"""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(9)
                
                if header == self.MAGIC_HEADER:
                    print("📱 Format détecté: Binaire PHANTOM original")
                    return "BINARY_PHANTOM"
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print("🔮 Format détecté: JSON/URN moderne")
                    return "JSON_URN"
            except:
                print("❌ Format inconnu")
                return "UNKNOWN"
                
        except Exception as e:
            print(f"❌ Erreur détection: {e}")
            return "UNKNOWN"
    
    def parse_binary_phantom(self, filepath: str) -> Dict[str, Any]:
        """Parser format binaire avec support WebSocket amélioré"""
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
                
            if len(data) < 25:
                raise ValueError("Fichier trop petit")
                
            if data[:9] != self.MAGIC_HEADER:
                raise ValueError("Magic header incorrect")
            
            # Version
            version = data[9:13].rstrip(b'\x00').decode()
            
            # Tailles des sections
            offset = 13
            metadata_size = int.from_bytes(data[offset:offset+4], 'little')
            access_size = int.from_bytes(data[offset+4:offset+8], 'little')
            security_size = int.from_bytes(data[offset+8:offset+12], 'little')
            
            # Extraction des sections
            offset = 25
            
            metadata_json = data[offset:offset+metadata_size]
            offset += metadata_size
            
            access_json = data[offset:offset+access_size]
            offset += access_size
            
            security_json = data[offset:offset+security_size]
            
            # Parsing JSON
            metadata = json.loads(metadata_json.decode())
            access_data = json.loads(access_json.decode())
            security_data = json.loads(security_json.decode())
            
            # Extraction des informations de connexion
            server_url = access_data.get('server_url', 'ws://localhost:8001')
            phantom_id = metadata.get('phantom_id', 'unknown')
            
            # Support hybride WebSocket/HTTP
            parsed_url = urlparse(server_url)
            connection_info = {
                'protocol': parsed_url.scheme,  # ws, wss, http, https
                'host': parsed_url.hostname or 'localhost',
                'port': parsed_url.port or (8001 if parsed_url.scheme in ['ws', 'wss'] else 80),
                'path': parsed_url.path or '/ws'
            }
            
            return {
                'format_type': 'BINARY_PHANTOM',
                'version': version,
                'metadata': metadata,
                'access_data': access_data,
                'security_data': security_data,
                'server_url': server_url,
                'phantom_id': phantom_id,
                'connection_info': connection_info
            }
            
        except Exception as e:
            raise Exception(f"Erreur parsing binaire: {e}")
    
    def parse_json_urn(self, filepath: str) -> Dict[str, Any]:
        """Parser format JSON/URN"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            has_urn = False
            urn_info = None
            
            if 'encrypted_data' in data:
                print("🔐 Protection URN détectée: encrypted_data présent")
                has_urn = True
                urn_info = {
                    'type': 'URN_ENCRYPTED',
                    'has_fragments': 'fragments' in data.get('encrypted_data', {}),
                    'server_required': True
                }
            elif 'urn' in str(data).lower() or 'burn' in str(data).lower():
                print("🔥 Protection URN détectée: signatures URN/BURN trouvées")
                has_urn = True
                urn_info = {
                    'type': 'URN_METADATA',
                    'server_required': True
                }
            
            return {
                'format_type': 'JSON_URN',
                'has_urn': has_urn,
                'urn_info': urn_info,
                'data': data,
                'requires_server': has_urn
            }
            
        except Exception as e:
            raise Exception(f"Erreur parsing JSON: {e}")
    
    def analyze_orp_file(self, filepath: str) -> Dict[str, Any]:
        """Analyser fichier avec support hybride"""
        print(f"🔍 Analyse du fichier: {os.path.basename(filepath)}")
        
        format_type = self.detect_orp_format(filepath)
        
        if format_type == "BINARY_PHANTOM":
            return self.parse_binary_phantom(filepath)
        elif format_type == "JSON_URN":
            return self.parse_json_urn(filepath)
        else:
            raise Exception("Format non supporté")
    
    def fetch_phantom_via_websocket(self, analysis: Dict[str, Any]) -> Optional[np.ndarray]:
        """Récupérer image PHANTOM via WebSocket"""
        connection_info = analysis['connection_info']
        phantom_id = analysis['phantom_id']
        
        if connection_info['protocol'] in ['ws', 'wss']:
            # Construction de l'URL WebSocket
            protocol = connection_info['protocol']
            host = connection_info['host']
            port = connection_info['port']
            path = connection_info['path']
            
            ws_url = f"{protocol}://{host}:{port}{path}"
            
            print(f"🌐 Tentative connexion WebSocket: {ws_url}")
            print(f"🎭 ID Phantom demandé: {phantom_id}")
            
            # Exécution WebSocket
            image_data, error = run_websocket_client(ws_url, phantom_id)
            
            if image_data is not None:
                print(f"✅ Image récupérée via WebSocket: {image_data.shape}")
                return image_data
            else:
                print(f"❌ Erreur WebSocket: {error}")
                return None
        else:
            print(f"⚠️  Protocole non-WebSocket détecté: {connection_info['protocol']}")
            return None
    
    def validate_urn_access(self, urn_id: str, filename: str) -> Dict[str, Any]:
        """Validation URN pour formats modernes"""
        print(f"🔗 Tentative de connexion aux serveurs URN...")
        
        for server_url in self.urn_servers:
            try:
                print(f"   Tentative: {server_url}")
                
                response = requests.get(f"{server_url}/status", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Serveur URN opérationnel: {server_url}")
                    
                    headers = {"Node-ID": self.node_id}
                    validation_data = {"urn_id": urn_id, "filename": filename}
                    
                    validation_response = requests.post(
                        f"{server_url}/validate_urn_access",
                        json=validation_data,
                        headers=headers,
                        timeout=15
                    )
                    
                    if validation_response.status_code == 200:
                        result = validation_response.json()
                        if result.get("validation_status") == "success":
                            print(f"✅ Validation URN réussie!")
                            return {
                                "status": "validated",
                                "server": server_url,
                                **result
                            }
                            
            except requests.exceptions.ConnectionError:
                print(f"❌ Impossible de se connecter à {server_url}")
            except Exception as e:
                print(f"❌ Erreur {server_url}: {e}")
        
        print(f"❌ Aucun serveur URN accessible")
        return {"status": "no_server", "message": "Aucun serveur URN accessible"}

class PureImageWindow:
    """Fenêtre image pure optimisée"""
    
    def __init__(self, image_data: np.ndarray, title: str = "PHANTOM Image", 
                 phantom_type: str = "UNKNOWN", metadata: Dict = None):
        
        self.original_image = Image.fromarray(image_data.astype(np.uint8))
        self.original_ratio = self.original_image.width / self.original_image.height
        self.phantom_type = phantom_type
        self.metadata = metadata or {}
        
        # Fenêtre Tkinter
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("800x600")
        self.root.configure(bg='black')
        
        # Suppression bordures
        self.root.attributes('-topmost', False)
        self.root.overrideredirect(False)  # Garder les contrôles de fenêtre
        
        print(f"🖼️  Ouverture image: ({self.original_image.width}, {self.original_image.height})")
        print(f"   Ratio d'aspect: {self.original_ratio:.3f}")
        print(f"   Type PHANTOM: {phantom_type}")
        
        # Label pour l'image
        self.image_label = tk.Label(self.root, bg='black')
        self.image_label.pack(expand=True, fill='both')
        
        # Événements
        self.root.bind('<Configure>', self.on_window_resize)
        self.root.bind('<Double-Button-1>', self.close_window)
        self.root.bind('<Escape>', self.close_window)
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
        self.root.focus_set()
        
        # Affichage initial
        self.current_size = (self.original_image.width, self.original_image.height)
        self.update_image_display()
        
        print(f"🖥️  Fenêtre créée - Double-clic ou Escape pour fermer")
        
    def on_window_resize(self, event):
        """Redimensionnement avec respect du ratio"""
        if event.widget != self.root:
            return
            
        window_width = event.width
        window_height = event.height
        
        if window_width / window_height > self.original_ratio:
            new_height = window_height
            new_width = int(new_height * self.original_ratio)
        else:
            new_width = window_width
            new_height = int(new_width / self.original_ratio)
        
        if new_width > 0 and new_height > 0:
            self.current_size = (new_width, new_height)
            self.update_image_display()
    
    def update_image_display(self):
        """Mise à jour affichage image"""
        try:
            resized_image = self.original_image.resize(self.current_size, Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized_image)
            self.image_label.configure(image=self.photo)
        except Exception as e:
            print(f"❌ Erreur affichage: {e}")
    
    def close_window(self, event=None):
        """Fermeture fenêtre"""
        print(f"👋 Fermeture viewer")
        self.root.destroy()
    
    def show(self):
        """Affichage avec messages contextuels"""
        if self.phantom_type == "BINARY_PHANTOM":
            print(f"📱 === DOCUMENT PHANTOM BINAIRE OUVERT ===")
            print(f"🔗 Connexion WebSocket réussie")
        elif self.phantom_type == "JSON_URN":
            print(f"🔐 === DOCUMENT URN-PROTÉGÉ OUVERT ===")
            print(f"🛡️  Protection URN active")
        
        print(f"💡 Double-clic ou Escape pour fermer")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print(f"\n🔚 Fermeture par utilisateur")

def main():
    """Fonction principale avec support WebSocket complet"""
    if len(sys.argv) != 2:
        print("Usage: python orp_viewer_websocket_transition.py fichier.orp")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not os.path.exists(filepath):
        print(f"❌ Fichier non trouvé: {filepath}")
        sys.exit(1)
    
    print(f"🚀 === ORP VIEWER WEBSOCKET TRANSITION ===")
    print(f"Diego Morales Magri - Innovation URN-PHANTOM")
    print(f"Fichier: {os.path.basename(filepath)}")
    print("=" * 55)
    
    # Analyse du fichier
    detector = URNDetector()
    try:
        analysis = detector.analyze_orp_file(filepath)
        print(f"✅ Analyse terminée: format {analysis['format_type']}")
    except Exception as e:
        print(f"❌ Impossible d'ouvrir le fichier: {e}")
        sys.exit(1)
    
    # Traitement selon le format
    image_data = None
    phantom_type = "UNKNOWN"
    metadata = {}
    
    if analysis['format_type'] == 'BINARY_PHANTOM':
        phantom_type = "BINARY_PHANTOM"
        print(f"📱 Traitement format PHANTOM binaire...")
        print(f"   Serveur: {analysis['server_url']}")
        print(f"   ID Phantom: {analysis['phantom_id']}")
        print(f"   Protocole: {analysis['connection_info']['protocol']}")
        
        # Récupération via WebSocket
        image_data = detector.fetch_phantom_via_websocket(analysis)
        metadata = analysis.get('metadata', {})
        
    elif analysis['format_type'] == 'JSON_URN':
        phantom_type = "JSON_URN"
        print(f"🔐 Traitement format JSON/URN...")
        
        if analysis['has_urn'] and analysis.get('requires_server', False):
            print(f"\n🔐 === VALIDATION URN REQUISE ===")
            validation_result = detector.validate_urn_access(
                analysis['data'].get('urn_id', 'unknown'), 
                os.path.basename(filepath)
            )
            
            if validation_result["status"] not in ["validated", "no_urn"]:
                print(f"⚠️  Avertissement: Validation URN échouée")
        
        # Extraction données image JSON
        if 'image_data' in analysis['data']:
            image_data = analysis['data']['image_data']
        
        metadata = analysis['data'].get('metadata', {})
    
    # Vérification finale
    if image_data is None:
        print(f"❌ Aucune donnée image accessible")
        print(f"💡 Causes possibles:")
        if analysis['format_type'] == 'BINARY_PHANTOM':
            print(f"   - Serveur PHANTOM hors ligne")
            print(f"   - Erreur protocole WebSocket")
            print(f"   - ID Phantom invalide: {analysis.get('phantom_id', 'N/A')}")
        else:
            print(f"   - Serveur URN hors ligne") 
            print(f"   - Format de fichier incomplet")
        sys.exit(1)
    
    try:
        image_array = np.array(image_data, dtype=np.uint8)
        print(f"✅ Image reconstituée: {image_array.shape}")
    except Exception as e:
        print(f"❌ Erreur reconstruction image: {e}")
        sys.exit(1)
    
    # Titre adaptatif
    title_parts = ["PHANTOM"]
    if phantom_type == "BINARY_PHANTOM":
        title_parts.append("WEBSOCKET")
    elif phantom_type == "JSON_URN":
        title_parts.append("URN-PROTECTED")
    
    title = f"{' | '.join(title_parts)} - {os.path.basename(filepath)}"
    
    print(f"\n🖥️  === OUVERTURE VIEWER ===")
    
    # Création et affichage
    viewer = PureImageWindow(
        image_data=image_array,
        title=title,
        phantom_type=phantom_type,
        metadata=metadata
    )
    
    viewer.show()
    
    print(f"✅ Viewer fermé correctement")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n🔚 Arrêt par utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)