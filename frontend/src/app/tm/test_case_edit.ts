import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from './navbar/navbar';
import { TestCase } from './test_cases';

interface TestCaseForm {
  test_case_key: string;
  title: string;
  description: string;
  test_script: string;
  folder: string;
  status: string;
  priority: string;
  test_frequency: string;
  labels: string;
  links: string;
}

@Component({
  selector: 'test-case-edit',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  styleUrls: ['./test_case_edit.css'],
  templateUrl: './test_case_edit.html'
})

export class TestCaseEdit implements OnInit {
  route = inject(ActivatedRoute);
  router = inject(Router);
  http = inject(HttpClient);
  cdr = inject(ChangeDetectorRef);
  projectKey = '';
  testCaseKey = '';
  loading = true;
  testCase: TestCaseForm = {
    test_case_key: '',
    title: '',
    description: '',
    test_script: '',
    folder: '',
    status: 'DRAFT',
    priority: 'MEDIUM',
    test_frequency: '',
    labels: '',
    links: ''
  };
  apiError = '';
  errors = {
    title: ''
  };

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.projectKey = params['projectKey'];
      this.testCaseKey = params['testCaseKey'];
      console.log('Edit test case:', this.testCaseKey, 'for project:', this.projectKey);
      this.loadTestCase();
    });
  }

  loadTestCase() {
    this.loading = true;
    const url = `/api/tm/projects/${this.projectKey}/test-cases/${this.testCaseKey}`;
    console.log('Loading test case from URL:', url);
    this.http.get<any>(url)
      .subscribe({
        next: (data) => {
          console.log('Test case loaded:', data);
          try {
            this.testCase.test_case_key = data.test_case_key || '';
            this.testCase.title = data.title || '';
            this.testCase.description = data.description || '';
            this.testCase.test_script = data.test_script || '';
            this.testCase.folder = data.folder || '';
            this.testCase.status = data.status || 'DRAFT';
            this.testCase.priority = data.priority || 'MEDIUM';
            this.testCase.test_frequency = (data.test_frequency && Array.isArray(data.test_frequency)) ? data.test_frequency.join(', ') : '';
            this.testCase.labels = (data.labels && Array.isArray(data.labels)) ? data.labels.join(', ') : '';
            this.testCase.links = (data.links && Array.isArray(data.links)) ? data.links.join(', ') : '';
            console.log('Test case data processed successfully');
          } catch (error) {
            console.error('Error processing test case data:', error);
            this.apiError = 'Error processing test case data';
          } finally {
            this.loading = false;
            this.cdr.detectChanges();
          }
        },
        error: (err) => {
          console.error('Error loading test case:', err);
          console.error('Error details:', JSON.stringify(err, null, 2));
          this.apiError = `Failed to load test case: ${err.status} ${err.statusText || err.message}`;
          this.loading = false;
        }
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
      title: ''
    };
    let isValid = true;
    return isValid;
  }

  submitTestCase() {
    if (!this.validateForm()) {
      console.log('Validation failed');
      return;
    }

    this.apiError = '';
    console.log('Updating test case:', this.testCase);
    
    const payload: any = {
      title: this.testCase.title,
      description: this.testCase.description,
      test_script: this.testCase.test_script,
      folder: this.testCase.folder,
      status: this.testCase.status,
      priority: this.testCase.priority
    };

    // Only include test_frequency, labels, and links if they have values
    if (this.testCase.test_frequency && this.testCase.test_frequency.trim()) {
      const freqArray = this.testCase.test_frequency.split(',').map(s => s.trim()).filter(s => s);
      if (freqArray.length > 0) {
        payload.test_frequency = freqArray;
      }
    }

    if (this.testCase.labels && this.testCase.labels.trim()) {
      const labelsArray = this.testCase.labels.split(',').map(s => s.trim()).filter(s => s);
      if (labelsArray.length > 0) {
        payload.labels = labelsArray;
      }
    }

    if (this.testCase.links && this.testCase.links.trim()) {
      const linksArray = this.testCase.links.split(',').map(s => s.trim()).filter(s => s);
      if (linksArray.length > 0) {
        payload.links = linksArray;
      }
    }

    this.http.put(`/api/tm/projects/${this.projectKey}/test-cases/${this.testCaseKey}`, payload).subscribe({
      next: (response) => {
        console.log('Test case updated successfully:', response);
        this.router.navigate(['/test-cases', this.projectKey]);
      },
      error: (error) => {
        console.error('Error updating test case:', error);
        let errorMessage = 'Failed to update test case. Please try again.';
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
