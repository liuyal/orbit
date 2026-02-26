import { Component, inject, ChangeDetectorRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { NavbarComponent } from '../../navbar/navbar';

export interface TestCycle {
  _id: string;
  test_cycle_key: string;
  project_key: string;
  title: string | null;
  description: string | null;
  created_at: string;
  updated_at: string | null;
  status: string | null;
  executions: any[] | null;
}

@Component({
  selector: 'test-cycles',
  standalone: true,
  imports: [CommonModule, NavbarComponent],
  styleUrls: ['./test_cycles.css'],
  templateUrl: './test_cycles.html'
})

export class TestCycles implements OnInit {
  route = inject(ActivatedRoute);
  router = inject(Router);
  http = inject(HttpClient);
  cdr = inject(ChangeDetectorRef);
  projectKey = '';
  testCycles: TestCycle[] = [];
  loading = false;
  error = '';

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.projectKey = params['projectKey'];
      console.log('Test Cycles page for project:', this.projectKey);
      this.loadTestCycles();
    });
  }

  loadTestCycles() {
    this.loading = true;
    this.error = '';
    console.log('Loading test cycles for project:', this.projectKey);
    console.log('API URL:', `/api/tm/projects/${this.projectKey}/cycles`);
    
    // Safety timeout to prevent infinite loading
    const timeout = setTimeout(() => {
      if (this.loading) {
        console.warn('Request timeout - forcing error state');
        this.error = 'Request timed out. Please try again.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    }, 10000); // 10 second timeout
    
    this.http.get<TestCycle[]>(`/api/tm/projects/${this.projectKey}/cycles`)
      .subscribe({
        next: (data) => {
          clearTimeout(timeout);
          console.log('Test cycles received:', data);
          console.log('Number of test cycles:', data?.length);
          this.testCycles = data;
          this.loading = false;
          this.error = '';
          this.cdr.detectChanges();
          console.log('Loading set to false, testCycles:', this.testCycles);
        },
        error: (err) => {
          clearTimeout(timeout);
          console.error('Error loading test cycles:', err);
          console.log('Setting error state and clearing loading');
          this.testCycles = [];
          this.error = 'Failed to load test cycles. Please try again.';
          this.loading = false;
          this.cdr.detectChanges();
          console.log('Error state set, loading:', this.loading, 'error:', this.error);
        },
        complete: () => {
          clearTimeout(timeout);
          console.log('Request completed');
        }
      });
  }

  goBack() {
    this.router.navigate(['/projects']);
  }

  createTestCycle() {
    this.router.navigate(['/test-cycles', this.projectKey, 'create']);
  }

  navigateToTestCases() {
    this.router.navigate(['/test-cases', this.projectKey]);
  }

  editTestCycle(testCycle: TestCycle) {
    this.router.navigate(['/test-cycles', this.projectKey, 'cycle', testCycle.test_cycle_key]);
  }

  deleteTestCycle(testCycle: TestCycle) {
    if (confirm(`Are you sure you want to delete test cycle ${testCycle.test_cycle_key}?`)) {
      console.log('Delete test cycle:', testCycle);
      this.http.delete(`/api/tm/cycles/${testCycle.test_cycle_key}`)
        .subscribe({
          next: () => {
            console.log('Test cycle deleted successfully');
            this.loadTestCycles();
            this.cdr.detectChanges();
          },
          error: (err) => {
            console.error('Error deleting test cycle:', err);
            alert('Failed to delete test cycle. Please try again.');
          }
        });
    }
  }
}
