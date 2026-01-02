"""
Blueprint des routes d'authentification.
Endpoints: /api/auth/register, /api/auth/login, /api/auth/me
"""
from flask import Blueprint, request, jsonify, current_app, g
from auth.services import AuthService, UserService
from auth.decorators import token_required, role_required, admin_required
from auth.models import UserRole
import re

# Créer le blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# --- Helpers de validation ---

def validate_email(email):
    """Valide le format d'un email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Valide la force d'un mot de passe.
    Minimum 8 caractères, 1 majuscule, 1 minuscule, 1 chiffre.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    
    return True, None


# --- Routes d'authentification ---

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    """
    Endpoint d'inscription d'un nouvel utilisateur.
    
    Body (JSON):
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "SecurePass123",
            "role": "USER"  // Optionnel, par défaut USER
        }
    
    Returns:
        201: Utilisateur créé avec succès
        400: Données invalides
        409: Utilisateur déjà existant
    """
    try:
        data = request.get_json()
        
        # Validation des champs requis
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        role = data.get('role', UserRole.USER).upper()
        
        if not username or not email or not password:
            return jsonify({
                'error': 'Missing required fields',
                'message': 'username, email and password are required'
            }), 400
        
        # Validation du format
        if len(username) < 3:
            return jsonify({
                'error': 'Invalid username',
                'message': 'Username must be at least 3 characters long'
            }), 400
        
        if not validate_email(email):
            return jsonify({
                'error': 'Invalid email',
                'message': 'Please provide a valid email address'
            }), 400
        
        # Validation du mot de passe
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({
                'error': 'Weak password',
                'message': error_msg
            }), 400
        
        # Validation du rôle
        if not UserRole.is_valid_role(role):
            return jsonify({
                'error': 'Invalid role',
                'message': f'Role must be one of: {", ".join(UserRole.all_roles())}'
            }), 400
        
        # Créer l'utilisateur
        user_service = UserService(current_app.config['DB'])
        user_id, error = user_service.create_user(username, email, password, role)
        
        if error:
            status_code = 409 if 'already exists' in error else 500
            return jsonify({
                'error': 'Registration failed',
                'message': error
            }), status_code
        
        # Générer un token pour l'utilisateur nouvellement créé
        token = AuthService.generate_token(user_id, username, role)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': str(user_id),
                'username': username,
                'email': email,
                'role': role
            },
            'token': token
        }), 201
        
    except Exception as e:
        print(f"[ERROR] Register endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """
    Endpoint de connexion d'un utilisateur.
    
    Body (JSON):
        {
            "username": "john_doe",
            "password": "SecurePass123"
        }
    
    Returns:
        200: Connexion réussie avec token JWT
        400: Données manquantes
        401: Identifiants invalides
    """
    try:
        data = request.get_json()
        
        # Validation des champs requis
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({
                'error': 'Missing credentials',
                'message': 'username and password are required'
            }), 400
        
        # Authentifier l'utilisateur
        user_service = UserService(current_app.config['DB'])
        user, error = user_service.authenticate_user(username, password)
        
        if error:
            return jsonify({
                'error': 'Authentication failed',
                'message': error
            }), 401
        
        # Générer le token JWT
        token = AuthService.generate_token(
            user['_id'],
            user['username'],
            user['role']
        )
        
        if not token:
            return jsonify({
                'error': 'Token generation failed',
                'message': 'Unable to generate authentication token'
            }), 500
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'last_login': user['last_login'].isoformat() if user.get('last_login') else None
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Login endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """
    Endpoint pour récupérer les informations de l'utilisateur courant.
    Nécessite un token JWT valide.
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: Informations de l'utilisateur
        401: Token manquant ou invalide
    """
    try:
        user = g.current_user
        
        return jsonify({
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'is_active': user.get('is_active', True),
                'created_at': user['created_at'].isoformat() if user.get('created_at') else None,
                'last_login': user['last_login'].isoformat() if user.get('last_login') else None
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get current user endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


# --- Routes supplémentaires pour la gestion des utilisateurs ---

@auth_bp.route('/users', methods=['GET'])
@token_required
@role_required('ADMIN', 'ANALYST')
def list_users():
    """
    Liste tous les utilisateurs (ADMIN et ANALYST uniquement).
    
    Query params:
        role: Filtrer par rôle (optionnel)
        active: Filtrer par statut actif (true/false)
        limit: Nombre max de résultats (défaut: 50)
        skip: Nombre de résultats à sauter (pagination)
    
    Returns:
        200: Liste des utilisateurs
        403: Permissions insuffisantes
    """
    try:
        # Paramètres de requête
        role_filter = request.args.get('role', '').upper()
        active_filter = request.args.get('active')
        limit = min(int(request.args.get('limit', 50)), 100)
        skip = int(request.args.get('skip', 0))
        
        # Construire le filtre MongoDB
        query = {}
        
        if role_filter and UserRole.is_valid_role(role_filter):
            query['role'] = role_filter
        
        if active_filter is not None:
            query['is_active'] = active_filter.lower() == 'true'
        
        # Récupérer les utilisateurs
        db = current_app.config['DB']
        users_cursor = db.users.find(query).skip(skip).limit(limit)
        total_count = db.users.count_documents(query)
        
        users_list = []
        for user in users_cursor:
            users_list.append({
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'is_active': user.get('is_active', True),
                'created_at': user['created_at'].isoformat() if user.get('created_at') else None,
                'last_login': user['last_login'].isoformat() if user.get('last_login') else None
            })
        
        return jsonify({
            'users': users_list,
            'total': total_count,
            'limit': limit,
            'skip': skip
        }), 200
        
    except Exception as e:
        print(f"[ERROR] List users endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@auth_bp.route('/users/<user_id>/role', methods=['PUT', 'OPTIONS'])
@token_required
@admin_required
def update_user_role(user_id):
    """
    Met à jour le rôle d'un utilisateur (ADMIN uniquement).
    
    Body (JSON):
        {
            "role": "ANALYST"
        }
    
    Returns:
        200: Rôle mis à jour
        400: Rôle invalide
        403: Permissions insuffisantes
        404: Utilisateur non trouvé
    """
    try:
        data = request.get_json()
        new_role = data.get('role', '').upper()
        
        if not UserRole.is_valid_role(new_role):
            return jsonify({
                'error': 'Invalid role',
                'message': f'Role must be one of: {", ".join(UserRole.all_roles())}'
            }), 400
        
        user_service = UserService(current_app.config['DB'])
        success = user_service.update_user_role(user_id, new_role)
        
        if not success:
            return jsonify({
                'error': 'Update failed',
                'message': 'User not found or role not changed'
            }), 404
        
        return jsonify({
            'message': 'User role updated successfully',
            'user_id': user_id,
            'new_role': new_role
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Update user role endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@auth_bp.route('/users/<user_id>/deactivate', methods=['PUT', 'OPTIONS'])
@token_required
@admin_required
def deactivate_user(user_id):
    """
    Désactive un compte utilisateur (ADMIN uniquement).
    
    Returns:
        200: Compte désactivé
        403: Permissions insuffisantes
        404: Utilisateur non trouvé
    """
    try:
        # Empêcher un admin de se désactiver lui-même
        if str(g.current_user['_id']) == user_id:
            return jsonify({
                'error': 'Cannot deactivate yourself',
                'message': 'You cannot deactivate your own account'
            }), 400
        
        user_service = UserService(current_app.config['DB'])
        success = user_service.deactivate_user(user_id)
        
        if not success:
            return jsonify({
                'error': 'Deactivation failed',
                'message': 'User not found or already inactive'
            }), 404
        
        return jsonify({
            'message': 'User deactivated successfully',
            'user_id': user_id
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Deactivate user endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


# --- Route de test pour vérifier les rôles ---

@auth_bp.route('/test/admin', methods=['GET'])
@token_required
@admin_required
def test_admin():
    """Route de test pour ADMIN uniquement"""
    return jsonify({
        'message': 'Admin access granted',
        'user': g.current_user['username'],
        'role': g.current_user['role']
    }), 200


@auth_bp.route('/test/analyst', methods=['GET'])
@token_required
@role_required('ADMIN', 'ANALYST')
def test_analyst():
    """Route de test pour ADMIN et ANALYST"""
    return jsonify({
        'message': 'Analyst access granted',
        'user': g.current_user['username'],
        'role': g.current_user['role']
    }), 200


@auth_bp.route('/test/user', methods=['GET'])
@token_required
@role_required('ADMIN', 'ANALYST', 'USER')
def test_user():
    """Route de test pour tous les utilisateurs authentifiés"""
    return jsonify({
        'message': 'User access granted',
        'user': g.current_user['username'],
        'role': g.current_user['role']
    }), 200
