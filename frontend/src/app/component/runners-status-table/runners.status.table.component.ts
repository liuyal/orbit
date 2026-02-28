import { Component, inject, OnInit, AfterViewInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { RunnersStatusService, RunnerStatus } from '../../services/runners.status.service';
import { AutoRefreshService } from '../../services/auto-refresh.service';
import { Subscription } from 'rxjs/internal/Subscription';
import { interval } from 'rxjs/internal/observable/interval';
import { LoaderComponent } from '../loader/loader.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { EmptyStateComponent } from '../empty-state/empty.state.component';
import { UrlLinkComponent } from '../url-link/url.link';
import { StatusBadgeComponent } from '../status-badge/status.badge.component';

@Component({
  selector: 'app-runners-status-table',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatProgressSpinnerModule,
    LoaderComponent,
    ErrorStateComponent,
    EmptyStateComponent,
    UrlLinkComponent,
    StatusBadgeComponent
  ],
  styleUrls: ['./runners.status.table.component.css'],
  templateUrl: './runners.status.table.component.html'
})

export class RunnersStatusTableComponent implements OnInit, AfterViewInit, OnDestroy {
  private static readonly AUTO_REFRESH_INTERVAL_MS = 60 * 1000;
  private refreshSubscription?: Subscription;
  private spinnerTimeout?: any;
  cdr = inject(ChangeDetectorRef);
  runnersDataSource: MatTableDataSource<RunnerStatus>;
  displayedColumns = ['NAME', 'DESIGNATION', 'STATUS', 'BUSY', 'USER', 'JOB LINK'];
  runners: any[] = [];
  autoRefresh = false;
  isLoading = false;
  showSpinner = false;
  error = '';

  constructor(
    private runnerStatusServices: RunnersStatusService,
    private autoRefreshService: AutoRefreshService,
  ) {
    this.runnersDataSource = new MatTableDataSource<RunnerStatus>([]);
  }

  loadRunners(): void {
    this.isLoading = true;
    this.showSpinner = false;

    // Clear any existing timeout
    if (this.spinnerTimeout) {
      clearTimeout(this.spinnerTimeout);
    }
    this.spinnerTimeout = setTimeout(() => {
      this.showSpinner = true;
      this.cdr.markForCheck();
    }, 3000);

    this.runnerStatusServices.getRunners().subscribe({
      next: (response) => {
        this.runnersDataSource.data = Array.isArray(response) ? response : [];
        console.log('Runners data received:', this.runnersDataSource.data);
        this.isLoading = false;
        this.showSpinner = false;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error fetching runners data:', error);
        this.error = `Failed to load runners: ${error.error || 'API error'}`;
        this.isLoading = false;
        this.showSpinner = false;
        this.cdr.markForCheck();
      }
    });
  }

  private startAutoRefresh(): void {
    if (!this.refreshSubscription) {
      this.refreshSubscription = interval(RunnersStatusTableComponent.AUTO_REFRESH_INTERVAL_MS).subscribe(() => {
        this.loadRunners();
        this.cdr.markForCheck();
      });
    }
  }

  private stopAutoRefresh(): void {
    if (this.refreshSubscription) {
      this.refreshSubscription.unsubscribe();
      this.refreshSubscription = undefined;
    }
  }

  ngOnInit(): void {
    this.autoRefresh = this.autoRefreshService.getAutoRefreshState('runnersStatus');
    if (this.autoRefresh) {
      this.startAutoRefresh();
    }
    this.loadRunners();
  }

  ngAfterViewInit(): void {
    this.startAutoRefresh();
  }

  ngOnDestroy(): void {
    this.stopAutoRefresh();
    if (this.spinnerTimeout) {
      clearTimeout(this.spinnerTimeout);
    }
  }
}

