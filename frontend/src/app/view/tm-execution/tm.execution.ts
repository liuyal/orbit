import { Component, inject, ChangeDetectorRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { NavbarComponent } from '../../component/navbar/navbar';

@Component({
    selector: 'app-tm-execution',
    standalone: true,
    imports: [
        CommonModule,
        NavbarComponent
    ],
    styleUrls: ['./tm.execution.css'],
    templateUrl: './tm.execution.html'
})

export class TmExecution implements OnInit {
    cdr = inject(ChangeDetectorRef);
    route = inject(ActivatedRoute);
    router = inject(Router);
    showCreateModal: boolean = false;
    showEditModal: boolean = false;

    goBack() {
        const projectKey = this.route.snapshot.paramMap.get('projectKey');
        this.router.navigate([`projects/${projectKey}`]);
    }

    ngOnInit(): void {}

    ngAfterViewInit(): void { }

    ngOnDestroy(): void { }
}
