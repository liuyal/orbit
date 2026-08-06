import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-status-badge',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './status.badge.component.html',
    changeDetection: ChangeDetectionStrategy.Eager,
    styleUrls: ['./status.badge.component.css']
})

export class StatusBadgeComponent {
    @Input() text: string = '';
    @Input() className: string = '';
    @Input() icon: string = '';
    @Input() font_size: string = '12px';
}
