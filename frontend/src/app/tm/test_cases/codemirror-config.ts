// CodeMirror 6 configuration for Angular
import { EditorView, basicSetup } from 'codemirror';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';

export function createCodeMirrorEditor(container: HTMLElement, initialValue: string, onChange: (value: string) => void): EditorView {
  const editor = new EditorView({
    doc: initialValue,
    extensions: [
      basicSetup,
      python(),
      oneDark,
      EditorView.updateListener.of((update: any) => {
        if (update.docChanged) {
          onChange(update.state.doc.toString());
        }
      }),
      EditorView.theme({
        '&': {
          height: '100%',
          fontSize: '14px'
        },
        '.cm-scroller': {
          overflow: 'auto',
          fontFamily: "'Consolas', 'Monaco', 'Courier New', monospace"
        },
        '.cm-content': {
          minHeight: '100%'
        }
      })
    ],
    parent: container
  });

  return editor;
}
