import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { marked } from 'marked';
import { TestCycleExecution } from '../../services/tm.cycles.service';
import { CodeMirrorViewerComponent } from '../code-mirror-viewer/code.mirror.viewer.component';

@Component({
  selector: 'app-tm-execution-detail',
  standalone: true,
  imports: [CommonModule, CodeMirrorViewerComponent],
  styleUrls: ['./tm.execution.detail.component.css'],
  templateUrl: './tm.execution.detail.component.html'
})
export class TmExecutionDetailComponent {
  @Input() execution: TestCycleExecution | null = null;

  constructor(private sanitizer: DomSanitizer) { }

  renderMarkdown(text: string): SafeHtml {
    const html = marked.parse(text.trim(), { async: false }) as string;
    return this.sanitizer.bypassSecurityTrustHtml(html);
  }

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
