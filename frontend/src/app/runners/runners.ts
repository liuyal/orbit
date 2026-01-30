import { Component, inject, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { NavbarComponent } from '../navbar/navbar';
import { Subscription, timeout, catchError, of } from 'rxjs';

@Component({
  selector: 'app-runners',
  standalone: true,
  imports: [CommonModule, NavbarComponent],
  styleUrls: ['./runners.css'],
  templateUrl: './runners.html'
})

export class Runners implements OnInit, OnDestroy {
  http = inject(HttpClient);
  cdr = inject(ChangeDetectorRef);
  runners: any[] = [];
  isLoading = true;
  showSpinner = false;
  error = '';
  private subscription?: Subscription;
  private spinnerTimeout?: any;

  ngOnInit(): void {
    console.log('ngOnInit called');
    this.loadRunners();
  }

  ngOnDestroy(): void {
    console.log('ngOnDestroy called');
    this.subscription?.unsubscribe();
    if (this.spinnerTimeout) {
      clearTimeout(this.spinnerTimeout);
    }
  }

  loadRunners(): void {
    console.log('loadRunners called');
    this.isLoading = true;
    this.showSpinner = false;
    this.error = '';
    this.runners = [];
    
    // Clear any existing timeout
    if (this.spinnerTimeout) {
      clearTimeout(this.spinnerTimeout);
    }
    
    // Show spinner after 5 seconds
    this.spinnerTimeout = setTimeout(() => {
      this.showSpinner = true;
      this.cdr.markForCheck();
    }, 5000);
    
    this.subscription?.unsubscribe();
    
    this.subscription = this.http.get<any[]>('/api/runners/status').pipe(
      timeout(10000),
      catchError(error => {
        console.error('HTTP error caught:', error);
        this.isLoading = false;
        this.error = 'Request timeout or error';
        this.cdr.markForCheck();
        return of([]);
      })
    ).subscribe({
      next: (response) => {
        console.log('Runners response received:', response?.length || 0);
        if (this.spinnerTimeout) {
          clearTimeout(this.spinnerTimeout);
        }
        this.runners = Array.isArray(response) ? response : [];
        // Sort runners by name alpha-numerically
        this.runners.sort((a, b) => {
          const nameA = (a.name || '').toLowerCase();
          const nameB = (b.name || '').toLowerCase();
          return nameA.localeCompare(nameB, undefined, { numeric: true, sensitivity: 'base' });
        });
        this.isLoading = false;
        this.showSpinner = false;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error in subscribe:', error);
        if (this.spinnerTimeout) {
          clearTimeout(this.spinnerTimeout);
        }
        this.error = `Failed to load runners: ${error.name || error.message}`;
        this.isLoading = false;
        this.showSpinner = false;
        this.cdr.markForCheck();
      },
      complete: () => {
        console.log('HTTP request completed');
      }
    });
  }
}
