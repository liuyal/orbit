declare module 'codemirror' {
  // Minimal ambient declarations for CodeMirror v6 surface used in this project.
  // These are intentionally permissive to avoid blocking builds when full types
  // aren't available. Replace with proper types if desired.
  export type EditorView = any;
  export const EditorView: any;
  export const basicSetup: any;
  export default any;
}
