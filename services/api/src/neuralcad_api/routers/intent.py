"""Rotas relacionadas ao Prompt Architect (`/api/v1/intent/elicit`)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from neuralcad_api.schemas.elicitation import ElicitClarification, ElicitRejected, ElicitSuccess
from neuralcad_api.services.prompt_architect import MAX_ATTEMPTS, PromptArchitectService

router = APIRouter(tags=["intent"])


class PromptElicitBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(min_length=1)
    attempt: int = Field(default=1, ge=1, le=MAX_ATTEMPTS)


@router.post("/api/v1/intent/elicit")
async def intent_elicit(body: PromptElicitBody):
    """POST /api/v1/intent/elicit — texto natural ⇒ intent válido OU clarificação/rejeição (422)."""
    try:
        svc = PromptArchitectService()
        result = svc.elicit(body.prompt, body.attempt)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if isinstance(result, ElicitSuccess):
        return result.model_dump(mode="json")
    if isinstance(result, (ElicitClarification, ElicitRejected)):
        raise HTTPException(status_code=422, detail=result.model_dump(mode="json"))
    raise HTTPException(status_code=500, detail="unexpected elicit result")
