"""
Middleware de rate limiting avancé pour OpenRed Central API

Protection contre les abus avec limitation de débit adaptative
et intégration Redis pour la scalabilité.
"""

import time
import asyncio
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as aioredis

from ..core.config import settings
from ..core.logging import logger


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting avec support Redis"""
    
    def __init__(self, app, redis_client: Optional[aioredis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client
        self.local_cache: Dict[str, Dict] = {}
        self.cache_cleanup_last = datetime.now()
        
        # Configuration par endpoint
        self.endpoint_limits = {
            # Authentification - strict
            "/api/v1/auth/register": {"requests": 5, "window": 3600},  # 5/heure
            "/api/v1/auth/login": {"requests": 10, "window": 3600},    # 10/heure
            "/api/v1/auth/refresh": {"requests": 20, "window": 3600},  # 20/heure
            
            # Nodes - modéré
            "/api/v1/nodes/register": {"requests": 10, "window": 3600}, # 10/heure
            "/api/v1/nodes/discover": {"requests": 100, "window": 3600}, # 100/heure
            "/api/v1/nodes/heartbeat": {"requests": 1440, "window": 3600}, # 24/minute (1440/heure)
            
            # Messages - élevé
            "/api/v1/messages/send": {"requests": 1000, "window": 3600}, # 1000/heure
            "/api/v1/messages/receive": {"requests": 2000, "window": 3600}, # 2000/heure
            
            # Admin - très strict
            "/api/v1/admin/*": {"requests": 20, "window": 3600}, # 20/heure
            
            # Défaut
            "*": {"requests": settings.rate_limit_per_minute * 60, "window": 3600}  # Par défaut
        }
    
    async def dispatch(self, request: Request, call_next):
        """Traite la requête avec rate limiting"""
        
        # Extraction des identifiants
        client_ip = self._get_client_ip(request)
        endpoint = self._normalize_endpoint(request.url.path)
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Clé de rate limiting
        rate_limit_key = f"rate_limit:{client_ip}:{endpoint}"
        
        # Vérification du rate limit
        is_allowed, remaining, reset_time = await self._check_rate_limit(
            rate_limit_key, endpoint, client_ip
        )
        
        if not is_allowed:
            logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                endpoint=endpoint,
                user_agent=user_agent
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": reset_time
                },
                headers={
                    "X-RateLimit-Limit": str(self._get_endpoint_limit(endpoint)["requests"]),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time)
                }
            )
        
        # Traitement de la requête
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Ajout des headers de rate limiting
        response.headers["X-RateLimit-Limit"] = str(self._get_endpoint_limit(endpoint)["requests"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        response.headers["X-Process-Time"] = str(round(process_time, 4))
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extrait l'IP réelle du client (gestion des proxies)"""
        # Headers à vérifier dans l'ordre de priorité
        ip_headers = [
            "x-forwarded-for",
            "x-real-ip",
            "x-client-ip",
            "cf-connecting-ip",  # Cloudflare
        ]
        
        for header in ip_headers:
            ip = request.headers.get(header)
            if ip:
                # Prend la première IP si multiples (proxy chain)
                return ip.split(",")[0].strip()
        
        # Fallback sur l'IP de connexion
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    def _normalize_endpoint(self, path: str) -> str:
        """Normalise l'endpoint pour la configuration"""
        # Supprime les paramètres de requête
        path = path.split("?")[0]
        
        # Vérifie les patterns spécifiques
        for pattern in self.endpoint_limits.keys():
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                if path.startswith(prefix):
                    return pattern
            elif pattern == path:
                return pattern
        
        return "*"  # Pattern par défaut
    
    def _get_endpoint_limit(self, endpoint: str) -> Dict[str, int]:
        """Récupère la configuration de limite pour un endpoint"""
        return self.endpoint_limits.get(endpoint, self.endpoint_limits["*"])
    
    async def _check_rate_limit(self, key: str, endpoint: str, client_ip: str) -> Tuple[bool, int, int]:
        """Vérifie le rate limit pour une clé donnée"""
        limit_config = self._get_endpoint_limit(endpoint)
        max_requests = limit_config["requests"]
        window_seconds = limit_config["window"]
        
        if self.redis_client:
            return await self._check_redis_rate_limit(key, max_requests, window_seconds)
        else:
            return await self._check_local_rate_limit(key, max_requests, window_seconds)
    
    async def _check_redis_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int, int]:
        """Vérification avec Redis (recommandé pour la production)"""
        try:
            current_time = int(time.time())
            window_start = current_time - window_seconds
            
            pipe = self.redis_client.pipeline()
            
            # Supprime les entrées expirées
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Compte les requêtes actuelles
            pipe.zcard(key)
            
            # Ajoute la requête actuelle
            pipe.zadd(key, {str(current_time): current_time})
            
            # Définit l'expiration
            pipe.expire(key, window_seconds)
            
            results = await pipe.execute()
            current_requests = results[1]
            
            # Calcul des valeurs de retour
            remaining = max(0, max_requests - current_requests - 1)
            reset_time = window_seconds - (current_time % window_seconds)
            
            return current_requests < max_requests, remaining, reset_time
            
        except Exception as e:
            logger.error("Redis rate limit check failed", error=str(e), key=key)
            # Fallback sur le cache local
            return await self._check_local_rate_limit(key, max_requests, window_seconds)
    
    async def _check_local_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int, int]:
        """Vérification avec cache local (fallback)"""
        current_time = time.time()
        
        # Nettoyage périodique du cache
        await self._cleanup_local_cache()
        
        # Initialise l'entrée si nécessaire
        if key not in self.local_cache:
            self.local_cache[key] = {"requests": [], "window_start": current_time}
        
        entry = self.local_cache[key]
        window_start = current_time - window_seconds
        
        # Supprime les requêtes expirées
        entry["requests"] = [req_time for req_time in entry["requests"] if req_time > window_start]
        
        # Ajoute la requête actuelle
        entry["requests"].append(current_time)
        
        # Calcul des valeurs de retour
        current_requests = len(entry["requests"])
        remaining = max(0, max_requests - current_requests)
        reset_time = int(window_seconds - (current_time % window_seconds))
        
        return current_requests <= max_requests, remaining, reset_time
    
    async def _cleanup_local_cache(self):
        """Nettoie le cache local périodiquement"""
        now = datetime.now()
        if (now - self.cache_cleanup_last).seconds > 300:  # Toutes les 5 minutes
            current_time = time.time()
            keys_to_delete = []
            
            for key, entry in self.local_cache.items():
                # Supprime les entrées inactives depuis plus d'une heure
                if current_time - max(entry["requests"], default=[0])[-1:][0] > 3600:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self.local_cache[key]
            
            self.cache_cleanup_last = now
            
            if keys_to_delete:
                logger.debug("Cleaned up local rate limit cache", cleaned_entries=len(keys_to_delete))


class AdaptiveRateLimiter:
    """Rate limiter adaptatif basé sur la charge système"""
    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self.redis_client = redis_client
        self.base_limits = settings.rate_limit_per_minute
        self.current_multiplier = 1.0
        self.last_adjustment = datetime.now()
    
    async def get_current_limit(self, endpoint: str) -> int:
        """Calcule la limite actuelle basée sur la charge"""
        await self._adjust_limits()
        base_limit = self._get_base_limit(endpoint)
        return int(base_limit * self.current_multiplier)
    
    async def _adjust_limits(self):
        """Ajuste les limites basé sur les métriques système"""
        now = datetime.now()
        if (now - self.last_adjustment).seconds < 60:  # Ajuste toutes les minutes
            return
        
        try:
            # Récupère les métriques système (CPU, mémoire, etc.)
            cpu_usage = await self._get_cpu_usage()
            memory_usage = await self._get_memory_usage()
            
            # Calcule le multiplicateur basé sur la charge
            if cpu_usage > 80 or memory_usage > 85:
                self.current_multiplier = max(0.5, self.current_multiplier * 0.9)
            elif cpu_usage < 50 and memory_usage < 70:
                self.current_multiplier = min(2.0, self.current_multiplier * 1.1)
            
            self.last_adjustment = now
            
            logger.info(
                "Rate limit adjusted",
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                multiplier=self.current_multiplier
            )
            
        except Exception as e:
            logger.error("Failed to adjust rate limits", error=str(e))
    
    def _get_base_limit(self, endpoint: str) -> int:
        """Récupère la limite de base pour un endpoint"""
        # Implémentation simplifiée
        return self.base_limits
    
    async def _get_cpu_usage(self) -> float:
        """Récupère l'utilisation CPU actuelle"""
        # Implémentation simplifiée - à remplacer par une vraie métrique
        return 50.0
    
    async def _get_memory_usage(self) -> float:
        """Récupère l'utilisation mémoire actuelle"""
        # Implémentation simplifiée - à remplacer par une vraie métrique
        return 60.0
