import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatChipsModule } from '@angular/material/chips';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { SearchFilters } from '../../models/log.models';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatChipsModule
  ],
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss']
})
export class SearchComponent implements OnInit {
  searchForm: FormGroup;
  recentSearches: any[] = [];
  searching = false;

  logLevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'];
  services = ['web-api', 'database', 'auth-service', 'payment', 'notification'];

  constructor(
    private fb: FormBuilder,
    private apiService: ApiService,
    private router: Router
  ) {
    this.searchForm = this.fb.group({
      query: [''],
      level: [''],
      service: [''],
      startDate: [''],
      endDate: ['']
    });
  }

  ngOnInit() {
    this.loadRecentSearches();
  }

  onSearch() {
    const filters: SearchFilters = this.searchForm.value;
    
    this.searching = true;
    
    // Save search to history
    this.apiService.saveSearch(filters).subscribe({
      next: () => {
        this.loadRecentSearches();
      },
      error: (err) => console.error('Error saving search:', err)
    });

    // Navigate to results with filters
    this.router.navigate(['/results'], { queryParams: filters });
  }

  onReset() {
    this.searchForm.reset();
  }

  loadRecentSearches() {
    this.apiService.getRecentSearches(5).subscribe({
      next: (searches) => {
        this.recentSearches = searches;
      },
      error: (err) => console.error('Error loading recent searches:', err)
    });
  }

  applyRecentSearch(search: any) {
    this.searchForm.patchValue({
      query: search.query || '',
      level: search.level || '',
      service: search.service || '',
      startDate: search.start_date || null,
      endDate: search.end_date || null
    });
  }

  removeRecentSearch(search: any) {
    // Implement if backend supports deletion
  }
}
