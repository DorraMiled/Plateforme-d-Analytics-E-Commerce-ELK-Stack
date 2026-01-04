import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

/**
 * Interceptor HTTP pour ajouter automatiquement le token JWT aux requêtes
 * et gérer les erreurs d'authentification
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  
  // Récupérer le token
  const token = authService.getToken();
  
  // Si le token existe, l'ajouter au header Authorization
  if (token) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  // Passer la requête au handler suivant et gérer les erreurs
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // Si erreur 401 ou 403, déconnecter l'utilisateur
      if (error.status === 401 || error.status === 403) {
        console.error('Authentication error, logging out');
        authService.logout();
      }
      
      return throwError(() => error);
    })
  );
};
