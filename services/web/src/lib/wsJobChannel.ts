import { getApiBase } from "./env";

/** Upgrade HTTP(S) FastAPI para WS no mesmo host. */
export function jobChannelWsUrl(jobId: string, clientSession: string): string {
  const api = getApiBase();
  const parsed = new URL(api);
  const wsScheme = parsed.protocol === "https:" ? "wss:" : "ws:";
  const base =
    parsed.pathname.replace(/\/$/, "") +
    `/ws/jobs/${encodeURIComponent(jobId)}` +
    `?client_session=${encodeURIComponent(clientSession)}`;
  return `${wsScheme}//${parsed.host}${base}`;
}
