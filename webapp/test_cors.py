"""
Script de test CORS pour vérifier que le backend répond correctement
"""
import requests

def test_options():
    """Test de la requête OPTIONS (preflight)"""
    print("=== Test OPTIONS (CORS preflight) ===")
    headers = {
        'Origin': 'http://localhost:4200',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    try:
        response = requests.options('http://localhost:8000/api/auth/register', headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ OPTIONS request successful!")
            cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
            print(f"CORS Headers: {cors_headers}")
        else:
            print(f"❌ OPTIONS request failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_post():
    """Test de la requête POST (register)"""
    print("\n=== Test POST (register) ===")
    headers = {
        'Origin': 'http://localhost:4200',
        'Content-Type': 'application/json'
    }
    data = {
        'username': 'testuser',
        'email': 'test@test.com',
        'password': 'Test1234',
        'role': 'USER'
    }
    
    try:
        response = requests.post('http://localhost:8000/api/auth/register', json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
        print(f"CORS Headers: {cors_headers}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_options()
    test_post()
