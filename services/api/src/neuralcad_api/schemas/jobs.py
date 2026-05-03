import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, ValidationError

from neuralcad_api.schemas.elicitation import GeoRisk
from neuralcad_api.schemas.intent_v1 import IntentSchemaV1
from neuralcad_api.services.payload_normalize import normalize_legacy_intent_payload


class PreflightEnvelope(BaseModel):
    """Preflight obrigatório quando presente inclui métricas de risco geométrico."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    geo_risk: GeoRisk


class IntentJobEnvelope(BaseModel):
    """Criação de job com IntentSchema validado mais snapshot opcional de preflight."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    intent: IntentSchemaV1
    preflight: Optional[PreflightEnvelope] = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    payload_json: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    artifact_key: Optional[str] = None
    dimensional_audit: Optional[dict[str, Any]] = None


def persist_payload_from_envelope(envelope: IntentJobEnvelope) -> dict[str, Any]:
    """Serializa modelo canónico + preflight para `jobs.payload_json`."""
    payload: dict[str, Any] = dict(envelope.intent.model_dump(by_alias=True, mode="json"))
    if envelope.preflight is not None:
        payload["preflight"] = envelope.preflight.model_dump(mode="json", by_alias=True)
    payload.setdefault("schemaVersion", "1")
    return payload


def parse_job_envelope_with_legacy_retry(raw: dict) -> IntentJobEnvelope:
    """Um parse directo ou, falhando, uma normalização legada antes de segunda validação."""
    try:
        return IntentJobEnvelope.model_validate(raw)
    except ValidationError:
        normalized = normalize_legacy_intent_payload(raw)
        return IntentJobEnvelope.model_validate(normalized)

