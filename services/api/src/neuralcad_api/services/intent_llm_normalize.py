"""
Normaliza saídas típicas de LLM (chaves extra, tipos errados) até `IntentSchemaV1`.
"""

from __future__ import annotations

import copy
import uuid
from typing import Any, Mapping


def _str_list(x: Any) -> list[str]:
    if x is None:
        return []
    if isinstance(x, str):
        return [x] if x.strip() else []
    if isinstance(x, (list, tuple)):
        return [str(i) for i in x]
    return []


def _dimensions_from_alternate_box(box: Mapping[str, Any]) -> dict[str, float] | None:
    if {"width", "height", "depth"} <= box.keys():
        try:
            return {
                "width": float(box["width"]),
                "height": float(box["height"]),
                "depth": float(box["depth"]),
            }
        except (TypeError, ValueError):
            return None
    if {"length", "width", "height"} <= box.keys():
        try:
            return {
                "width": float(box["length"]),
                "height": float(box["height"]),
                "depth": float(box["width"]),
            }
        except (TypeError, ValueError):
            return None
    return None


def _normalize_quality_targets(qt: dict[str, Any]) -> dict[str, Any]:
    wt = qt.get("preferWatertight")
    if wt is None:
        wt = qt.get("watertight")
    if wt is None:
        wt = qt.get("manifold")
    if wt is None:
        wt = True

    risk = qt.get("maxSelfIntersectionRisk")
    if risk not in ("low", "medium", "high"):
        risk = "low"

    return {"preferWatertight": bool(wt), "maxSelfIntersectionRisk": risk}


def normalize_intent_payload_for_v1(data: dict[str, Any], *, fallback_prompt: str) -> dict[str, Any]:
    """
    Copia defensiva + coerções mínimas antes de `IntentSchemaV1.model_validate`.
    """
    d: dict[str, Any] = copy.deepcopy(data)

    sid = d.get("sessionId")
    if not isinstance(sid, str) or not sid.strip():
        d["sessionId"] = f"llm-{uuid.uuid4().hex[:12]}"

    po = d.get("promptOriginal")
    if not isinstance(po, str) or not po.strip():
        d["promptOriginal"] = fallback_prompt.strip() or "(empty prompt)"

    inner = d.get("intent")
    if not isinstance(inner, dict):
        inner = {"objectType": "box", "style": [], "functionalGoal": "unspecified"}
    else:
        inner = copy.deepcopy(inner)
        inner["style"] = _str_list(inner.get("style"))
        if not isinstance(inner.get("objectType"), str) or not str(inner["objectType"]).strip():
            inner["objectType"] = "box"
        if not isinstance(inner.get("functionalGoal"), str) or not str(inner["functionalGoal"]).strip():
            inner["functionalGoal"] = "unspecified"
    d["intent"] = inner

    cons = d.get("constraints")
    if not isinstance(cons, dict):
        cons = {}
    else:
        cons = copy.deepcopy(cons)

    alt_box = cons.get("box") if isinstance(cons.get("box"), dict) else None
    cons.pop("units", None)
    cons.pop("assumedAxisOrder", None)
    cons.pop("box", None)

    if not cons.get("dimensionsMm") and alt_box is not None:
        mm = _dimensions_from_alternate_box(alt_box)
        if mm:
            cons["dimensionsMm"] = mm

    if cons.get("symmetry") is None:
        cons["symmetry"] = "none"
    if not isinstance(cons.get("manufacturingHints"), list):
        cons["manufacturingHints"] = _str_list(cons.get("manufacturingHints"))
    if not isinstance(cons.get("materialHints"), list):
        cons["materialHints"] = _str_list(cons.get("materialHints"))

    d["constraints"] = cons

    th = d.get("topologyHints")
    if isinstance(th, dict):
        ok = (
            isinstance(th.get("expectedFacesRange"), (list, tuple))
            and len(th.get("expectedFacesRange", ())) == 2
            and isinstance(th.get("expectedEdgesRange"), (list, tuple))
            and len(th.get("expectedEdgesRange", ())) == 2
            and isinstance(th.get("holes"), list)
        )
        if not ok:
            d.pop("topologyHints", None)
        else:
            clean_holes = []
            for h in th.get("holes", []):
                if isinstance(h, dict) and h.get("type") in ("concentric", "through", "blind"):
                    try:
                        c = int(h.get("count", 0))
                    except (TypeError, ValueError):
                        continue
                    clean_holes.append({"type": h["type"], "count": max(0, c)})
            th = {**th, "holes": clean_holes}
            d["topologyHints"] = th
    elif th is not None:
        d.pop("topologyHints", None)

    for opt in ("surfaceHints",):
        sub = d.get(opt)
        if sub is not None and not isinstance(sub, dict):
            d.pop(opt, None)

    sh = d.get("surfaceHints")
    if isinstance(sh, dict):
        need = {"curvature", "freeform", "continuityPreference"}
        if not need <= set(sh.keys()):
            d.pop("surfaceHints", None)

    gen = d.get("generationConfig")
    if isinstance(gen, dict):
        allowed = {
            "mode",
            "numSurfaces",
            "numEdgesPerSurface",
            "bboxThreshold",
            "zThreshold",
        }
        for k in list(gen.keys()):
            if k not in allowed:
                gen.pop(k, None)
        required = ("mode", "numSurfaces", "numEdgesPerSurface", "bboxThreshold", "zThreshold")
        if not all(k in gen for k in required):
            d.pop("generationConfig", None)

    qt = d.get("qualityTargets")
    if isinstance(qt, dict):
        try:
            d["qualityTargets"] = _normalize_quality_targets(qt)
        except Exception:
            d.pop("qualityTargets", None)
    elif qt is not None:
        d.pop("qualityTargets", None)

    return d
