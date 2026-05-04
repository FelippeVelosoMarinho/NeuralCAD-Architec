"""Publicação síncrona Redis no canal neuralcad:job:{id}."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import redis

logger = logging.getLogger(__name__)

_client: redis.Redis | None = None


def _redis_client() -> redis.Redis | None:
    global _client
    if _client is not None:
        return _client
    url = os.environ.get("REDIS_URL") or os.environ.get(
        "CELERY_BROKER_URL",
        "redis://localhost:6379/0",
    )
    try:
        _client = redis.Redis.from_url(url, decode_responses=True)
        _client.ping()
        return _client
    except Exception as exc:  # noqa: BLE001
        logger.warning("worker redis publish desactivado: %s", exc)
        return None


def build_envelope(job_id: str, msg_type: str, detail: dict[str, Any] | None = None) -> dict:
    return {
        "schemaVersion": "1",
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": msg_type,
        "jobId": str(job_id),
        "detail": detail or {},
    }


def publish(job_id: str, envelope: dict) -> None:
    r = _redis_client()
    if r is None:
        return
    try:
        r.publish(f"neuralcad:job:{job_id}", json.dumps(envelope))
    except Exception as exc:  # noqa: BLE001
        logger.warning("redis publish falhou job_id=%s: %s", job_id, exc)
