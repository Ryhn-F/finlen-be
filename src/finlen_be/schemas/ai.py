from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class EvaluationScores(BaseModel):
    model_config = ConfigDict(extra="ignore")

    critical_thinking: int = Field(ge=-5, le=5, description="Score delta between -5 and 5")
    risk_awareness: int = Field(ge=-5, le=5, description="Score delta between -5 and 5")
    impulse_control: int = Field(ge=-5, le=5, description="Score delta between -5 and 5")
    decision_making: int = Field(ge=-5, le=5, description="Score delta between -5 and 5")


class EvaluationConsequence(BaseModel):
    model_config = ConfigDict(extra="ignore")

    description: str = Field(min_length=1, description="Immediate consequence of user's decision")
    severity: Literal["positive", "neutral", "negative", "critical"] = Field(
        description="Severity classification of consequence"
    )


class StateChanges(BaseModel):
    model_config = ConfigDict(extra="ignore")

    collector_pressure: int = Field(ge=-5, le=5, default=0)
    financial_risk: int = Field(ge=-5, le=5, default=0)
    trust_level: int = Field(ge=-5, le=5, default=0)
    negotiation_power: int = Field(ge=-5, le=5, default=0)


class TurnEvaluation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    scores: EvaluationScores
    consequence: EvaluationConsequence
    feedback: str = Field(min_length=1, description="Educational feedback teaching the financial concept")
    state_changes: StateChanges


class AITurnResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    evaluation: TurnEvaluation
    state_changes: StateChanges
    npc_response: str = Field(min_length=1, description="Dialogue response from NPC")
