/** UUID por separador (sessionStorage) — CONTEXT D‑04‑11 / PLAN 04‑03. */

const STORAGE_KEY = "neuralcad:tab_client_session_v1";

export function getTabClientSession(storage: Pick<Storage, "getItem" | "setItem">): string {
  try {
    const existing = storage.getItem(STORAGE_KEY);
    if (existing) return existing;
    const next = crypto.randomUUID();
    storage.setItem(STORAGE_KEY, next);
    return next;
  } catch {
    /* sessionStorage pode falhar (modo estrito); fallback ephemeral */
    return crypto.randomUUID();
  }
}
