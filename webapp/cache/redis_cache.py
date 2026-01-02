"""
Redis Cache Manager with decorators and utilities
Provides caching, invalidation, and error handling for Flask routes
"""

import json
import zlib
import hashlib
import time
from functools import wraps
from typing import Optional, Callable, Any, Dict, List
from flask import request, jsonify, make_response
import redis
from datetime import datetime

from .config import CacheConfig, CacheType


class CacheManager:
    """Gestionnaire centralisé du cache Redis avec gestion d'erreurs"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0
        }
    
    def set_client(self, redis_client: redis.Redis):
        """Configure le client Redis (appelé après l'initialisation de Flask)"""
        self.redis_client = redis_client
    
    def _is_available(self) -> bool:
        """Vérifie si Redis est disponible"""
        if self.redis_client is None:
            return False
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False
    
    def _compress_data(self, data: str) -> bytes:
        """Compresse les données si la configuration l'autorise"""
        if not CacheConfig.COMPRESSION_CONFIG["enabled"]:
            return data.encode('utf-8')
        
        if len(data) < CacheConfig.COMPRESSION_CONFIG["min_size"]:
            return data.encode('utf-8')
        
        level = CacheConfig.COMPRESSION_CONFIG["level"]
        return zlib.compress(data.encode('utf-8'), level)
    
    def _decompress_data(self, data: bytes) -> str:
        """Décompresse les données si nécessaire"""
        try:
            # Tenter la décompression
            return zlib.decompress(data).decode('utf-8')
        except zlib.error:
            # Si échec, les données ne sont pas compressées
            return data.decode('utf-8')
    
    def get(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur du cache
        Retourne None si la clé n'existe pas ou en cas d'erreur
        """
        if not self._is_available():
            return None
        
        try:
            data = self.redis_client.get(key)
            if data is None:
                self.stats["misses"] += 1
                return None
            
            # Décompression et désérialisation
            json_str = self._decompress_data(data)
            result = json.loads(json_str)
            self.stats["hits"] += 1
            return result
            
        except Exception as e:
            self.stats["errors"] += 1
            print(f"[CACHE ERROR] Get key '{key}': {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Stocke une valeur dans le cache avec TTL
        Retourne True si succès, False sinon
        """
        if not self._is_available():
            return False
        
        try:
            # Sérialisation et compression
            json_str = json.dumps(value)
            data = self._compress_data(json_str)
            
            # Définir le TTL
            if ttl is None:
                ttl = CacheConfig.DEFAULT_TTL
            
            # Stocker dans Redis
            self.redis_client.setex(key, ttl, data)
            return True
            
        except Exception as e:
            self.stats["errors"] += 1
            print(f"[CACHE ERROR] Set key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Supprime une clé du cache"""
        if not self._is_available():
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            self.stats["errors"] += 1
            print(f"[CACHE ERROR] Delete key '{key}': {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Supprime toutes les clés correspondant au pattern
        Retourne le nombre de clés supprimées
        """
        if not self._is_available():
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                return deleted
            return 0
        except Exception as e:
            self.stats["errors"] += 1
            print(f"[CACHE ERROR] Delete pattern '{pattern}': {e}")
            return 0
    
    def get_ttl(self, key: str) -> int:
        """Retourne le TTL restant d'une clé (-1 si pas de TTL, -2 si inexistante)"""
        if not self._is_available():
            return -2
        
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            print(f"[CACHE ERROR] Get TTL for key '{key}': {e}")
            return -2
    
    def exists(self, key: str) -> bool:
        """Vérifie si une clé existe dans le cache"""
        if not self._is_available():
            return False
        
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            print(f"[CACHE ERROR] Check existence of key '{key}': {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'utilisation du cache"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "errors": self.stats["errors"],
            "total_requests": total_requests,
            "hit_rate": round(hit_rate, 2),
            "is_available": self._is_available()
        }
    
    def reset_stats(self):
        """Réinitialise les statistiques"""
        self.stats = {"hits": 0, "misses": 0, "errors": 0}


# Instance globale du cache manager
cache_manager = CacheManager()


def _generate_cache_key(prefix: str, request_obj) -> str:
    """
    Génère une clé de cache unique basée sur l'URL et les paramètres
    """
    # Construire une chaîne unique à partir de la requête
    url = request_obj.url
    args = sorted(request_obj.args.items())
    key_str = f"{url}:{args}"
    
    # Hash pour garder une clé courte
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    
    return f"{prefix}{key_hash}"


def cache_response(
    cache_type: CacheType,
    ttl: Optional[int] = None,
    key_func: Optional[Callable] = None
):
    """
    Décorateur pour cacher les réponses des routes Flask
    
    Args:
        cache_type: Type de cache (définit le préfixe et TTL par défaut)
        ttl: TTL custom en secondes (optionnel)
        key_func: Fonction custom pour générer la clé (optionnel)
    
    Usage:
        @app.route('/api/dashboard')
        @cache_response(CacheType.DASHBOARD)
        def get_dashboard():
            return jsonify({"data": "expensive_computation"})
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Déterminer le TTL
            effective_ttl = ttl if ttl is not None else CacheConfig.get_ttl(cache_type)
            
            # Générer la clé de cache
            if key_func:
                cache_key = key_func(request)
            else:
                prefix = CacheConfig.get_key_prefix(cache_type)
                cache_key = _generate_cache_key(prefix, request)
            
            # Tenter de récupérer depuis le cache
            cached_data = cache_manager.get(cache_key)
            if cached_data is not None:
                print(f"[CACHE HIT] {cache_key}")
                response = make_response(jsonify(cached_data))
                response.headers['X-Cache'] = 'HIT'
                response.headers['X-Cache-Key'] = cache_key
                return response
            
            # Cache miss - exécuter la fonction
            print(f"[CACHE MISS] {cache_key}")
            result = func(*args, **kwargs)
            
            # Extraire les données de la réponse
            if hasattr(result, 'get_json'):
                data_to_cache = result.get_json()
            elif isinstance(result, tuple):
                # Format (response, status_code)
                data_to_cache = result[0].get_json() if hasattr(result[0], 'get_json') else None
            else:
                data_to_cache = None
            
            # Mettre en cache si possible
            if data_to_cache is not None:
                success = cache_manager.set(cache_key, data_to_cache, effective_ttl)
                if success:
                    print(f"[CACHE SET] {cache_key} (TTL: {effective_ttl}s)")
            
            # Ajouter des headers de debug
            if hasattr(result, 'headers'):
                result.headers['X-Cache'] = 'MISS'
                result.headers['X-Cache-Key'] = cache_key
            elif isinstance(result, tuple) and hasattr(result[0], 'headers'):
                result[0].headers['X-Cache'] = 'MISS'
                result[0].headers['X-Cache-Key'] = cache_key
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(cache_key: str) -> bool:
    """
    Invalide une entrée de cache spécifique
    
    Usage:
        invalidate_cache("cache:dashboard:abc123")
    """
    return cache_manager.delete(cache_key)


def invalidate_pattern(pattern: str) -> int:
    """
    Invalide toutes les entrées correspondant au pattern
    
    Usage:
        invalidate_pattern("cache:dashboard:*")  # Invalide tous les dashboards
        invalidate_pattern("cache:search:*")     # Invalide toutes les recherches
    """
    return cache_manager.delete_pattern(pattern)


def invalidate_cache_type(cache_type: CacheType) -> int:
    """
    Invalide tout le cache d'un type donné
    
    Usage:
        invalidate_cache_type(CacheType.DASHBOARD)
    """
    prefix = CacheConfig.get_key_prefix(cache_type)
    pattern = f"{prefix}*"
    return cache_manager.delete_pattern(pattern)


def get_cache_stats() -> Dict[str, Any]:
    """
    Retourne les statistiques d'utilisation du cache
    
    Returns:
        Dict contenant hits, misses, errors, hit_rate, etc.
    """
    return cache_manager.get_stats()
