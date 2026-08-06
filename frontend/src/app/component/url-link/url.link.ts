import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-url-link',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './url.link.html',
    changeDetection: ChangeDetectionStrategy.Eager,
    styleUrls: ['./url.link.css']
})

export class UrlLinkComponent {
    @Input() name: string = '-';
    @Input() href: string = '';
}
