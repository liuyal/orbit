import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from '../../navbar/navbar';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'test-execution',
  standalone: true,
  imports: [CommonModule, NavbarComponent],
  templateUrl: './test_execution.html',
  styleUrls: ['./test_execution.css']
})

export class TestExecutionComponent implements OnInit {
  route = inject(ActivatedRoute);
  router = inject(Router);
  http = inject(HttpClient);
  cdr = inject(ChangeDetectorRef);

  executionKey: string = '';
  loading: boolean = false;
  showSpinner: boolean = false;
  apiError: string = '';
  execution: any = null;

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.executionKey = params['executionKey'];
      if (this.executionKey) {
        this.loadExecution();
      }
    });
  }

  loadExecution() {
    if (!this.executionKey) {
      this.apiError = 'Invalid execution key';
      return;
    }

    this.loading = true;
    this.showSpinner = false;
    this.apiError = '';
    const url = `/api/tm/executions/${this.executionKey}`;
    
    // Show spinner after 3 seconds if still loading
    const spinnerTimeoutId = setTimeout(() => {
      if (this.loading) {
        this.showSpinner = true;
        this.cdr.detectChanges();
      }
    }, 3000);
    
    const timeoutId = setTimeout(() => {
      if (this.loading) {
        this.apiError = 'Request timed out while loading execution';
        this.loading = false;
        this.showSpinner = false;
        clearTimeout(spinnerTimeoutId);
        this.cdr.detectChanges();
      }
    }, 10000);

    this.http.get<any>(url).subscribe({
      next: (data) => {
        clearTimeout(timeoutId);
        clearTimeout(spinnerTimeoutId);
        this.execution = data;
        this.loading = false;
        this.showSpinner = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        clearTimeout(timeoutId);
        clearTimeout(spinnerTimeoutId);
        this.apiError = `Failed to load execution: ${err.status} ${err.statusText || err.message}`;
        this.loading = false;
        this.showSpinner = false;
        this.cdr.detectChanges();
      }
    });
  }

  goBack() {
    // If execution has project_key, return to its test-cases list, otherwise fallback home
    const projectKey = this.execution?.project_key || '';
    if (projectKey) {
      this.router.navigate(['/test-cases', projectKey]);
    } else {
      this.router.navigate(['/']);
    }
  }
}
