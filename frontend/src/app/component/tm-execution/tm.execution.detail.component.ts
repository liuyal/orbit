import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { marked } from 'marked';
import { TestCycleExecution } from '../../services/tm.cycles.service';
import { CodeMirrorViewerComponent } from '../code-mirror-viewer/code.mirror.viewer.component';
import { formatDate } from '../../utils/date.utils';
import { getResultColor } from '../../utils/result.utils';

@Component({
  selector: 'app-tm-execution-detail',
  standalone: true,
  imports: [
    CodeMirrorViewerComponent
  ],
  styleUrls: ['./tm.execution.detail.component.css'],
  changeDetection: ChangeDetectionStrategy.Eager,
  templateUrl: './tm.execution.detail.component.html'
})
export class TmExecutionDetailComponent {
  @Input() execution: TestCycleExecution | null = null;

  constructor(private sanitizer: DomSanitizer) { }

  renderMarkdown(text: string): SafeHtml {
    const html = marked.parse(text.trim(), { async: false }) as string;
    return this.sanitizer.bypassSecurityTrustHtml(html);
  }

  getResultColor(result: string): string {
    return getResultColor(result);
  }

  formatDate(dateStr: string | null): string {
    return formatDate(dateStr);
  }
}
1