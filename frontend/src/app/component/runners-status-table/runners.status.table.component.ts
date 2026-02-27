import { Component, inject, OnInit, AfterViewInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { RunnersStatusService, RunnerStatus } from '../../services/runners.status.service';
import { AutoRefreshService } from '../../services/auto-refresh.service';
import { Subscription } from 'rxjs/internal/Subscription';
import { interval } from 'rxjs/internal/observable/interval';

@Component({
  selector: 'app-runners-status-table',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatProgressSpinnerModule
  ],
  styleUrls: ['./runners.status.table.component.css'],
  templateUrl: './runners.status.table.component.html'
})

export class RunnersStatusTableComponent implements OnInit, AfterViewInit, OnDestroy {

  private static readonly AUTO_REFRESH_INTERVAL_MS = 60000;
  private refreshSubscription?: Subscription;

  runnersDataSource: MatTableDataSource<RunnerStatus>;
  displayedColumns = ['NAME', 'DESIGNATION', 'STATUS', 'BUSY', 'USER', 'JOB LINK'];

  autoRefresh = false;
  isLoading = false;
  showSpinner = false;

  runners: any[] = [];
  error = '';
  cdr = inject(ChangeDetectorRef);

  constructor(
    private runnerStatusServices: RunnersStatusService,
    private autoRefreshService: AutoRefreshService,
  ) {
    this.runnersDataSource = new MatTableDataSource<RunnerStatus>([]);
  }

  loadRunners(): void {
    this.isLoading = true;
    this.showSpinner = false;
    this.cdr.markForCheck();
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
  }

  ngOnDestroy(): void {
    this.stopAutoRefresh();
  }
}

