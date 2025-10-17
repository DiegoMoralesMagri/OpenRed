# OpenRed Micro-HTTP Engine - Serveur HTTP ultra-minimaliste révolutionnaire
# Revolutionary ultra-minimalist HTTP server for OpenRed
# Motor HTTP ultra-minimalista revolucionario para OpenRed
# OpenRed 革命性超极简HTTP引擎

import socket
import threading
import json
import urllib.parse
from typing import Dict, Any, Callable, Tuple, Optional
from datetime import datetime
import traceback
import asyncio
from dataclasses import dataclass

@dataclass
class HttpRequest:
    """
    Représentation minimaliste d'une requête HTTP
    Minimalist HTTP request representation
    Representación minimalista de solicitud HTTP
    极简HTTP请求表示
    """
    method: str
    path: str
    query_params: Dict[str, str]
    headers: Dict[str, str]
    body: bytes
    client_ip: str
    
    @property
    def json(self) -> Optional[Dict[str, Any]]:
        """Parse JSON body if possible"""
        try:
            return json.loads(self.body.decode('utf-8'))
        except:
            return None

@dataclass
class HttpResponse:
    """
    Réponse HTTP empathique
    Empathic HTTP response
    Respuesta HTTP empática
    同理心HTTP响应
    """
    status_code: int = 200
    headers: Dict[str, str] = None
    body: bytes = b''
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {
                'Content-Type': 'application/json',
                'Server': 'OpenRed-Micro-Engine/1.0',
                'X-Empathy-Level': 'Maximum',
                'Access-Control-Allow-Origin': '*'
            }
    
    @classmethod
    def json(cls, data: Dict[str, Any], status_code: int = 200) -> 'HttpResponse':
        """Réponse JSON avec empathie technique intégrée"""
        # Ajout automatique de métadonnées empathiques
        # Automatic addition of empathic metadata
        # Adición automática de metadatos empáticos
        # 自动添加同理心元数据
        if isinstance(data, dict) and 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow().isoformat()
            data['openred_version'] = '3.0'
            data['empathy_enabled'] = True
        
        body = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Content-Length': str(len(body)),
            'Server': 'OpenRed-Micro-Engine/1.0',
            'X-Empathy-Level': 'Maximum'
        }
        
        return cls(status_code=status_code, headers=headers, body=body)
    
    @classmethod
    def error(cls, message: str, status_code: int = 400) -> 'HttpResponse':
        """Réponse d'erreur empathique"""
        return cls.json({
            'success': False,
            'error': message,
            'suggestion': 'Check the API documentation or contact support',
            'empathy_note': 'We understand errors can be frustrating. We are here to help!'
        }, status_code)

class OpenRedMicroEngine:
    """
    Moteur HTTP ultra-minimaliste pour OpenRed
    Ultra-minimalist HTTP engine for OpenRed
    Motor HTTP ultra-minimalista para OpenRed
    OpenRed超极简HTTP引擎
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8000):
        self.host = host
        self.port = port
        self.routes: Dict[str, Dict[str, Callable]] = {}
        self.middleware_stack = []
        self.running = False
        self.server_socket = None
        
        # Statistiques empathiques
        # Empathic statistics
        # Estadísticas empáticas
        # 同理心统计
        self.stats = {
            'requests_total': 0,
            'requests_successful': 0,
            'requests_failed': 0,
            'start_time': None,
            'empathy_responses': 0
        }
    
    def route(self, path: str, methods: list = None):
        """
        Décorateur pour enregistrer des routes
        Decorator to register routes
        Decorador para registrar rutas
        注册路由的装饰器
        """
        if methods is None:
            methods = ['GET']
        
        def decorator(func: Callable):
            for method in methods:
                if path not in self.routes:
                    self.routes[path] = {}
                self.routes[path][method.upper()] = func
            return func
        
        return decorator
    
    def add_middleware(self, middleware_func: Callable):
        """Ajouter un middleware empathique"""
        self.middleware_stack.append(middleware_func)
    
    def _parse_request(self, raw_request: bytes, client_ip: str) -> HttpRequest:
        """
        Parsing ultra-rapide des requêtes HTTP
        Ultra-fast HTTP request parsing
        Análisis ultra-rápido de solicitudes HTTP
        超快速HTTP请求解析
        """
        try:
            request_str = raw_request.decode('utf-8')
            lines = request_str.split('\r\n')
            
            # Parse request line
            request_line = lines[0]
            method, full_path, _ = request_line.split(' ', 2)
            
            # Parse path and query
            if '?' in full_path:
                path, query_string = full_path.split('?', 1)
                query_params = dict(urllib.parse.parse_qsl(query_string))
            else:
                path = full_path
                query_params = {}
            
            # Parse headers
            headers = {}
            body_start = 0
            for i, line in enumerate(lines[1:], 1):
                if line == '':
                    body_start = i + 1
                    break
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip().lower()] = value.strip()
            
            # Extract body
            body = b''
            if body_start < len(lines):
                body_content = '\r\n'.join(lines[body_start:])
                body = body_content.encode('utf-8')
            
            return HttpRequest(
                method=method.upper(),
                path=path,
                query_params=query_params,
                headers=headers,
                body=body,
                client_ip=client_ip
            )
        
        except Exception as e:
            # En cas d'erreur de parsing, requête minimale
            # In case of parsing error, minimal request
            # En caso de error de análisis, solicitud mínima
            # 解析错误时的最小请求
            return HttpRequest(
                method='UNKNOWN',
                path='/',
                query_params={},
                headers={},
                body=b'',
                client_ip=client_ip
            )
    
    def _build_response(self, response: HttpResponse) -> bytes:
        """
        Construction ultra-rapide des réponses HTTP
        Ultra-fast HTTP response building
        Construcción ultra-rápida de respuestas HTTP
        超快速HTTP响应构建
        """
        status_text = {
            200: 'OK',
            201: 'Created',
            400: 'Bad Request',
            401: 'Unauthorized',
            404: 'Not Found',
            500: 'Internal Server Error'
        }.get(response.status_code, 'Unknown')
        
        # Status line
        response_lines = [f'HTTP/1.1 {response.status_code} {status_text}']
        
        # Headers
        for key, value in response.headers.items():
            response_lines.append(f'{key}: {value}')
        
        # Empty line + body
        response_lines.append('')
        response_str = '\r\n'.join(response_lines)
        
        return response_str.encode('utf-8') + response.body
    
    def _handle_request(self, request: HttpRequest) -> HttpResponse:
        """
        Gestion empathique des requêtes
        Empathic request handling
        Manejo empático de solicitudes
        同理心请求处理
        """
        try:
            self.stats['requests_total'] += 1
            
            # Application des middlewares
            # Apply middlewares
            # Aplicar middlewares
            # 应用中间件
            for middleware in self.middleware_stack:
                try:
                    middleware_result = middleware(request)
                    if isinstance(middleware_result, HttpResponse):
                        return middleware_result
                except Exception as e:
                    print(f"Middleware error: {e}")
            
            # Recherche de route
            # Route lookup
            # Búsqueda de ruta
            # 路由查找
            if request.path in self.routes and request.method in self.routes[request.path]:
                handler = self.routes[request.path][request.method]
                response = handler(request)
                
                if not isinstance(response, HttpResponse):
                    # Auto-conversion en réponse JSON
                    # Auto-conversion to JSON response
                    # Auto-conversión a respuesta JSON
                    # 自动转换为JSON响应
                    response = HttpResponse.json(response)
                
                self.stats['requests_successful'] += 1
                return response
            
            else:
                # 404 empathique
                # Empathic 404
                # 404 empático
                # 同理心404
                return HttpResponse.error(
                    f"Route '{request.path}' not found. Available routes: {list(self.routes.keys())}",
                    404
                )
        
        except Exception as e:
            # 500 empathique avec détails
            # Empathic 500 with details
            # 500 empático con detalles
            # 同理心500与详细信息
            self.stats['requests_failed'] += 1
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'path': request.path,
                'method': request.method,
                'traceback': traceback.format_exc()
            }
            
            return HttpResponse.error(
                f"Internal server error: {str(e)}",
                500
            )
    
    def _handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]):
        """
        Gestion ultra-rapide des clients
        Ultra-fast client handling
        Manejo ultra-rápido de clientes
        超快速客户端处理
        """
        try:
            # Réception de la requête (timeout empathique de 30s)
            # Request reception (empathic 30s timeout)
            # Recepción de solicitud (timeout empático de 30s)
            # 请求接收（30秒同理心超时）
            client_socket.settimeout(30.0)
            raw_request = client_socket.recv(4096)
            
            if not raw_request:
                return
            
            # Parsing et traitement
            # Parsing and processing
            # Análisis y procesamiento
            # 解析和处理
            request = self._parse_request(raw_request, client_address[0])
            response = self._handle_request(request)
            
            # Envoi de la réponse
            # Send response
            # Enviar respuesta
            # 发送响应
            response_bytes = self._build_response(response)
            client_socket.sendall(response_bytes)
            
        except socket.timeout:
            # Timeout empathique
            # Empathic timeout
            # Timeout empático
            # 同理心超时
            timeout_response = HttpResponse.error("Request timeout (30s limit for server health)", 408)
            response_bytes = self._build_response(timeout_response)
            try:
                client_socket.sendall(response_bytes)
            except:
                pass
        
        except Exception as e:
            print(f"Client handling error: {e}")
        
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def start(self):
        """
        Démarrage du serveur ultra-minimaliste
        Start ultra-minimalist server
        Iniciar servidor ultra-minimalista
        启动超极简服务器
        """
        print(f"🚀 OpenRed Micro-Engine starting on {self.host}:{self.port}")
        print(f"📊 Ultra-minimalist HTTP server with maximum empathy")
        print(f"🔗 P2P optimized | Zero external dependencies")
        
        self.stats['start_time'] = datetime.utcnow()
        
        try:
            # Création du socket serveur
            # Create server socket
            # Crear socket del servidor
            # 创建服务器套接字
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(100)  # Queue empathique
            
            self.running = True
            print(f"✅ Server running! Ready for empathic P2P connections")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    
                    # Gestion dans un thread séparé
                    # Handle in separate thread
                    # Manejar en hilo separado
                    # 在单独线程中处理
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                
                except socket.error as e:
                    if self.running:
                        print(f"Accept error: {e}")
        
        except Exception as e:
            print(f"❌ Server startup error: {e}")
        
        finally:
            self.stop()
    
    def stop(self):
        """Arrêt empathique du serveur"""
        print("🛑 Stopping OpenRed Micro-Engine...")
        self.running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        # Affichage des statistiques finales
        # Display final statistics
        # Mostrar estadísticas finales
        # 显示最终统计
        uptime = datetime.utcnow() - self.stats['start_time'] if self.stats['start_time'] else None
        print(f"📊 Final stats:")
        print(f"   Total requests: {self.stats['requests_total']}")
        print(f"   Successful: {self.stats['requests_successful']}")
        print(f"   Failed: {self.stats['requests_failed']}")
        if uptime:
            print(f"   Uptime: {uptime}")
        print("✅ Server stopped gracefully")

# Instance globale du moteur
# Global engine instance
# Instancia global del motor
# 全局引擎实例
app = OpenRedMicroEngine()

# Export
__all__ = [
    "OpenRedMicroEngine",
    "HttpRequest", 
    "HttpResponse",
    "app"
]