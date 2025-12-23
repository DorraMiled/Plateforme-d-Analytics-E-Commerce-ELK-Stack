import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatPaginatorModule, MatPaginator } from '@angular/material/paginator';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../services/api.service';
import { LogEntry, SearchFilters } from '../../models/log.models';

@Component({
  selector: 'app-results',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatDialogModule,
    MatSnackBarModule
  ],
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.scss']
})
export class ResultsComponent implements OnInit {
  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  dataSource: MatTableDataSource<LogEntry> = new MatTableDataSource<LogEntry>([]);
  displayedColumns: string[] = ['timestamp', 'level', 'service', 'message', 'actions'];
  
  totalResults = 0;
  loading = true;
  filters: SearchFilters = {};
  exporting = false;

  constructor(
    private apiService: ApiService,
    private route: ActivatedRoute,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.filters = {
        query: params['query'] || '',
        level: params['level'] || '',
        service: params['service'] || '',
        startDate: params['startDate'] ? new Date(params['startDate']) : undefined,
        endDate: params['endDate'] ? new Date(params['endDate']) : undefined
      };
      
      this.loadResults();
    });
  }

  loadResults() {
    this.loading = true;
    
    const pageSize = this.paginator?.pageSize || 50;
    const pageIndex = this.paginator?.pageIndex || 0;
    
    this.apiService.searchLogs(this.filters, pageSize, pageIndex * pageSize).subscribe({
      next: (results) => {
        this.dataSource.data = results.hits;
        this.totalResults = results.total;
        this.loading = false;
        
        // Setup paginator and sort after data is loaded
        setTimeout(() => {
          this.dataSource.paginator = this.paginator;
          this.dataSource.sort = this.sort;
        });
      },
      error: (err) => {
        this.loading = false;
        this.showError('Erreur lors du chargement des résultats');
        console.error('Results error:', err);
      }
    });
  }

  onPageChange() {
    this.loadResults();
  }

  getLevelClass(level: string): string {
    return `status-badge ${level.toLowerCase()}`;
  }

  viewDetails(log: LogEntry) {
    // Open dialog with log details
    const message = `
      ID: ${log._id}
      Timestamp: ${log.timestamp}
      Level: ${log.level}
      Service: ${log.service}
      Message: ${log.message}
      
      ${JSON.stringify(log, null, 2)}
    `;
    
    this.snackBar.open(message, 'Fermer', {
      duration: 10000,
      horizontalPosition: 'end',
      verticalPosition: 'top'
    });
  }

  exportToCSV() {
    this.exporting = true;
    
    this.apiService.exportToCSV(this.filters).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `logs_export_${new Date().getTime()}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
        
        this.exporting = false;
        this.showSuccess('Export CSV réussi!');
      },
      error: (err) => {
        this.exporting = false;
        this.showError('Erreur lors de l\'export CSV');
        console.error('Export error:', err);
      }
    });
  }

  private showSuccess(message: string) {
    this.snackBar.open(message, 'Fermer', {
      duration: 3000,
      panelClass: ['success-snackbar']
    });
  }

  private showError(message: string) {
    this.snackBar.open(message, 'Fermer', {
      duration: 5000,
      panelClass: ['error-snackbar']
    });
  }
}
