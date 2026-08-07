import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { LoaderComponent } from '../loader/loader.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { TmCaseHeaderComponent } from './tm.case.header.component';
import { TestCases } from '../../services/tm.cases.service';
import { formatDate } from '../../utils/date.utils';
import { getResultColor } from '../../utils/result.utils';

@Component({
    selector: 'app-tm-case-detail',
    standalone: true,
    imports: [
        LoaderComponent,
        ErrorStateComponent,
        TmCaseHeaderComponent,
    ],
    styleUrls: ['./tm.case.detail.component.css'],
    changeDetection: ChangeDetectionStrategy.Eager,
    templateUrl: './tm.case.detail.component.html',
})
export class TmCaseDetailComponent {
    @Input() testCase: TestCases | null = null;
    @Input() isLoading = false;
    @Input() error = '';

    formatDate(dateStr: string | null): string {
        return formatDate(dateStr);
    }

    getResultColor(result: string): string {
        return getResultColor(result);
    }
}
