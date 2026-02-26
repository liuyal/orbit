import { Component, Input, OnInit, ChangeDetectorRef, AfterViewInit, OnDestroy, ViewChild, ElementRef, PLATFORM_ID, inject, OnChanges, SimpleChanges } from '@angular/core';
import { Subscription } from 'rxjs';
import { isPlatformBrowser } from '@angular/common';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'test-cycle-execution',
  standalone: true,
  imports: [CommonModule, FormsModule],
  styleUrls: ['./test_cycle_execution.css'],
  templateUrl: './test_cycle_execution.html'
})

export class TestCycleExecutionComponent implements OnInit, AfterViewInit, OnDestroy, OnChanges {
  @Input() testCycle: any;
  @Input() projectKey: string = '';
  @Input() testCycleKey: string = '';

  http = inject(HttpClient);
  cdr = inject(ChangeDetectorRef);
  platformId = inject(PLATFORM_ID);

  selectedExecution: any = null;
  loading: boolean = false;
  apiError: string = '';
  
  // Local executions array - populated from API, used by template
  executions: any[] = [];

  @ViewChild('scriptEditorContainer', { static: false })
  scriptEditorContainer?: ElementRef<HTMLDivElement>;
  private isBrowser = false;
  private lastLoadedKey: string | null = null;
  private testCaseSub?: Subscription;
  private executionSub?: Subscription;

  ngOnInit() {
    this.isBrowser = isPlatformBrowser(this.platformId);
    // Load test cycle if we have a key on initialization (e.g., after page refresh)
    if (this.testCycleKey) {
      this.loadTestCycle();
    }
  }

  ngOnChanges(changes: SimpleChanges) {
    // If parent provides/updates testCycle or testCycleKey (for example after a refresh), reload
    if (changes['testCycle']) {
      const tc = changes['testCycle'].currentValue;
      if (tc && tc.executions) {
        // Ensure executions array is normalized
        this.testCycle = tc;
        if (!Array.isArray(this.testCycle.executions)) {
          try {
            this.testCycle.executions = Object.entries(this.testCycle.executions || {}).map(([test_case_key, exec]) => {
              const execObj: any = (exec && typeof exec === 'object') ? exec : {};
              return {
                test_case_key,
                ...execObj,
                result: execObj.result ?? 'NOT_EXECUTED'
              };
            });
          } catch (e) {
            // leave as-is
          }
        }
        this.populateExecutionTitles();
        this.cdr.detectChanges();
      }
    }

    if (changes['testCycleKey'] && changes['testCycleKey'].currentValue) {
      // When the key becomes available (e.g. on refresh), reload the cycle from server
      this.loadTestCycle();
    }
  }

  ngAfterViewInit() {
    // nothing by default; editor will be initialized when an execution is selected
  }

  ngOnDestroy() {
  }

  selectExecution(execution: any) {
    console.log('Selected execution:', execution);

    // Cancel any pending requests to avoid race conditions
    this.testCaseSub?.unsubscribe();
    this.executionSub?.unsubscribe();

    // Fetch both test case data and execution data from backend
    this.loadTestCaseAndExecutionData(execution.test_case_key, execution.execution_key);

    // Use the execution object from the list so updates remain consistent
    this.selectedExecution = execution;
    // Ensure placeholder fields exist so UI doesn't appear empty
    if (this.selectedExecution) {
      this.selectedExecution.title = this.selectedExecution.title ?? 'Loading...';
      this.selectedExecution.description = this.selectedExecution.description ?? '';
      this.selectedExecution.comment = this.selectedExecution.comment ?? '';
      this.selectedExecution.result = this.selectedExecution.result ?? 'NOT_EXECUTED';
    }
    this.cdr.detectChanges();
  }

  loadTestCaseAndExecutionData(testCaseKey: string, testExecutionKey: string) {
    console.log('Loading test case and execution data for:', testCaseKey);

    // Fetch execution data
    const executionUrl = `/api/tm/executions/${testExecutionKey}`;
    const executionRequest = this.http.get<any>(executionUrl);

    // Fetch test case data
    const testCaseUrl = `/api/tm/projects/${this.projectKey}/test-cases/${testCaseKey}`;
    const testCaseRequest = this.http.get<any>(testCaseUrl);

    // Wait for both requests to complete. Keep subscriptions so we can cancel if user selects another execution.
    this.testCaseSub = testCaseRequest.subscribe({
      next: (testCaseData) => {
        console.log('Test case data loaded:', testCaseData);
        if (this.selectedExecution && testCaseData && typeof testCaseData === 'object') {
          // Only assign when properties are present to avoid wiping existing values
          if (testCaseData.title !== undefined) this.selectedExecution.title = testCaseData.title;
          if (testCaseData.description !== undefined) this.selectedExecution.description = testCaseData.description;
          if (testCaseData.test_script !== undefined) this.selectedExecution.test_script = testCaseData.test_script;
          if (testCaseData.folder !== undefined) this.selectedExecution.folder = testCaseData.folder;
          if (testCaseData.status !== undefined) this.selectedExecution.status = testCaseData.status;
          if (testCaseData.priority !== undefined) this.selectedExecution.priority = testCaseData.priority;
          if (testCaseData.execution_key !== undefined) this.selectedExecution.execution_key = testCaseData.execution_key;
        }
      },
      error: (err) => {
        console.error('Error loading test case data:', err);
      }
    });

    this.executionSub = executionRequest.subscribe({
      next: (executionData) => {
        console.log('Execution data loaded:', executionData);
        if (this.selectedExecution && executionData && typeof executionData === 'object') {
          if (executionData.result != null) this.selectedExecution.result = executionData.result;
          if (executionData.comments !== undefined) this.selectedExecution.comments = executionData.comments;
          if (executionData.executed_at !== undefined) this.selectedExecution.executed_at = executionData.executed_at;
        }
      },
      error: (err) => {
        console.error('Error loading execution data:', err);
      }
    });
    this.cdr.detectChanges();
  }

  addTestCase() {
    // TODO: Implement add test case to cycle functionality
    console.log('Add test case to cycle');
    this.cdr.detectChanges();
  }

  // Fetch the title for each execution and set it
  populateExecutionTitles() {
    // Use single API to fetch all executions for the cycle (includes title and result)
    const cycleKey = this.testCycle?.test_cycle_key || this.testCycleKey;
    if (!cycleKey) {
      console.warn('populateExecutionTitles: no cycle key available');
      return;
    }

    // Ensure testCycle object exists
    if (!this.testCycle) {
      this.testCycle = { test_cycle_key: cycleKey, executions: [] };
    }

    const url = `/api/tm/cycles/${encodeURIComponent(cycleKey)}/executions`;
    console.log('populateExecutionTitles: fetching', url);

    this.http.get<any>(url).subscribe({
      next: (data) => {
        console.log('populateExecutionTitles: received data', data);
        if (!data) {
          console.warn('populateExecutionTitles: no data received');
          return;
        }

        // Normalize response into an array of execution-like objects.
        // API returns object keyed by test_case_key: {LIB-T2: {...}, LIB-T3: {...}}
        let items: any[] = [];
        if (Array.isArray(data)) {
          items = data;
        } else if (data && typeof data === 'object') {
          try {
            items = Object.entries(data).map(([key, exec]: [string, any]) => {
              // exec already contains the full execution object with test_case_key, title, result, etc.
              return { ...exec, test_case_key: exec?.test_case_key || key };
            });
          } catch (e) {
            console.error('Error normalizing executions response:', e);
            return;
          }
        }

        console.log('populateExecutionTitles: normalized items count:', items.length);

        // Replace executions array with enriched data from the API response
        // This ensures the sidebar shows titles and results
        this.executions = items.map((item: any) => ({
          ...item,
          result: item.result ?? 'NOT_EXECUTED'
        }));
        
        // Also update testCycle.executions for consistency
        if (this.testCycle) {
          this.testCycle.executions = this.executions;
        }
        
        console.log('populateExecutionTitles: updated executions count:', this.executions.length);
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading executions for cycle:', err);
      }
    });
  }

  loadTestCycle() {
    if (!this.testCycleKey) {
      console.warn('No testCycleKey provided to loadTestCycle()');
      return;
    }

    // Avoid duplicate concurrent loads
    if (this.loading) {
      console.debug('loadTestCycle skipped: already loading');
      return;
    }

    // If we've already loaded this key and have executions, skip unless forced
    if (this.testCycleKey && this.lastLoadedKey === this.testCycleKey && this.testCycle && Array.isArray(this.testCycle.executions) && this.testCycle.executions.length) {
      console.debug('loadTestCycle skipped: already loaded for key', this.testCycleKey);
      return;
    }

    this.loading = true;

    // Safety timeout to prevent infinite loading
    const timeout = setTimeout(() => {
      if (this.loading) {
        console.warn('Request timeout - forcing error state');
        this.apiError = 'Request timed out. Please try again.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    }, 10000);

    this.http.get<any>(`/api/tm/cycles/${this.testCycleKey}`).subscribe({
      next: (data) => {

        clearTimeout(timeout);
        console.log('Test cycle loaded in execution component:', data);
        
        try {
          this.testCycle = this.testCycle || {};
          this.testCycle.test_cycle_key = data.test_cycle_key || '';
          this.testCycle.title = data.title || '';
          this.testCycle.description = data.description || '';

          // Initialize executions as empty array - populateExecutionTitles() will fill it
          // with complete data including titles and results from the executions API
          this.testCycle.executions = [];

          // mark this key as loaded so subsequent duplicate calls are ignored
          this.lastLoadedKey = this.testCycleKey;

          // Fetch execution details (titles/results) and populate the sidebar list.
          // This is the primary source of execution data.
          this.populateExecutionTitles();

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
      }
    });
  }
}
