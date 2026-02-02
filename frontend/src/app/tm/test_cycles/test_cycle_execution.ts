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
  
  @ViewChild('scriptEditorContainer', { static: false }) scriptEditorContainer?: ElementRef<HTMLDivElement>;
  private scriptEditor?: EditorView;
  private isBrowser = false;
  private editorInitializing = false;
  private editorDisposed = false;
  
  selectedExecution: any = null;

  ngOnInit() {
    this.isBrowser = isPlatformBrowser(this.platformId);
  }

  ngAfterViewInit() {
    // nothing by default; editor will be initialized when an execution is selected
  }

  ngOnDestroy() {
    this.editorDisposed = true;
    if (this.scriptEditor && this.selectedExecution) {
      try {
        this.selectedExecution.test_script = this.scriptEditor.state.doc.toString();
      } catch (e) {}
    }
    this.disposeScriptEditor();
  }

  selectExecution(execution: any) {
    // Save and dispose current editor value if present
    if (this.scriptEditor && this.selectedExecution) {
      try {
        this.selectedExecution.test_script = this.scriptEditor.state.doc.toString();
      } catch (e) {
        // ignore
      }
      this.disposeScriptEditor();
    }

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
          
          // Initialize editor after all data is loaded
          this.waitForEditorContainerAndInit();
        }
      },
      error: (err) => {
        console.error('Error loading execution data:', err);
        // Still initialize editor with test case data
        this.waitForEditorContainerAndInit();
      }
    });
  }

  private async waitForEditorContainerAndInit() {
    // Try multiple times to find the ViewChild after Angular renders it
    for (let attempt = 0; attempt < 10; attempt++) {
      await new Promise(resolve => setTimeout(resolve, 100));
      if (this.scriptEditorContainer) {
        console.log('Editor container found on attempt', attempt);
        this.initializeScriptEditor();
        return;
      }
      console.log('Waiting for editor container, attempt', attempt);
    }
    console.warn('Editor container never became available');
  }

  async initializeScriptEditor() {
    console.log('initializeScriptEditor called', { hasContainer: !!this.scriptEditorContainer, hasEditor: !!this.scriptEditor, initializing: this.editorInitializing, disposed: this.editorDisposed });
    if (!this.scriptEditorContainer || this.scriptEditor || this.editorInitializing || this.editorDisposed) return;
    this.editorInitializing = true;
    try {
      const container = this.scriptEditorContainer.nativeElement;
      this.cdr.detectChanges();
      // wait for container size
      let retries = 0;
      while ((container.offsetWidth === 0 || container.offsetHeight === 0) && retries < 5) {
        console.log('editor container has zero size, retry', { retries, offsetWidth: container.offsetWidth, offsetHeight: container.offsetHeight });
        await new Promise(r => setTimeout(r, 100));
        retries++;
      }
      if (container.offsetWidth === 0 || container.offsetHeight === 0) {
        console.warn('Editor container still has no dimensions after retries', { offsetWidth: container.offsetWidth, offsetHeight: container.offsetHeight });
        this.editorInitializing = false;
        return;
      }

      this.scriptEditor = createCodeMirrorEditor(
        container,
        this.selectedExecution?.test_script || '',
        (value: string) => {
          if (this.selectedExecution) this.selectedExecution.test_script = value;
        }
      );
      console.log('script editor initialized successfully');
    } catch (e) {
      console.warn('Failed to init script editor', e);
    } finally {
      this.editorInitializing = false;
    }
  }

  disposeScriptEditor() {
    if (this.scriptEditor) {
      try { this.scriptEditor.destroy(); } catch (e) {}
      this.scriptEditor = undefined;
    }
  }

  addTestCase() {
    // TODO: Implement add test case to cycle functionality
    console.log('Add test case to cycle');
  }
}
