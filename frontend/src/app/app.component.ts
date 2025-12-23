import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { Observable } from 'rxjs';
import { map, shareReplay } from 'rxjs/operators';

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
    MatListModule
  ],
  template: `
    <mat-sidenav-container class="sidenav-container">
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
          
          <span class="toolbar-title">Log Management System</span>
          <span class="spacer"></span>
          
          <button mat-icon-button aria-label="Notifications">
            <mat-icon>notifications</mat-icon>
          </button>
          
          <button mat-icon-button aria-label="Settings">
            <mat-icon>settings</mat-icon>
          </button>
        </mat-toolbar>
        
        <div class="main-content">
          <router-outlet></router-outlet>
        </div>
        
        <footer class="footer">
          <div class="footer-content">
            <div class="footer-section">
              <h3>Log Management System</h3>
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
    .sidenav-container {
      height: 100%;
    }

    .sidenav {
      width: 260px;
      background-color: #fafafa;
    }

    .sidenav-header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 16px;
      font-size: 18px;
      font-weight: 500;
    }

    .top-toolbar {
      position: sticky;
      top: 0;
      z-index: 10;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .toolbar-title {
      font-size: 18px;
      font-weight: 500;
    }

    .spacer {
      flex: 1 1 auto;
    }

    .main-content {
      min-height: calc(100vh - 200px);
      padding: 20px;
      
      @media (max-width: 768px) {
        padding: 10px;
      }
    }

    .active-link {
      background-color: #e3f2fd;
      color: #1976d2;
    }

    .footer {
      background-color: #263238;
      color: #eceff1;
      padding: 40px 20px 20px;
      margin-top: 40px;
    }

    .footer-content {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 30px;
      max-width: 1200px;
      margin: 0 auto 30px;
    }

    .footer-section h3 {
      color: #fff;
      margin-bottom: 15px;
      font-size: 20px;
    }

    .footer-section h4 {
      color: #90caf9;
      margin-bottom: 10px;
      font-size: 16px;
    }

    .footer-section p {
      line-height: 1.6;
      color: #b0bec5;
    }

    .footer-section ul {
      list-style: none;
      padding: 0;
    }

    .footer-section li {
      padding: 5px 0;
      color: #b0bec5;
    }

    .footer-bottom {
      text-align: center;
      padding-top: 20px;
      border-top: 1px solid #37474f;
      color: #90a4ae;
    }

    @media (max-width: 768px) {
      .footer-content {
        grid-template-columns: 1fr;
        gap: 20px;
      }
    }
  `]
})
export class AppComponent {
  isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
    .pipe(
      map(result => result.matches),
      shareReplay()
    );

  constructor(private breakpointObserver: BreakpointObserver) {}
}
