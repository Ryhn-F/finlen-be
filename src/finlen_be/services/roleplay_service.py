from datetime import datetime, timezone
import logging
from typing import Any, Dict, List
import uuid
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from finlen_be.models.roleplay_session import RoleplaySession
from finlen_be.models.scenario import Scenario
from finlen_be.models.user import User
from finlen_be.schemas.roleplay import (
    CreateSessionRequest,
    CreateSessionResponse,
    ProgressionChartPoint,
    ProgressionChartResponse,
    RoleplayMessageItem,
    SendMessageRequest,
    SendMessageResponse,
    SessionCompleteResponse,
    SessionDetailResponse,
    SessionHistoryDetailResponse,
    SessionHistoryItem,
    SessionHistoryResponse,
    SessionScores,
    SessionStateData,
)
from finlen_be.services.ai.base import BaseAIService
from finlen_be.services.ai.gemini import ai_service
from finlen_be.services.firebase_service import FirebaseService, firebase_service
from finlen_be.services.progression_service import progression_service
from finlen_be.services.scenario_service import scenario_service

logger = logging.getLogger(__name__)


class RoleplayService:
    def __init__(
        self,
        fb_service: FirebaseService | None = None,
        llm_service: BaseAIService | None = None,
    ) -> None:
        self.fb = fb_service or firebase_service
        self.ai = llm_service or ai_service

    async def create_session(
        self,
        db: AsyncSession,
        user: User,
        req: CreateSessionRequest,
    ) -> CreateSessionResponse:
        """Create a new roleplay session in PostgreSQL and initialize Firebase state."""
        scenario = await scenario_service.get_scenario_by_id(db, req.scenario_id)

        session_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        # 1. Create PostgreSQL session
        db_session = RoleplaySession(
            id=session_id,
            user_id=user.id,
            scenario=scenario.slug,
            scenario_id=scenario.id,
            critical_thinking=50,
            risk_awareness=50,
            impulse_control=50,
            decision_making=50,
            financial_instinct_score=50,
            xp_earned=0,
            status="active",
            created_at=now,
        )
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)

        # 2. Initialize Firestore document and state
        initial_state = dict(scenario.initial_state)
        await self.fb.create_session(
            session_id=str(session_id),
            scenario_data={
                "slug": scenario.slug,
                "title": scenario.title,
                "category": scenario.category,
            },
            initial_state=initial_state,
        )

        # 3. Generate and persist the first NPC message
        first_message = await self.ai.generate_first_npc_message(scenario)
        await self.fb.save_message(
            session_id=str(session_id),
            sender="npc",
            message=first_message,
            turn_number=1,
        )
        await self.fb.update_session_state(
            session_id=str(session_id),
            state_data=initial_state,
            turn_number=1,
            message_count_increment=1,
        )

        state_data = SessionStateData.model_validate(initial_state)

        return CreateSessionResponse(
            session_id=session_id,
            scenario=scenario.slug,
            scenario_title=scenario.title,
            status="active",
            turn_number=1,
            initial_state=state_data,
            first_npc_message=first_message,
            created_at=now,
            max_turns=scenario.max_turns,
        )

    async def get_session_history(
        self,
        db: AsyncSession,
        user: User,
        limit: int = 20,
        offset: int = 0,
    ) -> SessionHistoryResponse:
        """Return the current user's persisted roleplay sessions, newest first."""
        filters = (RoleplaySession.user_id == user.id,)
        total_result = await db.execute(
            select(func.count()).select_from(RoleplaySession).where(*filters)
        )
        total = total_result.scalar_one()

        stmt = (
            select(RoleplaySession, Scenario.title)
            .outerjoin(Scenario, RoleplaySession.scenario_id == Scenario.id)
            .where(*filters)
            .order_by(RoleplaySession.created_at.desc(), RoleplaySession.id.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(stmt)
        items = [
            SessionHistoryItem(
                session_id=session.id,
                scenario=session.scenario,
                scenario_title=scenario_title or session.scenario.replace("-", " ").title(),
                status=session.status,
                average_score=session.financial_instinct_score,
                xp_earned=session.xp_earned,
                created_at=session.created_at,
                completed_at=session.completed_at,
            )
            for session, scenario_title in result.all()
        ]
        return SessionHistoryResponse(items=items, total=total, limit=limit, offset=offset)

    async def get_history_detail(
        self,
        db: AsyncSession,
        user: User,
        session_id: uuid.UUID,
    ) -> SessionHistoryDetailResponse:
        """Return durable historical results for one owned roleplay session."""
        stmt = (
            select(RoleplaySession, Scenario.title)
            .outerjoin(Scenario, RoleplaySession.scenario_id == Scenario.id)
            .where(RoleplaySession.id == session_id)
        )
        result = await db.execute(stmt)
        record = result.one_or_none()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        session, scenario_title = record
        if session.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not own this session",
            )

        scores = SessionScores(
            critical_thinking=session.critical_thinking,
            risk_awareness=session.risk_awareness,
            impulse_control=session.impulse_control,
            decision_making=session.decision_making,
            financial_instinct=session.financial_instinct_score,
        )
        return SessionHistoryDetailResponse(
            session_id=session.id,
            scenario=session.scenario,
            scenario_title=scenario_title or session.scenario.replace("-", " ").title(),
            status=session.status,
            scores=scores,
            average_score=session.financial_instinct_score,
            xp_earned=session.xp_earned,
            created_at=session.created_at,
            completed_at=session.completed_at,
        )

    async def get_progression_chart(
        self,
        db: AsyncSession,
        user: User,
        limit: int = 100,
    ) -> ProgressionChartResponse:
        """Return a bounded set of completed-session composite scores for charting."""
        stmt = (
            select(RoleplaySession)
            .where(
                RoleplaySession.user_id == user.id,
                RoleplaySession.status == "completed",
                RoleplaySession.completed_at.is_not(None),
            )
            .order_by(RoleplaySession.completed_at.desc(), RoleplaySession.id.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        recent_sessions = list(result.scalars())
        points = [
            ProgressionChartPoint(
                session_id=session.id,
                completed_at=session.completed_at,
                average_score=session.financial_instinct_score,
            )
            for session in reversed(recent_sessions)
        ]
        return ProgressionChartResponse(points=points, count=len(points), limit=limit)

    async def get_session(
        self,
        db: AsyncSession,
        user: User,
        session_id: uuid.UUID,
    ) -> SessionDetailResponse:
        """Fetch session metadata, PostgreSQL scores, and Firebase runtime state."""
        stmt = select(RoleplaySession).where(RoleplaySession.id == session_id)
        result = await db.execute(stmt)
        sess = result.scalar_one_or_none()

        if not sess:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        if sess.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not own this session",
            )

        runtime_state_dict = await self.fb.get_session_state(str(session_id))
        runtime_state = SessionStateData.model_validate(runtime_state_dict)

        scores = SessionScores(
            critical_thinking=sess.critical_thinking,
            risk_awareness=sess.risk_awareness,
            impulse_control=sess.impulse_control,
            decision_making=sess.decision_making,
            financial_instinct=sess.financial_instinct_score,
        )

        scenario_stmt = select(Scenario).where(Scenario.slug == sess.scenario)
        scenario_res = await db.execute(scenario_stmt)
        scenario = scenario_res.scalar_one_or_none()
        if not scenario and sess.scenario_id:
            scenario = await scenario_service.get_scenario_by_id(db, sess.scenario_id)

        max_turns = scenario.max_turns if scenario else 10

        return SessionDetailResponse(
            session_id=sess.id,
            scenario=sess.scenario,
            scenario_title=scenario.title if scenario else sess.scenario.replace("-", " ").title(),
            status=sess.status,
            turn_number=runtime_state_dict.get("turn_number", 1),
            scores=scores,
            current_state=runtime_state,
            xp_earned=sess.xp_earned,
            created_at=sess.created_at,
            completed_at=sess.completed_at,
            max_turns=max_turns,
        )

    async def process_message(
        self,
        db: AsyncSession,
        user: User,
        session_id: uuid.UUID,
        req: SendMessageRequest,
    ) -> SendMessageResponse:
        """Process a user message, run AI evaluation, update state, and return NPC response."""
        # 1. Fetch and validate session
        stmt = select(RoleplaySession).where(RoleplaySession.id == session_id)
        result = await db.execute(stmt)
        sess = result.scalar_one_or_none()

        if not sess:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        if sess.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not own this session",
            )
        if sess.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot send messages to a '{sess.status}' session",
            )

        # 2. Fetch scenario
        scenario_stmt = select(Scenario).where(Scenario.slug == sess.scenario)
        scenario_res = await db.execute(scenario_stmt)
        scenario = scenario_res.scalar_one_or_none()
        if not scenario and sess.scenario_id:
            scenario = await scenario_service.get_scenario_by_id(db, sess.scenario_id)
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Associated scenario configuration could not be loaded",
            )

        # 3. Retrieve recent history and state from Firebase
        history = await self.fb.get_recent_messages(str(session_id), limit=8)
        current_state = await self.fb.get_session_state(str(session_id))
        current_turn = current_state.get("turn_number", len(history) // 2) + 1

        # 4. Invoke AI evaluation and dialogue generation
        ai_turn = await self.ai.evaluate_and_respond(
            scenario=scenario,
            current_state=current_state,
            history=history,
            user_message=req.message,
        )

        # 5. Compute state changes and bounded new state
        def bound(v: int) -> int:
            return max(0, min(10, v))

        changes = ai_turn.state_changes
        new_state = {
            "collector_pressure": bound(current_state.get("collector_pressure", 5) + changes.collector_pressure),
            "financial_risk": bound(current_state.get("financial_risk", 5) + changes.financial_risk),
            "trust_level": bound(current_state.get("trust_level", 0) + changes.trust_level),
            "negotiation_power": bound(current_state.get("negotiation_power", 5) + changes.negotiation_power),
            "current_stage": "negotiation" if current_turn > 2 else "opening",
            "last_decision": req.message[:50],
        }

        # 6. Compute turn XP and update PostgreSQL session stats
        turn_xp = progression_service.calculate_turn_xp(ai_turn.evaluation)
        session_scores = progression_service.apply_turn_scores(
            session=sess,
            scores_delta=ai_turn.evaluation.scores,
            turn_xp=turn_xp,
        )

        # 7. Persist to Firebase (User message + NPC response + updated state)
        await self.fb.save_message(
            session_id=str(session_id),
            sender="user",
            message=req.message,
            turn_number=current_turn,
            evaluation=ai_turn.evaluation.model_dump(),
        )
        await self.fb.save_message(
            session_id=str(session_id),
            sender="npc",
            message=ai_turn.npc_response,
            turn_number=current_turn,
        )
        await self.fb.update_session_state(
            session_id=str(session_id),
            state_data=new_state,
            turn_number=current_turn,
            message_count_increment=2,
        )

        # 8. Commit PostgreSQL transaction
        await db.commit()
        await db.refresh(sess)

        return SendMessageResponse(
            turn_number=current_turn,
            user_message=req.message,
            npc_response=ai_turn.npc_response,
            evaluation=ai_turn.evaluation,
            state_changes=changes,
            current_state=SessionStateData.model_validate(new_state),
            session_scores=session_scores,
            xp_earned_this_turn=turn_xp,
            max_turns=scenario.max_turns if scenario else 10,
        )

    async def complete_session(
        self,
        db: AsyncSession,
        user: User,
        session_id: uuid.UUID,
    ) -> SessionCompleteResponse:
        """Finalize a session, apply progression to user account, and mark status completed."""
        stmt = select(RoleplaySession).where(RoleplaySession.id == session_id)
        result = await db.execute(stmt)
        sess = result.scalar_one_or_none()

        if not sess:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        if sess.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not own this session",
            )
        if sess.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is already completed",
            )

        now = datetime.now(timezone.utc)
        sess.status = "completed"
        sess.completed_at = now

        # Finalize user progression
        progression = progression_service.finalize_user_progression(user, sess)

        await db.commit()
        await db.refresh(sess)
        await db.refresh(user)

        scores = SessionScores(
            critical_thinking=sess.critical_thinking,
            risk_awareness=sess.risk_awareness,
            impulse_control=sess.impulse_control,
            decision_making=sess.decision_making,
            financial_instinct=sess.financial_instinct_score,
        )

        return SessionCompleteResponse(
            session_id=sess.id,
            status=sess.status,
            scores=scores,
            xp_earned=sess.xp_earned,
            completed_at=now,
            progression=progression,
        )

    async def get_messages(
        self,
        db: AsyncSession,
        user: User,
        session_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[RoleplayMessageItem]:
        """Fetch conversation messages for the session from Firebase."""
        stmt = select(RoleplaySession).where(RoleplaySession.id == session_id)
        result = await db.execute(stmt)
        sess = result.scalar_one_or_none()

        if not sess:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        if sess.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not own this session",
            )

        raw_messages = await self.fb.get_all_messages(str(session_id), limit=limit, offset=offset)
        return [RoleplayMessageItem.model_validate(m) for m in raw_messages]


roleplay_service = RoleplayService()
