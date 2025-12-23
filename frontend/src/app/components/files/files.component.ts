import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Router, RouterModule } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { FileInfo } from '../../models/log.models';

@Component({
  selector: 'app-files',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTableModule, MatIconModule, MatButtonModule, MatProgressSpinnerModule, RouterModule],
  templateUrl: './files.component.html',
  styleUrls: ['./files.component.scss']
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

  getTotalSize(): string {
    const totalBytes = this.files.reduce((sum, file) => sum + file.size, 0);
    return this.formatFileSize(totalBytes);
  }

  getFileTypes(): number {
    const uniqueTypes = new Set(this.files.map(file => file.type));
    return uniqueTypes.size;
  }
}
