#!/usr/bin/env python3
"""
🎭 SERVEUR DE PROJECTION PHANTOM ORP
===================================
Serveur de streaming temps réel pour projections Phantom URN
Basé sur phantom_projection_server.py avec intégration Web API

Fonctionnalités:
- WebSocket streaming pour projections temps réel
- Support protocole ORP (OpenRed Protocol)
- Intégration avec système URN authentique
- Protection anti-capture pendant projection
"""

import asyncio
import json
import base64
import time
import weakref
import logging
from typing import Dict, Set, Optional, Any
from pathlib import Path
import threading
from aiohttp import web, WSMsgType
import aiohttp_cors
from PIL import Image
import numpy as np
import io

logger = logging.getLogger(__name__)

class PhantomProjectionServer:
    """
    Serveur de projection temps réel pour URNs Phantom
    """
    
    def __init__(self, urn_system, port: int = 8002):
        self.urn_system = urn_system
        self.port = port
        
        # Connexions WebSocket actives
        self.active_connections: Set[web.WebSocketResponse] = set()
        
        # Mapping viewer -> phantoms regardés
        self.viewer_phantoms: Dict[str, Set[str]] = {}
        
        # Cache des projections actives
        self.active_projections: Dict[str, dict] = {}
        
        # Application web
        self.app = None
        self.runner = None
        
        logger.info(f"🎭 Serveur Projection Phantom - Port: {port}")
    
    def setup_app(self):
        """Configure l'application web"""
        self.app = web.Application()
        
        # Configuration CORS
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Routes WebSocket
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # Routes HTTP
        self.app.router.add_get('/phantom/{phantom_id}', self.get_phantom_info)
        self.app.router.add_get('/phantom/{phantom_id}/stream', self.stream_phantom)
        self.app.router.add_get('/status', self.server_status)
        self.app.router.add_get('/phantoms', self.list_phantoms)
        
        # CORS pour toutes les routes
        for route in list(self.app.router.routes()):
            cors.add(route)
        
        logger.info("🌐 Routes Phantom configurées")
    
    async def websocket_handler(self, request):
        """Handler principal WebSocket pour streaming ORP"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.active_connections.add(ws)
        client_id = f"client_{len(self.active_connections)}_{int(time.time())}"
        
        logger.info(f"🔌 Connexion WebSocket: {client_id}")
        
        try:
            # Envoyer liste des phantoms disponibles
            await self.send_phantom_list(ws)
            
            # Boucle de traitement des messages
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self.handle_websocket_message(ws, client_id, data)
                    except json.JSONDecodeError:
                        await self.send_error(ws, "Message JSON invalide")
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"Erreur WebSocket: {ws.exception()}")
                    break
        
        except Exception as e:
            logger.error(f"❌ Erreur WebSocket {client_id}: {e}")
        
        finally:
            self.active_connections.discard(ws)
            if client_id in self.viewer_phantoms:
                del self.viewer_phantoms[client_id]
            logger.info(f"🔌 Déconnexion: {client_id}")
        
        return ws
    
    async def handle_websocket_message(self, ws: web.WebSocketResponse, client_id: str, data: dict):
        """Traite les messages WebSocket clients"""
        try:
            message_type = data.get('type')
            
            if message_type == 'request_phantom':
                phantom_id = data.get('phantom_id')
                access_token = data.get('access_token')
                
                if phantom_id and access_token:
                    await self.stream_phantom_to_client(ws, client_id, phantom_id, access_token)
                else:
                    await self.send_error(ws, "phantom_id et access_token requis")
            
            elif message_type == 'stop_phantom':
                phantom_id = data.get('phantom_id')
                if client_id in self.viewer_phantoms:
                    self.viewer_phantoms[client_id].discard(phantom_id)
                
                await self.send_message(ws, {
                    'type': 'phantom_stopped',
                    'phantom_id': phantom_id
                })
            
            elif message_type == 'list_phantoms':
                await self.send_phantom_list(ws)
            
            else:
                await self.send_error(ws, f"Type de message inconnu: {message_type}")
        
        except Exception as e:
            logger.error(f"❌ Erreur traitement message: {e}")
            await self.send_error(ws, "Erreur traitement message")
    
    async def stream_phantom_to_client(self, ws: web.WebSocketResponse, client_id: str, phantom_id: str, access_token: str):
        """Streaming d'un phantom vers un client via WebSocket"""
        try:
            logger.info(f"🎭 Début streaming {phantom_id} vers {client_id}")
            
            # Reconstruction Phoenix depuis URN
            phantom_image = self.urn_system.get_phantom_for_projection(phantom_id, access_token)
            
            if phantom_image is None:
                await self.send_error(ws, f"Phantom {phantom_id} non accessible")
                return
            
            # Conversion en image PIL
            pil_image = Image.fromarray(phantom_image)
            
            # Convertir en base64 pour transmission
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=85)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Enregistrer viewer
            if client_id not in self.viewer_phantoms:
                self.viewer_phantoms[client_id] = set()
            self.viewer_phantoms[client_id].add(phantom_id)
            
            # Envoyer projection
            projection_data = {
                'type': 'phantom_projection',
                'phantom_id': phantom_id,
                'data': image_base64,
                'mime_type': 'image/jpeg',
                'dimensions': {
                    'width': phantom_image.shape[1],
                    'height': phantom_image.shape[0]
                },
                'timestamp': time.time(),
                'anti_capture_active': True
            }
            
            await self.send_message(ws, projection_data)
            
            logger.info(f"✅ Streaming {phantom_id} envoyé à {client_id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur streaming {phantom_id}: {e}")
            await self.send_error(ws, f"Erreur streaming: {e}")
    
    async def send_phantom_list(self, ws: web.WebSocketResponse):
        """Envoie la liste des phantoms disponibles"""
        try:
            phantoms = self.urn_system.list_active_phantoms()
            
            message = {
                'type': 'phantom_list',
                'phantoms': phantoms,
                'server': 'Phantom Projection Server',
                'protocol': 'ORP',
                'count': len(phantoms)
            }
            
            await self.send_message(ws, message)
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi liste phantoms: {e}")
    
    async def send_message(self, ws: web.WebSocketResponse, data: dict):
        """Envoie un message JSON via WebSocket"""
        try:
            message = json.dumps(data)
            await ws.send_str(message)
        except Exception as e:
            logger.error(f"❌ Erreur envoi message: {e}")
    
    async def send_error(self, ws: web.WebSocketResponse, error_message: str):
        """Envoie un message d'erreur"""
        error_data = {
            'type': 'error',
            'message': error_message,
            'timestamp': time.time()
        }
        await self.send_message(ws, error_data)
    
    async def get_phantom_info(self, request):
        """Informations sur un phantom spécifique"""
        phantom_id = request.match_info['phantom_id']
        
        if phantom_id in self.urn_system.active_urns:
            config = self.urn_system.active_urns[phantom_id]
            
            info = {
                'phantom_id': phantom_id,
                'dimensions': config.image_dimensions,
                'total_fragments': config.total_fragments,
                'created_at': config.creation_time,
                'authorized_node': config.authorized_node,
                'status': 'active',
                'type': 'phantom_urn'
            }
            
            return web.json_response(info)
        else:
            return web.json_response({'error': 'Phantom non trouvé'}, status=404)
    
    async def stream_phantom(self, request):
        """Endpoint HTTP pour streaming direct"""
        phantom_id = request.match_info['phantom_id']
        access_token = request.query.get('token')
        
        if not access_token:
            return web.json_response({'error': 'Token d\'accès requis'}, status=401)
        
        phantom_image = self.urn_system.get_phantom_for_projection(phantom_id, access_token)
        
        if phantom_image is None:
            return web.json_response({'error': 'Phantom non accessible'}, status=404)
        
        # Convertir en JPEG
        pil_image = Image.fromarray(phantom_image)
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG', quality=90)
        buffer.seek(0)
        
        return web.Response(
            body=buffer.getvalue(),
            content_type='image/jpeg',
            headers={
                'X-Phantom-ID': phantom_id,
                'X-Anti-Capture': 'active',
                'Cache-Control': 'no-store, no-cache, must-revalidate'
            }
        )
    
    async def server_status(self, request):
        """Statut du serveur"""
        status = {
            'server': 'Phantom Projection Server',
            'protocol': 'ORP',
            'port': self.port,
            'active_connections': len(self.active_connections),
            'active_phantoms': len(self.urn_system.active_urns),
            'viewers_connected': len(self.viewer_phantoms),
            'timestamp': time.time()
        }
        
        return web.json_response(status)
    
    async def list_phantoms(self, request):
        """Liste tous les phantoms disponibles"""
        phantoms = self.urn_system.list_active_phantoms()
        
        response = {
            'phantoms': phantoms,
            'count': len(phantoms),
            'server': 'Phantom Projection Server'
        }
        
        return web.json_response(response)
    
    async def broadcast_to_all(self, message: dict):
        """Diffuse un message à tous les clients connectés"""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message)
        
        for ws in self.active_connections.copy():
            try:
                await ws.send_str(message_str)
            except Exception as e:
                logger.error(f"❌ Erreur broadcast: {e}")
                self.active_connections.discard(ws)
    
    def start_server(self):
        """Démarre le serveur (bloquant)"""
        self.setup_app()
        
        async def run_server():
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            site = web.TCPSite(self.runner, '0.0.0.0', self.port)
            await site.start()
            
            logger.info(f"🎭 Serveur Projection démarré sur port {self.port}")
            logger.info(f"🌐 WebSocket: ws://localhost:{self.port}/ws")
            logger.info(f"🌐 HTTP: http://localhost:{self.port}")
            
            # Maintenir le serveur en vie
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("🛑 Arrêt serveur Projection")
        
        asyncio.run(run_server())
    
    def start_server_thread(self):
        """Démarre le serveur dans un thread séparé"""
        def run():
            self.start_server()
        
        server_thread = threading.Thread(target=run, daemon=True)
        server_thread.start()
        
        logger.info(f"🎭 Serveur Projection lancé en arrière-plan - Port: {self.port}")
        return server_thread
    
    async def stop_server(self):
        """Arrête le serveur"""
        if self.runner:
            await self.runner.cleanup()
        logger.info("🛑 Serveur Projection arrêté")