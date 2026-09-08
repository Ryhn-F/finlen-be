from typing import Annotated, List
import uuid
from fastapi import APIRouter, Path

from finlen_be.api.deps import DbSessionDep, ScenarioServiceDep
from finlen_be.schemas.scenario import ScenarioDetail, ScenarioListItem

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


@router.get(
    "",
    response_model=List[ScenarioListItem],
    summary="List available scenarios",
    description="Browse all active financial roleplay scenarios available to players.",
)
async def list_scenarios(
    db: DbSessionDep,
    service: ScenarioServiceDep,
) -> List[ScenarioListItem]:
    return await service.list_scenarios(db)


@router.get(
    "/{scenario_id}",
    response_model=ScenarioDetail,
    summary="Get scenario details",
    description="Retrieve complete financial context and objective for a scenario (system prompts hidden).",
)
async def get_scenario(
    scenario_id: Annotated[uuid.UUID, Path(description="The UUID of the scenario")],
    db: DbSessionDep,
    service: ScenarioServiceDep,
) -> ScenarioDetail:
    return await service.get_scenario_detail(db, scenario_id)
