import { Component, inject, ChangeDetectorRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { NavbarComponent } from '../../component/navbar/navbar';

@Component({
    selector: 'app-tm-cycle',
    standalone: true,
    imports: [
        CommonModule,
        NavbarComponent
    ],
    styleUrls: ['./tm.cycle.css'],
    templateUrl: './tm.cycle.html'
})

export class TmCycle implements OnInit {
    cdr = inject(ChangeDetectorRef);
    route = inject(ActivatedRoute);
    router = inject(Router);
    showCreateModal: boolean = false;
    showEditModal: boolean = false;
    selectedTab: string = "executions";

    selectTab(tab: string) {
        this.selectedTab = tab;
        localStorage.setItem('tm-cycle-selectedTab', tab);
    }

    goBack() {
        const projectKey = this.route.snapshot.paramMap.get('projectKey');
        this.router.navigate([`projects/${projectKey}`]);
    }

    ngOnInit(): void {
        const cycleKey = this.route.snapshot.paramMap.get('cycleKey');
        const savedCycle = localStorage.getItem('tm-cycle-cycleKey');

        if (cycleKey !== savedCycle) {
            localStorage.removeItem('tm-cycle-selectedTab');
            localStorage.setItem('tm-cycle-cycleKey', cycleKey ?? '');
        }

        const saved = localStorage.getItem('tm-cycle-selectedTab');
        if (saved) {
            this.selectedTab = saved;
        }
    }

    ngAfterViewInit(): void { }

    ngOnDestroy(): void { }
}
