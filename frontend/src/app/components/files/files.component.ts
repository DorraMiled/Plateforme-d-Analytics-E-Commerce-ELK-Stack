import { Component, OnInit, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog, MatDialogModule, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Router, RouterModule } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { FileInfo } from '../../models/log.models';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-files',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTableModule, MatIconModule, MatButtonModule, MatProgressSpinnerModule, MatSnackBarModule, MatDialogModule, MatTooltipModule, RouterModule],
  templateUrl: './files.component.html',
  styleUrls: ['./files.component.scss']
})
export class FilesComponent implements OnInit {
  files: FileInfo[] = [];
  loading = true;

  constructor(
    private apiService: ApiService, 
    private router: Router,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    private authService: AuthService
  ) {}

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

  getTotalSize(): string {
    const totalBytes = this.files.reduce((sum, file) => sum + file.size, 0);
    return this.formatFileSize(totalBytes);
  }

  getFileTypes(): number {
    const uniqueTypes = new Set(this.files.map(file => file.type));
    return uniqueTypes.size;
  }

  canDelete(): boolean {
    return this.authService.hasAnyRole(['ADMIN', 'ANALYST']);
  }

  deleteFile(file: FileInfo) {
    const dialogRef = this.dialog.open(ConfirmDeleteDialog, {
      width: '400px',
      data: { filename: file.filename }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.apiService.deleteFile(file.filename).subscribe({
          next: () => {
            this.snackBar.open('Fichier supprimé avec succès', 'Fermer', { duration: 3000 });
            this.loadFiles();
          },
          error: (err) => {
            this.snackBar.open('Erreur lors de la suppression: ' + (err.error?.error || 'Erreur inconnue'), 'Fermer', { duration: 5000 });
          }
        });
      }
    });
  }
}

@Component({
  selector: 'confirm-delete-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule, MatIconModule],
  template: `
    <h2 mat-dialog-title>Confirmer la suppression</h2>
    <mat-dialog-content>
      <p>Êtes-vous sûr de vouloir supprimer le fichier <strong>{{ data.filename }}</strong> ?</p>
      <p style="color: #f44336; margin-top: 16px;">
        <mat-icon style="vertical-align: middle; margin-right: 8px;">warning</mat-icon>
        Cette action est irréversible.
      </p>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button [mat-dialog-close]="false">Annuler</button>
      <button mat-raised-button color="warn" [mat-dialog-close]="true">Supprimer</button>
    </mat-dialog-actions>
  `
})
export class ConfirmDeleteDialog {
  constructor(@Inject(MAT_DIALOG_DATA) public data: { filename: string }) {}
}
