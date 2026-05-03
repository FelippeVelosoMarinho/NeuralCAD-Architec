import { useEffect, useState } from "react";

import { getApiBase } from "../lib/env";

/** Descarrega STL binário assim que job termina em sucesso (abort em cleanup). */
export function useMeshFromJob(jobId: string | null, jobStatus: string | undefined) {
  const [buffer, setBuffer] = useState<ArrayBuffer | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!jobId || jobStatus !== "success") {
      setBuffer(null);
      setLoadError(null);
      setLoading(false);
      return;
    }

    const ac = new AbortController();
    setLoading(true);
    setLoadError(null);

    const url = `${getApiBase()}/api/v1/jobs/${jobId}/artifacts/stl`;

    void (async () => {
      try {
        const r = await fetch(url, { signal: ac.signal, credentials: "omit" });
        if (!r.ok) throw new Error(`STL HTTP ${r.status}`);
        const ab = await r.arrayBuffer();
        if (ab.byteLength > 26 * 1024 * 1024) throw new Error("STL demasiado grande para o MVP (>26MB)");
        setBuffer(ab);
      } catch (e) {
        if ((e as Error).name === "AbortError") return;
        setLoadError(e instanceof Error ? e.message : String(e));
        setBuffer(null);
      } finally {
        setLoading(false);
      }
    })();

    return () => ac.abort();
  }, [jobId, jobStatus]);

  return { buffer, loadError, loading };
}
