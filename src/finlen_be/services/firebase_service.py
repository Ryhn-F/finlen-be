from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
import uuid
from google.cloud import firestore as google_firestore

from finlen_be.core.firebase import get_firestore_client

logger = logging.getLogger(__name__)


class FirebaseService:
    def __init__(self, client: Any | None = None) -> None:
        self._client = client
        # In-memory fallback if Firestore is not initialized or in isolated tests
        self._in_memory_sessions: Dict[str, Dict[str, Any]] = {}
        self._in_memory_states: Dict[str, Dict[str, Any]] = {}
        self._in_memory_messages: Dict[str, List[Dict[str, Any]]] = {}

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = get_firestore_client()
        return self._client

    async def create_session(
        self,
        session_id: str,
        scenario_data: Dict[str, Any],
        initial_state: Dict[str, Any],
    ) -> None:
        """Create session document and initial session_state/current in Firestore."""
        now = datetime.now(timezone.utc).isoformat()
        session_payload = {
            "scenario": scenario_data.get("slug", "unknown"),
            "scenario_title": scenario_data.get("title", ""),
            "turn_number": 0,
            "message_count": 0,
            "current_stage": initial_state.get("current_stage", "opening"),
            "last_message_at": now,
            "created_at": now,
            "updated_at": now,
        }

        state_payload = {
            "collector_pressure": initial_state.get("collector_pressure", 5),
            "financial_risk": initial_state.get("financial_risk", 5),
            "trust_level": initial_state.get("trust_level", 0),
            "negotiation_power": initial_state.get("negotiation_power", 5),
            "current_stage": initial_state.get("current_stage", "opening"),
            "last_decision": "session_started",
            "turn_number": 1,
            "updated_at": now,
        }

        cli = self.client
        if cli is not None:
            try:
                session_ref = cli.collection("roleplay_sessions").document(session_id)
                session_ref.set(session_payload)
                session_ref.collection("session_state").document("current").set(state_payload)
                logger.info("Created Firestore session document for %s", session_id)
                return
            except Exception as e:
                logger.error("Error creating Firestore session %s: %s", session_id, e)
                # Fall back to in-memory store so app continues functioning
        
        # In-memory fallback
        self._in_memory_sessions[session_id] = session_payload
        self._in_memory_states[session_id] = state_payload
        self._in_memory_messages[session_id] = []

    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Fetch current session state from session_state/current."""
        cli = self.client
        if cli is not None:
            try:
                state_ref = (
                    cli.collection("roleplay_sessions")
                    .document(session_id)
                    .collection("session_state")
                    .document("current")
                )
                doc = state_ref.get()
                if doc.exists:
                    data = doc.to_dict() or {}
                    if "turn_number" not in data:
                        root_doc = cli.collection("roleplay_sessions").document(session_id).get()
                        if root_doc.exists:
                            root_data = root_doc.to_dict() or {}
                            data["turn_number"] = root_data.get("turn_number", 1)
                    return data
            except Exception as e:
                logger.error("Error reading Firestore session state %s: %s", session_id, e)

        # Fallback or default
        return self._in_memory_states.get(
            session_id,
            {
                "collector_pressure": 5,
                "financial_risk": 5,
                "trust_level": 0,
                "negotiation_power": 5,
                "current_stage": "opening",
                "last_decision": "unknown",
                "turn_number": 1,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    async def update_session_state(
        self,
        session_id: str,
        state_data: Dict[str, Any],
        turn_number: int,
        message_count_increment: int = 1,
    ) -> None:
        """Update session state document and root session turn / message count."""
        now = datetime.now(timezone.utc).isoformat()
        state_payload = {**state_data, "turn_number": turn_number, "updated_at": now}

        cli = self.client
        if cli is not None:
            try:
                session_ref = cli.collection("roleplay_sessions").document(session_id)
                session_ref.update({
                    "turn_number": turn_number,
                    "message_count": google_firestore.Increment(message_count_increment),
                    "current_stage": state_data.get("current_stage", "in_progress"),
                    "last_message_at": now,
                    "updated_at": now,
                })
                session_ref.collection("session_state").document("current").set(
                    state_payload, merge=True
                )
                return
            except Exception as e:
                logger.error("Error updating Firestore session state %s: %s", session_id, e)

        # In-memory fallback
        self._in_memory_states[session_id] = state_payload
        if session_id in self._in_memory_sessions:
            s = self._in_memory_sessions[session_id]
            s["turn_number"] = turn_number
            s["message_count"] = s.get("message_count", 0) + message_count_increment
            s["current_stage"] = state_data.get("current_stage", "in_progress")
            s["last_message_at"] = now
            s["updated_at"] = now

    async def save_message(
        self,
        session_id: str,
        sender: str,
        message: str,
        turn_number: int,
        evaluation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Save a message under roleplay_sessions/{session_id}/messages."""
        msg_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        payload: Dict[str, Any] = {
            "id": msg_id,
            "sender": sender,
            "message": message,
            "turn_number": turn_number,
            "created_at": now,
        }
        if sender == "user" and evaluation is not None:
            payload["evaluation"] = evaluation

        cli = self.client
        if cli is not None:
            try:
                msg_ref = (
                    cli.collection("roleplay_sessions")
                    .document(session_id)
                    .collection("messages")
                    .document(msg_id)
                )
                msg_ref.set(payload)
                return payload
            except Exception as e:
                logger.error("Error saving Firestore message %s: %s", session_id, e)

        # In-memory fallback
        if session_id not in self._in_memory_messages:
            self._in_memory_messages[session_id] = []
        self._in_memory_messages[session_id].append(payload)
        return payload

    async def get_recent_messages(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent messages for AI prompt context."""
        cli = self.client
        if cli is not None:
            try:
                query = (
                    cli.collection("roleplay_sessions")
                    .document(session_id)
                    .collection("messages")
                    .order_by("created_at", direction=google_firestore.Query.DESCENDING)
                    .limit(limit)
                )
                docs = query.stream()
                messages = [doc.to_dict() for doc in docs]
                messages.reverse()  # Return in chronological order
                return messages
            except Exception as e:
                logger.error("Error querying recent messages from Firestore %s: %s", session_id, e)

        # In-memory fallback
        all_msgs = self._in_memory_messages.get(session_id, [])
        return all_msgs[-limit:]

    async def get_all_messages(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Retrieve paginated messages for frontend history."""
        cli = self.client
        if cli is not None:
            try:
                query = (
                    cli.collection("roleplay_sessions")
                    .document(session_id)
                    .collection("messages")
                    .order_by("created_at", direction=google_firestore.Query.ASCENDING)
                    .offset(offset)
                    .limit(limit)
                )
                docs = query.stream()
                return [doc.to_dict() for doc in docs]
            except Exception as e:
                logger.error("Error querying all messages from Firestore %s: %s", session_id, e)

        # In-memory fallback
        all_msgs = self._in_memory_messages.get(session_id, [])
        return all_msgs[offset : offset + limit]


firebase_service = FirebaseService()
