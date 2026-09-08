import pytest
from finlen_be.models.scenario import Scenario
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


def test_fallback_response_cautious():
    service = GeminiAIService()
    scenario = Scenario(
        title="Test Scenario",
        slug="test-scenario",
        npc_role="Debt Collector",
        financial_context={"loan": 1000000},
        objective="Learn negotiation",
        system_prompt="Be strict",
    )
    res = service._create_fallback_response("Saya mau cek kontrak dulu", scenario)
    assert res.evaluation.scores.critical_thinking > 0
    assert res.evaluation.consequence.severity == "positive"
    assert "kontrak" not in res.npc_response.lower() or len(res.npc_response) > 5


def test_fallback_response_impulsive():
    service = GeminiAIService()
    scenario = Scenario(
        title="Test Scenario",
        slug="test-scenario",
        npc_role="Debt Collector",
        financial_context={"loan": 1000000},
        objective="Learn negotiation",
        system_prompt="Be strict",
    )
    res = service._create_fallback_response("Oke saya transfer sekarang", scenario)
    assert res.evaluation.scores.critical_thinking < 0
    assert res.evaluation.consequence.severity == "neutral"

