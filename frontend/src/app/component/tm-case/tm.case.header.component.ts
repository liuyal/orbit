import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { TestCases } from '../../services/tm.cases.service';

@Component({
    selector: 'app-tm-case-header',
    standalone: true,
    imports: [],
    templateUrl: './tm.case.header.component.html',
    changeDetection: ChangeDetectionStrategy.Eager,
    styleUrls: ['./tm.case.header.component.css'],
})
export class TmCaseHeaderComponent {
    @Input() testCase: TestCases | null = null;
}
