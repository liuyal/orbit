import { Component, Input, OnDestroy, ChangeDetectorRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-loader',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './loader.component.html',
    styleUrls: ['./loader.component.css']
})

export class LoaderComponent implements OnDestroy {
    private timer?: ReturnType<typeof setTimeout>;
    private cdr = inject(ChangeDetectorRef);
    private _active = false;
    showSpinner = false;

    @Input() delay = 3000;
    @Input()
    set active(v: boolean) {
        this._active = !!v;
        if (this._active) {
            this.startTimer();
        } else {
            this.clearTimer();
            this.showSpinner = false;
        }
    }
    get active(): boolean {
        return this._active;
    }

    private startTimer(): void {
        this.clearTimer();
        this.timer = setTimeout(() => {
            this.showSpinner = true;
            this.cdr.markForCheck();
        }, this.delay);
    }

    private clearTimer(): void {
        if (this.timer) {
            clearTimeout(this.timer);
            this.timer = undefined;
            this.cdr.markForCheck();
        }
    }

    ngOnDestroy(): void {
        this.clearTimer();
    }
}
