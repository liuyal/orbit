import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from '../loader/loader.component';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { StatusBadgeComponent } from '../status-badge/status.badge.component';
import { ActivatedRoute, Router } from '@angular/router';
import { TestCyclesService, TestCycle } from '../../services/tm.cycles.service';
import { ProgressSegment, getProgressSummary as cycleProgress } from './tm.cycle.progress.utils';
import { formatDate } from '../../utils/date.utils';

@Component({
  selector: 'app-tm-cycles-details',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    LoaderComponent,
    ErrorStateComponent,
    StatusBadgeComponent
  ],
  styleUrls: ['./tm.cycle.details.component.css'],
  templateUrl: './tm.cycle.details.component.html'
})

export class TmCyclesDetailsComponent implements OnInit {
  cdr = inject(ChangeDetectorRef);
  router = inject(Router);
  route = inject(ActivatedRoute);
  cyclesDataSource: MatTableDataSource<TestCycle>;
  isLoading = false;
  error = '';
  cycleKey = '';

  constructor(
    private testCyclesService: TestCyclesService
  ) {
    this.cyclesDataSource = new MatTableDataSource<TestCycle>([]);
  }

  loadTestCycle() {
    this.isLoading = true;
    this.error = '';

    this.testCyclesService.getCycleInfo(this.cycleKey).subscribe({
      next: (response) => {
        this.cyclesDataSource.data = response ? [response] : [];
        console.log('Test cycle data loaded:', this.cyclesDataSource.data);
        this.isLoading = false;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error fetching test cycle data:', error);
        this.error = `Error fetching test cycle data: ${error.message || error}`;
        this.isLoading = false;
        this.cdr.markForCheck();
      }
    });
  }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.cycleKey = params['cycleKey'];
      console.log('Test cycle: ', this.cycleKey);
      this.loadTestCycle();
    });
  }

  formatDate(dateStr: string | null): string {
    return formatDate(dateStr);
  }

  getExecutionCount(cycle: TestCycle): number {
    return cycle.executions ? Object.keys(cycle.executions).length : 0;
  }

  getExecutionEntries(cycle: TestCycle): { key: string; value: string }[] {
    if (!cycle.executions) return [];
    return Object.entries(cycle.executions).map(([key, value]) => ({ key, value }));
  }

  getProgressSummary(cycle: TestCycle): ProgressSegment[] {
    return cycleProgress(cycle);
  }

}
