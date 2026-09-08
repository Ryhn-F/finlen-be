from abc import ABC, abstractmethod
from typing import Any, Dict, List

from finlen_be.models.scenario import Scenario
from finlen_be.schemas.ai import AITurnResponse


class BaseAIService(ABC):
    @abstractmethod
    async def generate_first_npc_message(self, scenario: Scenario) -> str:
        """Generate the opening in-character message for an NPC."""
        pass

    @abstractmethod
    async def evaluate_and_respond(
        self,
        scenario: Scenario,
        current_state: Dict[str, Any],
        history: List[Dict[str, Any]],
        user_message: str,
    ) -> AITurnResponse:
        """Evaluate the user's turn and generate the NPC response."""
        pass
