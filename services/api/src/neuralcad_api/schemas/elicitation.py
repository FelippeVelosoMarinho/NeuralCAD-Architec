"""Respostas do Prompt Architect (discriminador `kind`)."""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

from neuralcad_api.schemas.intent_v1 import IntentSchemaV1


class GeoRisk(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    severity: Literal["info", "warn", "critical"]
    messages: list[str] = Field(min_length=1)
    related_field: str | None = None


class ElicitSuccess(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["success"] = "success"
    intent: IntentSchemaV1
    geo_risk: GeoRisk
    attempt: int = Field(ge=1)


class ElicitClarification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["clarification_needed"] = "clarification_needed"
    questions: list[str]
    missing_fields: list[str] = Field(default_factory=list)
    attempt: int = Field(ge=1)
    max_attempts: int = 2

    @field_validator("questions")
    @classmethod
    def _max_three(cls, qs: list[str]) -> list[str]:
        if len(qs) > 3:
            raise ValueError("at most 3 clarifying questions")
        if len(qs) < 1:
            raise ValueError("at least 1 question when clarification_needed")
        return qs


class ElicitRejected(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["rejected"] = "rejected"
    reason: str = Field(min_length=1)


ElicitResult = Annotated[
    Union[ElicitSuccess, ElicitClarification, ElicitRejected],
    Field(discriminator="kind"),
]


def parse_elicit_payload(data: dict) -> ElicitSuccess | ElicitClarification | ElicitRejected:
    k = data.get("kind")
    if k == "success":
        return ElicitSuccess.model_validate(data)
    if k == "clarification_needed":
        return ElicitClarification.model_validate(data)
    if k == "rejected":
        return ElicitRejected.model_validate(data)
    raise ValueError(f"unknown elicit kind {k!r}")
