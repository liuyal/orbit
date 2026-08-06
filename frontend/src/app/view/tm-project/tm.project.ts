import { Component, inject, ChangeDetectorRef, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from '../../component/navbar/navbar';
import { TmProjectsTableComponent } from '../../component/tm-project/tm.project.table.component';

@Component({
    selector: 'app-tm-project',
    standalone: true,
    imports: [
        CommonModule,
        NavbarComponent,
        TmProjectsTableComponent
    ],
    styleUrls: ['./tm.project.css'],
    changeDetection: ChangeDetectionStrategy.Eager,
    templateUrl: './tm.project.html'
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
