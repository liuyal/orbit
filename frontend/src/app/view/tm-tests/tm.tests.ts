import { Component, inject, ChangeDetectorRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { NavbarComponent } from '../../component/navbar/navbar';

@Component({
    selector: 'app-tm-tests',
    standalone: true,
    imports: [
        CommonModule,
        NavbarComponent,
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
        console.log(`Selected tab: ${tab}`);
    }

    goBack() {
        this.router.navigate(['/projects']);
    }

    ngOnInit(): void { }

    ngAfterViewInit(): void { }

    ngOnDestroy(): void { }
}
