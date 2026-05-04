import os
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Job(Base):
    """Espelha `neuralcad_api.db.models.Job` — mesma tabela `jobs`."""

    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    status: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    payload_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    artifact_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    dimensional_audit: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


def sync_engine():
    from sqlalchemy import create_engine

    url = os.environ.get("DATABASE_URL_SYNC", "postgresql://neuralcad:change_me@localhost:5432/neuralcad")
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        url = "postgresql+psycopg2://" + url.split("postgresql://", 1)[1]
    return create_engine(url, pool_pre_ping=True)


def sync_session():
    from sqlalchemy.orm import sessionmaker

    return sessionmaker(sync_engine(), expire_on_commit=False)
