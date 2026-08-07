import { Component, Input, ChangeDetectionStrategy } from '@angular/core';

@Component({
    selector: 'app-url-link',
    standalone: true,
    imports: [],
    templateUrl: './url.link.html',
    changeDetection: ChangeDetectionStrategy.Eager,
    styleUrls: ['./url.link.css']
})

export class UrlLinkComponent {
    @Input() name: string = '-';
    @Input() href: string = '';
}
