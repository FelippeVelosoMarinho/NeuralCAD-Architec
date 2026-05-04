import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef, useState } from "react";

import { jobDetailKey } from "./queryKeys";
import * as api from "../lib/api";
import { getTabClientSession } from "../lib/tabClientSession";
import { jobChannelWsUrl } from "../lib/wsJobChannel";

export type JobFlowPhase =
  | "idle"
  | "eliciting"
  | "creating"
  | "listening"
  | "done"
  | "cancelled_done"
  | "error";

export type JobRecord = {
  id: string;
  status: string;
  dimensional_audit?: unknown;
  artifact_key?: string | null;
  error_message?: string | null;
};

/** Envelope válido quando o elicit falha — exige apenas API + worker; não exige Claude. */
const FALLBACK_ENVELOPE: api.IntentEnvelopeJson = {
  intent: {
    sessionId: "ui-demo",
    promptOriginal: "demo box via UI fallback",
    intent: { objectType: "box", style: [], functionalGoal: "demo" },
    constraints: {
      dimensionsMm: { width: 100, height: 50, depth: 25 },
      symmetry: "none",
      manufacturingHints: [],
      materialHints: [],
    },
  },
  preflight: {
    geo_risk: {
      severity: "info",
      messages: ["sem elicit activo"],
    },
  },
};

function isRecord(x: unknown): x is Record<string, unknown> {
  return typeof x === "object" && x !== null;
}

function parseJob(data: unknown): JobRecord | null {
  if (!isRecord(data) || typeof data.id !== "string" || typeof data.status !== "string") return null;
  return {
    id: data.id,
    status: data.status,
    dimensional_audit: data.dimensional_audit,
    artifact_key: typeof data.artifact_key === "string" ? data.artifact_key : null,
    error_message: typeof data.error_message === "string" ? data.error_message : null,
  };
}

async function fetchJobRecord(id: string): Promise<JobRecord> {
  const raw = await api.getJob(id);
  const j = parseJob(raw);
  if (!j) throw new Error("payload de GET /jobs inválido");
  return j;
}

/** Elicitar (best-effort), criar job, snapshot GET inicial e estado via WS — sem polling. */
export function useJobFlow() {
  const qc = useQueryClient();
  const tabSessionRef = useRef<string | null>(null);
  if (typeof window !== "undefined" && tabSessionRef.current === null) {
    tabSessionRef.current = getTabClientSession(sessionStorage);
  }

  const [phase, setPhase] = useState<JobFlowPhase>("idle");
  const [prompt, setPrompt] = useState("caixa 100x50x25 mm");
  const [lastResponse, setLastResponse] = useState<unknown>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pipelineStageLabel, setPipelineStageLabel] = useState<string | null>(null);
  const endedRef = useRef(false);

  useEffect(() => {
    endedRef.current = phase === "done" || phase === "cancelled_done" || phase === "error";
  }, [phase]);

  const clientSession = typeof window !== "undefined" ? (tabSessionRef.current ?? "") : "";

  const jobQuery = useQuery({
    queryKey: jobDetailKey(jobId ?? ""),
    queryFn: () => fetchJobRecord(jobId!),
    enabled: !!jobId,
    staleTime: Infinity,
    retry: false,
  });

  const job = jobQuery.data ?? null;

  /** WS lifecycle + opcional reconnect alinhado a CONTEXT (GET único antes de novo socket). */
  useEffect(() => {
    if (!jobId || !clientSession || phase !== "listening") return;
    let aborted = false;
    let ws: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let reopenAttempts = 0;
    const maxReopenAttempts = 4;

    const handlePayload = async (payload: Record<string, unknown>) => {
      const t = payload.type;
      if (typeof t !== "string") return;

      const detail = payload.detail;
      const dRec = detail && isRecord(detail) ? detail : null;

      if (t === "job.progress") {
        const ps = dRec && typeof dRec.pipelineStage === "string" ? dRec.pipelineStage : null;
        if (ps) setPipelineStageLabel(ps);
      }

      const terminalLifecycle =
        t === "job.lifecycle" &&
        dRec &&
        typeof dRec.lifecycle === "string" &&
        (dRec.lifecycle === "success" ||
          dRec.lifecycle === "failed" ||
          dRec.lifecycle === "cancelled");

      if (terminalLifecycle || t === "job.cancelled") {
        aborted = true;
        try {
          ws?.close();
        } catch {
          /* ignore */
        }
        ws = null;
        try {
          await qc.fetchQuery({ queryKey: jobDetailKey(jobId), queryFn: () => fetchJobRecord(jobId) });
        } catch {
          /* ignore */
        }
        const sj = qc.getQueryData<JobRecord>(jobDetailKey(jobId));
        const st = sj?.status ?? "";
        if (st === "success") setPhase("done");
        else if (st === "cancelled") setPhase("cancelled_done");
        else setPhase("error");
        setError(sj?.error_message ?? null);
        reopenAttempts = maxReopenAttempts;
      }
    };

    async function attachSocket() {
      if (aborted) return;

      reopenAttempts++;

      /** Antes de reabrir, um único snapshot GET conforme PLAN 04‑03. */
      if (reopenAttempts > 1) {
        try {
          await qc.fetchQuery({
            queryKey: jobDetailKey(jobId),
            queryFn: () => fetchJobRecord(jobId),
          });
        } catch {
          setPhase("error");
          setError("re-sync GET após erro WS falhou");
          return;
        }
      }

      if (endedRef.current) return;

      const url = jobChannelWsUrl(jobId, clientSession);
      ws = new WebSocket(url);

      ws.onopen = () => {
        void qc.fetchQuery({
          queryKey: jobDetailKey(jobId),
          queryFn: () => fetchJobRecord(jobId),
        });
      };

      ws.onmessage = async (evt) => {
        if (typeof evt.data !== "string") return;
        let parsed: unknown;
        try {
          parsed = JSON.parse(evt.data);
        } catch {
          return;
        }
        if (!isRecord(parsed)) return;
        await handlePayload(parsed);
      };

      ws.onerror = () => {
        try {
          ws?.close();
        } catch {
          /* ignore */
        }
      };

      ws.onclose = () => {
        if (endedRef.current || aborted) return;
        if (reopenAttempts >= maxReopenAttempts) return;
        reconnectTimer = setTimeout(() => {
          void attachSocket();
        }, 850);
      };
    }

    void attachSocket();

    return () => {
      aborted = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      try {
        ws?.close();
      } catch {
        /* ignore */
      }
    };
  }, [clientSession, jobId, phase, qc]);

  const run = useCallback(async () => {
    setError(null);
    setLastResponse(null);
    setJobId(null);
    qc.removeQueries({ queryKey: ["job"], exact: false });
    setPipelineStageLabel(null);

    let envelope: api.IntentEnvelopeJson = FALLBACK_ENVELOPE;

    try {
      setPhase("eliciting");
      try {
        const elicit = await api.postIntentElicit(prompt, 1);
        setLastResponse(elicit);
        if (isRecord(elicit) && elicit.kind === "success" && isRecord(elicit.intent)) {
          envelope = { intent: elicit.intent };
          if (isRecord(elicit.geo_risk)) {
            envelope = { ...envelope, preflight: { geo_risk: elicit.geo_risk } };
          }
        }
      } catch {
        setLastResponse({ note: "elicit skipped — using fallback envelope", prompt });
        envelope = FALLBACK_ENVELOPE;
      }

      setPhase("creating");
      const created = await api.postJob(envelope);
      setLastResponse(created);
      const parsed = parseJob(created);
      if (!parsed) throw new Error("resposta de criação de job inválida");
      qc.setQueryData(jobDetailKey(parsed.id), parsed);
      await qc.prefetchQuery({
        queryKey: jobDetailKey(parsed.id),
        queryFn: () => fetchJobRecord(parsed.id),
        staleTime: Infinity,
      });

      endedRef.current = false;
      setJobId(parsed.id);
      setPhase("listening");
    } catch (err) {
      setPhase("error");
      setError(err instanceof Error ? err.message : String(err));
    }
  }, [prompt, qc]);

  return {
    phase,
    prompt,
    setPrompt,
    lastResponse,
    jobId,
    job,
    error,
    pipelineStageLabel,
    run,
    queryFetchError: jobQuery.error instanceof Error ? jobQuery.error.message : null,
  };
}
