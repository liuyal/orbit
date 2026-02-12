import { Component, inject, OnInit, ChangeDetectorRef, AfterViewInit, OnDestroy, ViewChild, ElementRef, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../../navbar/navbar';
import { createCodeMirrorEditor } from './codemirror-config';
import type { EditorView } from 'codemirror';

export interface TestCaseForm {
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
  selector: 'test-case-form',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  styleUrls: ['./test_case_form.css'],
  templateUrl: './test_case_form.html'
})

export class TestCaseFormComponent implements OnInit, AfterViewInit, OnDestroy {
  route = inject(ActivatedRoute);
  router = inject(Router);
  http = inject(HttpClient);
  cdr = inject(ChangeDetectorRef);
  platformId = inject(PLATFORM_ID);
  
  @ViewChild('editorContainer', { static: false }) editorContainer?: ElementRef<HTMLDivElement>;
  private editor?: EditorView;
  private isBrowser = false;
  private isEditorInitializing = false;
  private editorDisposed = false;
  
  projectKey = '';
  testCaseKey = '';
  isEditMode = false;
  loading = false;
  activeTab: 'details' | 'script' | 'links' | 'executions' = 'details';
  
  testCase: TestCaseForm = {
    test_case_key: '',
    title: '',
    description: '',
    test_script: '',
    folder: '',
    status: 'DRAFT',
    priority: 'MEDIUM',
    test_frequency: 'Nightly',
    labels: '',
    links: ''
  };

  // All available labels gathered from projects
  allLabels: string[] = [];
  // Currently selected labels for this test case
  selectedLabels: string[] = [];
  // (no dropdown state - using chip selection UI)
  
  apiError = '';
  errors = {
    test_case_key: '',
    title: ''
  };

  ngOnInit() {
    // Check if running in browser
    this.isBrowser = isPlatformBrowser(this.platformId);
    
    this.route.params.subscribe(params => {
      this.projectKey = params['projectKey'];
      this.testCaseKey = params['testCaseKey'];
      this.isEditMode = !!this.testCaseKey;
      
      if (this.isEditMode) {
        console.log('Edit mode - test case:', this.testCaseKey, 'for project:', this.projectKey);
        this.loadTestCase();
      } else {
        console.log('Create mode - project:', this.projectKey);
      }
    });

    // Load labels from projects so we can offer them in a select
    this.loadProjectLabels();
  }

  ngAfterViewInit() {
    // Initialize editor once - container now persists in DOM
    setTimeout(() => {
      if (this.editorContainer && !this.editor && !this.editorDisposed) {
        this.initializeEditor();
      }
    }, 100);
  }

  // No document click handler needed for chip UI

  ngOnDestroy() {
    // Mark as disposed to prevent any pending operations
    this.editorDisposed = true;
    
    // Save current value before disposing
    if (this.editor) {
      try {
        this.testCase.test_script = this.editor.state.doc.toString();
      } catch (e) {
        // Ignore errors during cleanup
      }
    }
    
    // Clean up editor
    this.disposeEditor();
  }

  async initializeEditor() {
    // Prevent multiple initializations
    if (!this.isBrowser || this.isEditorInitializing || this.editor || !this.editorContainer || this.editorDisposed) {
      console.log('Skipping editor init:', { isBrowser: this.isBrowser, isInit: this.isEditorInitializing, hasEditor: !!this.editor, hasContainer: !!this.editorContainer, disposed: this.editorDisposed });
      return;
    }

    this.isEditorInitializing = true;

    try {
      // Check again after async operations
      if (this.editorDisposed || this.editor || !this.editorContainer) {
        this.isEditorInitializing = false;
        return;
      }

      const container = this.editorContainer.nativeElement;
      
      // Verify container has dimensions with retry logic
      let retries = 0;
      while ((container.offsetWidth === 0 || container.offsetHeight === 0) && retries < 5) {
        await new Promise(resolve => setTimeout(resolve, 100));
        retries++;
      }
      
      if (container.offsetWidth === 0 || container.offsetHeight === 0) {
        console.warn('Editor container still has no dimensions after retries');
        this.isEditorInitializing = false;
        return;
      }
      
      // Final check before creating editor
      if (this.editorDisposed || this.editor || !this.editorContainer) {
        this.isEditorInitializing = false;
        return;
      }

      // Create CodeMirror editor
      this.editor = createCodeMirrorEditor(
        container,
        this.testCase.test_script || '',
        (value: string) => {
          this.testCase.test_script = value;
        }
      );

    } catch (error) {
      console.error('Failed to initialize CodeMirror Editor:', error);
    } finally {
      this.isEditorInitializing = false;
    }
  }

  disposeEditor() {
    if (this.editor) {
      try {
        this.editor.destroy();
      } catch (error) {
        console.warn('Error disposing editor:', error);
      }
      this.editor = undefined;
    }
    
    this.isEditorInitializing = false;
  }

  onTabChange(tab: 'details' | 'script' | 'links' | 'executions') {
    const previousTab = this.activeTab;
    
    // Save script value before changing tabs
    if (previousTab === 'script' && this.editor) {
      this.testCase.test_script = this.editor.state.doc.toString();
    }
    
    this.activeTab = tab;
    
    // If switching to script tab, ensure editor exists (CodeMirror handles layout automatically)
    if (tab === 'script' && !this.editor && !this.isEditorInitializing && this.editorContainer) {
      setTimeout(() => {
        this.initializeEditor();
      }, 50);
    }
  }

  loadTestCase() {
    this.loading = true;
    const url = `/api/tm/projects/${this.projectKey}/test-cases/${this.testCaseKey}`;
    console.log('Loading test case from URL:', url);
    
    this.http.get<any>(url).subscribe({
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
          this.selectedLabels = (data.labels && Array.isArray(data.labels)) ? [...data.labels] : [];
          // keep legacy string for compatibility
          this.testCase.labels = this.selectedLabels.join(', ');
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
        this.apiError = `Failed to load test case: ${err.status} ${err.statusText || err.message}`;
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  loadProjectLabels() {
    this.http.get<any[]>('/api/tm/projects').subscribe({
      next: (data) => {
        const labelSet = new Set<string>();
        for (const prj of data) {
          if (Array.isArray(prj.labels)) {
            prj.labels.forEach((l: string) => labelSet.add(l));
          }
        }
        this.allLabels = Array.from(labelSet).sort();
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.warn('Failed to load project labels:', err);
      }
    });
  }

  toggleLabel(label: string) {
    const idx = this.selectedLabels.indexOf(label);
    if (idx > -1) {
      this.selectedLabels.splice(idx, 1);
    } else {
      this.selectedLabels.push(label);
    }
    this.testCase.labels = this.selectedLabels.join(', ');
    this.cdr.detectChanges();
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
    return true;
  }

  submitTestCase() {
    if (!this.validateForm()) {
      console.log('Validation failed');
      return;
    }

    this.apiError = '';
    console.log(this.isEditMode ? 'Updating test case:' : 'Creating test case:', this.testCase);
    
    const payload: any = {
      title: this.testCase.title,
      description: this.testCase.description,
      test_script: this.testCase.test_script,
      folder: this.testCase.folder,
      status: this.testCase.status,
      priority: this.testCase.priority
    };

    // For create mode, include project_key and optional test_case_key
    if (!this.isEditMode) {
      payload.project_key = this.projectKey;
      if (this.testCase.test_case_key && this.testCase.test_case_key.trim()) {
        payload.test_case_key = this.testCase.test_case_key;
      }
    }

    // Only include test_frequency, labels, and links if they have values
    if (this.testCase.test_frequency && this.testCase.test_frequency.trim()) {
      const freqArray = this.testCase.test_frequency.split(',').map((s: string) => s.trim()).filter((s: string) => s);
      if (freqArray.length > 0) {
        payload.test_frequency = freqArray;
      }
    }

    if (this.selectedLabels && this.selectedLabels.length > 0) {
      payload.labels = [...this.selectedLabels];
    }

    if (this.testCase.links && this.testCase.links.trim()) {
      const linksArray = this.testCase.links.split(',').map((s: string) => s.trim()).filter((s: string) => s);
      if (linksArray.length > 0) {
        payload.links = linksArray;
      }
    }

    // Use POST for create, PUT for edit
    const request = this.isEditMode
      ? this.http.put(`/api/tm/projects/${this.projectKey}/test-cases/${this.testCaseKey}`, payload)
      : this.http.post(`/api/tm/projects/${this.projectKey}/test-cases`, payload);

    request.subscribe({
      next: (response) => {
        console.log(`Test case ${this.isEditMode ? 'updated' : 'created'} successfully:`, response);
        this.router.navigate(['/test-cases', this.projectKey]);
      },
      error: (error) => {
        console.error(`Error ${this.isEditMode ? 'updating' : 'creating'} test case:`, error);
        let errorMessage = `Failed to ${this.isEditMode ? 'update' : 'create'} test case. Please try again.`;
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

  removeSelectedLabel(label: string) {
    const idx = this.selectedLabels.indexOf(label);
    if (idx > -1) {
      this.selectedLabels.splice(idx, 1);
      this.testCase.labels = this.selectedLabels.join(', ');
    }
  }
}
