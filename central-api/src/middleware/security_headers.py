"""
Middleware de headers de sécurité pour OpenRed Central API
Security headers middleware for OpenRed Central API  
Middleware de headers de seguridad para OpenRed Central API
OpenRed 中央 API 的安全标头中间件
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time

from src.core.logging import logger


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware qui ajoute des headers de sécurité à toutes les réponses
    Middleware that adds security headers to all responses
    Middleware que agrega headers de seguridad a todas las respuestas  
    为所有响应添加安全标头的中间件
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # Headers de sécurité OWASP | OWASP security headers | Headers de seguridad OWASP | OWASP 安全标头
        self.security_headers = {
            # Protection XSS | XSS Protection | Protección XSS | XSS 保护
            "X-XSS-Protection": "1; mode=block",
            
            # Prévention du sniffing MIME | MIME sniffing prevention | Prevención de sniffing MIME | MIME 嗅探防护
            "X-Content-Type-Options": "nosniff",
            
            # Protection contre le clickjacking | Clickjacking protection | Protección contra clickjacking | 点击劫持保护
            "X-Frame-Options": "DENY",
            
            # Politique de référent | Referrer policy | Política de referente | 引用者策略
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Permissions Policy | Permissions Policy | Política de permisos | 权限策略
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            
            # Content Security Policy | Content Security Policy | Política de seguridad de contenido | 内容安全策略
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            ),
            
            # HSTS (HTTPS Strict Transport Security) | HSTS | HSTS | HSTS
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Headers de cache sécurisé | Secure cache headers | Headers de cache seguro | 安全缓存标头
            "Cache-Control": "no-store, no-cache, must-revalidate, private",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Traite la requête et ajoute les headers de sécurité
        Process request and add security headers
        Procesa la solicitud y agrega headers de seguridad
        处理请求并添加安全标头
        """
        
        start_time = time.time()
        
        try:
            # Traiter la requête | Process request | Procesar solicitud | 处理请求
            response = await call_next(request)
            
            # Ajouter les headers de sécurité | Add security headers | Agregar headers de seguridad | 添加安全标头
            for header_name, header_value in self.security_headers.items():
                response.headers[header_name] = header_value
            
            # Header de temps de traitement | Processing time header | Header de tiempo de procesamiento | 处理时间标头
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # Header de version API | API version header | Header de versión API | API 版本标头
            response.headers["X-API-Version"] = "2.0.0"
            
            # Header de serveur personnalisé | Custom server header | Header de servidor personalizado | 自定义服务器标头
            response.headers["Server"] = "OpenRed-Central-API/2.0"
            
            return response
            
        except Exception as e:
            logger.error(
                "Security headers middleware error",
                error=str(e),
                path=request.url.path,
                method=request.method
            )
            
            # Réponse d'erreur avec headers de sécurité | Error response with security headers | Respuesta de error con headers de seguridad | 带安全标头的错误响应
            error_response = JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred"
                }
            )
            
            # Ajouter les headers même en cas d'erreur | Add headers even on error | Agregar headers incluso en error | 即使出错也添加标头
            for header_name, header_value in self.security_headers.items():
                error_response.headers[header_name] = header_value
            
            return error_response
