"""Cliente Prompt Architect — Claude (Anthropic) ou Cursor via bridge HTTP."""

from __future__ import annotations

import json
import logging
import os
from typing import Callable

import httpx
from anthropic import Anthropic

from neuralcad_api.schemas.elicitation import (
    ElicitRejected,
    ElicitResult,
    ElicitSuccess,
    GeoRisk,
    parse_elicit_payload,
)
from neuralcad_api.schemas.intent_v1 import IntentSchemaV1
from neuralcad_api.services.intent_llm_normalize import normalize_intent_payload_for_v1

log = logging.getLogger(__name__)

MAX_ATTEMPTS = 2

VALID_BACKENDS = frozenset({"anthropic", "cursor"})

PROMPT_ARCHITECT_SYSTEM = """You are NeuralCAD Prompt Architect. Output ONLY one JSON object (no markdown fences, no explanatory text).

Discriminator field: kind ∈ success | clarification_needed | rejected

If kind=success, include top-level keys: kind, intent, geo_risk, attempt.
- "intent" MUST be a single object matching IntentSchemaV1 with camelCase keys exactly:
  sessionId (string), promptOriginal (string),
  intent: { objectType (string), style (JSON array of strings, never a single string), functionalGoal (string) },
  constraints: { optional dimensionsMm: {width, height, depth} all numbers > 0; symmetry; manufacturingHints; materialHints; thicknessMm — do NOT use keys "units", "box", "assumedAxisOrder" },
  optional topologyHints (object with expectedFacesRange, expectedEdgesRange, holes only — never a bare array),
  optional surfaceHints, generationConfig, qualityTargets.
- For simple prismatic parts you may OMIT optional blocks (topologyHints, surfaceHints, generationConfig, qualityTargets) entirely.
- geo_risk: { severity: info|warn|critical, messages: string[] }

If kind=clarification_needed: questions array (1-3 strings), optional missing_fields, attempt, max_attempts=2.

If kind=rejected: reason string.

Minimal valid success example (intent object only, for shape reference):
{"sessionId":"s1","promptOriginal":"user text here","intent":{"objectType":"box","style":[],"functionalGoal":"shape"},"constraints":{"dimensionsMm":{"width":100,"height":50,"depth":25},"symmetry":"none","manufacturingHints":[],"materialHints":[]}}
"""


def _normalize_backend() -> str:
    raw = os.environ.get("PROMPT_LLM_BACKEND", "anthropic").strip().lower()
    if raw not in VALID_BACKENDS:
        raise RuntimeError(
            f"PROMPT_LLM_BACKEND must be one of {sorted(VALID_BACKENDS)}, got {raw!r}"
        )
    return raw


def _cursor_combined_prompt(user_prompt: str) -> str:
    return (
        PROMPT_ARCHITECT_SYSTEM
        + "\n\n---\nNatural language request:\n"
        + user_prompt
    )


def _fetch_cursor_raw(user_prompt: str) -> str:
    base = os.environ.get("CURSOR_PROMPT_BRIDGE_URL", "").strip().rstrip("/")
    if not base:
        raise RuntimeError(
            "CURSOR_PROMPT_BRIDGE_URL is not set — required when PROMPT_LLM_BACKEND=cursor."
        )

    payload = {"prompt": _cursor_combined_prompt(user_prompt)}
    timeout_s = float(os.environ.get("CURSOR_BRIDGE_TIMEOUT_SECONDS", "600"))

    try:
        with httpx.Client(timeout=timeout_s) as client:
            r = client.post(f"{base}/v1/complete", json=payload)
    except httpx.RequestError as exc:
        raise RuntimeError(f"cursor prompt-bridge unreachable: {exc}") from exc

    if r.status_code >= 400:
        detail = ""
        try:
            detail = r.text[:1200]
        except Exception:
            pass
        raise RuntimeError(f"cursor prompt-bridge HTTP {r.status_code}: {detail}")

    try:
        data = r.json()
    except ValueError as exc:
        raise RuntimeError("cursor prompt-bridge returned invalid JSON body") from exc

    raw = data.get("raw")
    if not isinstance(raw, str) or not raw.strip():
        raise RuntimeError(
            'cursor prompt-bridge JSON missing non-empty string field "raw"'
        )
    log.debug("cursor bridge response length=%s", len(raw))
    return raw


def _fetch_anthropic_raw(client: Anthropic, user_prompt: str) -> str:
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    msg = client.messages.create(
        model=model,
        max_tokens=4096,
        system=PROMPT_ARCHITECT_SYSTEM,
        messages=[{"role": "user", "content": user_prompt}],
    )
    chunk = getattr(msg.content[0], "text", None)
    if not chunk:
        raise RuntimeError("empty response body from Anthropic Messages API")
    log.debug("anthropic response length=%s", len(chunk))
    return chunk


def _extract_json_blob(raw: str) -> dict[str, object]:
    t = raw.strip()
    if t.startswith("```"):
        nl = t.find("\n")
        t = t[nl + 1 :] if nl != -1 else t
        if "```" in t:
            t = t[: t.index("```")]
    t = t.strip()
    return json.loads(t)


def _severity_from_quality_targets(intent: IntentSchemaV1) -> str:
    qt = intent.quality_targets
    if qt is not None and qt.max_self_intersection_risk == "high":
        return "warn"
    return "info"


class PromptArchitectService:
    """Orquestra modelo (Anthropic ou Cursor bridge) + validação Pydantic."""

    def __init__(
        self,
        *,
        anthropic_client: Anthropic | None = None,
        cursor_fetch_raw: Callable[[str], str] | None = None,
    ) -> None:
        self._anthropic_client = anthropic_client
        self._cursor_fetch_raw = cursor_fetch_raw or _fetch_cursor_raw

    def elicit(self, prompt: str, attempt: int = 1) -> ElicitResult:
        backend = _normalize_backend()

        if backend == "cursor":
            chunk = self._cursor_fetch_raw(prompt)
        else:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key and self._anthropic_client is None:
                raise RuntimeError(
                    "ANTHROPIC_API_KEY is not set — cannot call PromptArchitectService "
                    "without injecting a mocked Anthropic client (PROMPT_LLM_BACKEND=anthropic)."
                )
            cli = self._anthropic_client or Anthropic(api_key=api_key)
            chunk = _fetch_anthropic_raw(cli, prompt)

        if not chunk:
            return ElicitRejected(reason="empty response body from LLM backend")

        try:
            raw_dict = _extract_json_blob(chunk)
        except json.JSONDecodeError as exc:
            return ElicitRejected(reason=f"model output is not valid JSON: {exc}")
        except (TypeError, ValueError) as exc:
            return ElicitRejected(reason=f"unable to decode model JSON blob: {exc}")

        kind = raw_dict.get("kind")
        if kind == "clarification_needed" and attempt >= MAX_ATTEMPTS:
            return ElicitRejected(
                reason="maximum clarification rounds reached without a valid intent."
            )

        try:
            if kind == "success":
                inner = raw_dict.get("intent")
                if not isinstance(inner, dict):
                    return ElicitRejected(reason='success response missing object field "intent"')
                normalized = normalize_intent_payload_for_v1(inner, fallback_prompt=prompt)
                intent = IntentSchemaV1.model_validate(normalized)
                geo_in = raw_dict.get("geo_risk") or {}
                msgs = geo_in.get("messages")
                if not isinstance(msgs, list) or not msgs:
                    msgs = [_severity_heuristic_note(_severity_from_quality_targets(intent))]
                sev = geo_in.get("severity")
                if sev not in ("info", "warn", "critical"):
                    sev = _severity_from_quality_targets(intent)
                geo = GeoRisk(severity=sev, messages=[str(m) for m in msgs])
                return ElicitSuccess(
                    intent=intent,
                    geo_risk=geo,
                    attempt=int(raw_dict.get("attempt") or attempt),
                )
            return parse_elicit_payload(raw_dict)
        except Exception as exc:
            log.warning("elicit parse failure: %s", exc)
            return ElicitRejected(reason=f"failed to normalize model output: {exc}")


def _severity_heuristic_note(heuristic: str) -> str:
    return f"Baseline geometry risk heuristic: {heuristic}"
