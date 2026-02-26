import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { RunnersStatusService, RunnerStatus } from '../../services/runners.status.service';
import { AutoRefreshService } from '../../services/auto-refresh.service';
import { Subscription } from 'rxjs/internal/Subscription';

@Component({
  selector: 'app-runners-status-table',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule
  ],
  styleUrls: ['./runners.status.table.component.css'],
  templateUrl: './runners.status.table.component.html'
})

export class RunnersStatusTableComponent implements OnInit, OnDestroy {

  private static readonly AUTO_REFRESH_INTERVAL_MS = 30000;
  private refreshSubscription?: Subscription;

  runnersDataSource: MatTableDataSource<RunnerStatus>;
  autoRefresh = false;
  isLoading = false;

  constructor(
    private runnerStatusServices: RunnersStatusService,
    private autoRefreshService: AutoRefreshService,
  ) {
    this.runnersDataSource = new MatTableDataSource<RunnerStatus>([]);
  }

  ngOnInit(): void {
    // Initialize auto-refresh state from service
    this.loadRunners();
  }

  ngAfterViewInit(): void {
    // Start auto-refresh if enabled
  }

  ngOnDestroy(): void {
    // Clean up any subscriptions or timers
  }

  loadRunners(): void {
    this.runnerStatusServices.getRunners().subscribe({
      next: (response) => {
        console.log('Runners data received:', response);
        this.runnersDataSource.data = response.runners;
      },
      error: (error) => {
        console.error('Error fetching runners data:', error);
      }
    });
  }
}

