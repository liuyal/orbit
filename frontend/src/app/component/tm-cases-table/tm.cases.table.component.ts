import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from '../loader/loader.component';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { EmptyStateComponent } from '../empty-state/empty.state.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { StatusBadgeComponent } from '../status-badge/status.badge.component';
import { Router } from '@angular/router';
import { TestCasesService, TestCases } from '../../services/tm.cases.service';

@Component({
  selector: 'app-tm-cases-table',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    LoaderComponent,
    EmptyStateComponent,
    ErrorStateComponent,
    StatusBadgeComponent
  ],
  styleUrls: ['./tm.cases.table.component.css'],
  templateUrl: './tm.cases.table.component.html'
})

export class TmCasesTableComponent implements OnInit {
  cdr = inject(ChangeDetectorRef);
  router = inject(Router);
  displayedColumns = ['KEY', 'DESCRIPTION', '# TESTS', '# CYCLES', 'STATUS'];
  testCasesDataSource: MatTableDataSource<TestCases>;
  isLoading = false;
  error = '';

  constructor(
    private testCasesService: TestCasesService
  ) {
    this.testCasesDataSource = new MatTableDataSource<TestCases>([]);
  }

  loadTestCases() {
    this.isLoading = true;
    this.error = '';

    this.testCasesService.getTestCasesbyProjectKey('Key').subscribe({
      next: (response) => {
        this.testCasesDataSource.data = Array.isArray(response) ? response : [];
        console.log('Test cases data loaded:', this.testCasesDataSource.data);
        this.isLoading = false;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error fetching test cases data:', error);
        this.error = `Error fetching test cases data: ${error.message || error}`;
        this.isLoading = false;
        this.cdr.markForCheck();
      }
    });
  }

  ngOnInit(): void {
    this.loadTestCases();
  }
}

