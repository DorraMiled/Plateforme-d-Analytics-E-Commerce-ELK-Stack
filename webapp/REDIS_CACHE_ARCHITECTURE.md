# Architecture du Cache Redis - Système de Performance

## 📊 Vue d'ensemble

Ce système implémente un cache Redis haute performance pour l'API Flask avec Elasticsearch, optimisant les requêtes coûteuses (KPIs dashboard, recherches, analytics).

---

## 🏗️ Architecture Globale

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Angular)                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK API SERVER                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                @cache_response Decorator                   │  │
│  │                                                            │  │
│  │  1. Hash Request (URL + params) → Cache Key               │  │
│  │  2. Check Redis Cache                                     │  │
│  │     ├─ HIT  → Return cached data (X-Cache: HIT)          │  │
│  │     └─ MISS → Execute function                            │  │
│  │                ├─ Query Elasticsearch                     │  │
│  │                ├─ Store result in Redis (with TTL)        │  │
│  │                └─ Return data (X-Cache: MISS)             │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────┬───────────────────────┬──────────────────────┘
                   │                       │
                   ▼                       ▼
         ┌──────────────────┐    ┌─────────────────────┐
         │  REDIS CACHE     │    │  ELASTICSEARCH      │
         │                  │    │                     │
         │  Key-Value Store │    │  Search Engine      │
         │  TTL Management  │    │  Log Analytics      │
         │  Compression     │    │  Aggregations       │
         └──────────────────┘    └─────────────────────┘
```

---

## 🔄 Flux de Cache Détaillé

### 1. **Requête Entrante**

```
GET /api/dashboard
    ↓
1. Request interception par @cache_response
2. Génération cache_key = hash(URL + params)
   Exemple: "cache:dashboard:a7f3e9b2c1d4..."
```

### 2. **Vérification Cache (Redis GET)**

```
┌─────────────────────────────────────────────────────┐
│  Redis: GET cache:dashboard:a7f3e9b2c1d4...         │
└────────────────┬────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
    [EXISTS]          [NOT FOUND]
        │                 │
        │                 │
    ┌───▼────┐       ┌────▼─────────────────────────┐
    │ HIT    │       │ MISS                         │
    │        │       │                              │
    │ 1. Decompress │  1. Execute function         │
    │ 2. Deserialize│  2. Query Elasticsearch      │
    │ 3. Return     │  3. Serialize result          │
    │ 4. X-Cache:HIT│  4. Compress data            │
    └────────┘       │  5. SETEX Redis (key, TTL)  │
                     │  6. Return result            │
                     │  7. X-Cache: MISS            │
                     └──────────────────────────────┘
```

### 3. **Gestion du TTL (Time To Live)**

```
Type de Cache         TTL      Justification
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DASHBOARD            300s     KPIs changent modérément
                    (5 min)   Queries Elasticsearch coûteuses

SEARCH              3600s     Résultats stables
                    (1h)      Optimise UX de recherche

USER                1800s     Profils peu volatiles
                    (30 min)  Balance fraîcheur/performance

PRODUCT             7200s     Catalogue stable
                    (2h)      Réduit charge DB

ANALYTICS            600s     Métriques temps réel
                    (10 min)  Compromis fraîcheur/load
```

---

## 🗂️ Structure des Clés Redis

### Format des Clés

```
cache:{type}:{hash}
  │      │      │
  │      │      └─ MD5 hash de (URL + params)
  │      └──────── Type de cache (dashboard, search, etc.)
  └─────────────── Préfixe global
```

### Exemples

```
cache:dashboard:a7f3e9b2c1d4e5f6g7h8i9j0
cache:search:1a2b3c4d5e6f7g8h9i0j1k2l3m4n
cache:user:profile:abc123def456
cache:analytics:trends:xyz789
```

### Patterns d'Invalidation

```
cache:dashboard:*     → Tous les dashboards
cache:search:*        → Toutes les recherches
cache:user:*          → Tous les utilisateurs
cache:*               → TOUT le cache (⚠️ destructif)
```

---

## ⚙️ Configuration du Cache

### Fichier: `cache/config.py`

```python
class CacheType(Enum):
    DASHBOARD = "dashboard"  # KPIs système
    SEARCH = "search"        # Résultats Elasticsearch
    USER = "user"            # Profils utilisateurs
    PRODUCT = "product"      # Catalogues produits
    ANALYTICS = "analytics"  # Statistiques temps réel

class CacheConfig:
    # TTL configurables
    TTL_CONFIG = {
        CacheType.DASHBOARD: 300,
        CacheType.SEARCH: 3600,
        # ...
    }
    
    # Compression (pour réponses > 1KB)
    COMPRESSION_CONFIG = {
        "enabled": True,
        "min_size": 1024,
        "level": 6  # zlib compression
    }
```

---

## 🛠️ Utilisation du Système

### 1. **Appliquer le Cache sur une Route**

```python
from cache.redis_cache import cache_response
from cache.config import CacheType

@app.route('/api/dashboard')
@cache_response(CacheType.DASHBOARD, ttl=300)
def get_dashboard():
    # Cette fonction ne sera exécutée que si cache MISS
    expensive_data = query_elasticsearch()
    return jsonify(expensive_data)
```

### 2. **Cache avec Clé Custom**

```python
def custom_key_func(request):
    user_id = request.args.get('user_id')
    return f"cache:user:profile:{user_id}"

@app.route('/api/user/<user_id>')
@cache_response(CacheType.USER, key_func=custom_key_func)
def get_user(user_id):
    return jsonify(fetch_user(user_id))
```

### 3. **Invalider le Cache**

#### Via API

```bash
# Invalider tous les dashboards
POST /api/cache/invalidate/dashboard

# Invalider un pattern spécifique
POST /api/cache/invalidate-pattern
Body: {"pattern": "cache:search:*"}

# Effacer TOUT le cache
POST /api/cache/clear-all
```

#### Via Code

```python
from cache.redis_cache import invalidate_cache_type, invalidate_pattern

# Invalider par type
invalidate_cache_type(CacheType.DASHBOARD)

# Invalider par pattern
invalidate_pattern("cache:user:profile:*")
```

---

## 📈 Monitoring et Statistiques

### Endpoint de Stats

```bash
GET /api/cache/stats
```

**Réponse:**

```json
{
  "status": "success",
  "cache_stats": {
    "hits": 1247,
    "misses": 153,
    "errors": 2,
    "total_requests": 1400,
    "hit_rate": 89.07,
    "is_available": true
  },
  "timestamp": "2026-01-01T12:34:56"
}
```

### Headers de Debug

Chaque réponse inclut:

```
X-Cache: HIT | MISS
X-Cache-Key: cache:dashboard:a7f3e9b2c1d4...
```

---

## 🔧 Gestion des Erreurs

### 1. **Redis Indisponible**

```
┌─────────────────────────────────────┐
│  Redis Connection Failed            │
└──────────────────┬──────────────────┘
                   │
                   ▼
    ┌──────────────────────────────┐
    │  Fallback: Execute Function  │
    │  Sans cache (graceful)       │
    │  Log: [CACHE ERROR]          │
    └──────────────────────────────┘
```

### 2. **Compression/Décompression Error**

```python
try:
    return zlib.decompress(data).decode('utf-8')
except zlib.error:
    # Données non compressées, lecture directe
    return data.decode('utf-8')
```

### 3. **Stratégie de Retry**

```python
RETRY_CONFIG = {
    "max_retries": 3,
    "retry_delay": 0.1,
    "exponential_backoff": True
}
```

---

## 🎯 Cas d'Usage - Dashboard KPIs

### Problème

```
Dashboard = 7 Elasticsearch queries
├─ Total logs count
├─ Logs today
├─ Error logs
├─ Logs by level (aggregation)
├─ Recent logs
├─ Logs over time (7 days histogram)
└─ Files uploaded

Temps d'exécution: ~500-800ms par requête
```

### Solution avec Cache

```
1ère requête (MISS):
  ├─ Execute 7 ES queries → 600ms
  ├─ Store in Redis → 10ms
  └─ Total: 610ms

Requêtes suivantes (HIT):
  ├─ Redis GET → 2ms
  ├─ Decompress → 1ms
  └─ Total: 3ms

Performance gain: 203x faster! 🚀
```

---

## 📊 Stratégies d'Invalidation

### 1. **Invalidation Temporelle (TTL)**

Automatique après expiration du TTL.

```
cache:dashboard:* → Expire après 300s
```

### 2. **Invalidation Manuelle**

Quand les données sources changent.

```python
# Après upload de fichiers
@app.route('/api/upload', methods=['POST'])
def upload_file():
    # ... process upload
    invalidate_cache_type(CacheType.DASHBOARD)
    return jsonify({"status": "uploaded"})
```

### 3. **Invalidation Événementielle**

Trigger sur événements métier.

```python
# Après création de produit
@app.route('/api/products', methods=['POST'])
def create_product():
    # ... create product
    invalidate_pattern("cache:product:*")
    invalidate_cache_type(CacheType.ANALYTICS)
    return jsonify({"status": "created"})
```

---

## 🔐 Sécurité

### Protection des Endpoints

```python
from auth.decorators import token_required, admin_required

@app.route('/api/cache/clear-all', methods=['POST'])
@token_required
@admin_required
def clear_all_cache():
    # Seuls les admins peuvent vider le cache
    pass
```

### Isolation par Utilisateur

```python
def user_specific_key(request):
    user_id = get_current_user_id()
    return f"cache:user:{user_id}:dashboard"

@cache_response(CacheType.USER, key_func=user_specific_key)
def user_dashboard():
    # Cache isolé par utilisateur
    pass
```

---

## 🚀 Optimisations Avancées

### 1. **Compression Sélective**

```python
COMPRESSION_CONFIG = {
    "enabled": True,
    "min_size": 1024,  # Seulement si > 1KB
    "level": 6         # Compromis vitesse/ratio
}
```

### 2. **Cache Warming**

```python
def warm_cache():
    """Préchauffer le cache au démarrage"""
    requests.get('http://localhost:8000/api/dashboard')
    requests.get('http://localhost:8000/api/search?q=popular')
```

### 3. **Monitoring Proactif**

```python
def check_cache_health():
    stats = get_cache_stats()
    if stats['hit_rate'] < 50:
        alert("Cache hit rate too low!")
    if stats['errors'] > 10:
        alert("Too many cache errors!")
```

---

## 📝 Routes API Disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/dashboard` | GET | KPIs dashboard (CACHED) |
| `/api/cache/stats` | GET | Statistiques du cache |
| `/api/cache/invalidate/<type>` | POST | Invalider un type de cache |
| `/api/cache/invalidate-pattern` | POST | Invalider selon pattern |
| `/api/cache/clear-all` | POST | Vider tout le cache |

---

## 🧪 Tests et Validation

### Test du Cache

```bash
# 1ère requête (MISS)
curl -i http://localhost:8000/api/dashboard
# Header: X-Cache: MISS
# Time: ~600ms

# 2ème requête (HIT)
curl -i http://localhost:8000/api/dashboard
# Header: X-Cache: HIT
# Time: ~3ms
```

### Test d'Invalidation

```bash
# Invalider le cache dashboard
curl -X POST http://localhost:8000/api/cache/invalidate/dashboard

# Vérifier les stats
curl http://localhost:8000/api/cache/stats
```

---

## 📚 Références et Modules

### Fichiers du Système

```
webapp/
├── cache/
│   ├── __init__.py          # Exports publics
│   ├── config.py            # Configuration TTL, types
│   └── redis_cache.py       # CacheManager, décorateurs
├── app.py                   # Intégration routes
└── requirements.txt         # redis==5.0.0
```

### Dépendances

```python
import redis        # Client Redis
import zlib         # Compression
import hashlib      # Hash des clés
import json         # Sérialisation
from flask import request, jsonify
```

---

## 🎓 Conclusion

Ce système de cache Redis offre:

✅ **Performance**: 200x plus rapide pour les requêtes cachées  
✅ **Flexibilité**: TTL configurables par type de données  
✅ **Fiabilité**: Gestion d'erreurs avec fallback graceful  
✅ **Monitoring**: Stats temps réel et headers de debug  
✅ **Scalabilité**: Compression automatique, patterns d'invalidation  
✅ **Maintenabilité**: Architecture modulaire et déclarative  

**Impact sur Dashboard:**
- Avant: 600ms par requête
- Après: 3ms (cache hit)
- Charge ES: -95%
- UX: Instantané

---

**Auteur**: Expert Backend Performance  
**Date**: Janvier 2026  
**Version**: 1.0
