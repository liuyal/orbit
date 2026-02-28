import { Component, Input , NgModule} from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-status-badge',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './status.badge.component.html',
    styleUrls: ['./status.badge.component.css']
})

export class StatusBadgeComponent {
    @Input() text: string = '';
    @Input() className: string = '';
    @Input() icon: string = '';
}
