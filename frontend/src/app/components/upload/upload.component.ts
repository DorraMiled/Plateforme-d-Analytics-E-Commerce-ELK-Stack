import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../services/api.service';
import { FileInfo, UploadResponse } from '../../models/log.models';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule,
    MatTableModule,
    MatChipsModule,
    MatSnackBarModule
  ],
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss']
})
export class UploadComponent {
  selectedFile: File | null = null;
  uploading = false;
  uploadProgress = 0;
  recentUploads: FileInfo[] = [];
  displayedColumns: string[] = ['filename', 'size', 'type', 'upload_time', 'documents'];

  // Validation
  maxFileSize = 100 * 1024 * 1024; // 100MB
  allowedFormats = ['csv', 'json', 'txt'];

  constructor(
    private apiService: ApiService,
    private snackBar: MatSnackBar
  ) {
    this.loadRecentUploads();
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    const dropZone = event.currentTarget as HTMLElement;
    dropZone.classList.add('dragover');
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    const dropZone = event.currentTarget as HTMLElement;
    dropZone.classList.remove('dragover');
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    const dropZone = event.currentTarget as HTMLElement;
    dropZone.classList.remove('dragover');

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.handleFile(files[0]);
    }
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.handleFile(file);
    }
  }

  handleFile(file: File) {
    // Validate file size
    if (file.size > this.maxFileSize) {
      this.showError(`Fichier trop volumineux. Maximum ${this.maxFileSize / (1024 * 1024)}MB`);
      return;
    }

    // Validate file format
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    if (!fileExtension || !this.allowedFormats.includes(fileExtension)) {
      this.showError(`Format non supporté. Formats acceptés: ${this.allowedFormats.join(', ').toUpperCase()}`);
      return;
    }

    this.selectedFile = file;
  }

  uploadFile() {
    if (!this.selectedFile) {
      this.showError('Aucun fichier sélectionné');
      return;
    }

    this.uploading = true;
    this.uploadProgress = 0;

    // Simulate progress (in real app, use HttpClient with reportProgress)
    const progressInterval = setInterval(() => {
      this.uploadProgress += 10;
      if (this.uploadProgress >= 90) {
        clearInterval(progressInterval);
      }
    }, 200);

    this.apiService.uploadFile(this.selectedFile).subscribe({
      next: (response: UploadResponse) => {
        clearInterval(progressInterval);
        this.uploadProgress = 100;
        
        setTimeout(() => {
          this.uploading = false;
          this.uploadProgress = 0;
          this.selectedFile = null;
          
          this.showSuccess(`✓ ${response.documents_indexed} documents indexés avec succès!`);
          this.loadRecentUploads();
          
          // Reset file input
          const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
          if (fileInput) fileInput.value = '';
        }, 500);
      },
      error: (err) => {
        clearInterval(progressInterval);
        this.uploading = false;
        this.uploadProgress = 0;
        this.showError(err.error?.error || 'Erreur lors de l\'upload');
        console.error('Upload error:', err);
      }
    });
  }

  loadRecentUploads() {
    this.apiService.getFiles().subscribe({
      next: (response: any) => {
        const files = response.files || [];
        this.recentUploads = Array.isArray(files) ? files.slice(0, 10) : [];
      },
      error: (err) => {
        console.error('Error loading files:', err);
      }
    });
  }

  formatFileSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  }

  getFileIcon(type: string): string {
    if (type.includes('csv')) return 'table_chart';
    if (type.includes('json')) return 'code';
    if (type.includes('text')) return 'description';
    return 'insert_drive_file';
  }

  clearFile() {
    this.selectedFile = null;
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) fileInput.value = '';
  }

  private showSuccess(message: string) {
    this.snackBar.open(message, 'Fermer', {
      duration: 5000,
      horizontalPosition: 'end',
      verticalPosition: 'top',
      panelClass: ['success-snackbar']
    });
  }

  private showError(message: string) {
    this.snackBar.open(message, 'Fermer', {
      duration: 5000,
      horizontalPosition: 'end',
      verticalPosition: 'top',
      panelClass: ['error-snackbar']
    });
  }
}
