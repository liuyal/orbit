import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from '../loader/loader.component';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { EmptyStateComponent } from '../empty-state/empty.state.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { ActivatedRoute, Router } from '@angular/router';
import { TestCyclesService, TestCycleExecution } from '../../services/tm.cycles.service';
import { TmExecutionDetailComponent } from '../tm-execution/tm.execution.detail.component';

@Component({
  selector: 'app-tm-cycles-execution',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    LoaderComponent,
    EmptyStateComponent,
    ErrorStateComponent,
    TmExecutionDetailComponent,
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
  sortMode: 'status' | 'folder' | 'default' = 'status';
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

  setSortMode(mode: 'status' | 'folder'): void {
    this.sortMode = mode;
  }

  get groupedExecutions(): { label: string; color?: string; executions: TestCycleExecution[] }[] {
    const data = this.executionDataSource.data;
    if (this.sortMode === 'folder') {
      const map = new Map<string, TestCycleExecution[]>();
      for (const exec of data) {
        const key = exec.folder ?? 'No Folder';
        if (!map.has(key)) map.set(key, []);
        map.get(key)!.push(exec);
      }
      return Array.from(map.entries()).map(([label, executions]) => ({ label, executions }));
    }
    const map = new Map<string, TestCycleExecution[]>();
    for (const exec of data) {
      const key = exec.result ?? 'NOT_EXECUTED';
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(exec);
    }
    return Array.from(map.entries()).map(([label, executions]) => ({
      label,
      color: this.getResultColor(label),
      executions
    }));
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

