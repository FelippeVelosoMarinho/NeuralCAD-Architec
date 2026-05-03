import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class JobCreate(BaseModel):
    model_config = ConfigDict(extra="allow")

    intent: Optional[dict[str, Any]] = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    payload_json: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    artifact_key: Optional[str] = None
    dimensional_audit: Optional[dict[str, Any]] = None
