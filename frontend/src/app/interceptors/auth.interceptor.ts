import { Injectable } from '@angular/core';
import {
  HttpEvent,
  HttpInterceptor,
  HttpHandler,
  HttpRequest,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

/**
 * Interceptor HTTP pour ajouter automatiquement le token JWT aux requêtes
 * et gérer les erreurs d'authentification
 */
@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  
  constructor(private authService: AuthService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Récupérer le token
    const token = this.authService.getToken();
    
    // Si le token existe, l'ajouter au header Authorization
    if (token) {
      req = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }

    // Passer la requête au handler suivant et gérer les erreurs
    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        // Si erreur 401 ou 403, déconnecter l'utilisateur
        if (error.status === 401 || error.status === 403) {
          console.error('Authentication error, logging out');
          this.authService.logout();
        }
        
        return throwError(() => error);
      })
    );
  }
}
