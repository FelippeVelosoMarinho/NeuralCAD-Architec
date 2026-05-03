"""
IntentSchemaV1 — contrato espelho de IDEA.md § IntentSchemaV1.

Dimensões 0 são placeholders no brief; valores reais devem ser &gt; 0 para jobs geométricos
(validação estrita opcional aplicada antes de enqueue no plano 03).
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class DimensionsMm(BaseModel):
    """Dimensões em mm quando o bloco existe — todos obrigatórios no objecto."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    width: float = Field(gt=0)
    height: float = Field(gt=0)
    depth: float = Field(gt=0)


class IntentBlock(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    object_type: str = Field(alias="objectType", min_length=1)
    style: list[str] = Field(default_factory=list)
    functional_goal: str = Field(alias="functionalGoal", min_length=1)


class ConstraintsBlock(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    dimensions_mm: Optional[DimensionsMm] = Field(default=None, alias="dimensionsMm")
    thickness_mm: Optional[float] = Field(default=None, alias="thicknessMm")
    symmetry: Optional[
        Literal["none", "x", "y", "z", "xy", "xz", "yz"]
    ] = Field(default=None, alias="symmetry")
    manufacturing_hints: list[str] = Field(default_factory=list, alias="manufacturingHints")
    material_hints: list[str] = Field(default_factory=list, alias="materialHints")


HoleType = Literal["concentric", "through", "blind"]


class HoleHint(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    hole_type: HoleType = Field(alias="type")
    count: int = Field(ge=0)


class TopologyHints(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    expected_faces_range: tuple[int, int] = Field(alias="expectedFacesRange")
    expected_edges_range: tuple[int, int] = Field(alias="expectedEdgesRange")
    holes: list[HoleHint] = Field(default_factory=list)


class SurfaceHints(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    curvature: Literal["low", "medium", "high"]
    freeform: bool
    continuity_preference: Literal["G0", "G1", "G2"] = Field(alias="continuityPreference")


class GenerationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    mode: str = Field(min_length=1)
    num_surfaces: int = Field(ge=0, alias="numSurfaces")
    num_edges_per_surface: int = Field(ge=0, alias="numEdgesPerSurface")
    bbox_threshold: float = Field(alias="bboxThreshold")
    z_threshold: float = Field(alias="zThreshold")


class QualityTargets(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    prefer_watertight: bool = Field(alias="preferWatertight")
    max_self_intersection_risk: Literal["low", "medium", "high"] = Field(
        alias="maxSelfIntersectionRisk"
    )


class IntentSchemaV1(BaseModel):
    """
    Payload raiz IDEA (sessionId ... qualityTargets opcionais no JSON exemplar são
    representados aqui como opcionais excepto onde o MVP exige sempre presente).
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    session_id: str = Field(alias="sessionId", min_length=1)
    prompt_original: str = Field(alias="promptOriginal", min_length=1)
    intent: IntentBlock
    constraints: ConstraintsBlock
    topology_hints: Optional[TopologyHints] = Field(default=None, alias="topologyHints")
    surface_hints: Optional[SurfaceHints] = Field(default=None, alias="surfaceHints")
    generation_config: Optional[GenerationConfig] = Field(default=None, alias="generationConfig")
    quality_targets: Optional[QualityTargets] = Field(default=None, alias="qualityTargets")
