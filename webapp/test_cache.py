"""
Tests du système de cache Redis
Valide le décorateur, la compression, le TTL et l'invalidation
"""

import unittest
import json
import time
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from cache.config import CacheType, CacheConfig
from cache.redis_cache import CacheManager, cache_response, invalidate_cache_type


class TestCacheConfig(unittest.TestCase):
    """Tests de la configuration du cache"""
    
    def test_ttl_configuration(self):
        """Vérifie que les TTL sont configurés correctement"""
        self.assertEqual(CacheConfig.get_ttl(CacheType.DASHBOARD), 300)
        self.assertEqual(CacheConfig.get_ttl(CacheType.SEARCH), 3600)
        self.assertEqual(CacheConfig.get_ttl(CacheType.USER), 1800)
        self.assertEqual(CacheConfig.get_ttl(CacheType.PRODUCT), 7200)
        self.assertEqual(CacheConfig.get_ttl(CacheType.ANALYTICS), 600)
    
    def test_key_prefix(self):
        """Vérifie les préfixes de clés"""
        self.assertEqual(
            CacheConfig.get_key_prefix(CacheType.DASHBOARD),
            "cache:dashboard:"
        )
        self.assertEqual(
            CacheConfig.get_key_prefix(CacheType.SEARCH),
            "cache:search:"
        )
    
    def test_build_cache_key(self):
        """Vérifie la construction des clés de cache"""
        key = CacheConfig.build_cache_key(CacheType.DASHBOARD, "test123")
        self.assertEqual(key, "cache:dashboard:test123")


class TestCacheManager(unittest.TestCase):
    """Tests du gestionnaire de cache"""
    
    def setUp(self):
        """Initialisation avant chaque test"""
        self.mock_redis = MagicMock()
        self.cache_manager = CacheManager(self.mock_redis)
    
    def test_set_and_get(self):
        """Test du stockage et récupération"""
        # Mock Redis responses
        self.mock_redis.ping.return_value = True
        self.mock_redis.get.return_value = json.dumps({"test": "data"}).encode()
        self.mock_redis.setex.return_value = True
        
        # Set
        result = self.cache_manager.set("test_key", {"test": "data"}, 300)
        self.assertTrue(result)
        self.mock_redis.setex.assert_called_once()
        
        # Get
        data = self.cache_manager.get("test_key")
        self.assertEqual(data, {"test": "data"})
    
    def test_cache_miss(self):
        """Test du cache miss"""
        self.mock_redis.ping.return_value = True
        self.mock_redis.get.return_value = None
        
        data = self.cache_manager.get("nonexistent_key")
        self.assertIsNone(data)
        self.assertEqual(self.cache_manager.stats["misses"], 1)
    
    def test_cache_hit(self):
        """Test du cache hit"""
        self.mock_redis.ping.return_value = True
        self.mock_redis.get.return_value = json.dumps({"cached": True}).encode()
        
        data = self.cache_manager.get("cached_key")
        self.assertIsNotNone(data)
        self.assertEqual(self.cache_manager.stats["hits"], 1)
    
    def test_delete(self):
        """Test de suppression"""
        self.mock_redis.ping.return_value = True
        self.mock_redis.delete.return_value = 1
        
        result = self.cache_manager.delete("test_key")
        self.assertTrue(result)
        self.mock_redis.delete.assert_called_once_with("test_key")
    
    def test_delete_pattern(self):
        """Test de suppression par pattern"""
        self.mock_redis.ping.return_value = True
        self.mock_redis.keys.return_value = [
            "cache:dashboard:key1",
            "cache:dashboard:key2"
        ]
        self.mock_redis.delete.return_value = 2
        
        deleted = self.cache_manager.delete_pattern("cache:dashboard:*")
        self.assertEqual(deleted, 2)
    
    def test_redis_unavailable(self):
        """Test du comportement quand Redis est indisponible"""
        self.cache_manager.redis_client = None
        
        # Les opérations doivent échouer gracieusement
        self.assertIsNone(self.cache_manager.get("key"))
        self.assertFalse(self.cache_manager.set("key", "value"))
        self.assertFalse(self.cache_manager.delete("key"))
    
    def test_compression(self):
        """Test de la compression des données"""
        large_data = {"data": "x" * 2000}  # > 1KB
        
        self.mock_redis.ping.return_value = True
        self.mock_redis.setex.return_value = True
        
        # La compression devrait être appliquée
        result = self.cache_manager.set("large_key", large_data, 300)
        self.assertTrue(result)
        
        # Vérifier que setex a été appelé avec des données compressées
        call_args = self.mock_redis.setex.call_args
        stored_data = call_args[0][2]
        
        # Les données compressées devraient être plus petites que l'original
        original_size = len(json.dumps(large_data).encode())
        self.assertLess(len(stored_data), original_size)
    
    def test_stats(self):
        """Test des statistiques"""
        self.mock_redis.ping.return_value = True
        self.mock_redis.get.side_effect = [
            json.dumps({"hit": 1}).encode(),
            None,
            json.dumps({"hit": 2}).encode(),
        ]
        
        # 2 hits, 1 miss
        self.cache_manager.get("key1")
        self.cache_manager.get("key2")
        self.cache_manager.get("key3")
        
        stats = self.cache_manager.get_stats()
        self.assertEqual(stats["hits"], 2)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["total_requests"], 3)
        self.assertAlmostEqual(stats["hit_rate"], 66.67, places=1)


class TestCacheDecorator(unittest.TestCase):
    """Tests du décorateur @cache_response"""
    
    def setUp(self):
        """Initialisation"""
        self.mock_redis = MagicMock()
        self.mock_redis.ping.return_value = True
        
        # Créer un cache manager mock
        self.cache_manager = CacheManager(self.mock_redis)
    
    @patch('cache.redis_cache.cache_manager')
    def test_decorator_cache_miss(self, mock_cache_mgr):
        """Test du décorateur avec cache miss"""
        # Setup
        mock_cache_mgr.get.return_value = None
        mock_cache_mgr.set.return_value = True
        
        # Fonction à décorer
        call_count = [0]
        
        @cache_response(CacheType.DASHBOARD, ttl=300)
        def test_function():
            call_count[0] += 1
            return {"result": "computed"}
        
        # Mock Flask request
        with patch('cache.redis_cache.request') as mock_request:
            mock_request.url = "http://test.com/api/test"
            mock_request.args.items.return_value = []
            
            with patch('cache.redis_cache.make_response') as mock_make_response:
                with patch('cache.redis_cache.jsonify') as mock_jsonify:
                    mock_jsonify.return_value = Mock()
                    mock_make_response.return_value = Mock(
                        get_json=lambda: {"result": "computed"},
                        headers={}
                    )
                    
                    # Première appel - cache miss
                    result = test_function()
                    
                    # La fonction doit être appelée
                    self.assertEqual(call_count[0], 1)
    
    @patch('cache.redis_cache.cache_manager')
    def test_decorator_cache_hit(self, mock_cache_mgr):
        """Test du décorateur avec cache hit"""
        # Setup - retourne des données cachées
        cached_data = {"result": "from_cache"}
        mock_cache_mgr.get.return_value = cached_data
        
        # Fonction à décorer
        call_count = [0]
        
        @cache_response(CacheType.DASHBOARD, ttl=300)
        def test_function():
            call_count[0] += 1
            return {"result": "computed"}
        
        # Mock Flask request
        with patch('cache.redis_cache.request') as mock_request:
            mock_request.url = "http://test.com/api/test"
            mock_request.args.items.return_value = []
            
            with patch('cache.redis_cache.make_response') as mock_make_response:
                with patch('cache.redis_cache.jsonify') as mock_jsonify:
                    mock_jsonify.return_value = cached_data
                    mock_response = Mock()
                    mock_response.headers = {}
                    mock_make_response.return_value = mock_response
                    
                    # Appel avec cache hit
                    result = test_function()
                    
                    # La fonction ne doit PAS être appelée
                    self.assertEqual(call_count[0], 0)
                    
                    # Le header X-Cache doit être HIT
                    self.assertEqual(mock_response.headers.get('X-Cache'), 'HIT')


class TestIntegration(unittest.TestCase):
    """Tests d'intégration (nécessitent Redis réel)"""
    
    @unittest.skipUnless(
        os.getenv('TEST_REDIS', 'false').lower() == 'true',
        "Redis integration tests disabled. Set TEST_REDIS=true to enable."
    )
    def test_real_redis_cache(self):
        """Test avec un vrai Redis (si disponible)"""
        import redis
        try:
            redis_client = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=True
            )
            redis_client.ping()
            
            # Créer un cache manager avec le vrai client
            cache_mgr = CacheManager(redis_client)
            
            # Test set/get
            test_data = {"integration": "test", "value": 123}
            cache_mgr.set("integration_test_key", test_data, 60)
            
            retrieved = cache_mgr.get("integration_test_key")
            self.assertEqual(retrieved, test_data)
            
            # Test delete
            cache_mgr.delete("integration_test_key")
            self.assertIsNone(cache_mgr.get("integration_test_key"))
            
            print("✅ Integration test with real Redis passed!")
            
        except redis.ConnectionError:
            self.skipTest("Redis not available for integration test")


class TestPerformance(unittest.TestCase):
    """Tests de performance"""
    
    def test_compression_performance(self):
        """Mesure le temps de compression"""
        large_data = {"data": [{"item": i} for i in range(1000)]}
        json_str = json.dumps(large_data)
        
        import zlib
        
        start = time.time()
        compressed = zlib.compress(json_str.encode(), 6)
        compression_time = time.time() - start
        
        start = time.time()
        decompressed = zlib.decompress(compressed).decode()
        decompression_time = time.time() - start
        
        compression_ratio = len(compressed) / len(json_str.encode())
        
        print(f"\n📊 Compression Performance:")
        print(f"   Original size: {len(json_str.encode())} bytes")
        print(f"   Compressed size: {len(compressed)} bytes")
        print(f"   Ratio: {compression_ratio:.2%}")
        print(f"   Compression time: {compression_time*1000:.2f}ms")
        print(f"   Decompression time: {decompression_time*1000:.2f}ms")
        
        # Assertions
        self.assertLess(compression_ratio, 0.5, "Compression should reduce size by >50%")
        self.assertLess(compression_time, 0.1, "Compression should be fast (<100ms)")


def run_tests():
    """Lance tous les tests"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║           REDIS CACHE SYSTEM - TEST SUITE                   ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Créer une suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter tous les tests
    suite.addTests(loader.loadTestsFromTestCase(TestCacheConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheManager))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheDecorator))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Afficher le résumé
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
