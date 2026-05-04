import asyncio
import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Literal

import boto3
from botocore.exceptions import ClientError
from celery import Celery
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from neuralcad_api.db.models import Job
from neuralcad_api.db.session import async_session_maker, engine
from neuralcad_api.realtime_envelope import cancelled_envelope, lifecycle_envelope
from neuralcad_api.routers.intent import router as intent_router
from neuralcad_api.schemas.jobs import (
    JobResponse,
    parse_job_envelope_with_legacy_retry,
    persist_payload_from_envelope,
)
from neuralcad_api.services.redis_bus import publish_json, redis_url_from_env
from neuralcad_api.ws.job_channel import router as job_ws_router

logger = logging.getLogger(__name__)

celery_app = Celery(
    "neuralcad_api",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.environ.get(
        "CELERY_RESULT_BACKEND",
        os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    ),
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    redis: Redis | None = None
    try:
        redis = Redis.from_url(redis_url_from_env(), decode_responses=True)
        await redis.ping()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Redis inicialização falhou — WS realtime desactivado (%s)", exc)
        redis = None
    app.state.redis = redis  # None evita handshake WS em dev sem broker
    yield
    if redis is not None:
        await redis.aclose()
    await engine.dispose()


app = FastAPI(title="NeuralCAD Architect API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(intent_router)
app.include_router(job_ws_router)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


def _minio_client():
    return boto3.client(
        "s3",
        endpoint_url=os.environ.get("MINIO_ENDPOINT", "http://127.0.0.1:9000"),
        aws_access_key_id=os.environ["MINIO_ACCESS_KEY"],
        aws_secret_access_key=os.environ["MINIO_SECRET_KEY"],
        region_name="us-east-1",
    )


def _artifact_key_for_kind(primary: str | None, kind: Literal["step", "stl"]) -> str | None:
    if not primary:
        return None
    if kind == "step":
        return primary
    if primary.endswith(".step"):
        return primary[:-5] + ".stl"
    base = primary.rsplit(".", 1)[0]
    return f"{base}.stl"


@app.post("/api/v1/jobs", response_model=JobResponse)
async def create_job(request: Request, db: AsyncSession = Depends(get_db)) -> Job:
    # TODO: auth phase N
    body = await request.json()
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Job body must be a JSON object")
    try:
        envelope = parse_job_envelope_with_legacy_retry(body)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=jsonable_encoder(exc.errors())) from exc
    payload_json = persist_payload_from_envelope(envelope)
    job = Job(status="pending", payload_json=payload_json)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    redis: Redis | None = request.app.state.redis
    try:
        ar = await asyncio.to_thread(
            celery_app.send_task,
            "process_geometry_job",
            args=[str(job.id)],
        )
        tid = getattr(ar, "id", None)
        if tid:
            job.celery_task_id = tid
            await db.commit()
            await db.refresh(job)
    except Exception as exc:  # noqa: BLE001
        logger.exception("enqueue Celery falhou job_id=%s", job.id)
        raise HTTPException(status_code=502, detail="failed to enqueue worker task") from exc
    return job


@app.delete("/api/v1/jobs/{job_id}", response_model=JobResponse)
async def cancel_job(job_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db)) -> Job:
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")

    terminal = frozenset({"success", "failed", "cancelled"})
    if job.status in terminal:
        raise HTTPException(
            status_code=409,
            detail={"reason": "job_terminal", "status": job.status},
        )

    job.status = "cancelled"
    tid = job.celery_task_id
    redis: Redis | None = request.app.state.redis
    await db.commit()
    await db.refresh(job)

    if tid:
        await asyncio.to_thread(
            lambda t=tid: celery_app.control.revoke(t, terminate=True),
        )
    else:
        logger.warning("DELETE job sem celery_task_id (corrida enqueue?) — job_id=%s", job_id)

    if redis is not None:
        await publish_json(
            redis,
            str(job_id),
            lifecycle_envelope(str(job_id), "cancelled"),
        )
        await publish_json(
            redis,
            str(job_id),
            cancelled_envelope(str(job_id)),
        )

    return job


@app.get("/api/v1/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Job:
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job


@app.get("/api/v1/jobs/{job_id}/artifacts/{kind}")
async def get_job_artifact(
    job_id: uuid.UUID,
    kind: Literal["step", "stl"],
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Descarrega STEP ou STL correspondente ao job (MinIO via S3 API)."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    if job.status != "success":
        raise HTTPException(status_code=409, detail="artifact not ready")
    key = _artifact_key_for_kind(job.artifact_key, kind)
    if not key:
        raise HTTPException(status_code=404, detail="no artifact key")
    bucket = os.environ.get("MINIO_BUCKET", "neuralcad-artifacts")

    def _load() -> bytes:
        cli = _minio_client()
        try:
            obj = cli.get_object(Bucket=bucket, Key=key)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            raise FileNotFoundError(code or str(exc)) from exc
        return obj["Body"].read()

    try:
        data = await asyncio.to_thread(_load)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"object missing: {exc}") from exc

    if len(data) > 32 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="artifact too large")

    media = "application/step" if kind == "step" else "model/stl"
    return Response(content=data, media_type=media)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
