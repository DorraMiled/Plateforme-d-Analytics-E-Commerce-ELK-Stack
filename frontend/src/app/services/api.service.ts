import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  LogEntry,
  SearchFilters,
  SearchResult,
  UploadResponse,
  FileInfo,
  SystemStats,
  DashboardStats
} from '../models/log.models';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * Get system statistics (Elasticsearch, MongoDB, Redis)
   */
  getStats(): Observable<SystemStats> {
    return this.http.get<SystemStats>(`${this.baseUrl}/stats`);
  }

  /**
   * Get dashboard statistics
   */
  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.baseUrl}/dashboard`);
  }

  /**
   * Upload log file (CSV, JSON, TXT)
   * Max size: 100MB
   */
  uploadFile(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<UploadResponse>(`${this.baseUrl}/upload`, formData, {
      reportProgress: true
    });
  }

  /**
   * Search logs with filters
   */
  searchLogs(filters: SearchFilters, size: number = 50, from: number = 0): Observable<SearchResult> {
    const body = {
      query: filters.query || '',
      level: filters.level || '',
      service: filters.service || '',
      start_date: filters.startDate ? filters.startDate.toISOString() : '',
      end_date: filters.endDate ? filters.endDate.toISOString() : '',
      size: size,
      from: from
    };
    
    return this.http.post<SearchResult>(`${this.baseUrl}/search`, body);
  }

  /**
   * Get analytics and aggregations
   */
  getResults(): Observable<any> {
    return this.http.get(`${this.baseUrl}/results`);
  }

  /**
   * Get list of uploaded files
   */
  getFiles(): Observable<FileInfo[]> {
    return this.http.get<FileInfo[]>(`${this.baseUrl}/files`);
  }

  /**
   * Get log details by ID
   */
  getLogDetails(id: string): Observable<LogEntry> {
    return this.http.get<LogEntry>(`${this.baseUrl}/logs/${id}`);
  }

  /**
   * Export search results to CSV
   */
  exportToCSV(filters: SearchFilters): Observable<Blob> {
    let params = new HttpParams();

    if (filters.query) params = params.set('q', filters.query);
    if (filters.level) params = params.set('level', filters.level);
    if (filters.service) params = params.set('service', filters.service);
    if (filters.startDate) params = params.set('start_date', filters.startDate.toISOString());
    if (filters.endDate) params = params.set('end_date', filters.endDate.toISOString());

    return this.http.get(`${this.baseUrl}/export/csv`, {
      params,
      responseType: 'blob'
    });
  }

  /**
   * Save search to history (MongoDB)
   */
  saveSearch(filters: SearchFilters): Observable<any> {
    return this.http.post(`${this.baseUrl}/searches/save`, filters);
  }

  /**
   * Get recent searches from MongoDB
   */
  getRecentSearches(limit: number = 10): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/searches/recent?limit=${limit}`);
  }

  /**
   * Health check endpoint
   */
  healthCheck(): Observable<any> {
    return this.http.get(`${this.baseUrl}/health`);
  }
}
