import { useCallback, useEffect, useRef, useState } from "react";

import * as api from "../lib/api";

export type JobFlowPhase = "idle" | "eliciting" | "creating" | "polling" | "done" | "error";

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

/** Elicitar (best-effort), criar job e fazer polling até estado terminal. */
export function useJobFlow() {
  const [phase, setPhase] = useState<JobFlowPhase>("idle");
  const [prompt, setPrompt] = useState("caixa 100x50x25 mm");
  const [lastResponse, setLastResponse] = useState<unknown>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [job, setJob] = useState<JobRecord | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearPoll = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  useEffect(() => () => clearPoll(), [clearPoll]);

  const run = useCallback(async () => {
    setError(null);
    setLastResponse(null);
    setJob(null);
    setJobId(null);
    clearPoll();

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
        // Modo B: ANTHROPIC_API_KEY ausente → 503; seguimos com envelope fixo demo.
        setLastResponse({ note: "elicit skipped — using fallback envelope", prompt });
        envelope = FALLBACK_ENVELOPE;
      }

      setPhase("creating");
      const created = await api.postJob(envelope);
      setLastResponse(created);
      const parsed = parseJob(created);
      if (!parsed) throw new Error("resposta de criação de job inválida");
      setJobId(parsed.id);
      setJob(parsed);

      setPhase("polling");
      pollRef.current = setInterval(async () => {
        try {
          const j = await api.getJob(parsed.id);
          const pj = parseJob(j);
          if (!pj) return;
          setJob(pj);
          if (pj.status === "success" || pj.status === "failed") {
            clearPoll();
            setPhase(pj.status === "success" ? "done" : "error");
            setError(pj.error_message ?? null);
          }
        } catch (err) {
          clearPoll();
          setPhase("error");
          setError(err instanceof Error ? err.message : String(err));
        }
      }, 2000);
    } catch (err) {
      setPhase("error");
      setError(err instanceof Error ? err.message : String(err));
    }
  }, [clearPoll, prompt]);

  return { phase, prompt, setPrompt, lastResponse, jobId, job, error, run };
}
