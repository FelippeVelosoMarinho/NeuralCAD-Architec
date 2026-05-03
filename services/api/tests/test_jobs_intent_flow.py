"""Fluxo jobs + envelope + normalização legada (fase 02-03)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from neuralcad_api import main as main_module
from neuralcad_api.main import app, get_db
from neuralcad_api.schemas.jobs import (
    IntentJobEnvelope,
    parse_job_envelope_with_legacy_retry,
    persist_payload_from_envelope,
)
from neuralcad_api.services.payload_normalize import normalize_legacy_intent_payload
import test_intent_schema


def _inner_intent_missing_dims_with_misplaced_block() -> dict:
    """IntentSchema onde ``dimensionsMm`` está só sob ``intent.constraints`` (legado)."""
    return {
        "sessionId": "s-legacy",
        "promptOriginal": "nested dims only",
        "intent": {
            "objectType": "box",
            "style": [],
            "functionalGoal": "demo",
            "constraints": {
                "dimensionsMm": {"width": 55.0, "height": 66.0, "depth": 77.0},
            },
        },
        "constraints": {
            "symmetry": "none",
            "manufacturingHints": [],
            "materialHints": [],
        },
    }


def test_normalize_promotes_dimensions_from_inner_intent_constraints():
    inner = _inner_intent_missing_dims_with_misplaced_block()
    body = {"intent": inner}

    normed = normalize_legacy_intent_payload(body)
    dims = normed["intent"]["constraints"]["dimensionsMm"]
    assert dims["width"] == 55.0
    IntentJobEnvelope.model_validate(normed)


def test_parse_job_envelope_retry_after_normalize_wrapped_legacy():
    """Envelope válido onde ``dimensionsMm`` vem só do caminho ``intent.constraints`` errado no bloco interno."""
    body = {"intent": _inner_intent_missing_dims_with_misplaced_block()}
    env = parse_job_envelope_with_legacy_retry(body)
    assert isinstance(env, IntentJobEnvelope)
    dm = env.intent.constraints.dimensions_mm
    assert dm is not None
    assert dm.width == 55.0


def test_parse_job_envelope_wrapped_preflight_geo_risk():
    intent_dict = json.loads(test_intent_schema.CANON_JSON)
    wrapped = {
        "intent": intent_dict,
        "preflight": {
            "geo_risk": {"severity": "warn", "messages": ["check"], "related_field": None}
        },
    }
    env = parse_job_envelope_with_legacy_retry(wrapped)
    payload = persist_payload_from_envelope(env)
    assert payload["preflight"]["geo_risk"]["severity"] == "warn"
    assert payload["preflight"]["geo_risk"]["messages"] == ["check"]
    assert payload.get("schemaVersion") == "1"


def test_intent_job_envelope_extra_top_level_forbidden():
    with pytest.raises(ValidationError):
        IntentJobEnvelope.model_validate(
            {
                "evil": True,
                "intent": json.loads(test_intent_schema.CANON_JSON),
            }
        )


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(main_module.celery_app, "send_task", MagicMock())

    class _FakeDb:
        def __init__(self) -> None:
            self.saved: list = []

        def add(self, obj: object) -> None:
            self.saved.append(obj)
            now = datetime.now(timezone.utc)
            setattr(obj, "id", uuid.uuid4())
            setattr(obj, "created_at", now)
            setattr(obj, "updated_at", now)

        async def commit(self) -> None:  # noqa: D401
            return None

        async def refresh(self, obj: object) -> None:  # noqa: D401
            return None

    fake = _FakeDb()

    async def _override_db():
        yield fake  # type: ignore[misc]

    app.dependency_overrides[get_db] = _override_db
    with TestClient(app) as tc:
        yield tc, fake
    app.dependency_overrides.pop(get_db, None)


def test_post_jobs_persists_preflight_and_enqueues(monkeypatch, client):
    tc, fake = client
    intent_dict = json.loads(test_intent_schema.CANON_JSON)
    wrapped = {
        "intent": intent_dict,
        "preflight": {
            "geo_risk": {"severity": "info", "messages": ["ok"]},
        },
    }

    resp = tc.post("/api/v1/jobs", json=wrapped)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "id" in data
    job = fake.saved[-1]
    assert job.payload_json["preflight"]["geo_risk"]["severity"] == "info"
    assert main_module.celery_app.send_task.called
