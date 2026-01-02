"""
Redis Cache Configuration
Defines TTL values and cache keys patterns for different data types
"""

from enum import Enum
from typing import Dict


class CacheType(Enum):
    """Types de données cachées avec leurs TTL respectifs"""
    DASHBOARD = "dashboard"
    SEARCH = "search"
    USER = "user"
    PRODUCT = "product"
    ANALYTICS = "analytics"


class CacheConfig:
    """Configuration centralisée du cache Redis"""
    
    # TTL par défaut (en secondes)
    DEFAULT_TTL = 300  # 5 minutes
    
    # TTL configurables par type de données
    TTL_CONFIG: Dict[CacheType, int] = {
        CacheType.DASHBOARD: 300,      # 5 minutes - KPIs dashboard
        CacheType.SEARCH: 3600,        # 1 heure - Résultats de recherche
        CacheType.USER: 1800,          # 30 minutes - Profils utilisateurs
        CacheType.PRODUCT: 7200,       # 2 heures - Catalogues produits
        CacheType.ANALYTICS: 600,      # 10 minutes - Statistiques temps réel
    }
    
    # Préfixes des clés Redis par type
    KEY_PREFIXES: Dict[CacheType, str] = {
        CacheType.DASHBOARD: "cache:dashboard:",
        CacheType.SEARCH: "cache:search:",
        CacheType.USER: "cache:user:",
        CacheType.PRODUCT: "cache:product:",
        CacheType.ANALYTICS: "cache:analytics:",
    }
    
    # Configuration de la stratégie de retry
    RETRY_CONFIG = {
        "max_retries": 3,
        "retry_delay": 0.1,  # secondes
        "exponential_backoff": True
    }
    
    # Configuration de compression (pour les grandes réponses)
    COMPRESSION_CONFIG = {
        "enabled": True,
        "min_size": 1024,  # Compresser si > 1KB
        "level": 6  # Niveau de compression zlib (1-9)
    }
    
    # Configuration de monitoring
    MONITORING_CONFIG = {
        "track_hits": True,
        "track_misses": True,
        "track_errors": True,
        "stats_ttl": 86400  # 24 heures
    }
    
    @classmethod
    def get_ttl(cls, cache_type: CacheType) -> int:
        """Retourne le TTL pour un type de cache donné"""
        return cls.TTL_CONFIG.get(cache_type, cls.DEFAULT_TTL)
    
    @classmethod
    def get_key_prefix(cls, cache_type: CacheType) -> str:
        """Retourne le préfixe de clé pour un type de cache donné"""
        return cls.KEY_PREFIXES.get(cache_type, "cache:default:")
    
    @classmethod
    def build_cache_key(cls, cache_type: CacheType, identifier: str) -> str:
        """Construit une clé de cache complète"""
        prefix = cls.get_key_prefix(cache_type)
        return f"{prefix}{identifier}"


# Export direct pour faciliter l'utilisation
TTL_CONFIG = CacheConfig.TTL_CONFIG
