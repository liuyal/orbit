import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from '../loader/loader.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { TmCaseHeaderComponent } from './tm.case.header.component';
import { TestCases } from '../../services/tm.cases.service';
import { formatDate } from '../../utils/date.utils';

@Component({
    selector: 'app-tm-case-detail',
    standalone: true,
    imports: [
        CommonModule,
        LoaderComponent,
        ErrorStateComponent,
        TmCaseHeaderComponent,
    ],
    styleUrls: ['./tm.case.detail.component.css'],
    templateUrl: './tm.case.detail.component.html',
})
export class TmCaseDetailComponent {
    @Input() testCase: TestCases | null = null;
    @Input() isLoading = false;
    @Input() error = '';

    formatDate(dateStr: string | null): string {
        return formatDate(dateStr);
    }
}
