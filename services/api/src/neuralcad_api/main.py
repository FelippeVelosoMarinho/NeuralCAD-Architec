import os
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from celery import Celery
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neuralcad_api.db.models import Job
from neuralcad_api.db.session import async_session_maker, engine
from neuralcad_api.schemas.jobs import JobCreate, JobResponse

celery_app = Celery(
    "neuralcad_api",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.environ.get(
        "CELERY_RESULT_BACKEND",
        os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    ),
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await engine.dispose()


app = FastAPI(title="NeuralCAD Architect API", lifespan=lifespan)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@app.post("/api/v1/jobs", response_model=JobResponse)
async def create_job(
    body: JobCreate | None = None,
    db: AsyncSession = Depends(get_db),
) -> Job:
    # TODO: auth phase N
    data = (body or JobCreate()).model_dump(exclude_none=True)
    payload = data if data else None
    job = Job(status="pending", payload_json=payload)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    celery_app.send_task("process_geometry_job", args=[str(job.id)])
    return job


@app.get("/api/v1/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Job:
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
