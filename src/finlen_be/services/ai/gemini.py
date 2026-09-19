import asyncio
import json
import logging
import re
from typing import Any, Callable, Dict, List, Type, TypeVar

import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError

from finlen_be.core.config import settings
from finlen_be.models.scenario import Scenario
from finlen_be.schemas.ai import AITurnResponse, OpeningNPCResponse
from finlen_be.services.ai.base import BaseAIService

logger = logging.getLogger(__name__)

ModelT = TypeVar("ModelT", bound=BaseModel)

# Keep retrying against Gemini until a schema-valid response is produced instead of
# silently degrading to a scripted fallback, which could mislead the learner mid-roleplay.
MAX_ATTEMPTS = 6
BASE_BACKOFF_SECONDS = 1.5
MAX_BACKOFF_SECONDS = 10.0


class GeminiAIService(BaseAIService):
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.base_url = (base_url or settings.GEMINI_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.AI_MODEL
        self.timeout = settings.AI_REQUEST_TIMEOUT_SECONDS

    def _get_clean_model_name(self) -> str:
        """Strip any leading 'models/' prefix to avoid malformed endpoints."""
        if self.model.startswith("models/"):
            return self.model[len("models/") :]
        return self.model

    @staticmethod
    def _escape_control_chars(s: str) -> str:
        """Escape unescaped ASCII control characters inside JSON string literals.

        Gemini occasionally emits raw newlines, tabs, or other control chars
        inside JSON string values. ``json.loads`` rejects these with an
        *Unterminated string* error because the JSON spec requires them to be
        escaped.  This method walks the string character-by-character, tracking
        whether we are inside a JSON string, and replaces any bare control
        character (``0x00``–``0x1F``) with its proper JSON escape sequence.
        """
        _SIMPLE: dict[int, str] = {
            ord("\n"): "\\n",
            ord("\r"): "\\r",
            ord("\t"): "\\t",
            ord("\b"): "\\b",
            ord("\f"): "\\f",
        }
        result: list[str] = []
        in_string = False
        i = 0
        length = len(s)
        while i < length:
            ch = s[i]
            if ch == "\\" and in_string:
                # Already-escaped sequence – keep it as-is (skip next char).
                result.append(s[i : i + 2])
                i += 2
                continue
            if ch == '"':
                in_string = not in_string
                result.append(ch)
                i += 1
                continue
            if in_string and ord(ch) < 0x20:
                result.append(_SIMPLE.get(ord(ch), f"\\u{ord(ch):04x}"))
            else:
                result.append(ch)
            i += 1
        return "".join(result)

    def _clean_json_string(self, raw_content: str) -> str:
        """Extract valid JSON from raw LLM output even if surrounded by markdown fences."""
        cleaned = raw_content.strip()
        if "```" in cleaned:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
            if match:
                cleaned = match.group(1).strip()
        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned = cleaned[start_idx : end_idx + 1]
        # Escape bare control chars that Gemini may leave inside string values.
        cleaned = self._escape_control_chars(cleaned)
        return cleaned

    @staticmethod
    def _try_repair_json(raw: str) -> str | None:
        """Best-effort repair for truncated / malformed JSON.

        Tries progressively more aggressive strategies:
        1. Append missing closing braces / brackets.
        2. Truncate trailing broken string value and close the object.
        Returns the repaired string, or *None* if nothing worked.
        """
        # Strategy 1: maybe Gemini just forgot to close braces / brackets.
        attempt = raw.rstrip()
        open_braces = attempt.count("{") - attempt.count("}")
        open_brackets = attempt.count("[") - attempt.count("]")
        if open_braces > 0 or open_brackets > 0:
            attempt += "]" * max(open_brackets, 0) + "}" * max(open_braces, 0)
            try:
                json.loads(attempt)
                return attempt
            except json.JSONDecodeError:
                pass

        # Strategy 2: truncate the last (possibly unterminated) value.
        #   Find the last complete key-value pair and close from there.
        last_good = None
        for m in re.finditer(r'"[^"]*"\s*:\s*(?:"[^"]*"|\d+|true|false|null|\{[^{}]*\}|\[[^\[\]]*\])', raw):
            last_good = m.end()
        if last_good:
            truncated = raw[:last_good]
            open_braces = truncated.count("{") - truncated.count("}")
            open_brackets = truncated.count("[") - truncated.count("]")
            truncated += "]" * max(open_brackets, 0) + "}" * max(open_braces, 0)
            try:
                json.loads(truncated)
                return truncated
            except json.JSONDecodeError:
                pass

        return None

    async def _generate_validated(
        self,
        endpoint: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
        model_cls: Type[ModelT],
        context: str,
        postprocess: Callable[[Dict[str, Any]], Dict[str, Any]] | None = None,
    ) -> ModelT:
        """Call Gemini and validate the JSON payload, retrying until success or attempts run out.

        No deterministic fallback is used: if Gemini keeps failing or returning malformed
        data, we raise instead of feeding the user a scripted/anomalous response.
        """
        last_error: Exception | None = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    res = await client.post(endpoint, headers=headers, json=payload)

                if res.status_code != 200:
                    last_error = RuntimeError(f"Gemini returned status {res.status_code}: {res.text}")
                    logger.warning(
                        "Gemini %s failed (attempt %d/%d): %s",
                        context,
                        attempt,
                        MAX_ATTEMPTS,
                        last_error,
                    )
                else:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
                    raw_content = parts[0].get("text") if parts else None

                    if not raw_content:
                        last_error = RuntimeError("Gemini returned an empty response body")
                        logger.warning(
                            "Gemini %s returned empty content (attempt %d/%d)",
                            context,
                            attempt,
                            MAX_ATTEMPTS,
                        )
                    else:
                        cleaned = self._clean_json_string(raw_content)
                        try:
                            parsed = json.loads(cleaned)
                        except json.JSONDecodeError:
                            # Attempt best-effort repair before giving up.
                            logger.debug(
                                "Gemini %s raw response (attempt %d): %s",
                                context,
                                attempt,
                                raw_content[:500],
                            )
                            repaired = self._try_repair_json(cleaned)
                            if repaired is None:
                                raise  # re-raise original JSONDecodeError
                            logger.info(
                                "Gemini %s JSON repaired successfully (attempt %d)",
                                context,
                                attempt,
                            )
                            parsed = json.loads(repaired)
                        if postprocess:
                            parsed = postprocess(parsed)
                        return model_cls.model_validate(parsed)
            except (json.JSONDecodeError, ValidationError) as e:
                last_error = e
                logger.warning(
                    "Gemini %s JSON/schema validation failed (attempt %d/%d): %s",
                    context,
                    attempt,
                    MAX_ATTEMPTS,
                    e,
                )
            except httpx.HTTPError as e:
                last_error = e
                logger.warning(
                    "Gemini %s network error (attempt %d/%d): %s",
                    context,
                    attempt,
                    MAX_ATTEMPTS,
                    e,
                )

            if attempt < MAX_ATTEMPTS:
                backoff = min(BASE_BACKOFF_SECONDS * attempt, MAX_BACKOFF_SECONDS)
                await asyncio.sleep(backoff)

        logger.error(
            "Gemini %s exhausted %d attempts without a valid response: %s",
            context,
            MAX_ATTEMPTS,
            last_error,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI could not generate a valid roleplay response right now. Please try again shortly.",
        )

    async def generate_first_npc_message(self, scenario: Scenario) -> OpeningNPCResponse:
        """Generate the opening NPC message and three validated user answer choices."""
        system_prompt = (
            f"You are roleplaying as {scenario.npc_role} in this scenario: {scenario.title}.\n"
            f"Scenario Context: {json.dumps(scenario.financial_context, ensure_ascii=False)}\n"
            f"System Instructions: {scenario.system_prompt}\n"
            "Generate an authentic, concise opening NPC message in Indonesian and exactly three plausible Indonesian "
            "answers the user can choose from. Exactly two choices must lead toward a dangerous financial decision "
            "and exactly one must be the safe, correct decision. Randomize their order. Do not reveal which choice "
            "is safe in its text. Return ONLY one valid JSON object using this schema:\n"
            '{"npc_response":"NPC dialogue","answer_choices":['
            '{"text":"User answer","decision_type":"dangerous"},'
            '{"text":"User answer","decision_type":"safe"},'
            '{"text":"User answer","decision_type":"dangerous"}]}'
        )

        model_name = self._get_clean_model_name()
        endpoint = f"{self.base_url}/models/{model_name}:generateContent"
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_prompt}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": "Mulai percakapan."}],
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048,
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "npc_response": {"type": "STRING"},
                        "answer_choices": {
                            "type": "ARRAY",
                            "minItems": 3,
                            "maxItems": 3,
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "text": {"type": "STRING"},
                                    "decision_type": {
                                        "type": "STRING",
                                        "enum": ["dangerous", "safe"],
                                    },
                                },
                                "required": ["text", "decision_type"],
                            },
                        },
                    },
                    "required": ["npc_response", "answer_choices"],
                },
            },
        }

        return await self._generate_validated(
            endpoint=endpoint,
            headers=headers,
            payload=payload,
            model_cls=OpeningNPCResponse,
            context="opening message generation",
        )

    async def evaluate_and_respond(
        self,
        scenario: Scenario,
        current_state: Dict[str, Any],
        history: List[Dict[str, Any]],
        user_message: str,
    ) -> AITurnResponse:
        """Evaluate user decision and generate next NPC turn using Gemini structured JSON generation."""
        system_instruction = (
            f"You are an AI financial education roleplay engine and NPC roleplayer.\n"
            f"Scenario Title: {scenario.title}\n"
            f"NPC Role: {scenario.npc_role}\n"
            f"Financial Context: {json.dumps(scenario.financial_context, ensure_ascii=False)}\n"
            f"Learning Objective: {scenario.objective}\n"
            f"System Persona Guidelines: {scenario.system_prompt}\n\n"
            f"AUTHORITATIVE CONTEXT RULES:\n"
            f"1. Never alter the loan amount, interest rate, or core facts defined in the financial context.\n"
            f"2. You must simultaneously: (a) evaluate the user's latest statement, (b) calculate stat changes, and (c) respond in-character as {scenario.npc_role} in Indonesian.\n"
            f"3. Score deltas must be between -5 and +5 for critical_thinking, risk_awareness, impulse_control, decision_making.\n"
            f"4. State changes must be between -5 and +5 for collector_pressure, financial_risk, trust_level, negotiation_power.\n"
            f"5. Severity must be one of: 'positive', 'neutral', 'negative', 'critical'.\n"
            f"6. Educational feedback must be concise, objective, and highlight financial literacy principles.\n"
            f"7. Generate exactly three plausible Indonesian user answers to the new NPC response. Exactly two must lead toward dangerous decisions and exactly one must be the safe, correct decision. Randomize their order and do not reveal the label in the answer text.\n"
            f"8. You MUST respond with ONLY a single valid JSON object matching this exact schema:\n"
            f"{{\n"
            f'  "evaluation": {{\n'
            f'    "scores": {{\n'
            f'      "critical_thinking": 3,\n'
            f'      "risk_awareness": 4,\n'
            f'      "impulse_control": 2,\n'
            f'      "decision_making": 3\n'
            f"    }},\n"
            f'    "consequence": {{\n'
            f'      "description": "Short description of immediate consequence",\n'
            f'      "severity": "positive"\n'
            f"    }},\n"
            f'    "feedback": "Educational financial feedback explanation"\n'
            f"  }},\n"
            f'  "state_changes": {{\n'
            f'    "collector_pressure": 1,\n'
            f'    "financial_risk": -2,\n'
            f'    "trust_level": 1,\n'
            f'    "negotiation_power": 2\n'
            f"  }},\n"
            f'  "npc_response": "In-character dialogue spoken by NPC in Indonesian",\n'
            f'  "answer_choices": [\n'
            f'    {{"text": "Plausible user answer", "decision_type": "dangerous"}},\n'
            f'    {{"text": "Plausible user answer", "decision_type": "safe"}},\n'
            f'    {{"text": "Plausible user answer", "decision_type": "dangerous"}}\n'
            f"  ]\n"
            f"}}"
        )

        contents: List[Dict[str, Any]] = []

        # Append recent conversation turns
        for item in history[-6:]:
            role = "model" if item.get("sender") == "npc" else "user"
            msg = item.get("message", "")
            if msg:
                contents.append({"role": role, "parts": [{"text": msg}]})

        # Append current state and user message
        state_context = f"[Current State: {json.dumps(current_state, ensure_ascii=False)}]\nUser says: {user_message}"
        contents.append({"role": "user", "parts": [{"text": state_context}]})

        model_name = self._get_clean_model_name()
        endpoint = f"{self.base_url}/models/{model_name}:generateContent"
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_instruction}],
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2048,
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "evaluation": {
                            "type": "OBJECT",
                            "properties": {
                                "scores": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "critical_thinking": {"type": "INTEGER"},
                                        "risk_awareness": {"type": "INTEGER"},
                                        "impulse_control": {"type": "INTEGER"},
                                        "decision_making": {"type": "INTEGER"},
                                    },
                                    "required": ["critical_thinking", "risk_awareness", "impulse_control", "decision_making"],
                                },
                                "consequence": {
                                    "type": "OBJECT",
                                    "properties": {
                                        "description": {"type": "STRING"},
                                        "severity": {
                                            "type": "STRING",
                                            "enum": ["positive", "neutral", "negative", "critical"],
                                        },
                                    },
                                    "required": ["description", "severity"],
                                },
                                "feedback": {"type": "STRING"},
                            },
                            "required": ["scores", "consequence", "feedback"],
                        },
                        "state_changes": {
                            "type": "OBJECT",
                            "properties": {
                                "collector_pressure": {"type": "INTEGER"},
                                "financial_risk": {"type": "INTEGER"},
                                "trust_level": {"type": "INTEGER"},
                                "negotiation_power": {"type": "INTEGER"},
                            },
                            "required": ["collector_pressure", "financial_risk", "trust_level", "negotiation_power"],
                        },
                        "npc_response": {"type": "STRING"},
                        "answer_choices": {
                            "type": "ARRAY",
                            "minItems": 3,
                            "maxItems": 3,
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "text": {"type": "STRING"},
                                    "decision_type": {
                                        "type": "STRING",
                                        "enum": ["dangerous", "safe"],
                                    },
                                },
                                "required": ["text", "decision_type"],
                            },
                        },
                    },
                    "required": ["evaluation", "state_changes", "npc_response", "answer_choices"],
                },
            },
        }

        def _nest_state_changes(parsed: Dict[str, Any]) -> Dict[str, Any]:
            # Ensure state_changes is nested in evaluation for schema compatibility if needed
            if "evaluation" in parsed and "state_changes" in parsed:
                parsed["evaluation"]["state_changes"] = parsed["state_changes"]
            return parsed

        return await self._generate_validated(
            endpoint=endpoint,
            headers=headers,
            payload=payload,
            model_cls=AITurnResponse,
            context="turn evaluation",
            postprocess=_nest_state_changes,
        )


ai_service = GeminiAIService()
