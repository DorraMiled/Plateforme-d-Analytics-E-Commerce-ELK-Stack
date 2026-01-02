"""
Script de test pour l'authentification JWT.
Teste tous les endpoints d'authentification et les différents rôles.
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
AUTH_URL = f"{BASE_URL}/api/auth"

# Couleurs pour le terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_test(name, status, message=""):
    """Affiche le résultat d'un test"""
    color = Colors.GREEN if status else Colors.RED
    status_text = "✓ PASS" if status else "✗ FAIL"
    print(f"{color}{status_text}{Colors.END} - {name}")
    if message:
        print(f"      {message}")


def print_section(title):
    """Affiche un titre de section"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}\n")


# Variables pour stocker les tokens
tokens = {}
users = {}


def test_register(username, email, password, role="USER"):
    """Test d'inscription"""
    print(f"\n{Colors.YELLOW}Testing registration: {username} ({role}){Colors.END}")
    
    try:
        response = requests.post(
            f"{AUTH_URL}/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "role": role
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            tokens[username] = data['token']
            users[username] = data['user']
            print_test(f"Register {username}", True, f"Token: {data['token'][:20]}...")
            return True
        else:
            print_test(f"Register {username}", False, response.json().get('message', 'Unknown error'))
            return False
            
    except Exception as e:
        print_test(f"Register {username}", False, str(e))
        return False


def test_login(username, password):
    """Test de connexion"""
    print(f"\n{Colors.YELLOW}Testing login: {username}{Colors.END}")
    
    try:
        response = requests.post(
            f"{AUTH_URL}/login",
            json={
                "username": username,
                "password": password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            tokens[username] = data['token']
            print_test(f"Login {username}", True, f"Role: {data['user']['role']}")
            return True
        else:
            print_test(f"Login {username}", False, response.json().get('message', 'Unknown error'))
            return False
            
    except Exception as e:
        print_test(f"Login {username}", False, str(e))
        return False


def test_get_me(username):
    """Test de récupération du profil"""
    print(f"\n{Colors.YELLOW}Testing /me endpoint: {username}{Colors.END}")
    
    if username not in tokens:
        print_test(f"Get me ({username})", False, "No token available")
        return False
    
    try:
        response = requests.get(
            f"{AUTH_URL}/me",
            headers={"Authorization": f"Bearer {tokens[username]}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            user = data['user']
            print_test(
                f"Get me ({username})",
                True,
                f"User: {user['username']}, Role: {user['role']}"
            )
            return True
        else:
            print_test(f"Get me ({username})", False, response.json().get('message', 'Unknown error'))
            return False
            
    except Exception as e:
        print_test(f"Get me ({username})", False, str(e))
        return False


def test_list_users(username, expected_status=200):
    """Test de listage des utilisateurs"""
    print(f"\n{Colors.YELLOW}Testing list users: {username}{Colors.END}")
    
    if username not in tokens:
        print_test(f"List users ({username})", False, "No token available")
        return False
    
    try:
        response = requests.get(
            f"{AUTH_URL}/users",
            headers={"Authorization": f"Bearer {tokens[username]}"}
        )
        
        success = response.status_code == expected_status
        
        if success and expected_status == 200:
            data = response.json()
            print_test(
                f"List users ({username})",
                True,
                f"Found {data['total']} users"
            )
        elif success and expected_status == 403:
            print_test(
                f"List users ({username})",
                True,
                "Correctly denied (USER role)"
            )
        else:
            print_test(
                f"List users ({username})",
                False,
                f"Expected {expected_status}, got {response.status_code}"
            )
        
        return success
            
    except Exception as e:
        print_test(f"List users ({username})", False, str(e))
        return False


def test_role_endpoint(endpoint, username, expected_status=200):
    """Test d'un endpoint avec rôle requis"""
    print(f"\n{Colors.YELLOW}Testing {endpoint}: {username}{Colors.END}")
    
    if username not in tokens:
        print_test(f"{endpoint} ({username})", False, "No token available")
        return False
    
    try:
        response = requests.get(
            f"{AUTH_URL}/{endpoint}",
            headers={"Authorization": f"Bearer {tokens[username]}"}
        )
        
        success = response.status_code == expected_status
        
        if success:
            message = response.json().get('message', '')
            if expected_status == 200:
                print_test(f"{endpoint} ({username})", True, message)
            else:
                print_test(f"{endpoint} ({username})", True, f"Correctly denied ({expected_status})")
        else:
            print_test(
                f"{endpoint} ({username})",
                False,
                f"Expected {expected_status}, got {response.status_code}"
            )
        
        return success
            
    except Exception as e:
        print_test(f"{endpoint} ({username})", False, str(e))
        return False


def test_invalid_token():
    """Test avec un token invalide"""
    print(f"\n{Colors.YELLOW}Testing invalid token{Colors.END}")
    
    try:
        response = requests.get(
            f"{AUTH_URL}/me",
            headers={"Authorization": "Bearer invalid_token_xyz"}
        )
        
        success = response.status_code == 401
        print_test(
            "Invalid token",
            success,
            "Correctly rejected" if success else f"Got status {response.status_code}"
        )
        return success
            
    except Exception as e:
        print_test("Invalid token", False, str(e))
        return False


def test_no_token():
    """Test sans token"""
    print(f"\n{Colors.YELLOW}Testing no token{Colors.END}")
    
    try:
        response = requests.get(f"{AUTH_URL}/me")
        
        success = response.status_code == 401
        print_test(
            "No token",
            success,
            "Correctly rejected" if success else f"Got status {response.status_code}"
        )
        return success
            
    except Exception as e:
        print_test("No token", False, str(e))
        return False


def run_all_tests():
    """Exécute tous les tests"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  JWT AUTHENTICATION TEST SUITE")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}{Colors.END}")
    
    results = []
    
    # 1. Test d'inscription
    print_section("1. REGISTRATION TESTS")
    results.append(test_register("admin_user", "admin@example.com", "AdminPass123", "ADMIN"))
    results.append(test_register("analyst_user", "analyst@example.com", "AnalystPass123", "ANALYST"))
    results.append(test_register("regular_user", "user@example.com", "UserPass123", "USER"))
    
    # 2. Test de connexion
    print_section("2. LOGIN TESTS")
    results.append(test_login("admin_user", "AdminPass123"))
    results.append(test_login("analyst_user", "AnalystPass123"))
    results.append(test_login("regular_user", "UserPass123"))
    
    # 3. Test /me
    print_section("3. GET CURRENT USER TESTS")
    results.append(test_get_me("admin_user"))
    results.append(test_get_me("analyst_user"))
    results.append(test_get_me("regular_user"))
    
    # 4. Test de tokens invalides
    print_section("4. INVALID TOKEN TESTS")
    results.append(test_invalid_token())
    results.append(test_no_token())
    
    # 5. Test des rôles
    print_section("5. ROLE-BASED ACCESS CONTROL TESTS")
    
    # Admin endpoint (ADMIN only)
    results.append(test_role_endpoint("test/admin", "admin_user", 200))
    results.append(test_role_endpoint("test/admin", "analyst_user", 403))
    results.append(test_role_endpoint("test/admin", "regular_user", 403))
    
    # Analyst endpoint (ADMIN + ANALYST)
    results.append(test_role_endpoint("test/analyst", "admin_user", 200))
    results.append(test_role_endpoint("test/analyst", "analyst_user", 200))
    results.append(test_role_endpoint("test/analyst", "regular_user", 403))
    
    # User endpoint (tous)
    results.append(test_role_endpoint("test/user", "admin_user", 200))
    results.append(test_role_endpoint("test/user", "analyst_user", 200))
    results.append(test_role_endpoint("test/user", "regular_user", 200))
    
    # 6. Test list users
    print_section("6. LIST USERS TESTS")
    results.append(test_list_users("admin_user", 200))
    results.append(test_list_users("analyst_user", 200))
    results.append(test_list_users("regular_user", 403))
    
    # Résumé
    print_section("TEST SUMMARY")
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100 if total > 0 else 0
    
    print(f"Total tests: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}Failed: {total - passed}{Colors.END}")
    print(f"Success rate: {percentage:.1f}%\n")
    
    if passed == total:
        print(f"{Colors.GREEN}✓ ALL TESTS PASSED!{Colors.END}\n")
    else:
        print(f"{Colors.RED}✗ SOME TESTS FAILED{Colors.END}\n")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.END}\n")
        exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Fatal error: {e}{Colors.END}\n")
        exit(1)
