import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from '../loader/loader.component';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { EmptyStateComponent } from '../empty-state/empty.state.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { StatusBadgeComponent } from '../status-badge/status.badge.component';
import { ActivatedRoute, Router } from '@angular/router';
import { TestCyclesService } from '../../services/tm.cycles.service';

@Component({
  selector: 'app-tm-cycles-execution',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    LoaderComponent,
    EmptyStateComponent,
    ErrorStateComponent,
    // StatusBadgeComponent
  ],
  styleUrls: ['./tm.cycle.execution.component.css'],
  templateUrl: './tm.cycle.execution.component.html'
})

export class TmCyclesExecutionComponent implements OnInit {
  cdr = inject(ChangeDetectorRef);
  router = inject(Router);
  route = inject(ActivatedRoute);
  executionDataSource: MatTableDataSource<object>;
  isLoading = false;
  error = '';

  constructor(
    private testCyclesService: TestCyclesService
  ) {
    this.executionDataSource = new MatTableDataSource<object>([]);
  }

  loadTestExecutions() {
    this.isLoading = true;
    this.error = '';
    this.testCyclesService.getCycleExecutionInfo(this.route.snapshot.paramMap.get('cycleKey') || '').subscribe({
      next: (data) => {
        this.executionDataSource.data = Array.isArray(data) ? data : Object.values(data as object);
        this.isLoading = false;
        this.cdr.markForCheck();
        console.log('Test cycles execution data loaded:', this.executionDataSource.data);
      },
      error: (err) => {
        this.error = 'Failed to load test executions';
        this.isLoading = false;
        console.error('Error loading test cycles execution data:', err);
      }
    });
  }

  ngOnInit(): void {
    this.loadTestExecutions();
  }
}

