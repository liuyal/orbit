import { Component, inject, ChangeDetectorRef, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { NavbarComponent } from '../../component/navbar/navbar';
import { LoaderComponent } from '../../component/loader/loader.component';
import { EmptyStateComponent } from '../../component/empty-state/empty.state.component';
import { ErrorStateComponent } from '../../component/error-state/error.state.component';
import { TmExecutionHeaderComponent } from '../../component/tm-execution/tm.execution.header.component';
import { TmExecutionDetailComponent } from '../../component/tm-execution/tm.execution.detail.component';
import { TestExecutionsService } from '../../services/tm.executions.service';
import { TestCasesService } from '../../services/tm.cases.service';
import { TestCycleExecution } from '../../services/tm.cycles.service';

@Component({
    selector: 'app-tm-execution',
    standalone: true,
    imports: [
        NavbarComponent,
        LoaderComponent,
        EmptyStateComponent,
        ErrorStateComponent,
        TmExecutionHeaderComponent,
        TmExecutionDetailComponent
    ],
    styleUrls: ['./tm.execution.css'],
    changeDetection: ChangeDetectionStrategy.Eager,
    templateUrl: './tm.execution.html'
})

export class TmExecution implements OnInit {
    cdr = inject(ChangeDetectorRef);
    route = inject(ActivatedRoute);
    router = inject(Router);
    showCreateModal: boolean = false;
    showEditModal: boolean = false;
    projectKey = '';
    caseKey = '';
    executionKey = '';
    execution: TestCycleExecution | null = null;
    isLoading = false;
    error = '';

    constructor(
        private testExecutionsService: TestExecutionsService,
        private testCasesService: TestCasesService
    ) { }

    goBack() {
        this.router.navigate([`projects/${this.projectKey}/case/${this.caseKey}`], { fragment: 'executions' });
    }

    private loadExecution(): void {
        if (!this.projectKey || !this.caseKey || !this.executionKey) return;
        this.isLoading = true;
        this.error = '';
        forkJoin({
            execution: this.testExecutionsService.getExecutionByKey(this.executionKey),
            testCase: this.testCasesService.getTestCasebyKey(this.projectKey, this.caseKey)
        }).subscribe({
            next: ({ execution, testCase }) => {
                // Merge test case details (title, folder, priority, labels, etc.) into the execution
                this.execution = { ...execution, ...testCase } as unknown as TestCycleExecution;
                this.isLoading = false;
                this.cdr.markForCheck();
            },
            error: (err) => {
                this.error = `Error loading test execution: ${err.message || err}`;
                this.isLoading = false;
                this.cdr.markForCheck();
            }
        });
    }

    ngOnInit(): void {
        this.projectKey = this.route.snapshot.paramMap.get('projectKey') ?? '';
        this.caseKey = this.route.snapshot.paramMap.get('caseKey') ?? '';
        this.executionKey = this.route.snapshot.paramMap.get('executionKey') ?? '';
        this.loadExecution();
    }

    ngAfterViewInit(): void { }

    ngOnDestroy(): void { }
}
