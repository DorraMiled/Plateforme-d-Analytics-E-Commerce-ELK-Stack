"""
Script de test simple pour vérifier que l'authentification fonctionne.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test 1: Health check
print("\n=== Test 1: Health check ===")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Register
print("\n=== Test 2: Register ===")
try:
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123",
        "role": "USER"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        token = response.json()['token']
        print(f"\nToken: {token[:50]}...")
        
        # Test 3: Get me
        print("\n=== Test 3: Get current user ===")
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n=== Tests completed ===\n")
