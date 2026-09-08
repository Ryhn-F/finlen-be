from typing import Annotated, List
import uuid
from fastapi import APIRouter, Path, Query, status

from finlen_be.api.deps import CurrentUserDep, DbSessionDep, RoleplayServiceDep
from finlen_be.schemas.roleplay import (
    CreateSessionRequest,
    CreateSessionResponse,
    RoleplayMessageItem,
    SendMessageRequest,
    SendMessageResponse,
    SessionCompleteResponse,
    SessionDetailResponse,
)

router = APIRouter(prefix="/roleplay", tags=["Roleplay"])


@router.post(
    "/sessions",
    response_model=CreateSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create roleplay session",
    description="Start a new interactive roleplay session with initial AI greeting and Firestore state synchronization.",
)
async def create_session(
    req: CreateSessionRequest,
    db: DbSessionDep,
    current_user: CurrentUserDep,
    service: RoleplayServiceDep,
) -> CreateSessionResponse:
    return await service.create_session(db, current_user, req)


@router.get(
    "/sessions/{session_id}",
    response_model=SessionDetailResponse,
    summary="Get session details",
    description="Retrieve session metadata, PostgreSQL instinct scores, and Firebase runtime state.",
)
async def get_session(
    session_id: Annotated[uuid.UUID, Path(description="UUID of the roleplay session")],
    db: DbSessionDep,
    current_user: CurrentUserDep,
    service: RoleplayServiceDep,
) -> SessionDetailResponse:
    return await service.get_session(db, current_user, session_id)


@router.post(
    "/sessions/{session_id}/messages",
    response_model=SendMessageResponse,
    summary="Send roleplay message",
    description="Submit player dialogue/action. Evaluates decision with AI, adjusts stats, updates Firestore, and returns NPC response.",
)
async def send_message(
    session_id: Annotated[uuid.UUID, Path(description="UUID of the roleplay session")],
    req: SendMessageRequest,
    db: DbSessionDep,
    current_user: CurrentUserDep,
    service: RoleplayServiceDep,
) -> SendMessageResponse:
    return await service.process_message(db, current_user, session_id, req)


@router.get(
    "/sessions/{session_id}/messages",
    response_model=List[RoleplayMessageItem],
    summary="Get session messages",
    description="Retrieve full conversation history stored in Firebase Firestore.",
)
async def get_messages(
    session_id: Annotated[uuid.UUID, Path(description="UUID of the roleplay session")],
    db: DbSessionDep,
    current_user: CurrentUserDep,
    service: RoleplayServiceDep,
    limit: Annotated[int, Query(ge=1, le=100, description="Max messages to fetch")] = 50,
    offset: Annotated[int, Query(ge=0, description="Offset index")] = 0,
) -> List[RoleplayMessageItem]:
    return await service.get_messages(db, current_user, session_id, limit=limit, offset=offset)


@router.post(
    "/sessions/{session_id}/complete",
    response_model=SessionCompleteResponse,
    summary="Complete roleplay session",
    description="Finalize the session, calculate earned XP, update user profile progression, and lock session from future turns.",
)
async def complete_session(
    session_id: Annotated[uuid.UUID, Path(description="UUID of the roleplay session")],
    db: DbSessionDep,
    current_user: CurrentUserDep,
    service: RoleplayServiceDep,
) -> SessionCompleteResponse:
    return await service.complete_session(db, current_user, session_id)
