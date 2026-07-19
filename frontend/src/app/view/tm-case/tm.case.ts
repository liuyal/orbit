import { Component, inject, ChangeDetectorRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { NavbarComponent } from '../../component/navbar/navbar';
import { TmCaseDetailComponent } from '../../component/tm-case/tm.case.detail.component';
import { TmCaseScriptComponent } from '../../component/tm-case/tm.case.script.component';
import { TmCaseLinksComponent } from '../../component/tm-case/tm.case.links.component';
import { TmCaseExecutionsTableComponent } from '../../component/tm-case/tm.case.executions.table.component';
import { TestCasesService, TestCases } from '../../services/tm.cases.service';

@Component({
    selector: 'app-tm-case',
    standalone: true,
    imports: [
        CommonModule,
        NavbarComponent,
        TmCaseDetailComponent,
        TmCaseScriptComponent,
        TmCaseLinksComponent,
        TmCaseExecutionsTableComponent,
    ],
    styleUrls: ['./tm.case.css'],
    templateUrl: './tm.case.html'
})

export class TmCase implements OnInit {
    cdr = inject(ChangeDetectorRef);
    route = inject(ActivatedRoute);
    router = inject(Router);
    showCreateModal: boolean = false;
    showEditModal: boolean = false;
    selectedTab: string = "details";
    projectKey = '';
    caseKey = '';
    testCase: TestCases | null = null;
    isLoading = false;
    error = '';

    constructor(private testCasesService: TestCasesService) {}

    selectTab(tab: string) {
        this.selectedTab = tab;
        localStorage.setItem('tm-case-selectedTab', tab);
        this.router.navigate([], { fragment: tab, replaceUrl: true });
    }

    goBack() {
        const projectKey = this.route.snapshot.paramMap.get('projectKey');
        this.router.navigate([`projects/${projectKey}`]);
    }

    ngOnInit(): void {
        this.projectKey = this.route.snapshot.paramMap.get('projectKey') ?? '';
        this.caseKey = this.route.snapshot.paramMap.get('caseKey') ?? '';

        const savedCase = localStorage.getItem('tm-case-caseKey');
        if (this.caseKey !== savedCase) {
            localStorage.removeItem('tm-case-selectedTab');
            localStorage.setItem('tm-case-caseKey', this.caseKey);
        }

        const fragment = this.route.snapshot.fragment;
        if (fragment) {
            this.selectedTab = fragment;
            localStorage.setItem('tm-case-selectedTab', fragment);
        } else {
            const saved = localStorage.getItem('tm-case-selectedTab');
            if (saved) {
                this.selectedTab = saved;
            }
        }

        this.loadTestCase();
    }

    private loadTestCase(): void {
        if (!this.projectKey || !this.caseKey) return;
        this.isLoading = true;
        this.error = '';
        this.testCasesService.getTestCasebyKey(this.projectKey, this.caseKey).subscribe({
            next: (res) => {
                this.testCase = res;
                this.isLoading = false;
                this.cdr.markForCheck();
            },
            error: (err) => {
                this.error = `Error loading test case: ${err.message || err}`;
                this.isLoading = false;
                this.cdr.markForCheck();
            },
        });
    }

    ngAfterViewInit(): void { }

    ngOnDestroy(): void { }
}
