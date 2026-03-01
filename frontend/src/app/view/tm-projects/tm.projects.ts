import { Component, inject, ChangeDetectorRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from '../../component/navbar/navbar';
import { TmProjectsTableComponent } from '../../component/tm-projects-table/tm.project.table.component';

@Component({
    selector: 'app-tm-projects',
    standalone: true,
    imports: [
        CommonModule,
        NavbarComponent,
        TmProjectsTableComponent
    ],
    styleUrls: ['./tm.projects.css'],
    templateUrl: './tm.projects.html'
})

export class TmProjects implements OnInit {
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
