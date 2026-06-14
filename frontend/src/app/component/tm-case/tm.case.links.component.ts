import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from '../loader/loader.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { EmptyStateComponent } from '../empty-state/empty.state.component';
import { TmCaseHeaderComponent } from './tm.case.header.component';
import { TestCases } from '../../services/tm.cases.service';

@Component({
    selector: 'app-tm-case-links',
    standalone: true,
    imports: [
        CommonModule,
        LoaderComponent,
        ErrorStateComponent,
        EmptyStateComponent,
        TmCaseHeaderComponent
    ],
    styleUrls: ['./tm.case.links.component.css'],
    templateUrl: './tm.case.links.component.html',
})
export class TmCaseLinksComponent {
    @Input() testCase: TestCases | null = null;
    @Input() isLoading = false;
    @Input() error = '';

    asString(val: unknown): string {
        return typeof val === 'string' ? val : String(val);
    }
}
