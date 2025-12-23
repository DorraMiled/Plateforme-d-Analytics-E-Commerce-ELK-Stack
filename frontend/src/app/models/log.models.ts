// Log Models
export interface LogEntry {
  _id: string;
  timestamp: string;
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  service: string;
  message: string;
  customer_name?: string;
  product_name?: string;
  country?: string;
  total_amount?: number;
  [key: string]: any;
}

export interface SearchFilters {
  query?: string;
  level?: string;
  service?: string;
  startDate?: Date;
  endDate?: Date;
}

export interface SearchResult {
  total: number;
  hits: LogEntry[];
  took: number;
}

export interface UploadResponse {
  message: string;
  filename: string;
  documents_indexed: number;
  file_size: number;
}

export interface FileInfo {
  filename: string;
  upload_time: string;
  size: number;
  type: string;
  documents_count?: number;
}

export interface SystemStats {
  elasticsearch: {
    status: string;
    documents_count: number;
    indices_count: number;
  };
  mongodb: {
    status: string;
    database: string;
    collections_count?: number;
  };
  redis: {
    status: string;
    keys_count: number;
  };
}

export interface DashboardStats {
  total_logs: number;
  logs_today: number;
  error_logs: number;
  files_uploaded: number;
  logs_by_level: { level: string; count: number }[];
  logs_by_service: { service: string; count: number }[];
  logs_over_time: { date: string; count: number }[];
  recent_logs: LogEntry[];
}
