import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from '../loader/loader.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { TmCaseHeaderComponent } from './tm.case.header.component';
import { TestCases } from '../../services/tm.cases.service';

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

    formatDate(value: string | null | undefined): string {
        if (!value) return '—';
        const d = new Date(value);
        return isNaN(d.getTime()) ? value : d.toLocaleString();
    }
}
