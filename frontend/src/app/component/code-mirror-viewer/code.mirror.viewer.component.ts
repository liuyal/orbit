import {
  Component,
  Input,
  OnChanges,
  AfterViewInit,
  OnDestroy,
  ElementRef,
  ViewChild,
  SimpleChanges,
  ViewEncapsulation,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  EditorView,
  lineNumbers,
  highlightSpecialChars,
  drawSelection,
  keymap,
} from '@codemirror/view';
import { EditorState, Extension } from '@codemirror/state';
import {
  indentOnInput,
  LanguageDescription,
} from '@codemirror/language';
import { defaultKeymap } from '@codemirror/commands';
import { languages } from '@codemirror/language-data';
import { monokai } from '@uiw/codemirror-theme-monokai';

@Component({
  selector: 'app-code-mirror-viewer',
  standalone: true,
  imports: [CommonModule],
  encapsulation: ViewEncapsulation.None,
  template: `<div #editorHost class="cm-host"></div>`,
  styles: [
    `
      app-code-mirror-viewer .cm-host {
        border-radius: 0px;
        overflow: hidden;
        font-size: 14px;
      }
      app-code-mirror-viewer .cm-editor {
        max-height: 600px;
      }
      app-code-mirror-viewer .cm-scroller {
        overflow: auto;
        font-family: 'Consolas', 'Courier New', monospace;
      }
    `,
  ],
})
export class CodeMirrorViewerComponent implements AfterViewInit, OnChanges, OnDestroy {
  @Input() code = '';
  @Input() language: string | null = null;

  @ViewChild('editorHost', { static: true }) editorHost!: ElementRef<HTMLDivElement>;

  private editorView: EditorView | null = null;

  ngAfterViewInit(): void {
    this.createEditor();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['code'] && !changes['code'].firstChange) {
      this.createEditor();
    }
  }

  ngOnDestroy(): void {
    this.editorView?.destroy();
  }

  private async createEditor(): Promise<void> {
    this.editorView?.destroy();
    this.editorHost.nativeElement.innerHTML = '';

    const langExtension = await this.resolveLanguage();

    const baseExtensions: Extension[] = [
      lineNumbers(),
      highlightSpecialChars(),
      drawSelection(),
      indentOnInput(),
      monokai,
      keymap.of(defaultKeymap),
      EditorState.readOnly.of(true),
      EditorView.editable.of(false),
    ];

    if (langExtension) {
      baseExtensions.unshift(langExtension);
    }

    this.editorView = new EditorView({
      state: EditorState.create({
        doc: this.code ?? '',
        extensions: baseExtensions,
      }),
      parent: this.editorHost.nativeElement,
    });
  }

  private async resolveLanguage(): Promise<Extension | null> {
    const name = this.language ?? this.detectLanguage(this.code);
    if (!name) return null;

    const desc = LanguageDescription.matchLanguageName(languages, name, true);
    if (!desc) return null;

    return desc.load();
  }

  private detectLanguage(code: string): string | null {
    if (!code) return null;
    const trimmed = code.trimStart();

    if (/^(Feature:|Scenario:|Scenario Outline:|Background:|Given |When |Then |And |But )/.test(trimmed)) return 'Gherkin';
    if (/^(import |from |def |class |async def |#!.*python)/.test(trimmed)) return 'Python';
    if (/\bconst\b|\blet\b|\bvar\b|\bfunction\b|\b=>\b/.test(trimmed.slice(0, 200))) return 'JavaScript';
    if (/^(public |private |protected |void |int |class |interface )/.test(trimmed)) return 'Java';
    if (/^(#!.*sh|echo |if \[|for |while |grep |sed |awk )/.test(trimmed)) return 'Shell';
    if (/^(<\?xml|<\?php|<html|<div|<!DOCTYPE)/i.test(trimmed)) return 'HTML';
    if (/^---/.test(trimmed)) return 'YAML';
    if (/^\s*\{/.test(trimmed) || /^\s*\[/.test(trimmed)) return 'JSON';
    if (/^(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b/i.test(trimmed)) return 'SQL';
    if (/#/.test(trimmed.slice(0, 500)) && /\b(install|package|version)\b/i.test(trimmed.slice(0, 500))) return 'Shell';

    return 'Gherkin';
  }
}
