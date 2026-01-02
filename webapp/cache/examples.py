"""
Exemple d'utilisation du système de cache Redis
Démonstrations pratiques pour différents cas d'usage
"""

from flask import Flask, jsonify, request
from cache.redis_cache import cache_response, invalidate_cache_type, invalidate_pattern
from cache.config import CacheType

app = Flask(__name__)


# ============================================
# EXEMPLE 1: Cache Simple avec TTL par Défaut
# ============================================

@app.route('/api/products', methods=['GET'])
@cache_response(CacheType.PRODUCT)  # Utilise le TTL configuré (7200s)
def get_products():
    """Liste des produits - cache 2 heures"""
    # Requête coûteuse à la base de données
    products = fetch_products_from_db()
    return jsonify(products)


# ============================================
# EXEMPLE 2: Cache avec TTL Custom
# ============================================

@app.route('/api/trending', methods=['GET'])
@cache_response(CacheType.ANALYTICS, ttl=180)  # Cache 3 minutes seulement
def get_trending():
    """Produits tendances - cache court pour fraîcheur"""
    trending = calculate_trending_products()
    return jsonify(trending)


# ============================================
# EXEMPLE 3: Cache avec Clé Personnalisée
# ============================================

def search_cache_key(request_obj):
    """Génère une clé de cache basée sur la query de recherche"""
    query = request_obj.args.get('q', '')
    filters = request_obj.args.get('filters', '')
    page = request_obj.args.get('page', '1')
    return f"cache:search:q={query}:f={filters}:p={page}"

@app.route('/api/search', methods=['GET'])
@cache_response(CacheType.SEARCH, ttl=3600, key_func=search_cache_key)
def search_products():
    """
    Recherche de produits avec cache personnalisé
    Chaque combinaison (query + filters + page) = clé unique
    """
    query = request.args.get('q', '')
    filters = request.args.get('filters', '')
    page = int(request.args.get('page', 1))
    
    results = elasticsearch_search(query, filters, page)
    return jsonify(results)


# ============================================
# EXEMPLE 4: Cache par Utilisateur
# ============================================

def user_cache_key(request_obj):
    """Clé de cache isolée par utilisateur"""
    user_id = get_current_user_id()  # Depuis JWT token
    return f"cache:user:{user_id}:recommendations"

@app.route('/api/recommendations', methods=['GET'])
@cache_response(CacheType.USER, ttl=1800, key_func=user_cache_key)
def get_recommendations():
    """Recommandations personnalisées - cache isolé par user"""
    user_id = get_current_user_id()
    recommendations = generate_recommendations(user_id)
    return jsonify(recommendations)


# ============================================
# EXEMPLE 5: Invalidation Automatique
# ============================================

@app.route('/api/products', methods=['POST'])
def create_product():
    """Création d'un produit - invalide automatiquement le cache"""
    data = request.get_json()
    
    # Créer le produit
    new_product = save_product(data)
    
    # Invalider les caches impactés
    invalidate_cache_type(CacheType.PRODUCT)  # Liste des produits
    invalidate_cache_type(CacheType.SEARCH)   # Résultats de recherche
    invalidate_pattern("cache:analytics:*")   # Toutes les statistiques
    
    return jsonify({
        "status": "created",
        "product": new_product,
        "cache_invalidated": ["products", "search", "analytics"]
    }), 201


@app.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Mise à jour d'un produit - invalidation ciblée"""
    data = request.get_json()
    
    # Mettre à jour le produit
    updated_product = update_product_in_db(product_id, data)
    
    # Invalider seulement les caches liés
    invalidate_pattern(f"cache:product:*{product_id}*")  # Ce produit spécifique
    invalidate_pattern("cache:search:*")                  # Toutes les recherches
    
    return jsonify({
        "status": "updated",
        "product": updated_product
    })


# ============================================
# EXEMPLE 6: Cache Conditionnel
# ============================================

@app.route('/api/dashboard/<view>', methods=['GET'])
def get_dashboard_view(view):
    """
    Dashboard avec cache conditionnel selon le type de vue
    Certaines vues sont cachées, d'autres non
    """
    if view in ['overview', 'analytics']:
        # Vues avec données agrégées - cache activé
        @cache_response(CacheType.DASHBOARD, ttl=300)
        def cached_view():
            return jsonify(fetch_dashboard_data(view))
        return cached_view()
    else:
        # Vues temps réel - pas de cache
        return jsonify(fetch_realtime_data(view))


# ============================================
# EXEMPLE 7: Monitoring et Debug
# ============================================

@app.route('/api/cache/info/<cache_type>', methods=['GET'])
def get_cache_info(cache_type):
    """Informations détaillées sur un type de cache"""
    from cache.config import CacheConfig
    
    cache_type_map = {
        'dashboard': CacheType.DASHBOARD,
        'search': CacheType.SEARCH,
        'user': CacheType.USER,
        'product': CacheType.PRODUCT,
        'analytics': CacheType.ANALYTICS
    }
    
    if cache_type not in cache_type_map:
        return jsonify({"error": "Invalid cache type"}), 400
    
    ct = cache_type_map[cache_type]
    
    return jsonify({
        "cache_type": cache_type,
        "ttl": CacheConfig.get_ttl(ct),
        "key_prefix": CacheConfig.get_key_prefix(ct),
        "example_key": CacheConfig.build_cache_key(ct, "example123")
    })


# ============================================
# EXEMPLE 8: Warm Cache (Préchauffage)
# ============================================

@app.route('/api/cache/warm', methods=['POST'])
def warm_cache():
    """
    Préchauffe le cache avec les requêtes les plus fréquentes
    À appeler après un déploiement ou un vidage de cache
    """
    import requests
    
    warm_urls = [
        'http://localhost:8000/api/dashboard',
        'http://localhost:8000/api/products',
        'http://localhost:8000/api/trending',
        'http://localhost:8000/api/search?q=popular',
    ]
    
    results = []
    for url in warm_urls:
        try:
            resp = requests.get(url)
            results.append({
                "url": url,
                "status": resp.status_code,
                "cached": resp.headers.get('X-Cache', 'UNKNOWN')
            })
        except Exception as e:
            results.append({
                "url": url,
                "status": "error",
                "error": str(e)
            })
    
    return jsonify({
        "status": "cache_warmed",
        "results": results
    })


# ============================================
# EXEMPLE 9: Cache avec Fallback
# ============================================

@app.route('/api/external-api', methods=['GET'])
@cache_response(CacheType.ANALYTICS, ttl=600)
def fetch_external_api():
    """
    Appel à API externe avec cache
    Si l'API externe est lente/down, le cache sert de fallback
    """
    try:
        # Appel API externe (peut être lent)
        data = call_external_api()
        return jsonify(data)
    except Exception as e:
        # En cas d'erreur, le cache (si présent) sera retourné
        # grâce au décorateur @cache_response
        return jsonify({
            "error": "External API unavailable",
            "message": str(e)
        }), 503


# ============================================
# EXEMPLE 10: Multi-niveau Cache
# ============================================

@app.route('/api/complex-data/<data_id>', methods=['GET'])
def get_complex_data(data_id):
    """
    Stratégie multi-niveau: Cache Redis + Cache mémoire local
    """
    from functools import lru_cache
    
    # Cache mémoire (ultra-rapide, limité)
    @lru_cache(maxsize=100)
    def get_from_memory(data_id):
        # Cache Redis (rapide, partagé entre workers)
        @cache_response(CacheType.ANALYTICS, ttl=300)
        def get_from_redis():
            # Base de données (lent)
            return fetch_from_database(data_id)
        return get_from_redis()
    
    return jsonify(get_from_memory(data_id))


# ============================================
# Fonctions Helper (à implémenter)
# ============================================

def fetch_products_from_db():
    """Simuler récupération DB"""
    return [{"id": 1, "name": "Product A"}, {"id": 2, "name": "Product B"}]

def calculate_trending_products():
    """Calculer tendances"""
    return [{"id": 1, "trend_score": 95}]

def elasticsearch_search(query, filters, page):
    """Recherche Elasticsearch"""
    return {"results": [], "total": 0, "page": page}

def get_current_user_id():
    """Extraire user_id du JWT"""
    return "user123"

def generate_recommendations(user_id):
    """Générer recommandations"""
    return [{"product_id": 1, "score": 0.95}]

def save_product(data):
    """Sauvegarder produit"""
    return {"id": 123, **data}

def update_product_in_db(product_id, data):
    """Mettre à jour produit"""
    return {"id": product_id, **data}

def fetch_dashboard_data(view):
    """Récupérer données dashboard"""
    return {"view": view, "data": {}}

def fetch_realtime_data(view):
    """Récupérer données temps réel"""
    return {"view": view, "realtime": True}

def call_external_api():
    """Appeler API externe"""
    import requests
    return requests.get('https://api.example.com/data').json()

def fetch_from_database(data_id):
    """Récupérer depuis DB"""
    return {"id": data_id, "data": "complex"}


if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         EXEMPLES D'UTILISATION DU CACHE REDIS                ║
    ╚══════════════════════════════════════════════════════════════╝
    
    10 patterns d'utilisation du cache:
    
    1. ✅ Cache simple avec TTL par défaut
    2. ✅ Cache avec TTL personnalisé
    3. ✅ Cache avec clé personnalisée
    4. ✅ Cache isolé par utilisateur
    5. ✅ Invalidation automatique
    6. ✅ Cache conditionnel
    7. ✅ Monitoring et debug
    8. ✅ Warm cache (préchauffage)
    9. ✅ Cache avec fallback
    10. ✅ Multi-niveau (Memory + Redis)
    
    Consultez ce fichier pour des exemples concrets!
    """)
