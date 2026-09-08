from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: EmailStr
    level: int = Field(ge=1)
    xp: int = Field(ge=0)
    financial_instinct: float = Field(ge=0.0, le=100.0)
    created_at: datetime
    updated_at: datetime
