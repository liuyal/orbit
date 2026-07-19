import { Component, Input, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { LoaderComponent } from '../loader/loader.component';
import { EmptyStateComponent } from '../empty-state/empty.state.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { StatusBadgeComponent } from '../status-badge/status.badge.component';
import { PaginationComponent } from '../pagination/pagination.component';
import { TestExecutionsService, TestExecutions } from '../../services/tm.executions.service';
import { formatDate } from '../../utils/date.utils';

@Component({
  selector: 'app-tm-case-executions-table',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    LoaderComponent,
    EmptyStateComponent,
    ErrorStateComponent,
    StatusBadgeComponent,
    PaginationComponent
  ],
  styleUrls: ['./tm.case.executions.table.component.css'],
  templateUrl: './tm.case.executions.table.component.html'
})
export class TmCaseExecutionsTableComponent implements OnInit {
  cdr = inject(ChangeDetectorRef);
  router = inject(Router);

  @Input() projectKey = '';
  @Input() caseKey = '';

  executionsDataSource: MatTableDataSource<TestExecutions>;
  isLoading = false;
  error = '';
  displayedColumns = ['KEY', 'CYCLE', 'STARTED', 'FINISHED', 'RESULT'];

  pageSize = 20;
  pageIndex = 0;
  readonly pageSizeOptions = [20, 50, 100];

  constructor(private testExecutionsService: TestExecutionsService) {
    this.executionsDataSource = new MatTableDataSource<TestExecutions>([]);
  }

  get totalItems(): number {
    return this.executionsDataSource.data.length;
  }

  get pagedExecutions(): TestExecutions[] {
    const start = this.pageIndex * this.pageSize;
    return this.executionsDataSource.data.slice(start, start + this.pageSize);
  }

  onPageSizeChange(size: number): void {
    this.pageSize = size;
    this.pageIndex = 0;
  }

  formatDate(dateStr: string | null): string {
    return formatDate(dateStr);
  }

  onExecutionClick(event: MouseEvent, executionKey: string) {
    if (event.button === 1) {
      // Middle mouse button
      event.preventDefault();
      if (event.type === 'mousedown') {
        const url = this.router.serializeUrl(this.router.createUrlTree(
          ['/projects', this.projectKey, 'case', this.caseKey, 'execution', executionKey])
        );
        window.open(url, '_blank');
      }
    } else if (event.button === 0 && event.type === 'click') {
      // Left mouse button
      this.router.navigate(['/projects', this.projectKey, 'case', this.caseKey, 'execution', executionKey]);
    }
  }

  loadExecutions(): void {
    if (!this.projectKey || !this.caseKey) return;
    this.isLoading = true;
    this.error = '';
    this.testExecutionsService.getTestExecutionsbyTestCase(this.projectKey, this.caseKey).subscribe({
      next: (response) => {
        const data = Array.isArray(response) ? response : [];
        data.sort((a, b) => b.execution_key.localeCompare(a.execution_key, undefined, { numeric: true, sensitivity: 'base' }));
        this.executionsDataSource.data = data;
        this.pageIndex = 0;
        this.isLoading = false;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error fetching test executions data:', error);
        this.error = `Error fetching test executions data: ${error.message || error}`;
        this.isLoading = false;
        this.cdr.markForCheck();
      }
    });
  }

  ngOnInit(): void {
    this.loadExecutions();
  }
}
