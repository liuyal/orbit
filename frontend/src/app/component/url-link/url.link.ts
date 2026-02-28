import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-url-link',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './url.link.html',
    styleUrls: ['./url.link.css']
})

export class UrlLinkComponent {
    @Input() name: string = '-';
    @Input() href: string = '';
}
