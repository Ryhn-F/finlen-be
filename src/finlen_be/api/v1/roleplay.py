import logging
from typing import Annotated, List
import uuid

from fastapi import APIRouter, HTTPException, Path, Query, status
from sqlalchemy.exc import SQLAlchemyError

from finlen_be.api.deps import CurrentUserDep, DbSessionDep, RoleplayServiceDep
from finlen_be.schemas.roleplay import (
    CreateSessionRequest,
    CreateSessionResponse,
    ProgressionChartResponse,
    RoleplayMessageItem,
    SendMessageRequest,
    SendMessageResponse,
    SessionCompleteResponse,
    SessionDetailResponse,
    SessionHistoryDetailResponse,
    SessionHistoryResponse,
)

router = APIRouter(prefix="/roleplay", tags=["Roleplay"])
logger = logging.getLogger(__name__)


@router.post(
    "/sessions",
    response_model=CreateSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create roleplay session",
    description="Start a new interactive roleplay session with initial AI greeting and Firestore state synchronization.",
    responses={
        404: {"description": "Scenario not found"},
        500: {"description": "Internal server error"},
    },
)
async def create_session(
    req: CreateSessionRequest,
    db: DbSessionDep,
    current_user: CurrentUserDep,
    service: RoleplayServiceDep,
) -> CreateSessionResponse:
    try:
        return await service.create_session(db, current_user, req)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Database error creating session: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session due to a database error.",
        )
    except Exception as e:
        logger.error("Unexpected error creating session: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the session.",
        )


@router.get(
    "/history",
    response_model=SessionHistoryResponse,
    summary="Get roleplay history",
    description="Retrieve the authenticated user's persisted roleplay sessions, newest first.",
    responses={500: {"description": "Internal server error"}},
)
async def get_session_history(
    db: DbSessionDep,
    current_user: CurrentUserDep,
    service: RoleplayServiceDep,
    limit: Annotated[int, Query(ge=1, le=100, description="Max sessions to fetch")] = 20,
    offset: Annotated[int, Query(ge=0, description="Pagination offset")] = 0,
) -> SessionHistoryResponse:
    try:
        return await service.get_session_history(db, current_user, limit=limit, offset=offset)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Database error fetching roleplay history: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve roleplay history due to a database error.",
        )
    except Exception as e:
        logger.error("Unexpected error fetching roleplay history: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching roleplay history.",
        )


@router.get(
    "/history/progression",
    response_model=ProgressionChartResponse,
    summary="Get roleplay score progression",
    description="Retrieve chronological completed-session average scores for rendering a progression chart.",
    responses={500: {"description": "Internal server error"}},
)
async def get_progression_chart(
    db: DbSessionDep,
    current_user: CurrentUserDep,
    service: RoleplayServiceDep,
    limit: Annotated[int, Query(ge=1, le=100, description="Max recent completed sessions to chart")] = 100,
) -> ProgressionChartResponse:
    try:
        return await service.get_progression_chart(db, current_user, limit=limit)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Database error fetching score progression: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve score progression due to a database error.",
        )
    except Exception as e:
        logger.error("Unexpected error fetching score progression: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching score progression.",
        )


@router.get(
    "/history/{session_id}",
    response_model=SessionHistoryDetailResponse,
    summary="Get roleplay history detail",
    description="Retrieve durable historical results for one owned roleplay session without requiring Firebase state.",
    responses={
        403: {"description": "Access denied — session belongs to another user"},
        404: {"description": "Session not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_history_detail(
    session_id: Annotated[uuid.UUID, Path(description="UUID of the roleplay session")],
    db: DbSessionDep,
    current_user: CurrentUserDep,
    service: RoleplayServiceDep,
) -> SessionHistoryDetailResponse:
    try:
        return await service.get_history_detail(db, current_user, session_id)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Database error fetching history session %s: %s", session_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve roleplay history detail due to a database error.",
        )
    except Exception as e:
        logger.error("Unexpected error fetching history session %s: %s", session_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching roleplay history detail.",
        )


@router.get(
    "/sessions/{session_id}",
    response_model=SessionDetailResponse,
    summary="Get session details",
    description="Retrieve session metadata, PostgreSQL instinct scores, and Firebase runtime state.",
    responses={
        403: {"description": "Access denied — session belongs to another user"},
        404: {"description": "Session not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_session(
    session_id: Annotated[uuid.UUID, Path(description="UUID of the roleplay session")],
    db: DbSessionDep,
    current_user: CurrentUserDep,
    service: RoleplayServiceDep,
) -> SessionDetailResponse:
    try:
        return await service.get_session(db, current_user, session_id)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Database error fetching session %s: %s", session_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session due to a database error.",
        )
    except Exception as e:
        logger.error("Unexpected error fetching session %s: %s", session_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching session details.",
        )


@router.post(
    "/sessions/{session_id}/messages",
    response_model=SendMessageResponse,
    summary="Send roleplay message",
    description="Submit player dialogue/action. Evaluates decision with AI, adjusts stats, updates Firestore, and returns NPC response.",
    responses={
        400: {"description": "Session is not active"},
        403: {"description": "Access denied — session belongs to another user"},
        404: {"description": "Session not found"},
        500: {"description": "Internal server error"},
    },
)
async def send_message(
    session_id: Annotated[uuid.UUID, Path(description="UUID of the roleplay session")],
    req: SendMessageRequest,
    db: DbSessionDep,
    current_user: CurrentUserDep,
    service: RoleplayServiceDep,
) -> SendMessageResponse:
    try:
        return await service.process_message(db, current_user, session_id, req)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Database error processing message for session %s: %s", session_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message due to a database error.",
        )
    except Exception as e:
        logger.error("Unexpected error processing message for session %s: %s", session_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the message.",
        )


@router.get(
    "/sessions/{session_id}/messages",
    response_model=List[RoleplayMessageItem],
    summary="Get session messages",
    description="Retrieve full conversation history stored in Firebase Firestore.",
    responses={
        403: {"description": "Access denied — session belongs to another user"},
        404: {"description": "Session not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_messages(
    session_id: Annotated[uuid.UUID, Path(description="UUID of the roleplay session")],
    db: DbSessionDep,
    current_user: CurrentUserDep,
    service: RoleplayServiceDep,
    limit: Annotated[int, Query(ge=1, le=100, description="Max messages to fetch")] = 50,
    offset: Annotated[int, Query(ge=0, description="Offset index")] = 0,
) -> List[RoleplayMessageItem]:
    try:
        return await service.get_messages(db, current_user, session_id, limit=limit, offset=offset)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Database error fetching messages for session %s: %s", session_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages due to a database error.",
        )
    except Exception as e:
        logger.error("Unexpected error fetching messages for session %s: %s", session_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching messages.",
        )


@router.post(
    "/sessions/{session_id}/complete",
    response_model=SessionCompleteResponse,
    summary="Complete roleplay session",
    description="Finalize the session, calculate earned XP, update user profile progression, and lock session from future turns.",
    responses={
        400: {"description": "Session is already completed"},
        403: {"description": "Access denied — session belongs to another user"},
        404: {"description": "Session not found"},
        500: {"description": "Internal server error"},
    },
)
async def complete_session(
    session_id: Annotated[uuid.UUID, Path(description="UUID of the roleplay session")],
    db: DbSessionDep,
    current_user: CurrentUserDep,
    service: RoleplayServiceDep,
) -> SessionCompleteResponse:
    try:
        return await service.complete_session(db, current_user, session_id)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Database error completing session %s: %s", session_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete session due to a database error.",
        )
    except Exception as e:
        logger.error("Unexpected error completing session %s: %s", session_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while completing the session.",
        )
