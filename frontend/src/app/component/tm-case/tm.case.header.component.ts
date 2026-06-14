import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TestCases } from '../../services/tm.cases.service';

@Component({
    selector: 'app-tm-case-header',
    standalone: true,
    imports: [
        CommonModule
    ],
    templateUrl: './tm.case.header.component.html',
    styleUrls: ['./tm.case.header.component.css'],
})
export class TmCaseHeaderComponent {
    @Input() testCase: TestCases | null = null;
}
