"""
Middleware de logging des requêtes pour OpenRed Central API
Request logging middleware for OpenRed Central API
Middleware de logging de solicitudes para OpenRed Central API  
OpenRed 中央 API 的请求日志中间件
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logging import logger, audit_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware qui log toutes les requêtes HTTP entrantes et sortantes
    Middleware that logs all incoming and outgoing HTTP requests
    Middleware que registra todas las solicitudes HTTP entrantes y salientes
    记录所有传入和传出 HTTP 请求的中间件
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # Chemins à exclure du logging détaillé | Paths to exclude from detailed logging | Rutas a excluir del logging detallado | 要从详细日志中排除的路径
        self.exclude_paths = {
            "/health",
            "/metrics", 
            "/favicon.ico",
            "/robots.txt"
        }
        
        # Headers sensibles à masquer | Sensitive headers to mask | Headers sensibles a enmascarar | 要掩码的敏感标头
        self.sensitive_headers = {
            "authorization",
            "x-api-key", 
            "cookie",
            "x-auth-token"
        }
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Obtient l'IP réelle du client en tenant compte des proxies
        Get real client IP considering proxies
        Obtiene la IP real del cliente considerando proxies
        考虑代理获取真实客户端 IP
        """
        
        # Vérifier les headers de proxy | Check proxy headers | Verificar headers de proxy | 检查代理标头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
            
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        # IP directe | Direct IP | IP directa | 直接 IP
        return request.client.host if request.client else "unknown"
    
    def _mask_sensitive_data(self, headers: dict) -> dict:
        """
        Masque les données sensibles dans les headers
        Mask sensitive data in headers
        Enmascara datos sensibles en headers
        在标头中掩码敏感数据
        """
        
        masked_headers = {}
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                masked_headers[key] = "***MASKED***"
            else:
                masked_headers[key] = value
        return masked_headers
    
    def _should_log_detailed(self, path: str) -> bool:
        """
        Détermine si le chemin nécessite un logging détaillé
        Determine if path requires detailed logging
        Determina si la ruta requiere logging detallado
        确定路径是否需要详细日志
        """
        
        return path not in self.exclude_paths
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Traite la requête avec logging complet
        Process request with complete logging
        Procesa la solicitud con logging completo
        使用完整日志处理请求
        """
        
        # Générer un ID de requête unique | Generate unique request ID | Generar ID de solicitud único | 生成唯一请求 ID
        request_id = str(uuid.uuid4())
        
        # Informations de base de la requête | Basic request information | Información básica de la solicitud | 基本请求信息
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        path = request.url.path
        method = request.method
        user_agent = request.headers.get("User-Agent", "Unknown")
        
        # Logging détaillé pour certaines routes | Detailed logging for certain routes | Logging detallado para ciertas rutas | 某些路由的详细日志
        should_log_detailed = self._should_log_detailed(path)
        
        if should_log_detailed:
            # Headers masqués | Masked headers | Headers enmascarados | 掩码标头
            masked_headers = self._mask_sensitive_data(dict(request.headers))
            
            logger.info(
                "Request started",
                request_id=request_id,
                method=method,
                path=path,
                client_ip=client_ip,
                user_agent=user_agent,
                headers=masked_headers,
                query_params=dict(request.query_params)
            )
        
        try:
            # Traiter la requête | Process request | Procesar solicitud | 处理请求
            response = await call_next(request)
            
            # Calculer le temps de traitement | Calculate processing time | Calcular tiempo de procesamiento | 计算处理时间
            process_time = time.time() - start_time
            
            # Ajouter l'ID de requête à la réponse | Add request ID to response | Agregar ID de solicitud a la respuesta | 将请求 ID 添加到响应
            response.headers["X-Request-ID"] = request_id
            
            # Log de fin de requête | End of request log | Log de fin de solicitud | 请求结束日志
            if should_log_detailed:
                logger.info(
                    "Request completed",
                    request_id=request_id,
                    method=method,
                    path=path,
                    status_code=response.status_code,
                    client_ip=client_ip,
                    process_time=round(process_time, 4),
                    response_size=response.headers.get("content-length", "unknown")
                )
            
            # Log d'audit pour les opérations sensibles | Audit log for sensitive operations | Log de auditoría para operaciones sensibles | 敏感操作的审核日志
            if self._is_sensitive_operation(method, path, response.status_code):
                audit_logger.log_api_access(
                    endpoint=f"{method} {path}",
                    ip_address=client_ip,
                    user_agent=user_agent,
                    status_code=response.status_code,
                    request_id=request_id
                )
            
            return response
            
        except Exception as e:
            # Calculer le temps même en cas d'erreur | Calculate time even on error | Calcular tiempo incluso en error | 即使出错也计算时间
            process_time = time.time() - start_time
            
            logger.error(
                "Request failed",
                request_id=request_id,
                method=method,
                path=path,
                client_ip=client_ip,
                error=str(e),
                error_type=type(e).__name__,
                process_time=round(process_time, 4)
            )
            
            # Log d'audit pour les erreurs | Audit log for errors | Log de auditoría para errores | 错误的审核日志
            audit_logger.log_api_access(
                endpoint=f"{method} {path}",
                ip_address=client_ip,
                user_agent=user_agent,
                status_code=500,
                request_id=request_id,
                error=str(e)
            )
            
            # Re-lancer l'exception | Re-raise exception | Relanzar excepción | 重新抛出异常
            raise
    
    def _is_sensitive_operation(self, method: str, path: str, status_code: int) -> bool:
        """
        Détermine si l'opération est sensible et nécessite un audit
        Determine if operation is sensitive and requires audit
        Determina si la operación es sensible y requiere auditoría
        确定操作是否敏感并需要审核
        """
        
        # Opérations d'authentification | Authentication operations | Operaciones de autenticación | 认证操作
        auth_paths = ["/api/v1/auth/", "/api/v1/login", "/api/v1/register"]
        
        # Opérations d'administration | Administration operations | Operaciones de administración | 管理操作
        admin_paths = ["/api/v1/admin/", "/api/v1/nodes/", "/api/v1/users/"]
        
        # Vérifier si le chemin est sensible | Check if path is sensitive | Verificar si la ruta es sensible | 检查路径是否敏感
        is_sensitive_path = any(auth_path in path for auth_path in auth_paths + admin_paths)
        
        # Opérations de modification | Modification operations | Operaciones de modificación | 修改操作
        is_modification = method in ["POST", "PUT", "DELETE", "PATCH"]
        
        # Erreurs d'authentification | Authentication errors | Errores de autenticación | 认证错误
        is_auth_error = status_code in [401, 403]
        
        return is_sensitive_path or is_modification or is_auth_error
