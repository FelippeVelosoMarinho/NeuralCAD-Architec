import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from neuralcad_api.schemas.elicitation import ElicitClarification, ElicitSuccess
from neuralcad_api.services.prompt_architect import PROMPT_ARCHITECT_SYSTEM, PromptArchitectService

SUCCESS_INTENT = {
    "sessionId": "s-mock",
    "promptOriginal": "mock prompt",
    "intent": {"objectType": "box", "style": [], "functionalGoal": "test"},
    "constraints": {
        "dimensionsMm": {"width": 10.0, "height": 20.0, "depth": 30.0},
        "symmetry": "none",
        "manufacturingHints": [],
        "materialHints": [],
    },
}


def test_missing_api_key(monkeypatch):
    monkeypatch.setenv("PROMPT_LLM_BACKEND", "anthropic")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        PromptArchitectService().elicit("x")


def test_invalid_backend(monkeypatch):
    monkeypatch.setenv("PROMPT_LLM_BACKEND", "openai")
    with pytest.raises(RuntimeError, match="PROMPT_LLM_BACKEND"):
        PromptArchitectService().elicit("x")


def test_mock_success_path(monkeypatch):
    monkeypatch.setenv("PROMPT_LLM_BACKEND", "anthropic")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    blob = json.dumps(
        {
            "kind": "success",
            "intent": SUCCESS_INTENT,
            "attempt": 1,
            "geo_risk": {"severity": "info", "messages": ["ok"]},
        }
    )

    resp = SimpleNamespace(content=[SimpleNamespace(text=blob)])
    cli = MagicMock()
    cli.messages.create.return_value = resp

    out = PromptArchitectService(anthropic_client=cli).elicit("hello", attempt=1)
    assert isinstance(out, ElicitSuccess)
    called = cli.messages.create.call_args
    assert called.kwargs["system"] == PROMPT_ARCHITECT_SYSTEM
    assert called.kwargs["messages"][0]["content"] == "hello"


def test_mock_clarification(monkeypatch):
    monkeypatch.setenv("PROMPT_LLM_BACKEND", "anthropic")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    blob = json.dumps(
        {
            "kind": "clarification_needed",
            "questions": ["Qual espessura?"],
            "missing_fields": ["constraints.thicknessMm"],
            "attempt": 1,
            "max_attempts": 2,
        }
    )
    resp = SimpleNamespace(content=[SimpleNamespace(text=blob)])
    cli = MagicMock()
    cli.messages.create.return_value = resp

    out = PromptArchitectService(anthropic_client=cli).elicit("ambiguous", attempt=1)
    assert isinstance(out, ElicitClarification)
    assert len(out.questions) <= 3


def test_cursor_backend_success(monkeypatch):
    monkeypatch.setenv("PROMPT_LLM_BACKEND", "cursor")

    blob = json.dumps(
        {
            "kind": "success",
            "intent": SUCCESS_INTENT,
            "attempt": 1,
            "geo_risk": {"severity": "info", "messages": ["ok"]},
        }
    )

    def fake_fetch(_user: str) -> str:
        return blob

    out = PromptArchitectService(cursor_fetch_raw=fake_fetch).elicit("hi", attempt=1)
    assert isinstance(out, ElicitSuccess)


def test_cursor_backend_requires_bridge_url(monkeypatch):
    monkeypatch.setenv("PROMPT_LLM_BACKEND", "cursor")
    monkeypatch.delenv("CURSOR_PROMPT_BRIDGE_URL", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="CURSOR_PROMPT_BRIDGE_URL"):
        PromptArchitectService().elicit("x")
