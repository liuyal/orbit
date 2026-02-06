import { Component, Input, OnInit, ChangeDetectorRef, AfterViewInit, OnDestroy, ViewChild, ElementRef, PLATFORM_ID, inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { createCodeMirrorEditor } from '../test_cases/codemirror-config';
import type { EditorView } from 'codemirror';

@Component({
  selector: 'test-cycle-execution',
  standalone: true,
  imports: [CommonModule, FormsModule],
  styleUrls: ['./test_cycle_execution.css'],
  templateUrl: './test_cycle_execution.html'
})
export class TestCycleExecutionComponent implements OnInit, AfterViewInit, OnDestroy {
  @Input() testCycle: any;
  @Input() projectKey: string = '';
  @Input() testCycleKey: string = '';

  http = inject(HttpClient);
  cdr = inject(ChangeDetectorRef);
  platformId = inject(PLATFORM_ID);

  loading: boolean = false;
  apiError: string = '';

  @ViewChild('scriptEditorContainer', { static: false }) scriptEditorContainer?: ElementRef<HTMLDivElement>;
  private isBrowser = false;

  selectedExecution: any = null;

  ngOnInit() {
    this.isBrowser = isPlatformBrowser(this.platformId);
  }

  ngAfterViewInit() {
    // nothing by default; editor will be initialized when an execution is selected
  }

  ngOnDestroy() {
    // Dispose CodeMirror editor if present
  }

  selectExecution(execution: any) {
    console.log('Selected execution:', execution);

    this.selectedExecution = execution;
    this.cdr.detectChanges();

    // Fetch both test case data and execution data from backend
    this.loadTestCaseAndExecutionData(execution.test_case_key);
  }

  loadTestCaseAndExecutionData(testCaseKey: string) {
    console.log('Loading test case and execution data for:', testCaseKey);

    // Fetch test case data
    const testCaseUrl = `/api/tm/projects/${this.projectKey}/test-cases/${testCaseKey}`;
    const testCaseRequest = this.http.get<any>(testCaseUrl);

    // Fetch execution data
    const executionUrl = `/api/tm/cycles/${this.testCycleKey}/executions/${testCaseKey}`;
    const executionRequest = this.http.get<any>(executionUrl);

    // Wait for both requests to complete
    testCaseRequest.subscribe({
      next: (testCaseData) => {
        console.log('Test case data loaded:', testCaseData);
        if (this.selectedExecution) {
          // Populate test case fields
          this.selectedExecution.title = testCaseData.title || '';
          this.selectedExecution.description = testCaseData.description || '';
          this.selectedExecution.test_script = testCaseData.test_script || '';
          this.selectedExecution.folder = testCaseData.folder || '';
          this.selectedExecution.status = testCaseData.status || '';
          this.selectedExecution.priority = testCaseData.priority || '';

          this.cdr.detectChanges();
        }
      },
      error: (err) => {
        console.error('Error loading test case data:', err);
      }
    });

    executionRequest.subscribe({
      next: (executionData) => {
        console.log('Execution data loaded:', executionData);
        if (this.selectedExecution) {
          // Populate execution-specific fields
          this.selectedExecution.result = executionData.result || 'NOT_EXECUTED';
          this.selectedExecution.comment = executionData.comment || '';
          this.selectedExecution.executed_by = executionData.executed_by;
          this.selectedExecution.executed_at = executionData.executed_at;
          this.cdr.detectChanges();
        }
      },
      error: (err) => {
        console.error('Error loading execution data:', err);
      }
    });
  }

  addTestCase() {
    // TODO: Implement add test case to cycle functionality
    console.log('Add test case to cycle');
  }

  loadTestCycle() {
    if (!this.testCycleKey) {
      console.warn('No testCycleKey provided to loadTestCycle()');
      return;
    }

    this.loading = true;
    const url = `/api/tm/cycles/${this.testCycleKey}`;
    console.log('Loading test cycle from URL:', url);

    // Safety timeout to prevent infinite loading
    const timeout = setTimeout(() => {
      if (this.loading) {
        console.warn('Request timeout - forcing error state');
        this.apiError = 'Request timed out. Please try again.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    }, 10000);

    this.http.get<any>(url).subscribe({
      next: (data) => {
        clearTimeout(timeout);
        console.log('Test cycle loaded in execution component:', data);
        try {
          this.testCycle.test_cycle_key = data.test_cycle_key || '';
          this.testCycle.title = data.title || '';
          this.testCycle.description = data.description || '';
          this.testCycle.executions = data.executions || [];
          console.log('Test cycle data set on child component');
        } catch (error) {
          console.error('Error processing test cycle data in child:', error);
          this.apiError = 'Error processing test cycle data';
        } finally {
          this.loading = false;
          this.cdr.detectChanges();
        }
      },
      error: (err) => {
        clearTimeout(timeout);
        console.error('Error loading test cycle in child component:', err);
        this.apiError = `Failed to load test cycle: ${err.status} ${err.statusText || err.message}`;
        this.loading = false;
        this.cdr.detectChanges();
      },
      complete: () => {
        clearTimeout(timeout);
        console.log('Child component request completed');
      }
    });
  }
}
