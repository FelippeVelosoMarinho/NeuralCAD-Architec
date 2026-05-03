import json

import pytest
from pydantic import ValidationError

from neuralcad_api.schemas.intent_v1 import IntentSchemaV1

CANON_JSON = """
{
  "sessionId": "s1",
  "promptOriginal": "box bracket",
  "intent": {
    "objectType": "bracket",
    "style": ["minimal"],
    "functionalGoal": "mount"
  },
  "constraints": {
    "dimensionsMm": {"width": 100.0, "height": 50.0, "depth": 25.0},
    "thicknessMm": 2.5,
    "symmetry": "none",
    "manufacturingHints": [],
    "materialHints": []
  },
  "topologyHints": {
    "expectedFacesRange": [6, 6],
    "expectedEdgesRange": [12, 12],
    "holes": [{"type": "through", "count": 0}]
  },
  "surfaceHints": {
    "curvature": "low",
    "freeform": false,
    "continuityPreference": "G1"
  },
  "generationConfig": {
    "mode": "abc",
    "numSurfaces": 6,
    "numEdgesPerSurface": 12,
    "bboxThreshold": 0.01,
    "zThreshold": 0.02
  },
  "qualityTargets": {
    "preferWatertight": true,
    "maxSelfIntersectionRisk": "low"
  }
}
"""


def test_accepts_minimal_canonical_shape():
    IntentSchemaV1.model_validate_json(CANON_JSON)


def test_rejects_unknown_top_level_key():
    blob = json.loads(CANON_JSON)
    blob["evil"] = 1
    with pytest.raises(ValidationError):
        IntentSchemaV1.model_validate(blob)


def test_roundtrip_serialization():
    parsed = IntentSchemaV1.model_validate_json(CANON_JSON)
    out = parsed.model_dump(by_alias=True, mode="json")
    assert "sessionId" in out
    assert "constraints" in out
    assert isinstance(out["constraints"]["dimensionsMm"], dict)
