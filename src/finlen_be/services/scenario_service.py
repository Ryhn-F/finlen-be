from typing import List
import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from finlen_be.models.scenario import Scenario
from finlen_be.schemas.scenario import LearningMaterialItem, ScenarioDetail, ScenarioListItem
from finlen_be.services.storage_service import storage_service


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
        """Fetch scenario detail schema for public API, including learning materials
        with public PDF URLs resolved from Supabase Storage."""
        stmt = (
            select(Scenario)
            .options(selectinload(Scenario.learning_materials))
            .where(Scenario.id == scenario_id, Scenario.is_active.is_(True))
        )
        result = await db.execute(stmt)
        scenario = result.scalar_one_or_none()
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scenario not found",
            )

        detail = ScenarioDetail.model_validate(scenario)
        detail.learning_materials = [
            LearningMaterialItem(
                id=material.id,
                title=material.title,
                description=material.description,
                formal_file_url=storage_service.get_public_url(material.formal_file_path),
                brainrot_file_url=storage_service.get_public_url(material.brainrot_file_path),
                source_name=material.source_name,
                source_url=material.source_url,
                created_at=material.created_at,
            )
            for material in scenario.learning_materials
        ]
        return detail


scenario_service = ScenarioService()
