import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from '../loader/loader.component';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { EmptyStateComponent } from '../empty-state/empty.state.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { StatusBadgeComponent } from '../status-badge/status.badge.component';
import { ActivatedRoute, Router } from '@angular/router';
import { TestCyclesService, TestCycles } from '../../services/tm.cycles.service';

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
  cyclesDataSource: MatTableDataSource<TestCycles>;
  isLoading = false;
  error = '';
  projectKey = '';
  displayedColumns = ['KEY', 'TITLE', 'PROGRESS', 'STATUS'];

  constructor(
    private testCyclesService: TestCyclesService
  ) {
    this.cyclesDataSource = new MatTableDataSource<TestCycles>([]);
  }

  loadTestCycles() {
    this.isLoading = true;
    this.error = '';

    this.testCyclesService.getTestCyclesbyProjectKey(this.projectKey).subscribe({
      next: (response) => {
        this.cyclesDataSource.data = Array.isArray(response) ? response : [];
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

