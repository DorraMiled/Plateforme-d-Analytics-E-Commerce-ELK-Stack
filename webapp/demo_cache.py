"""
Script de démonstration du système de cache Redis
Lance des tests et affiche les performances
"""

import requests
import time
import json
from datetime import datetime


BASE_URL = "http://localhost:8000"


def print_header(text):
    """Affiche un header formaté"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_subheader(text):
    """Affiche un sous-header"""
    print(f"\n→ {text}")


def measure_request(url, label):
    """Mesure le temps d'une requête"""
    print(f"\n  {label}:")
    start = time.time()
    try:
        response = requests.get(url)
        elapsed = (time.time() - start) * 1000  # en ms
        
        cache_header = response.headers.get('X-Cache', 'UNKNOWN')
        cache_key = response.headers.get('X-Cache-Key', 'N/A')
        
        print(f"    Status: {response.status_code}")
        print(f"    X-Cache: {cache_header}")
        print(f"    Temps: {elapsed:.2f}ms")
        
        return elapsed, cache_header
    except Exception as e:
        print(f"    ❌ Erreur: {e}")
        return None, None


def demo_cache_performance():
    """Démontre les performances du cache"""
    print_header("DÉMONSTRATION - PERFORMANCE DU CACHE")
    
    # 1. Vider le cache
    print_subheader("1. Nettoyage du cache")
    try:
        resp = requests.post(f"{BASE_URL}/api/cache/clear-all")
        print(f"  Cache vidé: {resp.json()}")
    except Exception as e:
        print(f"  ⚠️ Impossible de vider le cache: {e}")
    
    # 2. Première requête (MISS)
    print_subheader("2. Première requête (Cache MISS)")
    time1, cache1 = measure_request(f"{BASE_URL}/api/dashboard", "GET /api/dashboard")
    
    # 3. Deuxième requête (HIT)
    print_subheader("3. Deuxième requête (Cache HIT)")
    time.sleep(0.5)  # Petit délai
    time2, cache2 = measure_request(f"{BASE_URL}/api/dashboard", "GET /api/dashboard")
    
    # 4. Troisième requête (HIT)
    print_subheader("4. Troisième requête (Cache HIT)")
    time.sleep(0.5)
    time3, cache3 = measure_request(f"{BASE_URL}/api/dashboard", "GET /api/dashboard")
    
    # 5. Résumé
    print_subheader("5. Résumé des performances")
    if time1 and time2 and time3:
        avg_cached = (time2 + time3) / 2
        speedup = time1 / avg_cached if avg_cached > 0 else 0
        
        print(f"\n  Cache MISS (1ère requête): {time1:.2f}ms")
        print(f"  Cache HIT (moyenne):       {avg_cached:.2f}ms")
        print(f"  Gain de performance:       {speedup:.1f}x plus rapide! 🚀")


def demo_cache_invalidation():
    """Démontre l'invalidation du cache"""
    print_header("DÉMONSTRATION - INVALIDATION DU CACHE")
    
    # 1. Créer du cache
    print_subheader("1. Création du cache")
    measure_request(f"{BASE_URL}/api/dashboard", "GET /api/dashboard")
    
    # 2. Vérifier que c'est caché
    print_subheader("2. Vérification (devrait être HIT)")
    time.sleep(0.5)
    measure_request(f"{BASE_URL}/api/dashboard", "GET /api/dashboard")
    
    # 3. Invalider
    print_subheader("3. Invalidation du cache dashboard")
    try:
        resp = requests.post(f"{BASE_URL}/api/cache/invalidate/dashboard")
        result = resp.json()
        print(f"  Résultat: {result['message']}")
        print(f"  Clés supprimées: {result['deleted_keys']}")
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    # 4. Vérifier que c'est invalidé
    print_subheader("4. Vérification (devrait être MISS)")
    time.sleep(0.5)
    measure_request(f"{BASE_URL}/api/dashboard", "GET /api/dashboard")


def demo_cache_stats():
    """Affiche les statistiques du cache"""
    print_header("DÉMONSTRATION - STATISTIQUES DU CACHE")
    
    try:
        resp = requests.get(f"{BASE_URL}/api/cache/stats")
        stats = resp.json()
        
        print("\n  Statistiques actuelles:")
        print(f"    Hits:            {stats['cache_stats']['hits']}")
        print(f"    Misses:          {stats['cache_stats']['misses']}")
        print(f"    Erreurs:         {stats['cache_stats']['errors']}")
        print(f"    Total:           {stats['cache_stats']['total_requests']}")
        print(f"    Hit Rate:        {stats['cache_stats']['hit_rate']:.2f}%")
        print(f"    Redis Status:    {'✅ Connected' if stats['cache_stats']['is_available'] else '❌ Down'}")
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")


def demo_full_workflow():
    """Démontre le workflow complet"""
    print_header("WORKFLOW COMPLET")
    
    # 1. Stats initiales
    print_subheader("1. Statistiques initiales")
    demo_cache_stats()
    
    # 2. Performance
    demo_cache_performance()
    
    # 3. Stats après test
    print_subheader("3. Statistiques après test de performance")
    demo_cache_stats()
    
    # 4. Invalidation
    demo_cache_invalidation()
    
    # 5. Stats finales
    print_subheader("5. Statistiques finales")
    demo_cache_stats()


def main():
    """Point d'entrée principal"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         SYSTÈME DE CACHE REDIS - DÉMONSTRATION              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Vérifier que le serveur est accessible
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=2)
        print(f"✅ Serveur Flask accessible: {BASE_URL}\n")
    except Exception as e:
        print(f"❌ Serveur Flask non accessible: {BASE_URL}")
        print(f"   Erreur: {e}")
        print("\n⚠️  Assurez-vous que le serveur Flask est lancé (python app.py)")
        return
    
    # Menu
    print("Choisissez une démonstration:")
    print("  1. Performance du cache (MISS vs HIT)")
    print("  2. Invalidation du cache")
    print("  3. Statistiques du cache")
    print("  4. Workflow complet (tout)")
    print("  5. Quitter")
    
    choice = input("\nVotre choix (1-5): ").strip()
    
    if choice == "1":
        demo_cache_performance()
    elif choice == "2":
        demo_cache_invalidation()
    elif choice == "3":
        demo_cache_stats()
    elif choice == "4":
        demo_full_workflow()
    elif choice == "5":
        print("\n👋 Au revoir!")
        return
    else:
        print("\n❌ Choix invalide")
        return
    
    print("\n" + "="*70)
    print("  Démonstration terminée!")
    print("="*70)
    print("\n📚 Consultez REDIS_CACHE_ARCHITECTURE.md pour plus de détails")
    print("📊 Consultez CACHE_DIAGRAMS.md pour les schémas visuels")
    print("💡 Consultez cache/examples.py pour 10 exemples pratiques\n")


if __name__ == "__main__":
    main()
