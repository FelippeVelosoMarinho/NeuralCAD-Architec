import { getApiBase } from "./env";

/** Corpo envelope job (JSON compatível com `IntentJobEnvelope` na API). */
export type IntentEnvelopeJson = Record<string, unknown>;

export async function postIntentElicit(prompt: string, attempt = 1): Promise<unknown> {
  const r = await fetch(`${getApiBase()}/api/v1/intent/elicit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, attempt }),
  });
  const text = await r.text();
  let data: unknown;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  if (!r.ok) {
    const err = new Error(`elicit ${r.status}`);
    Object.assign(err, { body: data });
    throw err;
  }
  return data;
}

export async function postJob(body: IntentEnvelopeJson): Promise<unknown> {
  const r = await fetch(`${getApiBase()}/api/v1/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const text = await r.text();
  let data: unknown;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  if (!r.ok) {
    const err = new Error(`job create ${r.status}`);
    Object.assign(err, { body: data });
    throw err;
  }
  return data;
}

export async function getJob(id: string): Promise<unknown> {
  const r = await fetch(`${getApiBase()}/api/v1/jobs/${id}`);
  const text = await r.text();
  let data: unknown;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  if (!r.ok) {
    const err = new Error(`get job ${r.status}`);
    Object.assign(err, { body: data });
    throw err;
  }
  return data;
}
