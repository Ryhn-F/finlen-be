from datetime import datetime
from typing import Any, Dict
import uuid
from pydantic import BaseModel, ConfigDict, Field


class ScenarioListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    description: str
    category: str
    difficulty: str
    npc_role: str
    max_turns: int


class ScenarioDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    description: str
    category: str
    difficulty: str
    npc_role: str
    financial_context: Dict[str, Any]
    objective: str
    initial_state: Dict[str, Any]
    max_turns: int
    created_at: datetime
