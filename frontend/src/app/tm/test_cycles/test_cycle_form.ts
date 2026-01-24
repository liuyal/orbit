import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../navbar/navbar';

export interface TestCycleForm {
  test_cycle_key: string;
  title: string;
  description: string;
  status: string;
  executions: any[];
}

@Component({
  selector: 'test-cycle-form',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  styleUrls: ['./test_cycle_form.css'],
  templateUrl: './test_cycle_form.html'
})

export class TestCycleFormComponent implements OnInit {
  route = inject(ActivatedRoute);
  router = inject(Router);
  http = inject(HttpClient);
  cdr = inject(ChangeDetectorRef);
  
  projectKey = '';
  testCycleKey = '';
  isEditMode = false;
  loading = false;
  activeTab: 'details' | 'executions' = 'details';
  
  testCycle: TestCycleForm = {
    test_cycle_key: '',
    title: '',
    description: '',
    status: 'DRAFT',
    executions: []
  };
  
  apiError = '';
  errors = {
    test_cycle_key: '',
    title: ''
  };

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.projectKey = params['projectKey'];
      this.testCycleKey = params['testCycleKey'];
      this.isEditMode = !!this.testCycleKey;
      
      if (this.isEditMode) {
        console.log('Edit mode - test cycle:', this.testCycleKey, 'for project:', this.projectKey);
        this.loadTestCycle();
      } else {
        console.log('Create mode - project:', this.projectKey);
      }
    });
  }

  onTabChange(tab: 'details' | 'executions') {
    this.activeTab = tab;
  }

  loadTestCycle() {
    this.loading = true;
    const url = `/api/tm/projects/${this.projectKey}/cycles/${this.testCycleKey}`;
    console.log('Loading test cycle from URL:', url);
    
    this.http.get<any>(url).subscribe({
      next: (data) => {
        console.log('Test cycle loaded:', data);
        try {
          this.testCycle.test_cycle_key = data.test_cycle_key || '';
          this.testCycle.title = data.title || '';
          this.testCycle.description = data.description || '';
          this.testCycle.status = data.status || 'DRAFT';
          this.testCycle.executions = data.executions || [];
          console.log('Test cycle data processed successfully');
        } catch (error) {
          console.error('Error processing test cycle data:', error);
          this.apiError = 'Error processing test cycle data';
        } finally {
          this.loading = false;
          this.cdr.detectChanges();
        }
      },
      error: (err) => {
        console.error('Error loading test cycle:', err);
        this.apiError = `Failed to load test cycle: ${err.status} ${err.statusText || err.message}`;
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  goBack() {
    this.router.navigate(['/test-cycles', this.projectKey]);
  }

  cancel() {
    this.router.navigate(['/test-cycles', this.projectKey]);
  }

  validateForm(): boolean {
    this.errors = {
      test_cycle_key: '',
      title: ''
    };
    return true;
  }

  submitTestCycle() {
    if (!this.validateForm()) {
      console.log('Validation failed');
      return;
    }

    this.apiError = '';
    console.log(this.isEditMode ? 'Updating test cycle:' : 'Creating test cycle:', this.testCycle);
    
    const payload: any = {
      title: this.testCycle.title,
      description: this.testCycle.description,
      status: this.testCycle.status,
      executions: this.testCycle.executions
    };

    // For create mode, include project_key and optional test_cycle_key
    if (!this.isEditMode) {
      payload.project_key = this.projectKey;
      if (this.testCycle.test_cycle_key && this.testCycle.test_cycle_key.trim()) {
        payload.test_cycle_key = this.testCycle.test_cycle_key;
      }
    }

    // Use POST for create, PUT for edit
    const request = this.isEditMode
      ? this.http.put(`/api/tm/projects/${this.projectKey}/cycles/${this.testCycleKey}`, payload)
      : this.http.post(`/api/tm/projects/${this.projectKey}/cycles`, payload);

    request.subscribe({
      next: (response) => {
        console.log(`Test cycle ${this.isEditMode ? 'updated' : 'created'} successfully:`, response);
        this.router.navigate(['/test-cycles', this.projectKey]);
      },
      error: (error) => {
        console.error(`Error ${this.isEditMode ? 'updating' : 'creating'} test cycle:`, error);
        let errorMessage = `Failed to ${this.isEditMode ? 'update' : 'create'} test cycle. Please try again.`;
        if (error.error) {
          if (typeof error.error === 'string') {
            errorMessage = error.error;
          } else if (typeof error.error === 'object') {
            errorMessage = error.error.message
              || error.error.detail
              || error.error.error
              || JSON.stringify(error.error);
          }
        }
        this.apiError = errorMessage;
      }
    });
  }
}
