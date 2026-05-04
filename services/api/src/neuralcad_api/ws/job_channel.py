"""WebSocket ligado ao canal Redis por job (`neuralcad:job:{id}`)."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neuralcad_api.db.models import Job
from neuralcad_api.db.session import async_session_maker
from neuralcad_api.realtime_envelope import channel_ready_envelope

logger = logging.getLogger(__name__)
router = APIRouter()


def _parse_client_session(raw: str | None) -> uuid.UUID | None:
    if not raw or not raw.strip():
        return None
    try:
        return uuid.UUID(raw.strip())
    except ValueError:
        return None


async def _discard_client_messages(websocket: WebSocket) -> None:
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        return
    except Exception:  # noqa: BLE001
        return


@router.websocket("/ws/jobs/{job_id}")
async def job_channel_ws(websocket: WebSocket, job_id: uuid.UUID) -> None:
    query = dict(websocket.query_params)
    client_session = _parse_client_session(query.get("client_session"))
    if client_session is None:
        await websocket.close(code=4401, reason="client_session UUID obrigatório na query")
        return

    async with async_session_maker() as db:
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
    if job is None:
        await websocket.close(code=4404, reason="job não encontrado")
        return

    redis = websocket.app.state.redis
    if redis is None:
        await websocket.close(code=1011, reason="Redis indisponível")
        return

    channel = f"neuralcad:job:{job_id}"
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)

    await websocket.accept()
    ready = channel_ready_envelope(str(job_id), str(client_session))
    await websocket.send_text(json.dumps(ready))

    drain = asyncio.create_task(_discard_client_messages(websocket))

    try:
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=30.0)
            if msg is None:
                continue
            if msg.get("type") != "message":
                continue
            data = msg.get("data")
            if data is None:
                continue
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            await websocket.send_text(data)
    except WebSocketDisconnect:
        logger.debug("ws disconnect job_id=%s", job_id)
    finally:
        drain.cancel()
        try:
            await drain
        except asyncio.CancelledError:
            pass
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
