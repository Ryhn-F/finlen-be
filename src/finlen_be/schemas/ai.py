from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class AnswerChoice(BaseModel):
    """Internally labeled choice used to enforce the required safety distribution."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, description="User dialogue or action in Indonesian")
    decision_type: Literal["dangerous", "safe"]


class AnswerChoicesMixin(BaseModel):
    answer_choices: list[AnswerChoice] = Field(min_length=3, max_length=3)

    @model_validator(mode="after")
    def validate_answer_choice_distribution(self) -> "AnswerChoicesMixin":
        decision_types = [choice.decision_type for choice in self.answer_choices]
        if decision_types.count("dangerous") != 2 or decision_types.count("safe") != 1:
            raise ValueError("answer_choices must contain exactly two dangerous choices and one safe choice")
        normalized_texts = {choice.text.strip().casefold() for choice in self.answer_choices}
        if len(normalized_texts) != 3:
            raise ValueError("answer_choices must contain three distinct choices")
        return self


class OpeningNPCResponse(AnswerChoicesMixin):
    model_config = ConfigDict(extra="ignore")

    npc_response: str = Field(min_length=1, description="Opening dialogue from NPC")


class AITurnResponse(AnswerChoicesMixin):
    model_config = ConfigDict(extra="ignore")

    evaluation: TurnEvaluation
    state_changes: StateChanges
    npc_response: str = Field(min_length=1, description="Dialogue response from NPC")
