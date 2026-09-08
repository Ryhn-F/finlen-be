import logging
from typing import Annotated, List
import uuid

from fastapi import APIRouter, HTTPException, Path, status
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from finlen_be.api.deps import DbSessionDep, ScenarioServiceDep
from finlen_be.schemas.scenario import ScenarioDetail, ScenarioListItem

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])
logger = logging.getLogger(__name__)


@router.get(
    "",
    response_model=List[ScenarioListItem],
    summary="List available scenarios",
    description="Browse all active financial roleplay scenarios available to players.",
    responses={
        500: {"description": "Internal server error"},
    },
)
async def list_scenarios(
    db: DbSessionDep,
    service: ScenarioServiceDep,
) -> List[ScenarioListItem]:
    try:
        return await service.list_scenarios(db)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Database error listing scenarios: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scenarios due to a database error.",
        )
    except Exception as e:
        logger.error("Unexpected error listing scenarios: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing scenarios.",
        )


@router.get(
    "/{scenario_id}",
    response_model=ScenarioDetail,
    summary="Get scenario details",
    description="Retrieve complete financial context and objective for a scenario (system prompts hidden).",
    responses={
        404: {"description": "Scenario not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_scenario(
    scenario_id: Annotated[uuid.UUID, Path(description="The UUID of the scenario")],
    db: DbSessionDep,
    service: ScenarioServiceDep,
) -> ScenarioDetail:
    try:
        return await service.get_scenario_detail(db, scenario_id)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Database error fetching scenario %s: %s", scenario_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scenario due to a database error.",
        )
    except Exception as e:
        logger.error("Unexpected error fetching scenario %s: %s", scenario_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching the scenario.",
        )
