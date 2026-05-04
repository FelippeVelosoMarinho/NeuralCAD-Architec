"""Smoke tests realtime (DELETE + WS handshake) sem Postgres."""

from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import fakeredis.aioredis as fakeredis_async
import pytest
from starlette.websockets import WebSocketDisconnect
from fastapi.testclient import TestClient

from neuralcad_api import main as main_module
from neuralcad_api.main import app, get_db


@pytest.fixture
def jid() -> uuid.UUID:
    return uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")


@pytest.fixture
def ws_session_id() -> str:
    return "11111111-2222-4333-8444-555555555555"


def test_cancel_returns_409_for_terminal_jobs(jid: uuid.UUID, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main_module.Redis, "from_url", lambda *a, **k: fakeredis_async.FakeRedis(decode_responses=True))

    class Row:
        id = jid
        status = "success"

    class FakeSession:
        async def execute(self, _stmt: object) -> object:
            class _Res:
                def scalar_one_or_none(self_inner) -> object:
                    return Row()

            return _Res()

        async def commit(self) -> None: ...

        async def refresh(self, _job: object) -> None: ...

    async def _ov() -> AsyncIterator[FakeSession]:
        yield FakeSession()

    app.dependency_overrides[get_db] = _ov

    try:
        with TestClient(main_module.app, raise_server_exceptions=False) as client:
            r = client.delete(f"/api/v1/jobs/{jid}")
            assert r.status_code == 409
            assert r.json()["detail"]["reason"] == "job_terminal"
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_cancel_pending_returns_cancelled(monkeypatch: pytest.MonkeyPatch, jid: uuid.UUID) -> None:
    monkeypatch.setattr(main_module.Redis, "from_url", lambda *a, **k: fakeredis_async.FakeRedis(decode_responses=True))

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    class MutableRow:
        def __init__(self, job_id: uuid.UUID) -> None:
            self.id = job_id
            self.status = "pending"
            self.celery_task_id = "celery-async-id-99"
            self.created_at = now
            self.updated_at = now
            self.payload_json = None
            self.error_message = None
            self.artifact_key = None
            self.dimensional_audit = None

    mutable = MutableRow(jid)

    class FakeSession:
        async def execute(self, _stmt: object) -> object:
            class _Res:
                def scalar_one_or_none(self_inner: object) -> object:
                    return mutable

            return _Res()

        async def commit(self) -> None: ...

        async def refresh(self, _job: object) -> None: ...

    revoke_calls: list[str] = []

    def fake_revoke(tid: str, *, terminate: bool = False) -> None:  # noqa: ARG001
        revoke_calls.append(tid)

    monkeypatch.setattr(main_module.celery_app.control, "revoke", fake_revoke)

    async def _ov() -> AsyncIterator[FakeSession]:
        yield FakeSession()

    app.dependency_overrides[get_db] = _ov

    try:
        with TestClient(main_module.app, raise_server_exceptions=False) as client:
            r = client.delete(f"/api/v1/jobs/{jid}")
            assert r.status_code == 200
            body = r.json()
            assert body["status"] == "cancelled"
            assert revoke_calls == ["celery-async-id-99"]
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_ws_rejected_without_client_session(jid: uuid.UUID, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main_module.Redis, "from_url", lambda *a, **k: fakeredis_async.FakeRedis(decode_responses=True))

    with TestClient(main_module.app, raise_server_exceptions=False) as client:
        with pytest.raises(WebSocketDisconnect) as ei:
            with client.websocket_connect(f"/ws/jobs/{jid}"):
                pass
        assert ei.value.code in (4401, 403, 4000)


def test_ws_handshake_emits_ready_and_optional_redis_message(
    jid: uuid.UUID,
    ws_session_id: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_r = fakeredis_async.FakeRedis(decode_responses=True)
    monkeypatch.setattr(main_module.Redis, "from_url", lambda *a, **k: fake_r)

    @asynccontextmanager
    async def fake_session_cm() -> AsyncIterator[FakeSessionMinimal]:
        class FakeSessionMinimal:
            async def execute(self, *_a, **_k) -> FakeResult:
                class JobLike:
                    id = jid

                class FakeResult:
                    def scalar_one_or_none(self_inner) -> object:
                        return JobLike()

                return FakeResult()

        yield FakeSessionMinimal()

    import neuralcad_api.ws.job_channel as jc

    monkeypatch.setattr(jc, "async_session_maker", fake_session_cm)

    import neuralcad_api.db.session as session_mod

    monkeypatch.setattr(session_mod, "async_session_maker", fake_session_cm)

    monkeypatch.setattr(main_module.Redis, "from_url", lambda *a, **k: fake_r)

    envelope = {"schemaVersion": "1", "type": "job.progress"}

    channel = f"neuralcad:job:{jid}"

    async def _publish_after_subscribed() -> None:
        await fake_r.publish(channel, json.dumps(envelope))

    with TestClient(main_module.app, raise_server_exceptions=False) as client:
        with client.websocket_connect(
            f"/ws/jobs/{jid}?client_session={ws_session_id}",
            auth=None,
        ) as websocket:
            first = websocket.receive_text()
            data = json.loads(first)
            assert data["type"] == "channel.ready"
            asyncio.run(_publish_after_subscribed())
            second = websocket.receive_text()
            outer = json.loads(second)
            assert outer["type"] == "job.progress"
