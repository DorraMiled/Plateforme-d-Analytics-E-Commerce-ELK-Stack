# 🔐 Authentification JWT - Frontend Angular

Documentation complète de l'implémentation de l'authentification JWT côté frontend avec Angular 17.

---

## 📋 Fichiers créés

### Services
- **`services/auth.service.ts`** - Service principal d'authentification avec gestion JWT

### Interceptors
- **`interceptors/auth.interceptor.ts`** - Interceptor HTTP pour ajouter automatiquement le token

### Guards
- **`guards/auth.guard.ts`** - Guard pour protéger les routes

### Components
- **`components/login/login.component.ts`** - Composant Login/Register
- **`components/login/login.component.html`** - Template avec Material Design
- **`components/login/login.component.scss`** - Styles modernes avec animations

---

## ✨ Fonctionnalités

### AuthService
✅ **Login** - Authentification avec username/password  
✅ **Register** - Inscription avec validation  
✅ **Logout** - Déconnexion avec nettoyage  
✅ **Token storage** - Stockage sécurisé dans localStorage  
✅ **Token verification** - Vérification automatique au démarrage  
✅ **Current user tracking** - Observable pour suivre l'utilisateur  
✅ **Role checking** - Méthodes hasRole(), isAdmin(), isAnalyst()  
✅ **Auto-logout** - Déconnexion automatique si token invalide

### AuthInterceptor
✅ **Auto-inject token** - Ajout automatique du header Authorization  
✅ **Error handling** - Gestion des erreurs 401/403  
✅ **Auto-logout** - Déconnexion si erreur d'authentification

### AuthGuard
✅ **Route protection** - Empêche l'accès non autorisé  
✅ **Role-based access** - Vérifie les rôles requis  
✅ **Redirect** - Redirige vers /login si non authentifié  
✅ **Return URL** - Mémorise l'URL de destination

### LoginComponent
✅ **Dual tabs** - Login et Register dans la même page  
✅ **Material Design** - UI moderne avec Angular Material  
✅ **Form validation** - Validation en temps réel  
✅ **Password strength** - Vérification de la force du mot de passe  
✅ **Role selection** - Choix du rôle à l'inscription  
✅ **Loading states** - Spinners pendant les requêtes  
✅ **Error messages** - Messages d'erreur clairs  
✅ **Animations** - Animations fluides

---

## 🚀 Utilisation

### 1. AuthService - Dans un composant

```typescript
import { Component, OnInit } from '@angular/core';
import { AuthService, User } from './services/auth.service';
import { Observable } from 'rxjs';

@Component({...})
export class MyComponent implements OnInit {
  currentUser$: Observable<User | null>;
  isAuthenticated$: Observable<boolean>;
  
  constructor(private authService: AuthService) {
    this.currentUser$ = this.authService.currentUser$;
    this.isAuthenticated$ = this.authService.isAuthenticated$;
  }
  
  ngOnInit() {
    // Obtenir l'utilisateur courant
    const user = this.authService.currentUserValue;
    if (user) {
      console.log('User:', user.username, 'Role:', user.role);
    }
    
    // Vérifier le rôle
    if (this.authService.isAdmin()) {
      console.log('User is admin');
    }
  }
  
  logout() {
    this.authService.logout();
  }
}
```

### 2. AuthGuard - Protection des routes

```typescript
// app.routes.ts
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  
  // Route protégée (authentification requise)
  { 
    path: 'dashboard', 
    component: DashboardComponent,
    canActivate: [AuthGuard]
  },
  
  // Route protégée avec rôle requis (ADMIN uniquement)
  { 
    path: 'admin', 
    component: AdminComponent,
    canActivate: [AuthGuard],
    data: { roles: ['ADMIN'] }
  },
  
  // Route protégée multi-rôles (ADMIN et ANALYST)
  { 
    path: 'reports', 
    component: ReportsComponent,
    canActivate: [AuthGuard],
    data: { roles: ['ADMIN', 'ANALYST'] }
  }
];
```

### 3. AuthInterceptor - Configuration

L'interceptor est déjà configuré dans `main.ts` et s'applique automatiquement à toutes les requêtes HTTP.

```typescript
// Exemple de requête - le token sera ajouté automatiquement
this.http.get('/api/protected-endpoint').subscribe(...);

// Résultat: Header ajouté automatiquement
// Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4. Template - Afficher l'utilisateur

```html
<!-- Dans votre template -->
<div *ngIf="currentUser$ | async as user">
  <p>Welcome, {{ user.username }}!</p>
  <p>Role: {{ user.role }}</p>
  
  <!-- Afficher conditionnellement selon le rôle -->
  <button *ngIf="authService.isAdmin()">
    Admin Only
  </button>
  
  <button (click)="logout()">Logout</button>
</div>

<div *ngIf="!(currentUser$ | async)">
  <a routerLink="/login">Please login</a>
</div>
```

---

## 🎨 Page de Login

### Fonctionnalités

**Tab Login:**
- Username (min 3 chars)
- Password (min 8 chars)
- Toggle password visibility
- Form validation en temps réel
- Loading state avec spinner

**Tab Register:**
- Username (min 3 chars)
- Email (validation regex)
- Password (min 8 chars, 1 maj, 1 min, 1 chiffre)
- Confirm Password (matching validation)
- Role selection (USER, ANALYST, ADMIN)
- Form validation complète

**Design:**
- Gradient background animé
- Card Material Design
- Animations fadeInUp
- Background circles flottants
- Responsive (mobile/desktop)
- Snackbar pour les messages
- Footer avec sécurité JWT

### Validation des mots de passe

```typescript
// Règles de validation
- Minimum 8 caractères
- Au moins 1 majuscule
- Au moins 1 minuscule
- Au moins 1 chiffre
- Confirmation de mot de passe correspondante
```

---

## 🔒 Sécurité

### Stockage du token

**LocalStorage vs SessionStorage:**

Actuellement utilise `localStorage` pour persister la session entre les onglets et après fermeture du navigateur.

```typescript
// Pour utiliser sessionStorage (expire à la fermeture)
// Dans auth.service.ts, remplacer:
localStorage.setItem(...)  →  sessionStorage.setItem(...)
localStorage.getItem(...)  →  sessionStorage.getItem(...)
localStorage.removeItem(...) →  sessionStorage.removeItem(...)
```

### Protection XSS

✅ Angular sanitize automatiquement les données  
✅ Pas de `dangerouslySetInnerHTML`  
✅ Token jamais exposé dans l'URL  
✅ Utilisation de HttpOnly cookies (recommandé en production)

### Bonnes pratiques

✅ **Token expiration** - Géré côté backend (24h)  
✅ **Auto-logout** - Si token invalide ou expiré  
✅ **HTTPS only** - En production uniquement  
✅ **Refresh token** - À implémenter pour UX améliorée  
✅ **Rate limiting** - Backend limite les tentatives

---

## 📊 Flux d'authentification

```
1. USER ACTION
   ↓
2. LoginComponent.onLogin()
   → authService.login(username, password)
   ↓
3. HTTP POST /api/auth/login
   → AuthInterceptor (pas de token pour /login)
   ↓
4. Backend vérifie credentials
   → Retourne { token, user }
   ↓
5. AuthService.setSession(token, user)
   → localStorage.setItem('jwt_token', token)
   → localStorage.setItem('current_user', JSON.stringify(user))
   → currentUserSubject.next(user)
   → isAuthenticatedSubject.next(true)
   ↓
6. Router.navigate(['/dashboard'])
   → AuthGuard vérifie l'authentification
   ↓
7. Toutes les requêtes futures
   → AuthInterceptor ajoute le header
   → Authorization: Bearer <token>
```

---

## 🛡️ AuthGuard - Exemples

### Route simple (authentification uniquement)

```typescript
{ 
  path: 'dashboard', 
  component: DashboardComponent,
  canActivate: [AuthGuard]
  // Accessible par tous les utilisateurs authentifiés
}
```

### Route avec rôle unique

```typescript
{ 
  path: 'admin', 
  component: AdminComponent,
  canActivate: [AuthGuard],
  data: { roles: ['ADMIN'] }
  // Accessible uniquement par ADMIN
}
```

### Route avec multiples rôles

```typescript
{ 
  path: 'analytics', 
  component: AnalyticsComponent,
  canActivate: [AuthGuard],
  data: { roles: ['ADMIN', 'ANALYST'] }
  // Accessible par ADMIN et ANALYST
}
```

### Guard avec enfants

```typescript
{
  path: 'admin',
  canActivate: [AuthGuard],
  data: { roles: ['ADMIN'] },
  children: [
    { path: 'users', component: UsersComponent },
    { path: 'settings', component: SettingsComponent }
  ]
  // Tous les enfants héritent de la protection
}
```

---

## 🔄 Auto-logout

Le système déconnecte automatiquement l'utilisateur dans les cas suivants:

1. **Token expiré** (401 Unauthorized)
2. **Token invalide** (403 Forbidden)
3. **Utilisateur supprimé** (403 Forbidden)
4. **Erreur de vérification** au démarrage

```typescript
// Dans AuthInterceptor
catchError((error: HttpErrorResponse) => {
  if (error.status === 401 || error.status === 403) {
    this.authService.logout(); // Auto-logout
  }
  return throwError(() => error);
})
```

---

## 📱 Responsive Design

La page de login s'adapte à toutes les tailles d'écran:

**Desktop (> 600px):**
- Card centrée avec max-width: 500px
- Padding généreux
- Animations complètes

**Mobile (≤ 600px):**
- Full-width avec padding réduit
- Font-sizes adaptés
- Touch-friendly buttons

---

## 🎯 Prochaines améliorations

### Recommandations

1. **Refresh Token** - Renouvellement automatique sans re-login
2. **Remember Me** - Option pour rester connecté
3. **Password Reset** - Email de réinitialisation
4. **Email Verification** - Vérification lors de l'inscription
5. **2FA** - Authentification à deux facteurs
6. **Social Login** - Google, GitHub, etc.
7. **Session Management** - Voir toutes les sessions actives
8. **Activity Log** - Historique des connexions

---

## 🧪 Tests

### Test manuel

1. **Démarrer le backend:**
```bash
cd webapp
python app.py
```

2. **Démarrer le frontend:**
```bash
cd frontend
npm start
```

3. **Tester l'inscription:**
- Aller sur http://localhost:4200/login
- Onglet "Register"
- Remplir le formulaire
- Créer un compte

4. **Tester la connexion:**
- Onglet "Login"
- Entrer username/password
- Cliquer "Login"
- Vérifier la redirection vers /dashboard

5. **Tester la protection:**
- Déconnexion (menu utilisateur)
- Essayer d'accéder à /dashboard
- Vérifier redirection vers /login

6. **Tester le rôle:**
- Créer un compte USER
- Essayer d'accéder à /files (ADMIN/ANALYST only)
- Vérifier redirection vers /dashboard

### Test avec console

```javascript
// Dans la console du navigateur
// Vérifier le token
localStorage.getItem('jwt_token')

// Vérifier l'utilisateur
JSON.parse(localStorage.getItem('current_user'))

// Supprimer manuellement (logout manuel)
localStorage.clear()
```

---

## 🐛 Troubleshooting

### "Token invalid or expired"
**Cause**: Le token a expiré (> 24h) ou est corrompu  
**Solution**: Se reconnecter pour obtenir un nouveau token

### "Authorization header is missing"
**Cause**: L'interceptor n'est pas configuré correctement  
**Solution**: Vérifier que `AuthInterceptor` est dans `main.ts` providers

### "Cannot access before initialization"
**Cause**: Import circulaire entre services/guards  
**Solution**: Vérifier les imports, utiliser `forwardRef` si nécessaire

### "User not found" (403)
**Cause**: L'utilisateur a été supprimé de la base  
**Solution**: Système déconnecte automatiquement

### Routes non protégées
**Cause**: `AuthGuard` n'est pas ajouté à la route  
**Solution**: Ajouter `canActivate: [AuthGuard]` dans `app.routes.ts`

---

## 📚 Ressources

- [Angular Guards](https://angular.io/api/router/CanActivate)
- [HTTP Interceptors](https://angular.io/guide/http-intercept-requests-and-responses)
- [Angular Material](https://material.angular.io/)
- [JWT.io](https://jwt.io/) - Déboguer les tokens
- [RxJS Observables](https://rxjs.dev/guide/observable)

---

**Version**: 1.0.0  
**Date**: Janvier 2026  
**Auteur**: E-Commerce Analytics Team

🎉 **Authentification JWT frontend complète et prête à l'emploi!**
