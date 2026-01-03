import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatChipsModule } from '@angular/material/chips';
import { LogEntry } from '../../models/log.models';

@Component({
  selector: 'app-log-details-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,
    MatChipsModule
  ],
  template: `
    <div class="dialog-header">
      <h2 mat-dialog-title>
        <mat-icon>info</mat-icon>
        Détails du Log
      </h2>
      <button mat-icon-button mat-dialog-close>
        <mat-icon>close</mat-icon>
      </button>
    </div>

    <mat-dialog-content>
      <!-- Main Information -->
      <div class="section">
        <h3 class="section-title">
          <mat-icon>article</mat-icon>
          Informations Principales
        </h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">ID</span>
            <span class="info-value monospace">{{ data._id }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Date/Heure</span>
            <span class="info-value">{{ data.timestamp | date:'dd/MM/yyyy à HH:mm:ss' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Niveau</span>
            <span class="info-value">
              <mat-chip [class]="getLevelClass(data.level)">
                {{ data.level }}
              </mat-chip>
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">Service</span>
            <span class="info-value">
              <mat-chip class="service-chip">{{ data.service }}</mat-chip>
            </span>
          </div>
        </div>
      </div>

      <mat-divider></mat-divider>

      <!-- Message -->
      <div class="section">
        <h3 class="section-title">
          <mat-icon>chat</mat-icon>
          Message
        </h3>
        <div class="message-box">
          {{ data.message }}
        </div>
      </div>

      <!-- Additional Fields -->
      <div class="section" *ngIf="hasAdditionalFields()">
        <mat-divider></mat-divider>
        <h3 class="section-title">
          <mat-icon>list_alt</mat-icon>
          Champs Additionnels
        </h3>
        <div class="info-grid">
          <div class="info-item" *ngFor="let field of getAdditionalFields()">
            <span class="info-label">{{ field.key }}</span>
            <span class="info-value" [class.monospace]="isMonospace(field.value)">
              {{ formatValue(field.value) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Raw Data -->
      <div class="section">
        <mat-divider></mat-divider>
        <h3 class="section-title">
          <mat-icon>code</mat-icon>
          Données Brutes (JSON)
        </h3>
        <pre class="json-box">{{ getJsonData() }}</pre>
      </div>
    </mat-dialog-content>

    <mat-dialog-actions align="end">
      <button mat-button (click)="copyToClipboard()">
        <mat-icon>content_copy</mat-icon>
        Copier JSON
      </button>
      <button mat-raised-button color="primary" mat-dialog-close>
        <mat-icon>check</mat-icon>
        Fermer
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .dialog-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 24px 0;
      
      h2 {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 0;
        font-size: 24px;
        color: #6200ea;
        
        mat-icon {
          font-size: 28px;
          width: 28px;
          height: 28px;
        }
      }
    }

    mat-dialog-content {
      min-width: 600px;
      max-width: 800px;
      padding: 24px;
    }

    .section {
      margin-bottom: 24px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }

    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 18px;
      font-weight: 500;
      margin: 0 0 16px 0;
      color: #6200ea;
      
      mat-icon {
        font-size: 22px;
        width: 22px;
        height: 22px;
      }
    }

    .info-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }

    .info-item {
      display: flex;
      flex-direction: column;
      gap: 6px;
      padding: 12px;
      background: #f5f5f5;
      border-radius: 8px;
      border-left: 3px solid #6200ea;
    }

    .info-label {
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      color: #666;
      letter-spacing: 0.5px;
    }

    .info-value {
      font-size: 14px;
      color: #333;
      word-break: break-word;
      
      &.monospace {
        font-family: 'Courier New', monospace;
        font-size: 13px;
      }
    }

    mat-chip {
      font-weight: 500;
      
      &.level-info {
        background-color: #2196f3;
        color: white;
      }
      
      &.level-warning {
        background-color: #ff9800;
        color: white;
      }
      
      &.level-error {
        background-color: #f44336;
        color: white;
      }
      
      &.level-debug {
        background-color: #9e9e9e;
        color: white;
      }
      
      &.service-chip {
        background-color: #6200ea;
        color: white;
      }
    }

    .message-box {
      padding: 16px;
      background: #f9f9f9;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      font-size: 14px;
      line-height: 1.6;
      color: #333;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .json-box {
      padding: 16px;
      background: #263238;
      color: #aed581;
      border-radius: 8px;
      overflow-x: auto;
      font-family: 'Courier New', monospace;
      font-size: 13px;
      line-height: 1.5;
      margin: 0;
      max-height: 400px;
      overflow-y: auto;
      
      &::-webkit-scrollbar {
        width: 8px;
        height: 8px;
      }
      
      &::-webkit-scrollbar-track {
        background: #1e272e;
        border-radius: 4px;
      }
      
      &::-webkit-scrollbar-thumb {
        background: #6200ea;
        border-radius: 4px;
        
        &:hover {
          background: #7c4dff;
        }
      }
    }

    mat-divider {
      margin: 24px 0;
    }

    mat-dialog-actions {
      padding: 16px 24px;
      
      button {
        mat-icon {
          margin-right: 8px;
        }
      }
    }
  `]
})
export class LogDetailsDialogComponent {
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: LogEntry,
    private dialogRef: MatDialogRef<LogDetailsDialogComponent>
  ) {}

  getLevelClass(level: string): string {
    return `level-${level.toLowerCase()}`;
  }

  hasAdditionalFields(): boolean {
    const standardFields = ['_id', '_index', '_score', 'timestamp', 'level', 'service', 'message'];
    return Object.keys(this.data).some(key => !standardFields.includes(key));
  }

  getAdditionalFields(): { key: string; value: any }[] {
    const standardFields = ['_id', '_index', '_score', 'timestamp', 'level', 'service', 'message'];
    return Object.keys(this.data)
      .filter(key => !standardFields.includes(key))
      .map(key => ({ key, value: (this.data as any)[key] }));
  }

  isMonospace(value: any): boolean {
    return typeof value === 'string' && (
      value.includes('/') || 
      value.includes('\\') || 
      value.includes('.') ||
      value.length > 50
    );
  }

  formatValue(value: any): string {
    if (value === null || value === undefined) {
      return 'N/A';
    }
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  }

  getJsonData(): string {
    return JSON.stringify(this.data, null, 2);
  }

  copyToClipboard(): void {
    navigator.clipboard.writeText(this.getJsonData()).then(() => {
      // Could add a snackbar notification here
      console.log('JSON copié dans le presse-papiers');
    });
  }
}
