# 🔐 Module d'Authentification JWT

Système d'authentification JWT sécurisé pour l'API Flask avec gestion des rôles (RBAC), hashage bcrypt et protection des routes.

---

## 📋 Table des matières

- [Architecture](#-architecture)
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Endpoints API](#-endpoints-api)
- [Utilisation](#-utilisation)
- [Rôles et Permissions](#-rôles-et-permissions)
- [Tests](#-tests)
- [Sécurité](#-sécurité)

---

## 🏗️ Architecture

```
webapp/
├── auth/
│   ├── __init__.py           # Module initialization
│   ├── models.py             # User model et UserRole enum
│   ├── services.py           # AuthService + UserService
│   ├── decorators.py         # Middlewares JWT
│   └── routes.py             # Blueprint des routes auth
├── app.py                    # Application Flask principale
├── requirements.txt          # Dépendances (bcrypt, PyJWT)
└── test_auth.py              # Suite de tests
```

### Composants

1. **models.py**: Modèles de données et énumérations
   - `UserRole`: ADMIN, ANALYST, USER
   - `User`: Modèle utilisateur
   - `create_user_indexes()`: Création des index MongoDB

2. **services.py**: Logique métier
   - `AuthService`: Hashage, génération/validation JWT
   - `UserService`: CRUD utilisateurs, authentification

3. **decorators.py**: Middlewares de protection
   - `@token_required`: Exige un JWT valide
   - `@role_required(*roles)`: Vérifie les rôles
   - `@admin_required`: Raccourci pour ADMIN
   - `@optional_token`: Auth optionnelle

4. **routes.py**: Endpoints REST
   - `/api/auth/register`: Inscription
   - `/api/auth/login`: Connexion
   - `/api/auth/me`: Profil utilisateur
   - `/api/auth/users`: Liste utilisateurs
   - Routes de test par rôle

---

## ✨ Fonctionnalités

### Authentification
- ✅ Inscription avec validation (email, mot de passe fort)
- ✅ Connexion avec credentials
- ✅ Tokens JWT (expiration 24h)
- ✅ Hashage bcrypt (12 rounds)
- ✅ Validation automatique des tokens

### Gestion des utilisateurs
- ✅ Profil utilisateur (`/me`)
- ✅ Liste des utilisateurs (ADMIN/ANALYST)
- ✅ Modification de rôle (ADMIN)
- ✅ Désactivation de compte (ADMIN)
- ✅ Index MongoDB (username, email unique)

### Contrôle d'accès (RBAC)
- ✅ 3 rôles: ADMIN, ANALYST, USER
- ✅ Middlewares configurables par rôle
- ✅ Protection des routes sensibles
- ✅ Messages d'erreur clairs (401, 403)

### Sécurité
- ✅ Mots de passe hashés (bcrypt)
- ✅ Validation de force du mot de passe
- ✅ Protection CSRF via JWT
- ✅ Expiration automatique des tokens
- ✅ Logs des échecs d'authentification

---

## 📦 Installation

### 1. Installer les dépendances

```bash
cd webapp
pip install -r requirements.txt
```

**Nouvelles dépendances:**
- `bcrypt==4.1.2` - Hashage des mots de passe
- `PyJWT==2.8.0` - Génération et validation JWT

### 2. Configurer la clé secrète

```bash
# Dans .env ou variables d'environnement
SECRET_KEY=your-super-secret-key-change-in-production-2024!
```

**⚠️ Important:** Changez la clé secrète en production!

### 3. Lancer l'application

```bash
python app.py
```

Le module d'authentification est automatiquement enregistré sur `/api/auth`.

---

## ⚙️ Configuration

### Variables d'environnement

```bash
# MongoDB
MONGODB_URI=mongodb://admin:admin123@localhost:27017/ecommerce?authSource=admin

# JWT
SECRET_KEY=your-secret-key-here  # 32+ caractères recommandés
JWT_EXPIRATION_HOURS=24          # Optionnel (défaut: 24h)

# Application
FLASK_ENV=development
FLASK_DEBUG=True
```

### Paramètres de sécurité

```python
# Dans auth/services.py
bcrypt.gensalt(rounds=12)  # Coût de hashage (10-14 recommandé)

# Dans auth/routes.py
- Mot de passe: min 8 caractères, 1 maj, 1 min, 1 chiffre
- Username: min 3 caractères
- Email: validation regex
```

---

## 🌐 Endpoints API

### Authentication

#### `POST /api/auth/register`
**Inscription d'un nouvel utilisateur**

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "role": "USER"  // Optionnel (USER par défaut)
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "65abc123...",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "USER"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:**
- `400`: Champs manquants ou invalides
- `409`: Username/email déjà existant

---

#### `POST /api/auth/login`
**Connexion d'un utilisateur**

**Request:**
```json
{
  "username": "john_doe",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "65abc123...",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "USER",
    "last_login": "2026-01-01T15:30:00"
  }
}
```

**Errors:**
- `400`: Champs manquants
- `401`: Identifiants invalides ou compte inactif

---

#### `GET /api/auth/me`
**Récupérer le profil de l'utilisateur courant**

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "user": {
    "id": "65abc123...",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "USER",
    "is_active": true,
    "created_at": "2026-01-01T10:00:00",
    "last_login": "2026-01-01T15:30:00"
  }
}
```

**Errors:**
- `401`: Token manquant ou invalide
- `403`: Utilisateur non trouvé ou inactif

---

### User Management (ADMIN/ANALYST)

#### `GET /api/auth/users`
**Liste tous les utilisateurs (ADMIN et ANALYST uniquement)**

**Headers:**
```
Authorization: Bearer <admin_or_analyst_token>
```

**Query params:**
- `role`: Filtrer par rôle (ADMIN, ANALYST, USER)
- `active`: Filtrer par statut (true/false)
- `limit`: Nombre max de résultats (défaut: 50, max: 100)
- `skip`: Pagination

**Response (200):**
```json
{
  "users": [
    {
      "id": "65abc123...",
      "username": "john_doe",
      "email": "john@example.com",
      "role": "USER",
      "is_active": true,
      "created_at": "2026-01-01T10:00:00",
      "last_login": "2026-01-01T15:30:00"
    }
  ],
  "total": 15,
  "limit": 50,
  "skip": 0
}
```

**Errors:**
- `403`: Permissions insuffisantes (USER role)

---

#### `PUT /api/auth/users/<user_id>/role`
**Modifier le rôle d'un utilisateur (ADMIN uniquement)**

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request:**
```json
{
  "role": "ANALYST"
}
```

**Response (200):**
```json
{
  "message": "User role updated successfully",
  "user_id": "65abc123...",
  "new_role": "ANALYST"
}
```

**Errors:**
- `400`: Rôle invalide
- `403`: Permissions insuffisantes
- `404`: Utilisateur non trouvé

---

#### `PUT /api/auth/users/<user_id>/deactivate`
**Désactiver un compte utilisateur (ADMIN uniquement)**

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "message": "User deactivated successfully",
  "user_id": "65abc123..."
}
```

**Errors:**
- `400`: Tentative de se désactiver soi-même
- `403`: Permissions insuffisantes
- `404`: Utilisateur non trouvé

---

### Test Endpoints

#### `GET /api/auth/test/admin`
**Route de test pour ADMIN uniquement**

#### `GET /api/auth/test/analyst`
**Route de test pour ADMIN et ANALYST**

#### `GET /api/auth/test/user`
**Route de test pour tous les utilisateurs authentifiés**

---

## 🚀 Utilisation

### Protéger une route existante

#### Exemple 1: Authentification simple

```python
from auth.decorators import token_required
from flask import g, jsonify

@app.route('/api/dashboard')
@token_required
def dashboard():
    """Dashboard accessible uniquement aux utilisateurs authentifiés"""
    user = g.current_user
    
    return jsonify({
        'message': f'Welcome {user["username"]}',
        'role': user['role']
    })
```

#### Exemple 2: Avec contrôle de rôle

```python
from auth.decorators import token_required, role_required

@app.route('/api/admin/stats')
@token_required
@role_required('ADMIN')
def admin_stats():
    """Stats réservées aux administrateurs"""
    return jsonify({'sensitive': 'data'})
```

#### Exemple 3: Plusieurs rôles autorisés

```python
from auth.decorators import token_required, role_required

@app.route('/api/reports')
@token_required
@role_required('ADMIN', 'ANALYST')
def reports():
    """Rapports accessibles aux ADMIN et ANALYST"""
    return jsonify({'report': 'data'})
```

#### Exemple 4: Authentification optionnelle

```python
from auth.decorators import optional_token
from flask import g

@app.route('/api/public-data')
@optional_token
def public_data():
    """Contenu adapté selon l'authentification"""
    if g.current_user:
        # Utilisateur authentifié - données personnalisées
        return jsonify({
            'message': f'Hello {g.current_user["username"]}',
            'premium_data': [...]
        })
    else:
        # Utilisateur anonyme - données publiques
        return jsonify({
            'message': 'Hello guest',
            'basic_data': [...]
        })
```

### Accéder à l'utilisateur courant

```python
from flask import g

@app.route('/api/my-route')
@token_required
def my_route():
    # g.current_user contient le document MongoDB complet
    user = g.current_user
    
    print(f"User ID: {user['_id']}")
    print(f"Username: {user['username']}")
    print(f"Email: {user['email']}")
    print(f"Role: {user['role']}")
    print(f"Is Active: {user['is_active']}")
    
    # g.token_payload contient le payload JWT
    payload = g.token_payload
    print(f"Token expires at: {payload['exp']}")
```

---

## 👥 Rôles et Permissions

### Hiérarchie des rôles

| Rôle | Description | Permissions |
|------|-------------|-------------|
| **ADMIN** | Administrateur système | Accès complet, gestion des utilisateurs, modification des rôles |
| **ANALYST** | Analyste de données | Consultation des utilisateurs, accès aux rapports, pas de gestion |
| **USER** | Utilisateur standard | Accès de base, consultation de ses propres données |

### Matrice de permissions

| Endpoint | ADMIN | ANALYST | USER |
|----------|:-----:|:-------:|:----:|
| `POST /api/auth/register` | ✅ | ✅ | ✅ |
| `POST /api/auth/login` | ✅ | ✅ | ✅ |
| `GET /api/auth/me` | ✅ | ✅ | ✅ |
| `GET /api/auth/users` | ✅ | ✅ | ❌ |
| `PUT /api/auth/users/:id/role` | ✅ | ❌ | ❌ |
| `PUT /api/auth/users/:id/deactivate` | ✅ | ❌ | ❌ |
| `GET /api/auth/test/admin` | ✅ | ❌ | ❌ |
| `GET /api/auth/test/analyst` | ✅ | ✅ | ❌ |
| `GET /api/auth/test/user` | ✅ | ✅ | ✅ |

---

## 🧪 Tests

### Lancer la suite de tests

```bash
cd webapp
python test_auth.py
```

**Tests inclus:**
- ✅ Inscription de 3 utilisateurs (ADMIN, ANALYST, USER)
- ✅ Connexion avec credentials valides
- ✅ Récupération du profil (`/me`)
- ✅ Tokens invalides et manquants
- ✅ Contrôle d'accès par rôle (9 scénarios)
- ✅ Liste des utilisateurs (permissions)

### Test manuel avec curl

#### 1. Inscription
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "TestPass123",
    "role": "USER"
  }'
```

#### 2. Connexion
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "TestPass123"
  }'
```

**Récupérer le token:**
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"TestPass123"}' \
  | jq -r '.token')
```

#### 3. Accès à une route protégée
```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

#### 4. Test avec Postman

1. **Register/Login**: Envoyer POST et copier le token
2. **Headers**: Ajouter `Authorization: Bearer <token>`
3. **Tester les routes**: `/me`, `/users`, `/test/admin`, etc.

---

## 🔒 Sécurité

### Bonnes pratiques implémentées

✅ **Hashage bcrypt**: 12 rounds de salage  
✅ **Validation du mot de passe**: Min 8 caractères, majuscules, minuscules, chiffres  
✅ **Index unique**: Username et email uniques en base  
✅ **Expiration JWT**: Tokens valides 24h  
✅ **Validation stricte**: Tous les inputs validés  
✅ **Messages d'erreur**: Pas de fuite d'informations  
✅ **Logs**: Échecs d'authentification enregistrés  

### Recommandations production

🔐 **Clé secrète**: Générer une clé de 32+ caractères aléatoires  
🔐 **HTTPS obligatoire**: Utiliser SSL/TLS en production  
🔐 **Rate limiting**: Limiter les tentatives de connexion  
🔐 **Rotation des tokens**: Implémenter refresh tokens  
🔐 **Audit logs**: Logger toutes les actions sensibles  
🔐 **2FA**: Ajouter l'authentification à deux facteurs  

### Génerer une clé secrète sécurisée

```python
import secrets

# Générer une clé de 32 bytes (64 caractères hex)
secret_key = secrets.token_hex(32)
print(secret_key)
```

Ou avec OpenSSL:
```bash
openssl rand -hex 32
```

---

## 📚 Ressources

- [JWT.io](https://jwt.io/) - Déboguer les tokens JWT
- [bcrypt](https://github.com/pyca/bcrypt/) - Documentation bcrypt
- [PyJWT](https://pyjwt.readthedocs.io/) - Documentation PyJWT
- [OWASP](https://owasp.org/www-project-web-security-testing-guide/) - Guide de sécurité

---

## 🐛 Troubleshooting

### Erreur: "Token expired"
**Cause**: Le token JWT a expiré (après 24h)  
**Solution**: Se reconnecter pour obtenir un nouveau token

### Erreur: "User not found"
**Cause**: L'utilisateur a été supprimé ou désactivé  
**Solution**: Vérifier l'état du compte avec un admin

### Erreur: "Insufficient permissions"
**Cause**: Le rôle de l'utilisateur n'a pas accès à la ressource  
**Solution**: Demander un changement de rôle à un admin

### Erreur: "Invalid authorization header format"
**Cause**: Le header n'est pas au format `Bearer <token>`  
**Solution**: Vérifier le format: `Authorization: Bearer eyJhbGc...`

---

**Version**: 1.0.0  
**Dernière mise à jour**: Janvier 2026  
**Auteur**: E-Commerce Analytics Team
