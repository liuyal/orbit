import { Component, inject, OnInit, ChangeDetectorRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../../navbar/navbar';
import { TestCycleExecutionComponent } from './test_cycle_execution';
import { ViewChild } from '@angular/core';

export interface TestCycleForm {
  test_cycle_key: string;
  title: string;
  description: string;
  executions: any[] | null;
}

@Component({
  selector: 'test-cycle-form',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent, TestCycleExecutionComponent],
  styleUrls: ['./test_cycle_form.css'],
  templateUrl: './test_cycle_form.html'
})

export class TestCycleFormComponent implements OnInit, AfterViewInit {
  @ViewChild(TestCycleExecutionComponent) executionComponent?: TestCycleExecutionComponent;
  
  route = inject(ActivatedRoute);
  router = inject(Router);
  http = inject(HttpClient);
  cdr = inject(ChangeDetectorRef);
  
  projectKey = '';
  testCycleKey = '';
  isEditMode = false;
  loading = false;
  activeTab: 'test-executions' | 'details' = 'details';
  
  testCycle: TestCycleForm = {
    test_cycle_key: '',
    title: '',
    description: '',
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
        this.activeTab = 'test-executions';
        // loadTestCycle moved to child component; will invoke after view init
      } else {
        console.log('Create mode - project:', this.projectKey);
        this.activeTab = 'details';
      }
    });
  }

  ngAfterViewInit() {
    if (this.isEditMode) {
      // ensure child is initialized then ask it to load the cycle
      setTimeout(() => {
        try {
          this.executionComponent?.loadTestCycle();
        } catch (err) {
          console.error('Failed to call executionComponent.loadTestCycle():', err);
        }
      }, 0);
    }
  }

  onTabChange(tab: 'test-executions' | 'details') {
    this.activeTab = tab;
  }

  // loadTestCycle moved to TestCycleExecutionComponent

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
      executions: this.testCycle.executions
    };

    // For create mode, include optional test_cycle_key (project_key comes from URL)
    if (!this.isEditMode) {
      if (this.testCycle.test_cycle_key && this.testCycle.test_cycle_key.trim()) {
        payload.test_cycle_key = this.testCycle.test_cycle_key;
      }
    }

    console.log('Payload being sent:', payload);

    // Use POST for create, PUT for edit
    const request = this.isEditMode
      ? this.http.put(`/api/tm/cycles/${this.testCycleKey}`, payload)
      : this.http.post(`/api/tm/projects/${this.projectKey}/cycles`, payload);

    request.subscribe({
      next: (response) => {
        console.log(`Test cycle ${this.isEditMode ? 'updated' : 'created'} successfully:`, response);
        this.router.navigate(['/test-cycles', this.projectKey]);
      },
      error: (error) => {
        console.error(`Error ${this.isEditMode ? 'updating' : 'creating'} test cycle:`, error);
        console.error('Full error object:', error);
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
        this.cdr.detectChanges();
      }
    });
  }
}
