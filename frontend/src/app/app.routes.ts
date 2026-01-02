import { Routes } from '@angular/router';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { UploadComponent } from './components/upload/upload.component';
import { SearchComponent } from './components/search/search.component';
import { ResultsComponent } from './components/results/results.component';
import { FilesComponent } from './components/files/files.component';
import { LoginComponent } from './components/login/login.component';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { 
    path: '', 
    redirectTo: '/dashboard', 
    pathMatch: 'full' 
  },
  { 
    path: 'dashboard', 
    component: DashboardComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'upload', 
    component: UploadComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'search', 
    component: SearchComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'results', 
    component: ResultsComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'files', 
    component: FilesComponent,
    canActivate: [AuthGuard],
    data: { roles: ['ADMIN', 'ANALYST'] } // Exemple: seuls ADMIN et ANALYST peuvent accéder
  },
  { path: '**', redirectTo: '/dashboard' }
];
