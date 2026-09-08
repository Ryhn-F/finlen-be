import json
import logging
import re
from typing import Any, Dict, List
import httpx
from pydantic import ValidationError

from finlen_be.core.config import settings
from finlen_be.models.scenario import Scenario
from finlen_be.schemas.ai import (
    AITurnResponse,
    EvaluationConsequence,
    EvaluationScores,
    StateChanges,
    TurnEvaluation,
)
from finlen_be.services.ai.base import BaseAIService

logger = logging.getLogger(__name__)


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
        return cleaned

    def _create_fallback_response(self, user_message: str, scenario: Scenario) -> AITurnResponse:
        """Safe deterministic fallback when external AI is unreachable or outputs malformed data."""
        msg_lower = user_message.lower()
        is_cautious = any(
            w in msg_lower
            for w in [
                "kontrak",
                "cek",
                "verifikasi",
                "bukti",
                "surat",
                "polisi",
                "ojk",
                "resmi",
                "tidak",
                "tunda",
                "pikir",
                "bunga",
            ]
        )
        if is_cautious:
            scores = EvaluationScores(
                critical_thinking=3,
                risk_awareness=3,
                impulse_control=2,
                decision_making=2,
            )
            consequence = EvaluationConsequence(
                description="You maintained caution and requested verification, resisting impulsive pressure.",
                severity="positive",
            )
            feedback = "You paused to evaluate legal/contractual facts instead of succumbing to panic or pressure."
            state_changes = StateChanges(
                collector_pressure=-1,
                financial_risk=-2,
                trust_level=1,
                negotiation_power=2,
            )
            npc_response = (
                f"Saya catat permintaan Anda. Tapi ingat, kewajiban Anda tetap harus diselesaikan. "
                f"Kapan tepatnya Anda bisa memastikan tanggal penyelesaiannya?"
            )
        else:
            scores = EvaluationScores(
                critical_thinking=-1,
                risk_awareness=-1,
                impulse_control=-1,
                decision_making=-1,
            )
            consequence = EvaluationConsequence(
                description="You responded without fully verifying conditions or terms.",
                severity="neutral",
            )
            feedback = "Take time to verify the agreement terms and consider your budget constraints before agreeing."
            state_changes = StateChanges(
                collector_pressure=1,
                financial_risk=1,
                trust_level=0,
                negotiation_power=-1,
            )
            npc_response = (
                f"Bagus kalau Anda paham. Sekarang juga Anda harus tunjukkan komitmen pembayaran Anda!"
            )

        evaluation = TurnEvaluation(
            scores=scores,
            consequence=consequence,
            feedback=feedback,
            state_changes=state_changes,
        )
        return AITurnResponse(
            evaluation=evaluation,
            state_changes=state_changes,
            npc_response=npc_response,
        )

    async def generate_first_npc_message(self, scenario: Scenario) -> str:
        """Generate the in-character greeting from the NPC using Gemini."""
        system_prompt = (
            f"You are roleplaying as {scenario.npc_role} in this scenario: {scenario.title}.\n"
            f"Scenario Context: {json.dumps(scenario.financial_context, ensure_ascii=False)}\n"
            f"System Instructions: {scenario.system_prompt}\n"
            f"Generate an authentic, concise first opening message (in Indonesian) to initiate contact with the user. "
            f"Do not include meta comments, greetings like 'Sure, here is the opening', or markdown formatting. Only dialogue."
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
                "maxOutputTokens": 300,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                )
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            content = parts[0].get("text", "")
                            if content and content.strip():
                                return content.strip()
        except Exception as e:
            logger.warning("Gemini request failed for opening message: %s. Using default opening.", e)

        # Fallback opening tailored per scenario
        if scenario.slug == "aggressive-debt-collector":
            return (
                "Halo! Ini Budi dari penagihan pelunasan kredit. Pinjaman Anda sebesar Rp3.000.000 sudah menunggak 2 bulan! "
                "Hari ini juga harus ada pembayaran, atau tim kami akan mendatangi alamat Anda!"
            )
        elif scenario.slug == "illegal-pinjol-threat":
            return (
                "Woi! Tagihan Rp2.800.000 Anda sudah lewat jatuh tempo! Dalam 30 menit kalau tidak transfer bukti bayar, "
                "semua kontak di HP Anda akan saya hubungi dan data Anda kami sebarkan!"
            )
        elif scenario.slug == "impulsive-flash-sale-fomo":
            return (
                "Halo Bosku! Tinggal 5 menit lagi flash sale 11.11 ditutup! HP Flagship cuma Rp5.999.000, sisa 3 unit lagi! "
                "Jangan sampai nyesel seumur hidup, langsung checkout pakai cicilan sekarang!"
            )
        else:
            return (
                f"Halo, saya {scenario.npc_role}. Mengenai situasi terkait {scenario.title}, "
                f"kita perlu membicarakan ini sekarang."
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
            f"7. You MUST respond with ONLY a single valid JSON object matching this exact schema:\n"
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
            f'  "npc_response": "In-character dialogue spoken by NPC in Indonesian"\n'
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
                "maxOutputTokens": 1000,
                "responseMimeType": "application/json",
            },
        }

        # Try API call with retry
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    res = await client.post(
                        endpoint,
                        headers=headers,
                        json=payload,
                    )
                    if res.status_code == 200:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if not candidates:
                            logger.warning("Gemini returned 200 but candidate list is empty (attempt %d)", attempt + 1)
                            continue
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if not parts:
                            logger.warning("Gemini returned 200 but parts list is empty (attempt %d)", attempt + 1)
                            continue
                        raw_content = parts[0].get("text")
                        if not raw_content:
                            logger.warning("Gemini returned 200 but content is null/empty (attempt %d)", attempt + 1)
                            continue
                        cleaned_json = self._clean_json_string(raw_content)
                        parsed = json.loads(cleaned_json)
                        # Ensure state_changes is nested in evaluation for schema compatibility if needed
                        if "evaluation" in parsed and "state_changes" in parsed:
                            parsed["evaluation"]["state_changes"] = parsed["state_changes"]
                        return AITurnResponse.model_validate(parsed)
                    else:
                        logger.warning(
                            "Gemini returned status %d (attempt %d): %s",
                            res.status_code,
                            attempt + 1,
                            res.text,
                        )
            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning("Gemini JSON or schema validation error (attempt %d): %s", attempt + 1, e)
            except Exception as e:
                logger.warning("Gemini HTTP network error (attempt %d): %s", attempt + 1, e)

        # If all attempts fail, use deterministic fallback
        logger.info("Using deterministic fallback response for turn.")
        return self._create_fallback_response(user_message, scenario)


ai_service = GeminiAIService()
