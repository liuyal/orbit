import { Component, OnDestroy, OnInit, ChangeDetectionStrategy } from '@angular/core';

@Component({
    selector: 'app-footer',
    templateUrl: './footer.html',
    changeDetection: ChangeDetectionStrategy.Eager,
    styleUrls: ['./footer.css'],
})

export class FooterComponent implements OnInit, OnDestroy {
    // Get the current year for display in the footer
    currentYear = new Date().getFullYear();

    ngOnInit(): void {
        // Initialize any resources if needed
    }

    ngOnDestroy(): void {
        // Clean up any resources if needed
    }
}

