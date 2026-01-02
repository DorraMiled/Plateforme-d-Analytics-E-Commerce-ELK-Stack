import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService } from '../services/auth.service';

/**
 * Guard pour protéger les routes nécessitant une authentification
 */
@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    
    // Vérifier d'abord si un token existe (plus fiable au rafraîchissement)
    if (!this.authService.hasToken()) {
      // Pas de token, rediriger vers login
      console.log('No token found, redirecting to login');
      this.router.navigate(['/login'], { 
        queryParams: { returnUrl: state.url } 
      });
      return false;
    }

    // Token existe, vérifier les rôles requis (si spécifiés)
    const requiredRoles = route.data['roles'] as string[];
    
    if (requiredRoles && requiredRoles.length > 0) {
      // Attendre que l'utilisateur soit chargé avant de vérifier les rôles
      const currentUser = this.authService.currentUserValue;
      
      if (!currentUser) {
        // L'utilisateur n'est pas encore chargé depuis localStorage
        // Autoriser l'accès temporairement, le service charge l'utilisateur
        return true;
      }
      
      // Vérifier si l'utilisateur a un des rôles requis
      if (this.authService.hasAnyRole(requiredRoles)) {
        return true;
      } else {
        // Utilisateur authentifié mais n'a pas le bon rôle
        console.warn('Access denied: insufficient permissions');
        this.router.navigate(['/dashboard']);
        return false;
      }
    }
    
    // Pas de rôle requis, autoriser l'accès
    return true;
  }
}
