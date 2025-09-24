#!/usr/bin/env python3
"""
Serveur de Projections Fantômes
================================
Système révolutionnaire d'images virtuelles qui ne se matérialisent jamais.
Les images existent uniquement en mémoire et sont projetées vers les viewers.
"""

import asyncio
import aiohttp
from aiohttp import web, WSMsgType
import json
import base64
import os
from datetime import datetime
from typing import Dict, Set, Optional
from pathlib import Path
import weakref
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhantomProjectionServer:
    def __init__(self, node_id: str, port: int = 8001):
        self.node_id = node_id
        self.port = port
        
        # Images fantômes en mémoire uniquement (jamais sur disque)
        self.phantom_images: Dict[str, dict] = {}
        
        # Viewers connectés par WebSocket
        self.active_viewers: Set[web.WebSocketResponse] = set()
        
        # Surveillance des connexions
        self.viewer_phantom_mapping: Dict[str, Set[str]] = {}  # viewer_id -> phantom_ids
        
        # Auto-détection des images locales pour créer des fantômes
        self.watch_folder = Path("shared-images")
        self.watch_folder.mkdir(exist_ok=True)
        
        self.app = None
        
    async def create_phantom_from_file(self, image_path: Path) -> str:
        """Crée un fantôme à partir d'un fichier local (qui sera ensuite supprimé)"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Conversion en base64 pour transport
            image_base64 = base64.b64encode(image_data).decode()
            
            # Détection du type MIME
            ext = image_path.suffix.lower()
            mime_types = {
                '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                '.png': 'image/png', '.gif': 'image/gif',
                '.webp': 'image/webp', '.bmp': 'image/bmp'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')
            
            # Création du fantôme
            phantom_id = f"phantom_{len(self.phantom_images)}_{int(datetime.now().timestamp())}"
            
            phantom_data = {
                'id': phantom_id,
                'name': image_path.name,
                'mime_type': mime_type,
                'data': image_base64,
                'size': len(image_data),
                'created_at': datetime.now().isoformat(),
                'projected_to': set(),  # Viewers qui voient ce fantôme
                'origin_file': str(image_path)
            }
            
            self.phantom_images[phantom_id] = phantom_data
            
            # Suppression du fichier original (plus de trace physique)
            try:
                os.remove(image_path)
                logger.info(f"🔥 Fichier source supprimé: {image_path.name}")
            except:
                pass
            
            logger.info(f"👻 Fantôme créé: {phantom_id} ({image_path.name})")
            
            # Notification aux viewers connectés
            await self.broadcast_phantom_update('phantom_created', phantom_id)
            
            return phantom_id
            
        except Exception as e:
            logger.error(f"Erreur création fantôme: {e}")
            return None
    
    async def delete_phantom(self, phantom_id: str):
        """Supprime un fantôme - disparition instantanée de tous les viewers"""
        if phantom_id in self.phantom_images:
            phantom_name = self.phantom_images[phantom_id]['name']
            del self.phantom_images[phantom_id]
            
            logger.info(f"💨 Fantôme supprimé: {phantom_id} ({phantom_name})")
            
            # Notification immédiate à tous les viewers
            await self.broadcast_phantom_update('phantom_deleted', phantom_id)
            
            # Nettoyage des mappings
            for viewer_id in self.viewer_phantom_mapping:
                self.viewer_phantom_mapping[viewer_id].discard(phantom_id)
    
    async def broadcast_phantom_update(self, event_type: str, phantom_id: str):
        """Diffusion temps réel vers tous les viewers connectés"""
        if not self.active_viewers:
            return
            
        message = {
            'type': event_type,
            'phantom_id': phantom_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Ajout des données si création
        if event_type == 'phantom_created' and phantom_id in self.phantom_images:
            phantom = self.phantom_images[phantom_id]
            message['phantom_data'] = {
                'id': phantom['id'],
                'name': phantom['name'],
                'mime_type': phantom['mime_type'],
                'data': phantom['data'],  # Image base64
                'size': phantom['size']
            }
        
        # Diffusion à tous les viewers actifs
        disconnected_viewers = []
        for ws in self.active_viewers:
            try:
                await ws.send_str(json.dumps(message))
            except:
                disconnected_viewers.append(ws)
        
        # Nettoyage des connexions fermées
        for ws in disconnected_viewers:
            self.active_viewers.discard(ws)
    
    async def scan_and_create_phantoms(self):
        """Surveillance automatique du dossier pour créer des fantômes"""
        for image_file in self.watch_folder.glob("*"):
            if image_file.is_file() and image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
                await self.create_phantom_from_file(image_file)
        
        # Re-scan périodique
        asyncio.create_task(self.periodic_scan())
    
    async def periodic_scan(self):
        """Scan périodique pour nouvelles images"""
        await asyncio.sleep(2)  # Attente 2 secondes
        await self.scan_and_create_phantoms()
    
    async def websocket_handler(self, request):
        """Gestionnaire WebSocket pour viewers en temps réel"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.active_viewers.add(ws)
        viewer_id = f"viewer_{len(self.active_viewers)}_{int(datetime.now().timestamp())}"
        self.viewer_phantom_mapping[viewer_id] = set()
        
        logger.info(f"🔗 Viewer connecté: {viewer_id}")
        
        # Envoi de la liste actuelle des fantômes
        await ws.send_str(json.dumps({
            'type': 'phantom_list',
            'phantoms': [
                {
                    'id': p['id'],
                    'name': p['name'],
                    'mime_type': p['mime_type'],
                    'data': p['data'],
                    'size': p['size']
                }
                for p in self.phantom_images.values()
            ]
        }))
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        
                        if data.get('type') == 'delete_phantom':
                            phantom_id = data.get('phantom_id')
                            if phantom_id:
                                await self.delete_phantom(phantom_id)
                        
                    except json.JSONDecodeError:
                        pass
                        
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'Erreur WebSocket: {ws.exception()}')
                    break
                    
        except Exception as e:
            logger.error(f"Erreur viewer {viewer_id}: {e}")
        finally:
            self.active_viewers.discard(ws)
            if viewer_id in self.viewer_phantom_mapping:
                del self.viewer_phantom_mapping[viewer_id]
            logger.info(f"❌ Viewer déconnecté: {viewer_id}")
        
        return ws
    
    async def status_handler(self, request):
        """API de statut du serveur"""
        return web.json_response({
            'node_id': self.node_id,
            'phantom_count': len(self.phantom_images),
            'active_viewers': len(self.active_viewers),
            'phantoms': [
                {
                    'id': p['id'],
                    'name': p['name'],
                    'size': p['size'],
                    'created_at': p['created_at']
                }
                for p in self.phantom_images.values()
            ]
        })
    
    async def phantoms_handler(self, request):
        """API pour récupérer la liste des phantoms"""
        return web.json_response({
            'phantoms': [
                {
                    'id': p['id'],
                    'name': p['name'],
                    'size': p['size'],
                    'mime_type': p.get('mime_type', 'image/jpeg'),
                    'created_at': p['created_at']
                }
                for p in self.phantom_images.values()
            ]
        })
    
    async def create_phantom_handler(self, request):
        """API pour créer un fantôme via JSON"""
        try:
            data = await request.json()
            phantom_id = data.get('id')
            phantom_name = data.get('name')
            phantom_data = data.get('data')  # base64 encoded image
            mime_type = data.get('mime_type', 'image/jpeg')
            
            if not all([phantom_id, phantom_name, phantom_data]):
                return web.json_response({'error': 'Missing required fields: id, name, data'}, status=400)
            
            # Décoder les données
            try:
                image_bytes = base64.b64decode(phantom_data)
            except:
                return web.json_response({'error': 'Invalid base64 data'}, status=400)
            
            # Créer le fantôme
            phantom_info = {
                'id': phantom_id,
                'name': phantom_name,
                'data': phantom_data,
                'size': len(image_bytes),
                'mime_type': mime_type,
                'created_at': datetime.now().isoformat()
            }
            
            self.phantom_images[phantom_id] = phantom_info
            
            # Notifier les viewers connectés
            await self.broadcast_phantom_update('phantom_created', phantom_id)
            
            logger.info(f"👻 Nouveau phantom créé: {phantom_name} (ID: {phantom_id})")
            
            return web.json_response({
                'status': 'created',
                'phantom_id': phantom_id,
                'name': phantom_name,
                'size': len(image_bytes)
            })
            
        except json.JSONDecodeError:
            return web.json_response({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Erreur création phantom: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def delete_phantom_handler(self, request):
        """API pour supprimer un fantôme"""
        phantom_id = request.match_info.get('phantom_id')
        if phantom_id and phantom_id in self.phantom_images:
            await self.delete_phantom(phantom_id)
            return web.json_response({'status': 'deleted', 'phantom_id': phantom_id})
        return web.json_response({'error': 'Phantom not found'}, status=404)
    
    def setup_routes(self):
        """Configuration des routes"""
        self.app.router.add_get('/ws', self.websocket_handler)
        self.app.router.add_get('/status', self.status_handler)
        self.app.router.add_get('/phantoms', self.phantoms_handler)
        self.app.router.add_post('/phantom', self.create_phantom_handler)
        self.app.router.add_delete('/phantom/{phantom_id}', self.delete_phantom_handler)
        
        # Page de contrôle simple
        self.app.router.add_get('/', self.control_panel_handler)
    
    async def control_panel_handler(self, request):
        """Interface de contrôle simple"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Phantom Projection Server - {self.node_id}</title>
            <style>
                body {{ font-family: monospace; background: #000; color: #0f0; margin: 20px; }}
                .phantom {{ border: 1px solid #0f0; margin: 10px; padding: 10px; }}
                .delete-btn {{ background: #f00; color: #fff; border: none; padding: 5px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <h1>👻 Phantom Projection Server</h1>
            <p>Node: {self.node_id} | Port: {self.port}</p>
            <p>Active Phantoms: <span id="count">{len(self.phantom_images)}</span></p>
            <p>Active Viewers: <span id="viewers">{len(self.active_viewers)}</span></p>
            
            <div id="phantoms">
                {''.join([f'''
                <div class="phantom">
                    <strong>{p["name"]}</strong> ({p["size"]} bytes)<br>
                    Created: {p["created_at"]}<br>
                    <button class="delete-btn" onclick="deletePhantom('{p["id"]}')">Delete Phantom</button>
                </div>
                ''' for p in self.phantom_images.values()])}
            </div>
            
            <script>
                function deletePhantom(phantomId) {{
                    if (confirm('Supprimer ce fantôme? Il disparaîtra de tous les viewers.')) {{
                        fetch(`/phantom/${{phantomId}}`, {{ method: 'DELETE' }})
                        .then(() => location.reload());
                    }}
                }}
                
                // Auto-refresh
                setInterval(() => location.reload(), 5000);
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def start_server(self):
        """Démarrage du serveur"""
        self.app = web.Application()
        self.setup_routes()
        
        # Scan initial
        await self.scan_and_create_phantoms()
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        logger.info(f"👻 Serveur Phantom Projection démarré")
        logger.info(f"🌐 Interface: http://localhost:{self.port}")
        logger.info(f"📁 Déposez des images dans: {self.watch_folder}")
        logger.info(f"⚡ WebSocket: ws://localhost:{self.port}/ws")
        
        return runner

async def main():
    import sys
    
    node_id = sys.argv[1] if len(sys.argv) > 1 else "phantom_projection_demo"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8001
    
    server = PhantomProjectionServer(node_id, port)
    runner = await server.start_server()
    
    try:
        # Serveur permanent
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())