import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import { Router } from '@angular/router';

/**
 * Interface pour les données utilisateur
 */
export interface User {
  id: string;
  username: string;
  email: string;
  role: 'ADMIN' | 'ANALYST' | 'USER';
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

/**
 * Interface pour la réponse de login
 */
export interface LoginResponse {
  message: string;
  token: string;
  user: User;
}

/**
 * Interface pour la réponse de register
 */
export interface RegisterResponse {
  message: string;
  user: User;
  token: string;
}

/**
 * Interface pour la réponse de /me
 */
export interface MeResponse {
  user: User;
}

/**
 * Service d'authentification JWT
 * Gère la connexion, l'inscription, le logout et le stockage du token
 */
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly API_URL = 'http://localhost:8000/api/auth';
  private readonly TOKEN_KEY = 'jwt_token';
  private readonly USER_KEY = 'current_user';
  
  // BehaviorSubject pour suivre l'état de connexion
  private currentUserSubject: BehaviorSubject<User | null>;
  public currentUser$: Observable<User | null>;
  
  // BehaviorSubject pour l'état d'authentification
  private isAuthenticatedSubject: BehaviorSubject<boolean>;
  public isAuthenticated$: Observable<boolean>;

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    // Initialiser avec l'utilisateur stocké (si existe)
    const storedUser = this.getStoredUser();
    this.currentUserSubject = new BehaviorSubject<User | null>(storedUser);
    this.currentUser$ = this.currentUserSubject.asObservable();
    
    this.isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasToken());
    this.isAuthenticated$ = this.isAuthenticatedSubject.asObservable();
    
    // Ne pas vérifier le token ici pour éviter une déconnexion au rafraîchissement
    // L'utilisateur est chargé depuis localStorage, l'interceptor gérera les erreurs d'auth
  }

  /**
   * Inscription d'un nouvel utilisateur
   */
  register(username: string, email: string, password: string, role: string = 'USER'): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(`${this.API_URL}/register`, {
      username,
      email,
      password,
      role
    }).pipe(
      tap(response => {
        this.setSession(response.token, response.user);
      }),
      catchError(error => {
        console.error('Registration error:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Connexion d'un utilisateur
   */
  login(username: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.API_URL}/login`, {
      username,
      password
    }).pipe(
      tap(response => {
        this.setSession(response.token, response.user);
      }),
      catchError(error => {
        console.error('Login error:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Déconnexion de l'utilisateur
   */
  logout(): void {
    // Supprimer le token et l'utilisateur
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    
    // Mettre à jour les subjects
    this.currentUserSubject.next(null);
    this.isAuthenticatedSubject.next(false);
    
    // Rediriger vers la page de login
    this.router.navigate(['/login']);
  }

  /**
   * Récupérer le profil de l'utilisateur courant
   */
  getCurrentUser(): Observable<User> {
    return this.http.get<MeResponse>(`${this.API_URL}/me`).pipe(
      map(response => response.user),
      tap(user => {
        this.setUser(user);
      }),
      catchError(error => {
        console.error('Get current user error:', error);
        // Si le token est invalide, déconnecter
        if (error.status === 401 || error.status === 403) {
          this.logout();
        }
        return throwError(() => error);
      })
    );
  }

  /**
   * Vérifier la validité du token
   * Ne déconnecte PAS automatiquement en cas d'échec pour éviter les faux positifs au rafraîchissement
   */
  verifyToken(): void {
    if (!this.hasToken()) {
      return;
    }

    this.getCurrentUser().subscribe({
      next: (user) => {
        console.log('Token valid, user:', user.username);
      },
      error: (error) => {
        console.warn('Token verification failed (may be temporary):', error);
        // Ne pas déconnecter automatiquement - l'interceptor gère les erreurs 401/403
        // Si c'est un vrai problème d'auth, la prochaine requête API déclenchera le logout
      }
    });
  }

  /**
   * Définir la session (token + utilisateur)
   */
  private setSession(token: string, user: User): void {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    
    this.currentUserSubject.next(user);
    this.isAuthenticatedSubject.next(true);
  }

  /**
   * Définir l'utilisateur courant
   */
  private setUser(user: User): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    this.currentUserSubject.next(user);
  }

  /**
   * Récupérer l'utilisateur stocké
   */
  private getStoredUser(): User | null {
    const userJson = localStorage.getItem(this.USER_KEY);
    if (userJson) {
      try {
        return JSON.parse(userJson);
      } catch (e) {
        console.error('Error parsing stored user:', e);
        return null;
      }
    }
    return null;
  }

  /**
   * Récupérer le token JWT
   */
  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Vérifier si un token existe
   */
  hasToken(): boolean {
    return !!this.getToken();
  }

  /**
   * Vérifier si l'utilisateur est authentifié
   */
  isAuthenticated(): boolean {
    return this.hasToken() && this.currentUserSubject.value !== null;
  }

  /**
   * Obtenir la valeur actuelle de l'utilisateur
   */
  get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  /**
   * Vérifier si l'utilisateur a un rôle spécifique
   */
  hasRole(role: string): boolean {
    const user = this.currentUserValue;
    return user !== null && user.role === role;
  }

  /**
   * Vérifier si l'utilisateur a un des rôles spécifiés
   */
  hasAnyRole(roles: string[]): boolean {
    const user = this.currentUserValue;
    return user !== null && roles.includes(user.role);
  }

  /**
   * Vérifier si l'utilisateur est admin
   */
  isAdmin(): boolean {
    return this.hasRole('ADMIN');
  }

  /**
   * Vérifier si l'utilisateur est analyst
   */
  isAnalyst(): boolean {
    return this.hasRole('ANALYST');
  }

  /**
   * Vérifier si l'utilisateur est un utilisateur standard
   */
  isUser(): boolean {
    return this.hasRole('USER');
  }
}
