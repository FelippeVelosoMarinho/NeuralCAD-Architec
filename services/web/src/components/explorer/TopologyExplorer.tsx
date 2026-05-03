import { useShellStore } from "../../stores/shellStore";

export type TopologySketch = {
  faces?: number;
  edges?: number;
  vertices?: number;
  confidence?: string;
};

type Props = {
  jobId: string | null;
  dimensionalAudit: unknown;
};

function pathsEqual(a: string[] | null, b: string[]): boolean {
  if (!a || a.length !== b.length) return false;
  return a.every((seg, i) => seg === b[i]);
}

function sketchFromAudit(audit: unknown): TopologySketch | null {
  if (typeof audit !== "object" || audit === null) return null;
  const a = audit as Record<string, unknown>;
  const s = a.topologySketch;
  if (typeof s !== "object" || s === null) return null;
  const o = s as Record<string, unknown>;
  const faces = typeof o.faces === "number" ? o.faces : undefined;
  const edges = typeof o.edges === "number" ? o.edges : undefined;
  const vertices = typeof o.vertices === "number" ? o.vertices : undefined;
  const confidence = typeof o.confidence === "string" ? o.confidence : undefined;
  if (faces === undefined && edges === undefined && vertices === undefined) return null;
  return { faces, edges, vertices, confidence };
}

/** Árvore sintética alinhada a `topologySketch` do job. */
export function TopologyExplorer({ jobId, dimensionalAudit }: Props) {
  const { selectedTopologyPath, selectTopologyPath } = useShellStore();
  const short = jobId ? jobId.slice(0, 8) : "—";
  const sketch = sketchFromAudit(dimensionalAudit);

  const faces = sketch?.faces ?? "--";
  const edges = sketch?.edges ?? "--";
  const vertices = sketch?.vertices ?? "--";

  const pick = (path: string[]) => {
    selectTopologyPath(pathsEqual(selectedTopologyPath, path) ? null : path);
  };

  const mark = (path: string[]) => (pathsEqual(selectedTopologyPath, path) ? "is-selected" : "");

  return (
    <nav className="explorer-body topology-root" aria-label="Explorer topológico">
      <div className={`topology-branch ${mark(["jobs", short])}`}>
        <button type="button" className="topology-row" onClick={() => pick(["jobs", short])}>
          Jobs / {short}
        </button>
        <div className="topology-children">
          <div className={`topology-branch ${mark(["jobs", short, "solid"])}`}>
            <button type="button" className="topology-row" onClick={() => pick(["jobs", short, "solid"])}>
              Corpo
            </button>
            <div className="topology-children">
              <button
                type="button"
                className={`topology-row ${mark(["jobs", short, "faces"])}`}
                onClick={() => pick(["jobs", short, "faces"])}
              >
                Faces ({String(faces)})
              </button>
              <button
                type="button"
                className={`topology-row ${mark(["jobs", short, "edges"])}`}
                onClick={() => pick(["jobs", short, "edges"])}
              >
                Arestas ({String(edges)})
              </button>
              <button
                type="button"
                className={`topology-row ${mark(["jobs", short, "vertices"])}`}
                onClick={() => pick(["jobs", short, "vertices"])}
              >
                Vértices ({String(vertices)})
              </button>
            </div>
          </div>
        </div>
      </div>
      {sketch?.confidence === "mvp" ? (
        <p style={{ color: "var(--text-muted)", fontSize: "0.72rem", marginTop: "0.5rem" }}>
          Contagens MVP OCC (confidence: mvp).
        </p>
      ) : null}
    </nav>
  );
}
