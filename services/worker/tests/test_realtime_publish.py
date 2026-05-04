"""Smoke fakeredis sobre `neuralcad_worker.realtime.publish`."""

from __future__ import annotations

import json
import uuid

import fakeredis
import pytest

from neuralcad_worker.realtime import build_envelope, publish


@pytest.fixture(autouse=True)
def clear_redis_client(monkeypatch: pytest.MonkeyPatch) -> None:
    import neuralcad_worker.realtime as rt

    monkeypatch.setattr(rt, "_client", None)


def test_publish_writes_envelope_to_channel(monkeypatch: pytest.MonkeyPatch) -> None:
    import neuralcad_worker.realtime as rt

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(rt, "_client", fake)

    jid = str(uuid.uuid4())
    envelope = build_envelope(jid, "job.lifecycle", {"lifecycle": "running"})
    channel = f"neuralcad:job:{jid}"

    pubsub = fake.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(channel)

    publish(jid, envelope)

    data = None
    for _ in range(20):
        m = pubsub.get_message(timeout=1.0)
        if not m:
            continue
        if m.get("type") == "message":
            raw = m.get("data")
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            data = json.loads(raw) if isinstance(raw, str) else None
            break

    assert data is not None
    assert data["type"] == "job.lifecycle"
    assert data["jobId"] == jid
    assert data["detail"]["lifecycle"] == "running"
