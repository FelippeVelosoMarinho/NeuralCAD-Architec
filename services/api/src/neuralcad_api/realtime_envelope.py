"""Contrato Redis/WS tempo real (`schemaVersion` 1) — uso na API."""

from __future__ import annotations

from datetime import datetime, timezone


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def envelope_v1(job_id: str, msg_type: str, *, detail: dict | None = None) -> dict:
    """Mensagem canónica publicada em `neuralcad:job:{job_id}` (texto JSON)."""
    return {
        "schemaVersion": "1",
        "ts": utc_iso(),
        "type": msg_type,
        "jobId": str(job_id),
        "detail": detail or {},
    }


def lifecycle_envelope(job_id: str, phase: str) -> dict:
    return envelope_v1(job_id, "job.lifecycle", detail={"lifecycle": phase})


def progress_envelope(job_id: str, pipeline_stage: str) -> dict:
    return envelope_v1(job_id, "job.progress", detail={"pipelineStage": pipeline_stage})


def cancelled_envelope(job_id: str) -> dict:
    return envelope_v1(job_id, "job.cancelled", detail={})


def channel_ready_envelope(job_id: str, client_session: str) -> dict:
    return envelope_v1(
        job_id,
        "channel.ready",
        detail={"clientSession": client_session},
    )
