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
  }

  ngOnInit(): void {
  }
}

