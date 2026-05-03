import { AppShell } from "./components/layout/AppShell";
import { PromptEditor } from "./components/editor/PromptEditor";
import { MeshViewport } from "./components/viewport/MeshViewport";
import { TopologyExplorer } from "./components/explorer/TopologyExplorer";
import { useJobFlow } from "./hooks/useJobFlow";
import { useMeshFromJob } from "./hooks/useMeshFromJob";

export default function App() {
  const flow = useJobFlow();
  const mesh = useMeshFromJob(flow.jobId, flow.job?.status);

  const bottomPanel = (
    <div style={{ padding: "0.5rem 0.75rem", fontSize: "0.85rem", lineHeight: 1.5 }}>
      <div>
        <strong>Estado:</strong> {flow.phase}
      </div>
      {flow.jobId ? (
        <div>
          <strong>Job:</strong> {flow.jobId}
        </div>
      ) : null}
      {flow.job ? (
        <div>
          <strong>Worker:</strong> {flow.job.status}
        </div>
      ) : null}
      {flow.error ? (
        <div style={{ color: "var(--error)", marginTop: "0.35rem" }}>
          <strong>Erro:</strong> {flow.error}
        </div>
      ) : null}
      <button type="button" style={{ marginTop: "0.5rem" }} onClick={() => void flow.run()}>
        Elicitar + criar job (demo)
      </button>
      <pre
        style={{
          marginTop: "0.5rem",
          maxHeight: "6rem",
          overflow: "auto",
          fontSize: "0.7rem",
          color: "var(--text-muted)",
        }}
      >
        {truncateJson(flow.lastResponse)}
      </pre>
    </div>
  );

  return (
    <AppShell
      explorerContent={<TopologyExplorer jobId={flow.jobId} dimensionalAudit={flow.job?.dimensional_audit} />}
      centerPromptContent={
        <PromptEditor value={flow.prompt} onChange={flow.setPrompt} onSubmit={() => void flow.run()} />
      }
      centerViewportContent={<MeshViewport buffer={mesh.buffer} error={mesh.loadError} loading={mesh.loading} />}
      bottomPanelContent={bottomPanel}
    />
  );
}

function truncateJson(data: unknown, max = 800): string {
  try {
    const s = JSON.stringify(data, null, 2);
    return s.length > max ? `${s.slice(0, max)}\n…` : s;
  } catch {
    return String(data);
  }
}
