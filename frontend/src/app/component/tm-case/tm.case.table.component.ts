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
  styleUrls: ['./tm.case.table.component.css'],
  templateUrl: './tm.case.table.component.html'
})

export class TmCasesTableComponent implements OnInit {
  cdr = inject(ChangeDetectorRef);
  router = inject(Router);
  route = inject(ActivatedRoute);
  testCasesDataSource: MatTableDataSource<TestCases>;
  isLoading = false;
  error = '';
  projectKey = '';
  displayedColumns = ['KEY', 'TITLE', 'FREQUENCY', 'LABELS', 'RESULT', 'STATUS'];

  pageSize = 20;
  pageIndex = 0;
  readonly pageSizeOptions = [20, 50, 100];

  constructor(
    private testCasesService: TestCasesService
  ) {
    this.testCasesDataSource = new MatTableDataSource<TestCases>([]);
  }

  get totalItems(): number {
    return this.testCasesDataSource.data.length;
  }

  get pagedTestCases(): TestCases[] {
    const start = this.pageIndex * this.pageSize;
    return this.testCasesDataSource.data.slice(start, start + this.pageSize);
  }

  get rangeStart(): number {
    return this.totalItems === 0 ? 0 : this.pageIndex * this.pageSize + 1;
  }

  get rangeEnd(): number {
    return Math.min(this.totalItems, (this.pageIndex + 1) * this.pageSize);
  }

  get hasPreviousPage(): boolean {
    return this.pageIndex > 0;
  }

  get hasNextPage(): boolean {
    return this.rangeEnd < this.totalItems;
  }

  goToFirstPage(): void {
    if (this.hasPreviousPage) this.pageIndex = 0;
  }

  goToPreviousPage(): void {
    if (this.hasPreviousPage) this.pageIndex--;
  }

  goToNextPage(): void {
    if (this.hasNextPage) this.pageIndex++;
  }

  goToLastPage(): void {
    this.pageIndex = Math.max(0, Math.ceil(this.totalItems / this.pageSize) - 1);
  }

  onPageSizeChange(size: number): void {
    this.pageSize = size;
    this.pageIndex = 0;
  }

  loadTestCases() {
    this.isLoading = true;
    this.error = '';
    this.testCasesService.getTestCasesbyProjectKey(this.projectKey).subscribe({
      next: (response) => {
        this.testCasesDataSource.data = Array.isArray(response) ? response : [];
        this.pageIndex = 0;
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

  onCaseClick(event: MouseEvent, caseKey: string) {
    if (event.button === 1) {
      // Middle mouse button
      event.preventDefault();
      if (event.type === 'mousedown') {
        const url = this.router.serializeUrl(this.router.createUrlTree(['/projects', this.projectKey, 'case', caseKey]));
        window.open(url, '_blank');
      }
    } else if (event.button === 0 && event.type === 'click') {
      // Left mouse button
      this.router.navigate(['/projects', this.projectKey, 'case', caseKey]);
    }
  }
}

