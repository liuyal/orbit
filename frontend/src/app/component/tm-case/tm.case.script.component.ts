import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from '../loader/loader.component';
import { ErrorStateComponent } from '../error-state/error.state.component';
import { EmptyStateComponent } from '../empty-state/empty.state.component';
import { CodeMirrorViewerComponent } from '../code-mirror-viewer/code.mirror.viewer.component';
import { TmCaseHeaderComponent } from './tm.case.header.component';
import { TestCases } from '../../services/tm.cases.service';

@Component({
    selector: 'app-tm-case-script',
    standalone: true,
    imports: [
        CommonModule,
        LoaderComponent,
        ErrorStateComponent,
        EmptyStateComponent,
        CodeMirrorViewerComponent,
        TmCaseHeaderComponent
    ],
    styleUrls: ['./tm.case.script.component.css'],
    templateUrl: './tm.case.script.component.html',
})
export class TmCaseScriptComponent {
    @Input() testCase: TestCases | null = null;
    @Input() isLoading = false;
    @Input() error = '';
}
