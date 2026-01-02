import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ApiService } from '../../services/api.service';
import { DashboardStats, LogEntry } from '../../models/log.models';
import { NgChartsModule } from 'ng2-charts';
import { Chart, ChartConfiguration, ChartType, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatTableModule,
    NgChartsModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  // @ViewChild(BaseChartDirective) chart?: BaseChartDirective;

  stats: DashboardStats | null = null;
  loading = true;
  error: string | null = null;

  displayedColumns: string[] = ['timestamp', 'level', 'service', 'message'];

  // Kibana Dashboard Integration
  kibanaDashboardUrl: SafeResourceUrl;
  kibanaBaseUrl = 'http://localhost:5601';
  kibanaDashboardId = '28c78c80-e733-11f0-981d-9db1c3ddaac0';

  // Chart.js Configuration
  public barChartType: ChartType = 'bar';
  public barChartData: ChartConfiguration['data'] = {
    labels: [],
    datasets: [
      {
        label: 'Logs par niveau',
        data: [],
        backgroundColor: [
          'rgba(33, 150, 243, 0.8)',
          'rgba(76, 175, 80, 0.8)',
          'rgba(255, 152, 0, 0.8)',
          'rgba(244, 67, 54, 0.8)',
          'rgba(156, 39, 176, 0.8)'
        ]
      }
    ]
  };

  public barChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      },
      title: {
        display: true,
        text: 'Distribution des logs par niveau'
      }
    }
  };

  public lineChartType: ChartType = 'line';
  public lineChartData: ChartConfiguration['data'] = {
    labels: [],
    datasets: [
      {
        label: 'Logs au fil du temps',
        data: [],
        fill: true,
        borderColor: 'rgb(63, 81, 181)',
        backgroundColor: 'rgba(63, 81, 181, 0.1)',
        tension: 0.4
      }
    ]
  };

  public lineChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      },
      title: {
        display: true,
        text: 'Évolution temporelle des logs'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  constructor(
    private apiService: ApiService,
    private sanitizer: DomSanitizer
  ) {
    // Créer l'URL sécurisée pour l'iframe Kibana
    const url = `${this.kibanaBaseUrl}/app/dashboards#/view/${this.kibanaDashboardId}?embed=true&_g=(refreshInterval:(pause:!t,value:60000),time:(from:now-30d%2Fd,to:now))&_a=()`;
    this.kibanaDashboardUrl = this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }

  ngOnInit() {
    this.loadDashboard();
    // Auto-refresh every 30 seconds
    setInterval(() => this.loadDashboard(), 30000);
  }

  loadDashboard() {
    this.loading = true;
    this.error = null;

    this.apiService.getDashboardStats().subscribe({
      next: (data) => {
        this.stats = data;
        this.updateCharts();
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Erreur lors du chargement des statistiques';
        this.loading = false;
        console.error('Dashboard error:', err);
      }
    });
  }

  updateCharts() {
    if (!this.stats) return;

    // Update bar chart (logs by level)
    if (this.stats.logs_by_level && this.stats.logs_by_level.length > 0) {
      this.barChartData.labels = this.stats.logs_by_level.map(item => item.level);
      this.barChartData.datasets[0].data = this.stats.logs_by_level.map(item => item.count);
    }

    // Update line chart (logs over time)
    if (this.stats.logs_over_time && this.stats.logs_over_time.length > 0) {
      this.lineChartData.labels = this.stats.logs_over_time.map(item => item.date);
      this.lineChartData.datasets[0].data = this.stats.logs_over_time.map(item => item.count);
    }
  }

  getLevelClass(level: string): string {
    return `status-badge ${level.toLowerCase()}`;
  }

  refresh() {
    this.loadDashboard();
  }
}
