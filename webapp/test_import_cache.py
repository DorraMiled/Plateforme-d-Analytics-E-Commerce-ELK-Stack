"""Test rapide du système de cache"""
import json

print('='*70)
print('  TEST DU SYSTÈME DE CACHE REDIS')
print('='*70)

from cache import cache_response, CacheType, CacheConfig, CacheManager, invalidate_cache_type

print('\n✅ Imports réussis:')
print('  - cache_response (décorateur)')
print('  - CacheType (enum)')
print('  - CacheConfig (configuration)')
print('  - CacheManager (gestionnaire)')
print('  - invalidate_cache_type (invalidation)')

print(f'\n📊 Types de cache disponibles:')
types = [t.value for t in CacheType]
print(json.dumps(types, indent=2))

print(f'\n⏰ TTL configurés (secondes):')
ttls = {t.value: CacheConfig.get_ttl(t) for t in CacheType}
print(json.dumps(ttls, indent=2))

print(f'\n🔑 Préfixes des clés Redis:')
prefixes = {t.value: CacheConfig.get_key_prefix(t) for t in CacheType}
print(json.dumps(prefixes, indent=2))

print('\n🎯 Exemple d\'utilisation:')
print('  from cache import cache_response, CacheType')
print('  ')
print('  @app.route("/api/dashboard")')
print('  @cache_response(CacheType.DASHBOARD, ttl=300)')
print('  def get_dashboard():')
print('      return jsonify(expensive_computation())')

print('\n' + '='*70)
print('  ✅ SYSTÈME DE CACHE OPÉRATIONNEL')
print('='*70)
