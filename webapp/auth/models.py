"""
Models pour l'authentification et la gestion des utilisateurs.
"""
from datetime import datetime
from bson import ObjectId

class UserRole:
    """Énumération des rôles utilisateurs"""
    ADMIN = 'ADMIN'
    ANALYST = 'ANALYST'
    USER = 'USER'
    
    @staticmethod
    def all_roles():
        return [UserRole.ADMIN, UserRole.ANALYST, UserRole.USER]
    
    @staticmethod
    def is_valid_role(role):
        return role in UserRole.all_roles()


class User:
    """Modèle utilisateur pour MongoDB"""
    
    def __init__(self, username, email, password_hash, role=UserRole.USER, **kwargs):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.is_active = kwargs.get('is_active', True)
        self.last_login = kwargs.get('last_login', None)
    
    def to_dict(self):
        """Convertit l'utilisateur en dictionnaire pour MongoDB"""
        return {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'last_login': self.last_login
        }
    
    def to_json(self):
        """Convertit l'utilisateur en JSON (sans mot de passe)"""
        return {
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @staticmethod
    def from_dict(data):
        """Crée un utilisateur depuis un dictionnaire MongoDB"""
        return User(
            username=data.get('username'),
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            role=data.get('role', UserRole.USER),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            is_active=data.get('is_active', True),
            last_login=data.get('last_login')
        )


def create_user_indexes(db):
    """Crée les index pour la collection users"""
    users_collection = db.users
    
    # Index unique sur username
    users_collection.create_index('username', unique=True)
    
    # Index unique sur email
    users_collection.create_index('email', unique=True)
    
    # Index sur role pour les recherches par rôle
    users_collection.create_index('role')
    
    # Index sur is_active
    users_collection.create_index('is_active')
    
    print("[OK] User indexes created")
