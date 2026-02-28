import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-error-state',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './error.state.component.html',
    styleUrls: ['./error.state.component.css']
})

export class ErrorStateComponent {
    @Input() visible = true;
    @Input() error = '';
}
