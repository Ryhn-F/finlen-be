import uuid
from datetime import datetime
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from finlen_be.models.base import Base


class RoleplaySession(Base):
    __tablename__ = "roleplay_sessions"
    __table_args__ = (
        CheckConstraint(
            "critical_thinking >= 0 AND critical_thinking <= 100",
            name="roleplay_sessions_critical_thinking_check",
        ),
        CheckConstraint(
            "risk_awareness >= 0 AND risk_awareness <= 100",
            name="roleplay_sessions_risk_awareness_check",
        ),
        CheckConstraint(
            "impulse_control >= 0 AND impulse_control <= 100",
            name="roleplay_sessions_impulse_control_check",
        ),
        CheckConstraint(
            "decision_making >= 0 AND decision_making <= 100",
            name="roleplay_sessions_decision_making_check",
        ),
        CheckConstraint(
            "financial_instinct_score >= 0 AND financial_instinct_score <= 100",
            name="roleplay_sessions_financial_instinct_score_check",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scenario: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    scenario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenarios.id", ondelete="SET NULL"),
        nullable=True,
    )
    critical_thinking: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    risk_awareness: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    impulse_control: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    decision_making: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    financial_instinct_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    xp_earned: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="roleplay_sessions",
    )
    scenario_rel: Mapped["Scenario | None"] = relationship(
        "Scenario",
        back_populates="roleplay_sessions",
    )
