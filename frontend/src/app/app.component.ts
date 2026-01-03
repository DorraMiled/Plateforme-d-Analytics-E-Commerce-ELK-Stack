import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, NavigationEnd } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { MatBadgeModule } from '@angular/material/badge';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { Observable } from 'rxjs';
import { map, shareReplay, filter } from 'rxjs/operators';
import { AuthService, User } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatSidenavModule,
    MatListModule,
    MatMenuModule,
    MatBadgeModule
  ],
  template: `
    <!-- Page Login isolée (sans navigation) -->
    <div *ngIf="isLoginPage" class="login-page-container">
      <router-outlet></router-outlet>
    </div>

    <!-- Application principale avec navigation -->
    <mat-sidenav-container class="sidenav-container" *ngIf="!isLoginPage">
      <mat-sidenav
        #drawer
        class="sidenav"
        fixedInViewport
        [attr.role]="(isHandset$ | async) ? 'dialog' : 'navigation'"
        [mode]="(isHandset$ | async) ? 'over' : 'side'"
        [opened]="(isHandset$ | async) === false">
        
        <mat-toolbar color="primary" class="sidenav-header">
          <mat-icon>analytics</mat-icon>
          <span class="toolbar-title">Log Management</span>
        </mat-toolbar>
        
        <mat-nav-list>
          <a mat-list-item routerLink="/dashboard" routerLinkActive="active-link">
            <mat-icon matListItemIcon>dashboard</mat-icon>
            <span matListItemTitle>Dashboard</span>
          </a>
          
          <a mat-list-item routerLink="/upload" routerLinkActive="active-link">
            <mat-icon matListItemIcon>cloud_upload</mat-icon>
            <span matListItemTitle>Upload Logs</span>
          </a>
          
          <a mat-list-item routerLink="/search" routerLinkActive="active-link">
            <mat-icon matListItemIcon>search</mat-icon>
            <span matListItemTitle>Recherche</span>
          </a>
          
          <a mat-list-item routerLink="/results" routerLinkActive="active-link">
            <mat-icon matListItemIcon>view_list</mat-icon>
            <span matListItemTitle>Résultats</span>
          </a>
          
          <a mat-list-item routerLink="/files" routerLinkActive="active-link">
            <mat-icon matListItemIcon>folder</mat-icon>
            <span matListItemTitle>Fichiers</span>
          </a>
          
          <mat-divider></mat-divider>
          
          <a mat-list-item href="http://localhost:5601" target="_blank">
            <mat-icon matListItemIcon>show_chart</mat-icon>
            <span matListItemTitle>Kibana</span>
          </a>
        </mat-nav-list>
      </mat-sidenav>
      
      <mat-sidenav-content>
        <mat-toolbar color="primary" class="top-toolbar">
          <button
            type="button"
            aria-label="Toggle sidenav"
            mat-icon-button
            (click)="drawer.toggle()"
            *ngIf="isHandset$ | async">
            <mat-icon>menu</mat-icon>
          </button>
          
          <span class="toolbar-title">Log Management System ECommerce</span>
          <span class="spacer"></span>
          
          <!-- User menu (if authenticated) -->
          <div *ngIf="currentUser$ | async as user" class="user-menu">
            <button mat-button [matMenuTriggerFor]="userMenu" class="user-button">
              <mat-icon>account_circle</mat-icon>
              <span class="username">{{ user.username }}</span>
              <span class="user-role" [class.admin]="user.role === 'ADMIN'" 
                                      [class.analyst]="user.role === 'ANALYST'">
                {{ user.role }}
              </span>
            </button>
            
            <mat-menu #userMenu="matMenu">
              <div class="user-info">
                <mat-icon>person</mat-icon>
                <div>
                  <div class="user-info-name">{{ user.username }}</div>
                  <div class="user-info-email">{{ user.email }}</div>
                </div>
              </div>
              
              <mat-divider></mat-divider>
              
              <button mat-menu-item routerLink="/profile">
                <mat-icon>account_box</mat-icon>
                <span>Profile</span>
              </button>
              
              <button mat-menu-item routerLink="/settings">
                <mat-icon>settings</mat-icon>
                <span>Settings</span>
              </button>
              
              <mat-divider></mat-divider>
              
              <button mat-menu-item (click)="logout()" class="logout-button">
                <mat-icon>logout</mat-icon>
                <span>Logout</span>
              </button>
            </mat-menu>
          </div>
          
          <!-- Login button (if not authenticated) -->
          <button mat-button *ngIf="!(currentUser$ | async)" routerLink="/login" class="login-link">
            <mat-icon>login</mat-icon>
            <span>Login</span>
          </button>
          
          <button mat-icon-button aria-label="Notifications">
            <mat-icon>notifications</mat-icon>
          </button>
        </mat-toolbar>
        
        <div class="main-content">
          <router-outlet></router-outlet>
        </div>
        
        <footer class="footer">
          <div class="footer-content">
            <div class="footer-section">
              <h3>Log Management System </h3>
              <p>Système de gestion et d'analyse de logs avec ELK Stack</p>
            </div>
            
            <div class="footer-section">
              <h4>Technologies</h4>
              <ul>
                <li>Angular 17 + Material UI</li>
                <li>Flask REST API</li>
                <li>Elasticsearch + Logstash + Kibana</li>
                <li>MongoDB + Redis</li>
              </ul>
            </div>
            
            <div class="footer-section">
              <h4>Projet</h4>
              <p>Développé dans le cadre du cours Big Data</p>
              <p>Année universitaire 2024-2025</p>
            </div>
          </div>
          
          <div class="footer-bottom">
            <p>&copy; 2025 Log Management System - Tous droits réservés</p>
          </div>
        </footer>
      </mat-sidenav-content>
    </mat-sidenav-container>
  `,
  styles: [`
    /* Container pour la page login isolée */
    .login-page-container {
      width: 100vw;
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      position: fixed;
      top: 0;
      left: 0;
      z-index: 1000;
    }

    .sidenav-container {
      height: 100%;
      background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
    }

    .sidenav {
      width: 280px;
      background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
      border-right: 1px solid rgba(0, 0, 0, 0.06);
      box-shadow: 4px 0 15px rgba(0, 0, 0, 0.05);
    }

    .sidenav-header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 24px 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      font-size: 20px;
      font-weight: 700;
      letter-spacing: 0.5px;
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
      
      mat-icon {
        font-size: 28px !important;
        width: 28px !important;
        height: 28px !important;
        line-height: 28px !important;
        display: inline-flex;
        align-items: center;
        justify-content: center;
      }
    }

    .top-toolbar {
      position: sticky;
      top: 0;
      z-index: 10;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
      box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .toolbar-title {
      font-size: 20px;
      font-weight: 700;
      letter-spacing: 0.5px;
      text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .spacer {
      flex: 1 1 auto;
    }

    mat-nav-list {
      padding: 12px 8px;
      
      a[mat-list-item] {
        margin: 4px 0;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-weight: 500;
        color: #4a5568;
        
        &:hover {
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
          transform: translateX(4px);
          
          mat-icon {
            transform: scale(1.1);
          }
        }
        
        mat-icon {
          transition: transform 0.3s ease;
        }
      }
    }

    .main-content {
      min-height: calc(100vh - 200px);
      padding: 32px;
      animation: fadeInUp 0.6s ease;
      
      @media (max-width: 768px) {
        padding: 16px;
      }
    }

    .active-link {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
      color: white !important;
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
      transform: translateX(4px);
      
      mat-icon {
        color: white !important;
      }
    }

    .footer {
      background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
      color: #e2e8f0;
      padding: 60px 32px 24px;
      margin-top: 60px;
      position: relative;
      overflow: hidden;
      
      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #667eea);
        background-size: 200% 100%;
        animation: shimmer 3s linear infinite;
      }
    }

    .footer-content {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 40px;
      max-width: 1200px;
      margin: 0 auto 40px;
    }

    .footer-section h3 {
      color: #fff;
      margin-bottom: 20px;
      font-size: 22px;
      font-weight: 700;
      letter-spacing: 0.5px;
      background: linear-gradient(135deg, #fff, #90caf9);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .footer-section h4 {
      color: #90caf9;
      margin-bottom: 16px;
      font-size: 18px;
      font-weight: 600;
      letter-spacing: 0.3px;
    }

    .footer-section p {
      line-height: 1.8;
      color: #cbd5e0;
      font-size: 14px;
    }

    .footer-section ul {
      list-style: none;
      padding: 0;
    }

    .footer-section li {
      padding: 8px 0;
      color: #cbd5e0;
      font-size: 14px;
      transition: all 0.3s ease;
      
      &:hover {
        color: #90caf9;
        transform: translateX(4px);
      }
      
      &::before {
        content: '▸';
        margin-right: 8px;
        color: #667eea;
      }
    }

    .footer-bottom {
      text-align: center;
      padding-top: 24px;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      color: #a0aec0;
      font-size: 14px;
    }

    @media (max-width: 768px) {
      .footer {
        padding: 40px 20px 20px;
      }
      
      .footer-content {
        grid-template-columns: 1fr;
        gap: 32px;
      }
    }
    
    /* User menu styles */
    .user-menu {
      margin-left: 16px;
    }
    
    .user-button {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 4px 12px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 24px;
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.2);
      }
      
      mat-icon {
        font-size: 24px;
        width: 24px;
        height: 24px;
      }
      
      .username {
        font-weight: 500;
        max-width: 120px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      
      .user-role {
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.2);
        font-weight: 600;
        
        &.admin {
          background: #f44336;
        }
        
        &.analyst {
          background: #ff9800;
        }
      }
    }
    
    .login-link {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-left: 16px;
    }
    
    ::ng-deep .mat-mdc-menu-content {
      padding: 0;
    }
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 16px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      
      mat-icon {
        font-size: 40px;
        width: 40px;
        height: 40px;
      }
      
      .user-info-name {
        font-weight: 600;
        font-size: 16px;
      }
      
      .user-info-email {
        font-size: 12px;
        opacity: 0.9;
      }
    }
    
    .logout-button {
      color: #f44336;
      
      mat-icon {
        color: #f44336;
      }
    }
    
    @keyframes fadeInUp {
      from {
        opacity: 0;
        transform: translateY(30px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    
    @keyframes shimmer {
      0% {
        background-position: -200% 0;
      }
      100% {
        background-position: 200% 0;
      }
    }
  `]
})
export class AppComponent implements OnInit {
  isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
    .pipe(
      map(result => result.matches),
      shareReplay()
    );
  
  currentUser$: Observable<User | null>;
  isLoginPage = false;
  
  constructor(
    private breakpointObserver: BreakpointObserver,
    private authService: AuthService,
    private router: Router
  ) {
    this.currentUser$ = this.authService.currentUser$;
    
    // Détecter les changements de route pour savoir si on est sur /login
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.isLoginPage = event.url === '/login' || event.url.startsWith('/login?');
    });
    
    // Vérifier la route initiale
    this.isLoginPage = this.router.url === '/login' || this.router.url.startsWith('/login?');
  }
  
  ngOnInit(): void {
    // L'utilisateur est déjà chargé depuis localStorage dans le constructeur du service
    // L'interceptor gérera les erreurs d'authentification (401/403) lors des prochaines requêtes
    // Pas besoin de vérifier le token ici pour éviter une déconnexion inutile au rafraîchissement
  }
  
  logout(): void {
    this.authService.logout();
  }
}
