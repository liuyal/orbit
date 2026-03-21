import { Component, inject, ChangeDetectorRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from '../../component/navbar/navbar';

@Component({
    selector: 'app-tm-test-cases',
    standalone: true,
    imports: [
        CommonModule,
        NavbarComponent,
    ],
    styleUrls: ['./tm.test-cases.css'],
    templateUrl: './tm.test-cases.html'
})

export class TmTestCases implements OnInit {
    cdr = inject(ChangeDetectorRef);
    showCreateModal = false;
    showEditModal = false;

    ngOnInit(): void {
    }

    ngAfterViewInit(): void {
    }

    ngOnDestroy(): void {
    }
}
