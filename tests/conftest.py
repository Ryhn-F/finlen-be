from collections.abc import AsyncGenerator
from typing import Any, Dict, List
import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from finlen_be.core.database import AsyncSessionLocal, engine
from finlen_be.main import app
from finlen_be.models.scenario import Scenario
from finlen_be.schemas.ai import (
    AITurnResponse,
    AnswerChoice,
    EvaluationConsequence,
    EvaluationScores,
    OpeningNPCResponse,
    StateChanges,
    TurnEvaluation,
)
from finlen_be.services.ai.base import BaseAIService
from finlen_be.services.ai.gemini import ai_service
from finlen_be.services.firebase_service import FirebaseService, firebase_service
from finlen_be.services.roleplay_service import roleplay_service


class MockAIService(BaseAIService):
    def _answer_choices(self) -> list[AnswerChoice]:
        return [
            AnswerChoice(text="Saya langsung membayar tanpa verifikasi.", decision_type="dangerous"),
            AnswerChoice(text="Saya meminjam uang lain untuk membayar.", decision_type="dangerous"),
            AnswerChoice(text="Saya verifikasi dokumen dan kanal resmi dahulu.", decision_type="safe"),
        ]

    async def generate_first_npc_message(self, scenario: Scenario) -> OpeningNPCResponse:
        return OpeningNPCResponse(
            npc_response=f"Halo, saya {scenario.npc_role}. Bayar sekarang juga!",
            answer_choices=self._answer_choices(),
        )

    async def evaluate_and_respond(
        self,
        scenario: Scenario,
        current_state: Dict[str, Any],
        history: List[Dict[str, Any]],
        user_message: str,
    ) -> AITurnResponse:
        scores = EvaluationScores(
            critical_thinking=3,
            risk_awareness=4,
            impulse_control=2,
            decision_making=3,
        )
        consequence = EvaluationConsequence(
            description="You verified the contract terms before paying.",
            severity="positive",
        )
        feedback = "Good cautious approach to debt collector pressure."
        state_changes = StateChanges(
            collector_pressure=-1,
            financial_risk=-2,
            trust_level=1,
            negotiation_power=2,
        )
        npc_response = "Baik, kirimkan surat resmi verifikasi Anda sekarang."

        return AITurnResponse(
            evaluation=TurnEvaluation(
                scores=scores,
                consequence=consequence,
                feedback=feedback,
                state_changes=state_changes,
            ),
            state_changes=state_changes,
            npc_response=npc_response,
            answer_choices=self._answer_choices(),
        )


@pytest.fixture(autouse=True)
def setup_mock_services():
    """Mock external AI and Firebase to keep tests fully hermetic and fast."""
    mock_ai = MockAIService()
    mock_fb = FirebaseService(client=None)  # Uses in-memory fallback

    # Monkeypatch singleton services
    roleplay_service.ai = mock_ai
    roleplay_service.fb = mock_fb

    yield

    # Restore
    roleplay_service.ai = ai_service
    roleplay_service.fb = firebase_service


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
