import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from '../loader/loader.component';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { EmptyStateComponent } from '../empty-state/empty.state.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { ActivatedRoute, Router } from '@angular/router';
import { TestCyclesService, TestCycleExecution } from '../../services/tm.cycles.service';

@Component({
  selector: 'app-tm-cycles-execution',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    LoaderComponent,
    EmptyStateComponent,
    ErrorStateComponent,
  ],
  styleUrls: ['./tm.cycle.execution.component.css'],
  templateUrl: './tm.cycle.execution.component.html'
})

export class TmCyclesExecutionComponent implements OnInit {
  cdr = inject(ChangeDetectorRef);
  router = inject(Router);
  route = inject(ActivatedRoute);
  executionDataSource: MatTableDataSource<TestCycleExecution>;
  selectedExecution: TestCycleExecution | null = null;
  isLoading = false;
  error = '';

  private readonly resultColors: Record<string, string> = {
    PASS: '#4caf50',
    FAIL: '#f44336',
    BLOCKED: '#2196f3',
    NOT_EXECUTED: '#757575',
    IN_PROGRESS: '#ffd700',
  };

  constructor(
    private testCyclesService: TestCyclesService
  ) {
    this.executionDataSource = new MatTableDataSource<TestCycleExecution>([]);
  }

  getResultColor(result: string): string {
    return this.resultColors[result?.toUpperCase()] ?? '#757575';
  }

  selectExecution(execution: TestCycleExecution): void {
    this.selectedExecution = execution;
  }

  loadTestExecutions() {
    this.isLoading = true;
    this.error = '';
    this.testCyclesService.getCycleExecutionInfo(this.route.snapshot.paramMap.get('cycleKey') || '').subscribe({
      next: (data) => {
        this.executionDataSource.data = Object.values(data);
        this.selectedExecution = this.executionDataSource.data[0] ?? null;
        this.isLoading = false;
        this.cdr.markForCheck();
        console.log('Test cycles execution data loaded:', this.executionDataSource.data);
      },
      error: (err) => {
        this.error = 'Failed to load test executions';
        this.isLoading = false;
        this.cdr.markForCheck();
        console.error('Error loading test cycles execution data:', err);
      }
    });
  }

  ngOnInit(): void {
    this.loadTestExecutions();
  }
}

