import Editor, { type OnMount } from "@monaco-editor/react";
import { useCallback } from "react";

type Props = {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
};

export function PromptEditor({ value, onChange, onSubmit }: Props) {
  const handleMount: OnMount = useCallback(
    (editor, monaco) => {
      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
        onSubmit();
      });
    },
    [onSubmit],
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", minHeight: 0 }}>
      <div style={{ padding: "0.35rem 0.5rem", borderBottom: "1px solid var(--border)", flexShrink: 0 }}>
        <button type="button" data-testid="prompt-submit" onClick={onSubmit}>
          Enviar
        </button>
        <span style={{ marginLeft: "0.75rem", color: "var(--text-muted)", fontSize: "0.8rem" }}>
          Ctrl+Enter
        </span>
      </div>
      <div style={{ flex: 1, minHeight: 0 }}>
        <Editor
          height="100%"
          defaultLanguage="markdown"
          theme="vs-dark"
          value={value}
          onChange={(v) => onChange(v ?? "")}
          onMount={handleMount}
          options={{ minimap: { enabled: false }, wordWrap: "on", fontSize: 14 }}
        />
      </div>
    </div>
  );
}
