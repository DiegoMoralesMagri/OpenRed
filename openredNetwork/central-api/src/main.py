# Serveur Central-API ultra-minimaliste pour OpenRed
# Ultra-minimalist Central-API server for OpenRed
# Servidor Central-API ultra-minimalista para OpenRed
# OpenRed 超极简中央API服务器

import os
import sys
import asyncio
import signal
from datetime import datetime

# Ajout du chemin pour les imports locaux
# Add path for local imports
# Agregar ruta para importaciones locales
# 添加本地导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.micro_engine import app, HttpRequest, HttpResponse
from core.directory import directory
from core.security import security_engine
from core.config import app_config, security_config, directory_config

def register_central_api_routes():
    """
    Enregistrement des routes ultra-simples de l'API centrale
    Register ultra-simple central API routes
    Registrar rutas ultra-simples de API central
    注册超简单的中央API路由
    """
    
    @app.route('/', ['GET'])
    def root_endpoint(request: HttpRequest) -> dict:
        """
        Endpoint racine avec informations de base
        Root endpoint with basic information
        Endpoint raíz con información básica
        根端点与基本信息
        """
        return {
            "service": "OpenRed Central-API",
            "version": "3.0",
            "description": "Ultra-minimalist P2P node directory with maximum empathy",
            "philosophy": "Code maison whenever possible",
            "engine": "OpenRed Micro-Engine",
            "endpoints": {
                "register": "POST /register - Register a new node",
                "discover": "GET /discover - Discover available nodes", 
                "heartbeat": "POST /heartbeat/{node_id} - Node heartbeat",
                "stats": "GET /stats - Directory statistics"
            },
            "empathy_level": "Maximum",
            "dependencies": "Zero external dependencies ✅"
        }
    
    @app.route('/register', ['POST'])
    def register_node(request: HttpRequest) -> dict:
        """
        Enregistrement d'un nouveau nœud
        Register a new node
        Registrar un nuevo nodo
        注册新节点
        """
        try:
            node_data = request.json
            
            if not node_data:
                return HttpResponse.error("Missing JSON body", 400)
            
            # Validation des champs requis
            # Validate required fields
            # Validar campos requeridos
            # 验证必填字段
            required_fields = ['node_id', 'ip_address', 'port', 'public_key']
            missing_fields = [field for field in required_fields if field not in node_data]
            
            if missing_fields:
                return HttpResponse.error(
                    f"Missing required fields: {', '.join(missing_fields)}", 
                    400
                )
            
            # Enregistrement via le directory (synchrone pour le Micro-Engine)
            # Registration via directory (synchronous for Micro-Engine)
            # Registro a través del directorio (síncrono para Micro-Engine)
            # 通过目录注册（Micro-Engine同步）
            result = asyncio.run(directory.register_node(node_data))
            
            return result
        
        except Exception as e:
            return HttpResponse.error(f"Registration failed: {str(e)}", 500)
    
    @app.route('/discover', ['GET'])
    def discover_nodes(request: HttpRequest) -> dict:
        """
        Découverte de nœuds disponibles
        Discover available nodes
        Descubrir nodos disponibles
        发现可用节点
        """
        try:
            # Paramètres de recherche optionnels
            # Optional search parameters
            # Parámetros de búsqueda opcionales
            # 可选搜索参数
            criteria = {}
            
            if 'capabilities' in request.query_params:
                capabilities = request.query_params['capabilities'].split(',')
                criteria['capabilities'] = [cap.strip() for cap in capabilities]
            
            # Découverte via le directory (synchrone pour le Micro-Engine)
            # Discovery via directory (synchronous for Micro-Engine)
            # Descubrimiento a través del directorio (síncrono para Micro-Engine)
            # 通过目录发现（Micro-Engine同步）
            result = asyncio.run(directory.discover_nodes(criteria))
            
            return result
        
        except Exception as e:
            return HttpResponse.error(f"Discovery failed: {str(e)}", 500)
    
    @app.route('/heartbeat/<node_id>', ['POST'])
    def node_heartbeat(request: HttpRequest) -> dict:
        """
        Heartbeat empathique d'un nœud
        Empathic node heartbeat
        Heartbeat empático de un nodo
        节点的同理心心跳
        """
        try:
            # Extraction du node_id depuis le path
            # Extract node_id from path
            # Extraer node_id del path
            # 从路径提取node_id
            path_parts = request.path.strip('/').split('/')
            if len(path_parts) < 2:
                return HttpResponse.error("Invalid heartbeat path", 400)
            
            node_id = path_parts[1]
            
            # Heartbeat via le directory (synchrone pour le Micro-Engine)
            # Heartbeat via directory (synchronous for Micro-Engine)
            # Heartbeat a través del directorio (síncrono para Micro-Engine)
            # 通过目录进行心跳（Micro-Engine同步）
            result = asyncio.run(directory.heartbeat_check(node_id))
            
            return result
        
        except Exception as e:
            return HttpResponse.error(f"Heartbeat failed: {str(e)}", 500)
    
    @app.route('/stats', ['GET'])
    def directory_stats(request: HttpRequest) -> dict:
        """
        Statistiques de l'annuaire
        Directory statistics
        Estadísticas del directorio
        目录统计
        """
        try:
            stats = directory.get_stats()
            
            # Ajout de statistiques du serveur
            # Add server statistics
            # Agregar estadísticas del servidor
            # 添加服务器统计
            stats.update({
                "server_info": {
                    "engine": "OpenRed Micro-Engine",
                    "version": "3.0",
                    "uptime_seconds": app.stats.get('start_time'),
                    "total_requests": app.stats.get('requests_total', 0),
                    "successful_requests": app.stats.get('requests_successful', 0),
                    "failed_requests": app.stats.get('requests_failed', 0)
                }
            })
            
            return {
                "success": True,
                "statistics": stats
            }
        
        except Exception as e:
            return HttpResponse.error(f"Stats retrieval failed: {str(e)}", 500)
    
    @app.route('/security/token', ['POST'])
    def create_security_token(request: HttpRequest) -> dict:
        """
        Création de tokens de sécurité asymétriques
        Create asymmetric security tokens
        Crear tokens de seguridad asimétricos
        创建非对称安全令牌
        """
        try:
            token_data = request.json
            
            if not token_data or 'node_id' not in token_data:
                return HttpResponse.error("Missing node_id in request", 400)
            
            node_id = token_data['node_id']
            lifetime = token_data.get('lifetime', 300)  # 5 minutes par défaut
            
            # Génération des clés si nécessaire
            # Generate keys if needed
            # Generar claves si es necesario
            # 如有必要生成密钥
            if not security_engine.private_key:
                security_engine.generate_key_pair()
            
            # Création du token
            # Create token
            # Crear token
            # 创建令牌
            token_result = security_engine.create_temporary_token(node_id, lifetime)
            
            return {
                "success": True,
                "token": token_result,
                "usage": "Use this token for P2P authentication between nodes"
            }
        
        except Exception as e:
            return HttpResponse.error(f"Token creation failed: {str(e)}", 500)

def setup_empathic_middleware():
    """
    Configuration des middlewares empathiques
    Setup empathic middleware
    Configurar middleware empático
    设置同理心中间件
    """
    
    def cors_middleware(request: HttpRequest):
        """Middleware CORS empathique"""
        # Les en-têtes CORS sont déjà dans HttpResponse par défaut
        # CORS headers are already in HttpResponse by default
        # Los headers CORS ya están en HttpResponse por defecto
        # CORS标头默认已在HttpResponse中
        pass
    
    def logging_middleware(request: HttpRequest):
        """Middleware de logging empathique"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print(f"📝 [{timestamp}] {request.method} {request.path} from {request.client_ip}")
    
    def security_middleware(request: HttpRequest):
        """Middleware de sécurité de base"""
        # Vérification des en-têtes dangereux
        # Check dangerous headers
        # Verificar headers peligrosos
        # 检查危险的标头
        if request.headers.get('user-agent', '').lower().find('bot') != -1:
            print(f"🤖 Bot detected from {request.client_ip}")
    
    app.add_middleware(cors_middleware)
    app.add_middleware(logging_middleware)
    app.add_middleware(security_middleware)

def handle_shutdown(signum, frame):
    """
    Gestionnaire d'arrêt empathique
    Empathic shutdown handler
    Manejador de apagado empático
    同理心关闭处理程序
    """
    print(f"\n🔄 Received signal {signum}, initiating graceful shutdown...")
    app.stop()
    sys.exit(0)

def main():
    """
    Point d'entrée principal du serveur Central-API
    Main entry point for Central-API server
    Punto de entrada principal del servidor Central-API
    中央API服务器的主要入口点
    """
    print("🚀 OpenRed Central-API v3.0 - Ultra-Minimalist Directory Server")
    print("📋 Philosophy: Code maison whenever possible")
    print("🔧 Engine: OpenRed Micro-Engine (Zero external dependencies)")
    print("💖 Empathy: Maximum level enabled")
    print()
    
    try:
        # Configuration des gestionnaires de signaux
        # Setup signal handlers
        # Configurar manejadores de señales
        # 设置信号处理程序
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)
        
        # Configuration des middlewares
        # Setup middleware
        # Configurar middleware
        # 设置中间件
        setup_empathic_middleware()
        
        # Enregistrement des routes
        # Register routes
        # Registrar rutas
        # 注册路由
        register_central_api_routes()
        
        # Génération des clés de sécurité
        # Generate security keys
        # Generar claves de seguridad
        # 生成安全密钥
        print("🔐 Generating security keys...")
        security_engine.generate_key_pair()
        print("✅ Security keys generated")
        
        # Configuration du serveur
        # Server configuration
        # Configuración del servidor
        # 服务器配置
        host = app_config.host
        port = app_config.port
        
        print(f"🌍 Starting server on {host}:{port}")
        print(f"📊 Max nodes: {app_config.max_nodes}")
        print(f"⏰ Heartbeat interval: {directory_config.heartbeat_check_interval}s (ultra-empathic)")
        print()
        
        # Démarrage du serveur
        # Start server
        # Iniciar servidor
        # 启动服务器
        app.start()
    
    except KeyboardInterrupt:
        print("\n⌨️  Keyboard interrupt received")
        handle_shutdown(signal.SIGINT, None)
    
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()