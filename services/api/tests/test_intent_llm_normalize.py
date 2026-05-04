"""Normalização de blobs LLM → IntentSchemaV1."""

import pytest

from neuralcad_api.schemas.intent_v1 import IntentSchemaV1
from neuralcad_api.services.intent_llm_normalize import normalize_intent_payload_for_v1


def test_normalizes_cursor_style_messy_payload():
    messy = {
        "sessionId": None,
        "promptOriginal": "",
        "intent": {
            "objectType": "box",
            "style": "minimal_solid",
            "functionalGoal": "prototype",
        },
        "constraints": {
            "units": "mm",
            "box": {"length": 100, "width": 50, "height": 25},
            "symmetry": "none",
            "manufacturingHints": [],
            "materialHints": [],
        },
        "topologyHints": ["solid", "enclosed_volume"],
        "generationConfig": {
            "targetFormat": "mesh_or_brep",
            "linearToleranceMm": 0.01,
        },
        "qualityTargets": {
            "manifold": True,
            "watertight": True,
            "minEdgeLengthMm": 0.1,
        },
    }
    out = normalize_intent_payload_for_v1(messy, fallback_prompt="esfera 5cm")
    IntentSchemaV1.model_validate(out)
    assert out["sessionId"].startswith("llm-")
    assert out["promptOriginal"] == "esfera 5cm"
    assert out["intent"]["style"] == ["minimal_solid"]
    assert out["constraints"]["dimensionsMm"]["width"] == 100.0
    assert "topologyHints" not in out
    assert "generationConfig" not in out
    assert out["qualityTargets"]["preferWatertight"] is True


def test_topology_hints_kept_when_valid():
    raw = {
        "sessionId": "s",
        "promptOriginal": "p",
        "intent": {"objectType": "box", "style": [], "functionalGoal": "g"},
        "constraints": {
            "dimensionsMm": {"width": 10, "height": 10, "depth": 10},
            "symmetry": "none",
            "manufacturingHints": [],
            "materialHints": [],
        },
        "topologyHints": {
            "expectedFacesRange": [6, 6],
            "expectedEdgesRange": [12, 12],
            "holes": [{"type": "through", "count": 0}],
        },
    }
    out = normalize_intent_payload_for_v1(raw, fallback_prompt="x")
    IntentSchemaV1.model_validate(out)
    assert out["topologyHints"]["holes"] == [{"type": "through", "count": 0}]


def test_invalid_hole_removed_still_validates_when_empty():
    raw = {
        "sessionId": "s",
        "promptOriginal": "p",
        "intent": {"objectType": "box", "style": [], "functionalGoal": "g"},
        "constraints": {
            "dimensionsMm": {"width": 10, "height": 10, "depth": 10},
            "symmetry": "none",
            "manufacturingHints": [],
            "materialHints": [],
        },
        "topologyHints": {
            "expectedFacesRange": [6, 6],
            "expectedEdgesRange": [12, 12],
            "holes": [{"type": "bad", "count": 1}],
        },
    }
    out = normalize_intent_payload_for_v1(raw, fallback_prompt="x")
    IntentSchemaV1.model_validate(out)
    assert out["topologyHints"]["holes"] == []


def test_llm_symmetry_spherical_mapped_to_none():
    raw = {
        "sessionId": "s1",
        "promptOriginal": "bola raio 60cm",
        "intent": {"objectType": "sphere", "style": [], "functionalGoal": "shape"},
        "constraints": {
            "dimensionsMm": {"width": 600, "height": 600, "depth": 600},
            "symmetry": "spherical",
            "manufacturingHints": [],
            "materialHints": [],
        },
    }
    out = normalize_intent_payload_for_v1(raw, fallback_prompt="bola")
    IntentSchemaV1.model_validate(out)
    assert out["constraints"]["symmetry"] == "none"