from datetime import datetime
from typing import Any, Dict, List
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


class LearningMaterialItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None = None
    formal_file_url: str | None = Field(
        default=None, description="Public URL of the formal-version PDF resolved from Supabase Storage"
    )
    source_name: str | None = None
    source_url: str | None = None
    created_at: datetime


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
    learning_materials: List[LearningMaterialItem] = Field(default_factory=list)
