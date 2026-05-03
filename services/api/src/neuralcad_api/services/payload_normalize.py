"""Normalização pontual payloads legados (Fase 1) antes de validação strict."""

from __future__ import annotations


def _promote_dimensions_into_constraints(intent_node: dict) -> None:
    """
    Copia ``dimensionsMm`` para ``constraints.dimensionsMm`` no mesmo nível onde vive um
    IntentSchemaV1 quando ainda só existir sob o bloco legado ``intent.constraints``.
    Remove o dict ``constraints`` inválido dentro do IntentBlock quando promove dims.
    """
    cons = intent_node.get("constraints")
    if isinstance(cons, dict):
        cons = dict(cons)
    else:
        cons = {}
    if cons.get("dimensionsMm") is not None:
        intent_node["constraints"] = cons
        return

    inner_block = intent_node.get("intent")
    misplaced: dict | None = None
    if isinstance(inner_block, dict):
        ic = inner_block.get("constraints")
        if isinstance(ic, dict) and ic.get("dimensionsMm") is not None:
            misplaced = ic["dimensionsMm"]
            inner_block.pop("constraints", None)

    if misplaced is not None:
        cons["dimensionsMm"] = misplaced
    intent_node["constraints"] = cons


def normalize_legacy_intent_payload(data: dict) -> dict:
    """
    - Envelope Job: corrige apenas ``data["intent"]`` (IntentSchema) e remove ruído na raíz.
    - IntentSchema plano na raíz: corrige esse dict.
    - ``schemaVersion`` é definido em ``persist_payload_from_envelope``; aqui não se adiciona
      chaves estranhas ao envelope (para ``IntentJobEnvelope`` com ``extra=forbid``).
    """
    out = dict(data)

    inner = out.get("intent")
    if isinstance(inner, dict) and (inner.get("sessionId") or inner.get("promptOriginal")):
        out.pop("constraints", None)
        _promote_dimensions_into_constraints(inner)
        return out

    _promote_dimensions_into_constraints(out)
    return out
