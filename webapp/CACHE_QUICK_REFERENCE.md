# 🚀 Quick Reference - Système de Cache Redis

## ⚡ Commandes Rapides

### Démarrer les Services

```bash
# Démarrer Redis (Docker)
docker-compose up -d redis

# Démarrer Flask
cd webapp
python app.py
```

### Tester le Cache

```bash
# Test simple (MISS → HIT)
curl -i http://localhost:8000/api/dashboard  # MISS
curl -i http://localhost:8000/api/dashboard  # HIT

# Vérifier les headers
curl -I http://localhost:8000/api/dashboard | grep X-Cache

# Statistiques
curl http://localhost:8000/api/cache/stats | python -m json.tool
```

### Gérer le Cache

```bash
# Invalider par type
curl -X POST http://localhost:8000/api/cache/invalidate/dashboard
curl -X POST http://localhost:8000/api/cache/invalidate/search

# Invalider par pattern
curl -X POST http://localhost:8000/api/cache/invalidate-pattern \
  -H "Content-Type: application/json" \
  -d '{"pattern": "cache:search:*"}'

# Vider tout le cache
curl -X POST http://localhost:8000/api/cache/clear-all
```

---

## 📝 Code Snippets

### Décorer une Route

```python
from cache import cache_response, CacheType

@app.route('/api/products')
@cache_response(CacheType.PRODUCT, ttl=3600)
def get_products():
    return jsonify(fetch_products())
```

### Invalider le Cache

```python
from cache import invalidate_cache_type, invalidate_pattern

# Après modification de données
@app.route('/api/products', methods=['POST'])
def create_product():
    product = save_product(data)
    
    # Invalider
    invalidate_cache_type(CacheType.PRODUCT)
    invalidate_pattern("cache:search:*")
    
    return jsonify(product), 201
```

### Clé Personnalisée

```python
def user_key(request):
    user_id = get_current_user_id()
    return f"cache:user:{user_id}:dashboard"

@app.route('/api/user/dashboard')
@cache_response(CacheType.USER, key_func=user_key)
def user_dashboard():
    return jsonify(get_user_data())
```

---

## 🧪 Tests

```bash
# Tests unitaires
cd webapp
python test_cache.py

# Tests avec Redis réel
TEST_REDIS=true python test_cache.py

# Démonstration interactive
python demo_cache.py
```

---

## 📊 Configuration

### Types de Cache (config.py)

```python
CacheType.DASHBOARD   → TTL: 300s  (5 min)
CacheType.SEARCH      → TTL: 3600s (1h)
CacheType.USER        → TTL: 1800s (30 min)
CacheType.PRODUCT     → TTL: 7200s (2h)
CacheType.ANALYTICS   → TTL: 600s  (10 min)
```

### Modifier le TTL

```python
# Dans config.py
TTL_CONFIG = {
    CacheType.DASHBOARD: 600,  # 10 minutes au lieu de 5
}
```

---

## 🔍 Debug

### Vérifier Redis

```bash
# Connexion Redis
redis-cli ping  # PONG si OK

# Voir les clés
redis-cli KEYS "cache:*"

# Voir une clé spécifique
redis-cli GET "cache:dashboard:abc123"

# TTL d'une clé
redis-cli TTL "cache:dashboard:abc123"
```

### Logs Flask

```bash
# Chercher les logs de cache
grep "CACHE" app.log

# En temps réel
tail -f app.log | grep CACHE
```

---

## 📈 Monitoring

### Check Health

```bash
# Stats du cache
curl http://localhost:8000/api/cache/stats

# Exemple de réponse
{
  "hits": 1247,
  "misses": 153,
  "hit_rate": 89.07,
  "is_available": true
}
```

### Hit Rate

```bash
# Calculer hit rate
curl -s http://localhost:8000/api/cache/stats | \
  python -c "import sys, json; stats=json.load(sys.stdin)['cache_stats']; print(f\"Hit Rate: {stats['hit_rate']}%\")"
```

---

## 🐛 Dépannage

### Cache Always MISS

```bash
# Vérifier Redis
redis-cli ping

# Vérifier connexion dans Flask
curl http://localhost:8000/api/cache/stats | grep is_available
```

### Performance Dégradée

```bash
# Vérifier hit rate
curl http://localhost:8000/api/cache/stats

# Si < 50%, augmenter TTL ou réduire invalidations
```

### Memory Full (Redis)

```bash
# Vérifier mémoire
redis-cli INFO memory

# Configurer eviction policy
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

---

## 📚 Documentation

| Fichier | Description |
|---------|-------------|
| [CACHE_SUMMARY.md](CACHE_SUMMARY.md) | Vue d'ensemble (1 page) |
| [cache/README.md](cache/README.md) | Guide utilisateur (5 pages) |
| [REDIS_CACHE_ARCHITECTURE.md](REDIS_CACHE_ARCHITECTURE.md) | Architecture complète (10+ pages) |
| [CACHE_DIAGRAMS.md](CACHE_DIAGRAMS.md) | Schémas visuels ASCII |
| [cache/examples.py](cache/examples.py) | 10 exemples pratiques |
| [test_cache.py](test_cache.py) | Tests unitaires |
| [demo_cache.py](demo_cache.py) | Démonstration interactive |

---

## 🎯 Use Cases Fréquents

### 1. Dashboard KPIs

```python
@app.route('/api/dashboard')
@cache_response(CacheType.DASHBOARD, ttl=300)
def dashboard():
    return jsonify(compute_expensive_kpis())
```

### 2. Recherche Elasticsearch

```python
@app.route('/api/search')
@cache_response(CacheType.SEARCH, ttl=3600)
def search():
    query = request.args.get('q')
    return jsonify(elasticsearch_search(query))
```

### 3. Profil Utilisateur

```python
def user_cache_key(req):
    return f"cache:user:{get_user_id()}:profile"

@app.route('/api/profile')
@cache_response(CacheType.USER, key_func=user_cache_key)
def profile():
    return jsonify(get_user_profile())
```

---

## ⚠️ Important

### À Faire

✅ Surveiller le hit rate (> 80%)  
✅ Configurer Redis persistence (AOF)  
✅ Définir maxmemory-policy  
✅ Invalider après modifications  
✅ Logger les erreurs cache  

### À Éviter

❌ TTL trop court (< 60s)  
❌ Invalider tout le cache (`cache:*`)  
❌ Cacher données sensibles sans isolation  
❌ Ignorer les erreurs Redis  
❌ Oublier la compression (> 1KB)  

---

## 🔗 Liens Rapides

```bash
# API Endpoints
http://localhost:8000/api/dashboard          # Route cachée
http://localhost:8000/api/cache/stats        # Statistiques
http://localhost:8000/api/cache/invalidate/dashboard  # Invalidation

# Redis CLI
redis-cli                                    # Console Redis
redis-cli MONITOR                            # Voir toutes les commandes
redis-cli --latency                          # Tester latence

# Tests
python test_cache.py                         # Tests unitaires
python demo_cache.py                         # Démo interactive
```

---

## 📞 Aide

### Problème: Cache ne fonctionne pas

1. Vérifier Redis: `redis-cli ping`
2. Vérifier import: `python -c "from cache import cache_response"`
3. Vérifier logs: `grep CACHE app.log`
4. Vérifier stats: `curl http://localhost:8000/api/cache/stats`

### Problème: Hit rate faible

1. Augmenter TTL dans `config.py`
2. Réduire invalidations
3. Vérifier patterns de clés
4. Analyser logs `[CACHE MISS]`

### Problème: Redis out of memory

1. Configurer maxmemory: `redis-cli CONFIG SET maxmemory 2gb`
2. Configurer eviction: `redis-cli CONFIG SET maxmemory-policy allkeys-lru`
3. Monitorer: `redis-cli INFO memory`

---

**🎓 Pro Tips:**

- Utiliser `@cache_response` sur routes coûteuses uniquement
- Invalider intelligemment (pas tout le cache)
- Monitorer le hit rate (objectif: > 80%)
- Tester avec et sans cache
- Documenter stratégie d'invalidation

---

**📊 Performance Attendue:**

- Cache HIT: 2-5ms
- Cache MISS: 50-600ms (selon query)
- Hit Rate: 85-95%
- Speedup: 100-300x

---

_Quick Reference v1.0 - Janvier 2026_
