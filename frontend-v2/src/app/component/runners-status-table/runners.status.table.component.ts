import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-runners-status-table',
  standalone: true,
  imports: [
    CommonModule
  ],
  styleUrls: ['./runners.status.table.component.css'],
  templateUrl: './runners.status.table.component.html'
})

export class RunnersStatusTableComponent implements OnInit, OnDestroy {

  loadRunners(): void {
    console.log('loadRunners called');
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
}

