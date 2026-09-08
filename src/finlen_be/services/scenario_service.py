from typing import List
import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finlen_be.models.scenario import Scenario
from finlen_be.schemas.scenario import ScenarioDetail, ScenarioListItem


class ScenarioService:
    async def list_scenarios(self, db: AsyncSession) -> List[ScenarioListItem]:
        """List all active scenarios for user selection."""
        stmt = select(Scenario).where(Scenario.is_active.is_(True)).order_by(Scenario.created_at.asc())
        result = await db.execute(stmt)
        scenarios = result.scalars().all()
        return [ScenarioListItem.model_validate(s) for s in scenarios]

    async def get_scenario_by_id(
        self,
        db: AsyncSession,
        scenario_id: uuid.UUID,
    ) -> Scenario:
        """Fetch full scenario entity by UUID or raise 404."""
        stmt = select(Scenario).where(Scenario.id == scenario_id, Scenario.is_active.is_(True))
        result = await db.execute(stmt)
        scenario = result.scalar_one_or_none()
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scenario not found",
            )
        return scenario

    async def get_scenario_detail(
        self,
        db: AsyncSession,
        scenario_id: uuid.UUID,
    ) -> ScenarioDetail:
        """Fetch scenario detail schema for public API."""
        scenario = await self.get_scenario_by_id(db, scenario_id)
        return ScenarioDetail.model_validate(scenario)


scenario_service = ScenarioService()
