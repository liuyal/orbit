import { Component, inject, ChangeDetectorRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { NavbarComponent } from '../../component/navbar/navbar';

@Component({
    selector: 'app-tm-results',
    standalone: true,
    imports: [
        CommonModule,
        NavbarComponent
    ],
    styleUrls: ['./tm.results.css'],
    templateUrl: './tm.results.html'
})

export class TmResults implements OnInit {
    cdr = inject(ChangeDetectorRef);
    route = inject(ActivatedRoute);
    router = inject(Router);

    goBack() { }

    ngOnInit(): void { }

    ngAfterViewInit(): void { }

    ngOnDestroy(): void { }
}
