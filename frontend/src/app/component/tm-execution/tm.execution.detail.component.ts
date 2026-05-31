import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TestCycleExecution } from '../../services/tm.cycles.service';

@Component({
  selector: 'app-tm-execution-detail',
  standalone: true,
  imports: [CommonModule],
  styleUrls: ['./tm.execution.detail.component.css'],
  templateUrl: './tm.execution.detail.component.html'
})
export class TmExecutionDetailComponent {
  @Input() execution: TestCycleExecution | null = null;

  private readonly resultColors: Record<string, string> = {
    PASS: '#4caf50',
    FAIL: '#f44336',
    BLOCKED: '#2196f3',
    NOT_EXECUTED: '#757575',
    IN_PROGRESS: '#ffd700',
  };

  getResultColor(result: string): string {
    return this.resultColors[result?.toUpperCase()] ?? '#757575';
  }

  formatDate(dateStr: string | null): string {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleString();
  }
}
