import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { FileInfo } from '../../models/log.models';

@Component({
  selector: 'app-files',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTableModule, MatIconModule, MatButtonModule, MatProgressSpinnerModule],
  template: `
    <div class="files-container">
      <div class="page-header">
        <h1><mat-icon>folder</mat-icon> Fichiers Uploadés</h1>
        <button mat-raised-button color="primary" (click)="refresh()" [disabled]="loading">
          <mat-icon>refresh</mat-icon> Actualiser
        </button>
      </div>

      <div *ngIf="loading" class="loading-container">
        <mat-spinner></mat-spinner>
        <p>Chargement des fichiers...</p>
      </div>

      <mat-card *ngIf="!loading && files.length === 0" class="no-files">
        <mat-icon>folder_open</mat-icon>
        <h2>Aucun fichier uploadé</h2>
        <button mat-raised-button color="primary" routerLink="/upload">
          <mat-icon>cloud_upload</mat-icon> Uploader un fichier
        </button>
      </mat-card>

      <mat-card *ngIf="!loading && files.length > 0">
        <mat-card-content>
          <div class="table-container">
            <table mat-table [dataSource]="files" class="full-width">
              <ng-container matColumnDef="filename">
                <th mat-header-cell *matHeaderCellDef>Fichier</th>
                <td mat-cell *matCellDef="let file">
                  <div style="display: flex; align-items: center; gap: 12px;">
                    <mat-icon color="primary">{{ getFileIcon(file.type) }}</mat-icon>
                    <span>{{ file.filename }}</span>
                  </div>
                </td>
              </ng-container>
              <ng-container matColumnDef="size">
                <th mat-header-cell *matHeaderCellDef>Taille</th>
                <td mat-cell *matCellDef="let file">{{ formatFileSize(file.size) }}</td>
              </ng-container>
              <ng-container matColumnDef="type">
                <th mat-header-cell *matHeaderCellDef>Type</th>
                <td mat-cell *matCellDef="let file">{{ file.type }}</td>
              </ng-container>
              <ng-container matColumnDef="upload_time">
                <th mat-header-cell *matHeaderCellDef>Date</th>
                <td mat-cell *matCellDef="let file">{{ file.upload_time | date:'dd/MM/yyyy HH:mm' }}</td>
              </ng-container>
              <tr mat-header-row *matHeaderRowDef="['filename', 'size', 'type', 'upload_time']"></tr>
              <tr mat-row *matRowDef="let row; columns: ['filename', 'size', 'type', 'upload_time'];"></tr>
            </table>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .files-container { max-width: 1200px; margin: 0 auto; }
    .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
    .page-header h1 { display: flex; align-items: center; gap: 12px; margin: 0; }
    .loading-container, .no-files { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; }
    .no-files mat-icon { font-size: 64px; width: 64px; height: 64px; color: #999; margin-bottom: 20px; }
    .table-container { overflow-x: auto; }
  `]
})
export class FilesComponent implements OnInit {
  files: FileInfo[] = [];
  loading = true;

  constructor(private apiService: ApiService, private router: Router) {}

  ngOnInit() {
    this.loadFiles();
  }

  loadFiles() {
    this.loading = true;
    this.apiService.getFiles().subscribe({
      next: (files) => { this.files = files; this.loading = false; },
      error: (err) => { console.error(err); this.loading = false; }
    });
  }

  refresh() {
    this.loadFiles();
  }

  formatFileSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  }

  getFileIcon(type: string): string {
    if (type && type.includes('csv')) return 'table_chart';
    if (type && type.includes('json')) return 'code';
    return 'description';
  }
}
