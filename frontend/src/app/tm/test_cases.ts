import { Component, inject, ChangeDetectorRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { NavbarComponent } from './navbar/navbar';

interface TestCase {
  _id: string;
  test_case_key: string;
  project_key: string;
  title: string | null;
  description: string | null;
  folder: string | null;
  created_at: string;
  updated_at: string | null;
  status: string | null;
  priority: string | null;
  test_script: string | null;
  test_script_type: string | null;
  last_result: string | null;
  last_execution_key: string | null;
  test_frequency: string[] | null;
  labels: string[] | null;
  links: string[] | null;
}

@Component({
  selector: 'test-cases',
  standalone: true,
  imports: [CommonModule, NavbarComponent],
  styleUrls: ['./test_cases.css'],
  templateUrl: './test_cases.html'
})

export class TestCases implements OnInit {
  route = inject(ActivatedRoute);
  router = inject(Router);
  http = inject(HttpClient);
  cdr = inject(ChangeDetectorRef);
  projectKey = '';
  activeTab: 'test-cases' | 'test-cycles' = 'test-cases';
  testCases: TestCase[] = [];
  loading = false;
  error = '';

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.projectKey = params['projectKey'];
      console.log('Test Cases page for project:', this.projectKey);
      this.loadTestCases();
    });
  }

  loadTestCases() {
    this.loading = true;
    this.error = '';
    console.log('Loading test cases for project:', this.projectKey);
    console.log('API URL:', `/api/tm/projects/${this.projectKey}/test-cases`);
    this.http.get<TestCase[]>(`/api/tm/projects/${this.projectKey}/test-cases`)
      .subscribe({
        next: (data) => {
          console.log('Test cases received:', data);
          console.log('Number of test cases:', data?.length);
          this.testCases = data;
          this.loading = false;
          this.cdr.detectChanges();
          console.log('Loading set to false, testCases:', this.testCases);
        },
        error: (err) => {
          this.error = 'Failed to load test cases. Please try again.';
          console.error('Error loading test cases:', err);
          this.loading = false;
          this.cdr.detectChanges();
        }
      });
  }

  goBack() {
    this.router.navigate(['/projects']);
  }
}