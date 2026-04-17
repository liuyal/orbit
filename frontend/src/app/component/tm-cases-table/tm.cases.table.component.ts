import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from '../loader/loader.component';
import { ActivatedRoute, Router } from '@angular/router';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { EmptyStateComponent } from '../empty-state/empty.state.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { StatusBadgeComponent } from '../status-badge/status.badge.component';
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
  route = inject(ActivatedRoute);
  testCasesDataSource: MatTableDataSource<TestCases>;
  isLoading = false;
  error = '';
  projectKey = '';
  displayedColumns = ['KEY', 'TITLE', 'STATUS', 'FREQUENCY', 'LABELS','RESULT'];

  constructor(
    private testCasesService: TestCasesService
  ) {
    this.testCasesDataSource = new MatTableDataSource<TestCases>([]);
  }

  loadTestCases() {
    this.isLoading = true;
    this.error = '';
    this.testCasesService.getTestCasesbyProjectKey(this.projectKey).subscribe({
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
    this.route.params.subscribe(params => {
      this.projectKey = params['projectKey'];
      console.log('Test cases tab for project:', this.projectKey);
      this.loadTestCases();
    });
  }

  sortLabels(labels: any[]): any[] {
    if (!labels) return [];
    return [...labels].sort((a, b) => String(a).localeCompare(String(b)));
  }
}

