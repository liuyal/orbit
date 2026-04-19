import { Component, inject, ChangeDetectorRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { NavbarComponent } from '../../component/navbar/navbar';
import { TmCasesTableComponent } from '../../component/tm-cases-table/tm.cases.table.component';
import { TmCyclesTableComponent } from '../../component/tm-cycle-table/tm.cycle.table.component';

@Component({
    selector: 'app-tm-tests',
    standalone: true,
    imports: [
        CommonModule,
        NavbarComponent,
        TmCasesTableComponent,
        TmCyclesTableComponent
    ],
    styleUrls: ['./tm.tests.css'],
    templateUrl: './tm.tests.html'
})

export class TmTests implements OnInit {
    cdr = inject(ChangeDetectorRef);
    route = inject(ActivatedRoute);
    router = inject(Router);
    showCreateModal: boolean = false;
    showEditModal: boolean = false;
    selectedTab: string = "tests";

    selectTab(tab: string) {
        this.selectedTab = tab;
        localStorage.setItem('tm-tests-selectedTab', tab);
    }

    goBack() {
        this.router.navigate(['/projects']);
    }

    ngOnInit(): void {
        const projectKey = this.route.snapshot.paramMap.get('projectKey') ?? this.route.snapshot.queryParamMap.get('projectKey');
        const savedProject = localStorage.getItem('tm-tests-projectKey');

        if (projectKey !== savedProject) {
            localStorage.removeItem('tm-tests-selectedTab');
            localStorage.setItem('tm-tests-projectKey', projectKey ?? '');
        }

        const saved = localStorage.getItem('tm-tests-selectedTab');
        if (saved) {
            this.selectedTab = saved;
        }
    }

    ngAfterViewInit(): void { }

    ngOnDestroy(): void { }
}
