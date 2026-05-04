"""Cliente Redis assíncrono partilhado (Pub/Sub canais de job)."""

from __future__ import annotations

import json
import os

from redis.asyncio import Redis


def redis_url_from_env() -> str:
    u = os.environ.get("REDIS_URL") or os.environ.get(
        "CELERY_BROKER_URL",
        "redis://localhost:6379/0",
    )
    return u


def job_channel(job_id: str) -> str:
    return f"neuralcad:job:{job_id}"


async def publish_json(redis: Redis, job_id: str, payload: dict) -> None:
    await redis.publish(job_channel(job_id), json.dumps(payload))
