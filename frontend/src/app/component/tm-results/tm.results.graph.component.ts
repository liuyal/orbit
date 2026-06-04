import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { LoaderComponent } from '../loader/loader.component';
import { EmptyStateComponent } from '../empty-state/empty.state.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { TestCyclesService, TestCycles } from '../../services/tm.cycles.service';
import { computeProgressSummaries, ProgressSegment } from '../tm-cycle/tm.cycle.table.component';

@Component({
  selector: 'app-tm-results-graph',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    LoaderComponent,
    EmptyStateComponent,
    ErrorStateComponent,

  ],
  styleUrls: ['./tm.results.graph.component.css'],
  templateUrl: './tm.results.graph.component.html'
})

export class TmResultsGraphComponent implements OnInit {
  cdr = inject(ChangeDetectorRef);
  router = inject(Router);
  route = inject(ActivatedRoute);
  cyclesDataSource: MatTableDataSource<TestCycles>;
  progressSummaries: Record<string, ProgressSegment[]> = {};
  projectKey = '';
  showGraph = false;
  isLoading = false;
  error = '';

  constructor(
    private testCyclesService: TestCyclesService
  ) {
    this.cyclesDataSource = new MatTableDataSource<TestCycles>([]);
  }

  loadTestCycles(): void {
    this.isLoading = true;
    this.error = '';

    this.testCyclesService.getTestCyclesbyProjectKey(this.projectKey).subscribe({
      next: (response) => {
        this.cyclesDataSource.data = Array.isArray(response) ? response : [];
        this.progressSummaries = computeProgressSummaries(this.cyclesDataSource.data);
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
}

