import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from '../loader/loader.component';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { EmptyStateComponent } from '../empty-state/empty.state.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { StatusBadgeComponent } from '../status-badge/status.badge.component';
import { ActivatedRoute, Router } from '@angular/router';
import { TestCyclesService, TestCycle } from '../../services/tm.cycles.service';
import { ProgressSegment, computeProgressSummaries } from './tm.cycle.progress.utils';

@Component({
  selector: 'app-tm-cycles-table',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    LoaderComponent,
    EmptyStateComponent,
    ErrorStateComponent,
    StatusBadgeComponent
  ],
  styleUrls: ['./tm.cycle.table.component.css'],
  templateUrl: './tm.cycle.table.component.html'
})

export class TmCyclesTableComponent implements OnInit {
  cdr = inject(ChangeDetectorRef);
  router = inject(Router);
  route = inject(ActivatedRoute);
  cyclesDataSource: MatTableDataSource<TestCycle>;
  isLoading = false;
  error = '';
  projectKey = '';
  displayedColumns = ['KEY', 'TITLE', 'PROGRESS', 'STATUS'];
  progressSummaries: Record<string, ProgressSegment[]> = {};
  tooltipVisible = false;
  tooltipPosition = { top: 0, left: 0 };
  activeTooltipSegments: ProgressSegment[] = [];

  constructor(
    private testCyclesService: TestCyclesService
  ) {
    this.cyclesDataSource = new MatTableDataSource<TestCycle>([]);
  }

  showProgressTooltip(event: MouseEvent, segments: ProgressSegment[]): void {
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
    this.activeTooltipSegments = segments;
    this.tooltipPosition = {
      top: rect.top + rect.height / 2,
      left: rect.right,
    };
    this.tooltipVisible = true;
  }

  hideProgressTooltip(): void {
    this.tooltipVisible = false;
  }

  private computeProgressSummaries(cycles: TestCycle[]): void {
    this.progressSummaries = computeProgressSummaries(cycles);
  }

  loadTestCycles() {
    this.isLoading = true;
    this.error = '';

    this.testCyclesService.getTestCyclesbyProjectKey(this.projectKey).subscribe({
      next: (response) => {
        this.cyclesDataSource.data = Array.isArray(response) ? response : [];
        this.computeProgressSummaries(this.cyclesDataSource.data);
        console.log('Test cycles data loaded:', this.cyclesDataSource.data);
        this.isLoading = false;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error fetching test cycles data:', error);
        this.error = `Error fetching test cycles data: ${error.message || error}`;
        this.isLoading = false;
        this.cdr.markForCheck();
      }
    });
  }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.projectKey = params['projectKey'];
      console.log('Test cycle tab for project:', this.projectKey);
      this.loadTestCycles();
    });
  }

  onCycleClick(event: MouseEvent, cycleKey: string) {
    if (event.button === 1) {
      // Middle mouse button
      event.preventDefault();
      if (event.type === 'mousedown') {
        const url = this.router.serializeUrl(this.router.createUrlTree(['/projects', this.projectKey, 'cycle', cycleKey]));
        window.open(url, '_blank');
      }
    } else if (event.button === 0 && event.type === 'click') {
      // Left mouse button
      this.router.navigate(['/projects', this.projectKey, 'cycle', cycleKey]);
    }
  }
}

