import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from './navbar/navbar';

@Component({
  selector: 'test-case-create',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  styleUrls: ['./test_case_create.css'],
  templateUrl: './test_case_create.html'
})

export class TestCaseCreate implements OnInit {
  route = inject(ActivatedRoute);
  router = inject(Router);
  http = inject(HttpClient);
  projectKey = '';
  newTestCase = {
    test_case_key: '',
    title: '',
    description: '',
    status: 'Draft',
    priority: 'Medium'
  };
  apiError = '';
  errors = {
    test_case_key: '',
    title: ''
  };

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.projectKey = params['projectKey'];
      console.log('Create test case for project:', this.projectKey);
      // Pre-fill the project key prefix
      this.newTestCase.test_case_key = this.projectKey + '-';
    });
  }

  goBack() {
    this.router.navigate(['/test-cases', this.projectKey]);
  }

  cancel() {
    this.router.navigate(['/test-cases', this.projectKey]);
  }

  validateForm(): boolean {
    this.errors = {
      test_case_key: '',
      title: ''
    };

    let isValid = true;

    if (!this.newTestCase.test_case_key || this.newTestCase.test_case_key.trim() === '') {
      this.errors.test_case_key = 'Test case key cannot be empty';
      isValid = false;
    } else if (!this.newTestCase.test_case_key.startsWith(this.projectKey + '-')) {
      this.errors.test_case_key = `Test case key must start with ${this.projectKey}-`;
      isValid = false;
    }

    if (!this.newTestCase.title || this.newTestCase.title.trim() === '') {
      this.errors.title = 'Title cannot be empty';
      isValid = false;
    }

    return isValid;
  }

  submitTestCase() {
    if (!this.validateForm()) {
      console.log('Validation failed');
      return;
    }

    this.apiError = '';
    console.log('Submitting test case:', this.newTestCase);
    
    const payload = {
      ...this.newTestCase,
      project_key: this.projectKey
    };

    this.http.post(`/api/tm/projects/${this.projectKey}/test-cases`, payload).subscribe({
      next: (response) => {
        console.log('Test case created successfully:', response);
        this.router.navigate(['/test-cases', this.projectKey]);
      },
      error: (error) => {
        console.error('Error creating test case:', error);
        let errorMessage = 'Failed to create test case. Please try again.';
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
