import { Component, inject, ChangeDetectorRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { NavbarComponent } from '../../navbar/navbar';

export interface TestCase {
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

export interface Folder {
  name: string;
  count: number;
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
  testCases: TestCase[] = [];
  filteredTestCases: TestCase[] = [];
  folders: Folder[] = [];
  selectedFolder: string | null = null;
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
    
    // Safety timeout to prevent infinite loading
    const timeout = setTimeout(() => {
      if (this.loading) {
        console.warn('Request timeout - forcing error state');
        this.error = 'Request timed out. Please try again.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    }, 10000); // 10 second timeout
    
    this.http.get<TestCase[]>(`/api/tm/projects/${this.projectKey}/test-cases`)
      .subscribe({
        next: (data) => {
          clearTimeout(timeout);
          console.log('Test cases received:', data);
          console.log('Number of test cases:', data?.length);
          this.testCases = data;
          this.updateFolders();
          this.applyFilter();
          this.loading = false;
          this.error = '';
          this.cdr.detectChanges();
          console.log('Loading set to false, testCases:', this.testCases);
        },
        error: (err) => {
          clearTimeout(timeout);
          console.error('Error loading test cases:', err);
          console.log('Setting error state and clearing loading');
          this.testCases = [];
          this.error = 'Failed to load test cases. Please try again.';
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

  editTestCase(testCase: TestCase) {
    this.router.navigate([
      '/test-cases',
      this.projectKey,
      'edit',
      testCase.test_case_key
    ], {
      queryParams: { loadExecutions: 'true' }
    });
  }

  createTestCase() {
    this.router.navigate(['/test-cases', this.projectKey, 'create']);
  }

  navigateToTestCycles() {
    this.router.navigate(['/test-cycles', this.projectKey]);
  }

  deleteTestCase(testCase: TestCase) {
    if (confirm(`Are you sure you want to delete test case ${testCase.test_case_key}?`)) {
      console.log('Delete test case:', testCase);
      this.http.delete(`/api/tm/projects/${this.projectKey}/test-cases/${testCase.test_case_key}`)
        .subscribe({
          next: () => {
            console.log('Test case deleted successfully');
            this.loadTestCases();
            this.cdr.detectChanges();
          },
          error: (err) => {
            console.error('Error deleting test case:', err);
            alert('Failed to delete test case. Please try again.');
          }
        });
    }
  }

  updateFolders() {
    const folderMap = new Map<string, number>();
    
    this.testCases.forEach(tc => {
      if (tc.folder) {
        folderMap.set(tc.folder, (folderMap.get(tc.folder) || 0) + 1);
      }
    });

    this.folders = Array.from(folderMap.entries())
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }

  selectFolder(folderName: string | null) {
    this.selectedFolder = folderName;
    this.applyFilter();
    this.cdr.detectChanges();
  }

  applyFilter() {
    if (this.selectedFolder === null) {
      this.filteredTestCases = [...this.testCases];
    } else {
      this.filteredTestCases = this.testCases.filter(tc => 
        tc.folder === this.selectedFolder
      );
    }
  }

  deleteFolder(folderName: string) {
    const hasTestCases = this.testCases.some(tc => 
      tc.folder === folderName
    );
    
    if (hasTestCases) {
      alert('Cannot delete folder with test cases. Please move or delete test cases first.');
      return;
    }

    if (confirm(`Delete folder "${folderName}"?`)) {
      this.folders = this.folders.filter(f => f.name !== folderName);
      if (this.selectedFolder === folderName) {
        this.selectFolder(null);
      }
      this.cdr.detectChanges();
    }
  }
}