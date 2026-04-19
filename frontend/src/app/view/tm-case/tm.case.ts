import { Component, inject, ChangeDetectorRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { NavbarComponent } from '../../component/navbar/navbar';

@Component({
    selector: 'app-tm-case',
    standalone: true,
    imports: [
        CommonModule,
        NavbarComponent
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

    selectTab(tab: string) {
        this.selectedTab = tab;
        localStorage.setItem('tm-case-selectedTab', tab);
    }

    goBack() {
        const projectKey = this.route.snapshot.paramMap.get('projectKey');
        this.router.navigate([`projects/${projectKey}`]);
    }

    ngOnInit(): void {
        const caseKey = this.route.snapshot.paramMap.get('caseKey');
        const savedCase = localStorage.getItem('tm-case-caseKey');

        if (caseKey !== savedCase) {
            localStorage.removeItem('tm-case-selectedTab');
            localStorage.setItem('tm-case-caseKey', caseKey ?? '');
        }

        const saved = localStorage.getItem('tm-case-selectedTab');
        if (saved) {
            this.selectedTab = saved;
        }
    }

    ngAfterViewInit(): void { }

    ngOnDestroy(): void { }
}
