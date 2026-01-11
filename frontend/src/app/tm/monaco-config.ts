// Monaco Editor configuration for Angular
export function configureMonaco() {
  if (typeof window !== 'undefined' && typeof (window as any).MonacoEnvironment === 'undefined') {
    // Configure Monaco Editor environment
    (window as any).MonacoEnvironment = {
      getWorkerUrl: function (_moduleId: string, label: string) {
        if (label === 'json') {
          return './assets/monaco-editor/esm/vs/language/json/json.worker.js';
        }
        if (label === 'css' || label === 'scss' || label === 'less') {
          return './assets/monaco-editor/esm/vs/language/css/css.worker.js';
        }
        if (label === 'html' || label === 'handlebars' || label === 'razor') {
          return './assets/monaco-editor/esm/vs/language/html/html.worker.js';
        }
        if (label === 'typescript' || label === 'javascript') {
          return './assets/monaco-editor/esm/vs/language/typescript/ts.worker.js';
        }
        return './assets/monaco-editor/esm/vs/editor/editor.worker.js';
      }
    };
  }
}
