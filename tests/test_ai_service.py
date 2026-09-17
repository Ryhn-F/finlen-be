import json

import httpx
import pytest
from fastapi import HTTPException

from finlen_be.services.ai import gemini as gemini_module
from finlen_be.services.ai.gemini import GeminiAIService


def test_clean_json_string_with_code_fences():
    service = GeminiAIService()
    raw_markdown = """```json
    {
      "evaluation": {
        "scores": {
          "critical_thinking": 2,
          "risk_awareness": 3,
          "impulse_control": 1,
          "decision_making": 2
        },
        "consequence": {
          "description": "You verified terms.",
          "severity": "positive"
        },
        "feedback": "Checking terms is crucial."
      },
      "state_changes": {
        "collector_pressure": -1,
        "financial_risk": -1,
        "trust_level": 1,
        "negotiation_power": 1
      },
      "npc_response": "Baik, saya tunggu suratnya."
    }
    ```"""
    cleaned = service._clean_json_string(raw_markdown)
    assert cleaned.startswith("{")
    assert cleaned.endswith("}")
    assert '"critical_thinking": 2' in cleaned


def _make_gemini_json_response(payload: dict) -> dict:
    return {
        "candidates": [
            {"content": {"parts": [{"text": json.dumps(payload)}]}},
        ]
    }


VALID_TURN_PAYLOAD = {
    "evaluation": {
        "scores": {
            "critical_thinking": 2,
            "risk_awareness": 3,
            "impulse_control": 1,
            "decision_making": 2,
        },
        "consequence": {
            "description": "You verified terms.",
            "severity": "positive",
        },
        "feedback": "Checking terms is crucial.",
    },
    "state_changes": {
        "collector_pressure": -1,
        "financial_risk": -1,
        "trust_level": 1,
        "negotiation_power": 1,
    },
    "npc_response": "Baik, saya tunggu suratnya.",
    "answer_choices": [
        {"text": "Saya akan transfer sekarang tanpa cek apapun.", "decision_type": "dangerous"},
        {"text": "Saya akan verifikasi surat dan kontrak dulu.", "decision_type": "safe"},
        {"text": "Saya akan pinjam uang lain untuk membayar ini.", "decision_type": "dangerous"},
    ],
}


@pytest.mark.asyncio
async def test_evaluate_and_respond_retries_until_valid(monkeypatch):
    """Malformed responses should be retried, not silently replaced by a scripted fallback."""
    service = GeminiAIService(base_url="https://example.test", api_key="key", model="test-model")
    monkeypatch.setattr(gemini_module.asyncio, "sleep", lambda *_args, **_kwargs: _noop_sleep())

    call_count = {"n": 0}

    class FakeResponse:
        def __init__(self, status_code: int, json_data: dict | None = None, text: str = ""):
            self.status_code = status_code
            self._json_data = json_data
            self.text = text

        def json(self):
            return self._json_data

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, *args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] < 3:
                return FakeResponse(500, text="server error")
            return FakeResponse(200, json_data=_make_gemini_json_response(VALID_TURN_PAYLOAD))

    monkeypatch.setattr(gemini_module.httpx, "AsyncClient", FakeClient)

    scenario = _make_scenario()
    result = await service.evaluate_and_respond(
        scenario=scenario,
        current_state={},
        history=[],
        user_message="Saya mau cek kontrak dulu",
    )

    assert call_count["n"] == 3
    assert result.npc_response == "Baik, saya tunggu suratnya."
    assert result.evaluation.scores.critical_thinking == 2


@pytest.mark.asyncio
async def test_evaluate_and_respond_raises_after_exhausting_attempts(monkeypatch):
    """When Gemini never returns a valid schema, raise instead of using a deterministic fallback."""
    service = GeminiAIService(base_url="https://example.test", api_key="key", model="test-model")
    monkeypatch.setattr(gemini_module.asyncio, "sleep", lambda *_args, **_kwargs: _noop_sleep())
    monkeypatch.setattr(gemini_module, "MAX_ATTEMPTS", 2)

    class FakeResponse:
        status_code = 500
        text = "server error"

        def json(self):
            return {}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(gemini_module.httpx, "AsyncClient", FakeClient)

    scenario = _make_scenario()
    with pytest.raises(HTTPException) as exc_info:
        await service.evaluate_and_respond(
            scenario=scenario,
            current_state={},
            history=[],
            user_message="Oke saya transfer sekarang",
        )

    assert exc_info.value.status_code == 502


def _make_scenario():
    from finlen_be.models.scenario import Scenario

    return Scenario(
        title="Test Scenario",
        slug="test-scenario",
        npc_role="Debt Collector",
        financial_context={"loan": 1000000},
        objective="Learn negotiation",
        system_prompt="Be strict",
    )


async def _noop_sleep(*_args, **_kwargs):
    return None
