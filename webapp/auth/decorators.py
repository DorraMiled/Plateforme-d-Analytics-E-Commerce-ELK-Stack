"""
Décorateurs pour la protection des routes avec JWT et contrôle des rôles.
"""
from functools import wraps
from flask import request, jsonify, g, current_app
from auth.services import AuthService, UserService


def token_required(f):
    """
    Décorateur pour exiger un token JWT valide.
    Ajoute l'utilisateur courant dans g.current_user.
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route():
            user = g.current_user
            return jsonify({'user': user['username']})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Récupérer le token depuis le header Authorization
        auth_header = request.headers.get('Authorization', None)
        
        if not auth_header:
            return jsonify({
                'error': 'Authorization header is missing',
                'message': 'Please provide a valid token'
            }), 401
        
        # Vérifier le format "Bearer <token>"
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({
                'error': 'Invalid authorization header format',
                'message': 'Format should be: Bearer <token>'
            }), 401
        
        token = parts[1]
        
        # Décoder le token
        payload = AuthService.decode_token(token)
        
        if not payload:
            return jsonify({
                'error': 'Invalid or expired token',
                'message': 'Please login again'
            }), 401
        
        # Récupérer l'utilisateur depuis la base de données
        user_service = UserService(current_app.config['DB'])
        user = user_service.get_user_by_id(payload['user_id'])
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'The user associated with this token does not exist'
            }), 403
        
        if not user.get('is_active'):
            return jsonify({
                'error': 'Account inactive',
                'message': 'Your account has been deactivated'
            }), 403
        
        # Stocker l'utilisateur et le payload dans g
        g.current_user = user
        g.token_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated


def role_required(*allowed_roles):
    """
    Décorateur pour exiger un ou plusieurs rôles spécifiques.
    Doit être utilisé APRÈS @token_required.
    
    Args:
        *allowed_roles: Rôles autorisés (ADMIN, ANALYST, USER)
    
    Usage:
        @app.route('/admin')
        @token_required
        @role_required('ADMIN')
        def admin_route():
            return jsonify({'message': 'Admin only'})
        
        @app.route('/staff')
        @token_required
        @role_required('ADMIN', 'ANALYST')
        def staff_route():
            return jsonify({'message': 'Admin and Analyst only'})
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Vérifier que token_required a été appelé avant
            if not hasattr(g, 'current_user'):
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'Use @token_required before @role_required'
                }), 500
            
            user = g.current_user
            user_role = user.get('role', 'USER')
            
            # Vérifier si l'utilisateur a un rôle autorisé
            if user_role not in allowed_roles:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'This route requires one of these roles: {", ".join(allowed_roles)}',
                    'your_role': user_role
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator


def admin_required(f):
    """
    Décorateur raccourci pour exiger le rôle ADMIN.
    Doit être utilisé APRÈS @token_required.
    
    Usage:
        @app.route('/admin-only')
        @token_required
        @admin_required
        def admin_only_route():
            return jsonify({'message': 'Admin access'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user'):
            return jsonify({
                'error': 'Authentication required',
                'message': 'Use @token_required before @admin_required'
            }), 500
        
        user = g.current_user
        
        if user.get('role') != 'ADMIN':
            return jsonify({
                'error': 'Admin access required',
                'message': 'Only administrators can access this resource'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated


def optional_token(f):
    """
    Décorateur pour les routes avec authentification optionnelle.
    Si un token est fourni et valide, l'utilisateur est ajouté à g.current_user.
    Sinon, g.current_user sera None mais la requête continue.
    
    Usage:
        @app.route('/public-or-private')
        @optional_token
        def hybrid_route():
            if g.current_user:
                return jsonify({'message': f'Hello {g.current_user["username"]}'})
            else:
                return jsonify({'message': 'Hello anonymous'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        
        g.current_user = None
        g.token_payload = None
        
        if auth_header:
            parts = auth_header.split()
            
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
                payload = AuthService.decode_token(token)
                
                if payload:
                    user_service = UserService(current_app.config['DB'])
                    user = user_service.get_user_by_id(payload['user_id'])
                    
                    if user and user.get('is_active'):
                        g.current_user = user
                        g.token_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated
