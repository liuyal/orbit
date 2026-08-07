import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { TestCycleExecution } from '../../services/tm.cycles.service';
import { getResultColor } from '../../utils/result.utils';

@Component({
    selector: 'app-tm-execution-header',
    standalone: true,
    imports: [],
    templateUrl: './tm.execution.header.component.html',
    changeDetection: ChangeDetectionStrategy.Eager,
    styleUrls: ['./tm.execution.header.component.css'],
})
export class TmExecutionHeaderComponent {
    @Input() execution: TestCycleExecution | null = null;

    getResultColor(result: string): string {
        return getResultColor(result);
    }
}
