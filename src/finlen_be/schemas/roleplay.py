from datetime import datetime
from typing import Any, Dict, List, Literal
import uuid
from pydantic import BaseModel, ConfigDict, Field

from finlen_be.schemas.ai import StateChanges, TurnEvaluation


class CreateSessionRequest(BaseModel):
    scenario_id: uuid.UUID = Field(description="UUID of the scenario to play")


class SessionStateData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    collector_pressure: int = Field(ge=0, le=10, default=5)
    financial_risk: int = Field(ge=0, le=10, default=5)
    trust_level: int = Field(ge=0, le=10, default=0)
    negotiation_power: int = Field(ge=0, le=10, default=5)
    current_stage: str = Field(default="opening")
    last_decision: str = Field(default="session_started")
    updated_at: str | None = None


class SessionScores(BaseModel):
    critical_thinking: int = Field(ge=0, le=100)
    risk_awareness: int = Field(ge=0, le=100)
    impulse_control: int = Field(ge=0, le=100)
    decision_making: int = Field(ge=0, le=100)
    financial_instinct: int = Field(ge=0, le=100)


class RoleplayMessageItem(BaseModel):
    id: str | None = None
    sender: Literal["user", "npc", "system"]
    message: str
    turn_number: int
    created_at: str | datetime
    evaluation: TurnEvaluation | None = None


class CreateSessionResponse(BaseModel):
    session_id: uuid.UUID
    scenario: str
    scenario_title: str
    status: str
    turn_number: int
    initial_state: SessionStateData
    first_npc_message: str
    created_at: datetime
    max_turns: int = 10


class SendMessageRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=2000, description="User's dialogue or action")


class SendMessageResponse(BaseModel):
    turn_number: int
    user_message: str
    npc_response: str
    evaluation: TurnEvaluation
    state_changes: StateChanges
    current_state: SessionStateData
    session_scores: SessionScores
    xp_earned_this_turn: int
    max_turns: int = 10


class SessionDetailResponse(BaseModel):
    session_id: uuid.UUID
    scenario: str
    scenario_title: str | None = None
    status: str
    turn_number: int
    scores: SessionScores
    current_state: SessionStateData | None = None
    xp_earned: int
    created_at: datetime
    completed_at: datetime | None = None
    max_turns: int = 10


class UserProgressionUpdate(BaseModel):
    user_id: uuid.UUID
    level: int
    xp: int
    xp_gained: int
    financial_instinct: float


class SessionHistoryItem(BaseModel):
    session_id: uuid.UUID
    scenario: str
    scenario_title: str
    status: str
    average_score: int = Field(ge=0, le=100)
    xp_earned: int = Field(ge=0)
    created_at: datetime
    completed_at: datetime | None = None


class SessionHistoryResponse(BaseModel):
    items: List[SessionHistoryItem]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)


class SessionHistoryDetailResponse(BaseModel):
    session_id: uuid.UUID
    scenario: str
    scenario_title: str
    status: str
    scores: SessionScores
    average_score: int = Field(ge=0, le=100)
    xp_earned: int = Field(ge=0)
    created_at: datetime
    completed_at: datetime | None = None


class ProgressionChartPoint(BaseModel):
    session_id: uuid.UUID
    completed_at: datetime
    average_score: int = Field(ge=0, le=100)


class ProgressionChartResponse(BaseModel):
    points: List[ProgressionChartPoint]
    count: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)


class SessionCompleteResponse(BaseModel):
    session_id: uuid.UUID
    status: str
    scores: SessionScores
    xp_earned: int
    completed_at: datetime
    progression: UserProgressionUpdate | None = None
