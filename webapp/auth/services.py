"""
Services d'authentification JWT : hashage, génération de tokens, validation.
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from bson import ObjectId
from functools import wraps
from flask import current_app


class AuthService:
    """Service de gestion de l'authentification JWT"""
    
    @staticmethod
    def hash_password(password):
        """
        Hash un mot de passe avec bcrypt.
        
        Args:
            password (str): Mot de passe en clair
            
        Returns:
            bytes: Mot de passe hashé
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed
    
    @staticmethod
    def verify_password(password, password_hash):
        """
        Vérifie si un mot de passe correspond au hash.
        
        Args:
            password (str): Mot de passe en clair
            password_hash (bytes): Hash du mot de passe
            
        Returns:
            bool: True si le mot de passe correspond
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash)
        except Exception as e:
            print(f"[ERROR] Password verification failed: {e}")
            return False
    
    @staticmethod
    def generate_token(user_id, username, role, expires_in_hours=24):
        """
        Génère un token JWT pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur (ObjectId ou str)
            username (str): Nom d'utilisateur
            role (str): Rôle de l'utilisateur
            expires_in_hours (int): Durée de validité en heures
            
        Returns:
            str: Token JWT encodé
        """
        try:
            payload = {
                'user_id': str(user_id),
                'username': username,
                'role': role,
                'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            
            return token
        except Exception as e:
            print(f"[ERROR] Token generation failed: {e}")
            return None
    
    @staticmethod
    def decode_token(token):
        """
        Décode et valide un token JWT.
        
        Args:
            token (str): Token JWT à décoder
            
        Returns:
            dict: Payload du token si valide, None sinon
        """
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            print("[WARNING] Token expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"[WARNING] Invalid token: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] Token decode error: {e}")
            return None


class UserService:
    """Service de gestion des utilisateurs"""
    
    def __init__(self, db):
        """
        Initialise le service utilisateur.
        
        Args:
            db: Instance de la base MongoDB
        """
        self.db = db
        self.users_collection = db.users
    
    def create_user(self, username, email, password, role='USER'):
        """
        Crée un nouvel utilisateur.
        
        Args:
            username (str): Nom d'utilisateur
            email (str): Email
            password (str): Mot de passe en clair
            role (str): Rôle de l'utilisateur
            
        Returns:
            tuple: (user_id, error_message)
        """
        # Vérifier si l'utilisateur existe déjà
        if self.users_collection.find_one({'username': username}):
            return None, "Username already exists"
        
        if self.users_collection.find_one({'email': email}):
            return None, "Email already exists"
        
        # Hasher le mot de passe
        password_hash = AuthService.hash_password(password)
        
        # Créer le document utilisateur
        user_doc = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True,
            'last_login': None
        }
        
        try:
            result = self.users_collection.insert_one(user_doc)
            return result.inserted_id, None
        except Exception as e:
            print(f"[ERROR] User creation failed: {e}")
            return None, str(e)
    
    def authenticate_user(self, username, password):
        """
        Authentifie un utilisateur.
        
        Args:
            username (str): Nom d'utilisateur
            password (str): Mot de passe en clair
            
        Returns:
            tuple: (user_doc, error_message)
        """
        user = self.users_collection.find_one({'username': username})
        
        if not user:
            return None, "Invalid credentials"
        
        if not user.get('is_active'):
            return None, "Account is inactive"
        
        # Vérifier le mot de passe
        if not AuthService.verify_password(password, user['password_hash']):
            return None, "Invalid credentials"
        
        # Mettre à jour la date de dernière connexion
        self.users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'last_login': datetime.utcnow()}}
        )
        
        return user, None
    
    def get_user_by_id(self, user_id):
        """
        Récupère un utilisateur par son ID.
        
        Args:
            user_id: ID de l'utilisateur (str ou ObjectId)
            
        Returns:
            dict: Document utilisateur ou None
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            user = self.users_collection.find_one({'_id': user_id})
            return user
        except Exception as e:
            print(f"[ERROR] Get user by id failed: {e}")
            return None
    
    def get_user_by_username(self, username):
        """
        Récupère un utilisateur par son nom d'utilisateur.
        
        Args:
            username (str): Nom d'utilisateur
            
        Returns:
            dict: Document utilisateur ou None
        """
        return self.users_collection.find_one({'username': username})
    
    def update_user_role(self, user_id, new_role):
        """
        Met à jour le rôle d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            new_role (str): Nouveau rôle
            
        Returns:
            bool: True si succès
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            result = self.users_collection.update_one(
                {'_id': user_id},
                {'$set': {'role': new_role, 'updated_at': datetime.utcnow()}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"[ERROR] Update user role failed: {e}")
            return False
    
    def deactivate_user(self, user_id):
        """
        Désactive un compte utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            bool: True si succès
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            result = self.users_collection.update_one(
                {'_id': user_id},
                {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"[ERROR] Deactivate user failed: {e}")
            return False
