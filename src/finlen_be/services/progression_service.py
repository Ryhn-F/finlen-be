from finlen_be.models.roleplay_session import RoleplaySession
from finlen_be.models.user import User
from finlen_be.schemas.ai import EvaluationScores, TurnEvaluation
from finlen_be.schemas.roleplay import SessionScores, UserProgressionUpdate


def clamp(val: int, min_val: int = 0, max_val: int = 100) -> int:
    return max(min_val, min(max_val, val))


class ProgressionService:
    @staticmethod
    def calculate_turn_xp(evaluation: TurnEvaluation) -> int:
        """Deterministic XP awarded per turn based on decision evaluation."""
        base_xp = 10
        score_deltas_sum = (
            evaluation.scores.critical_thinking
            + evaluation.scores.risk_awareness
            + evaluation.scores.impulse_control
            + evaluation.scores.decision_making
        )
        delta_bonus = max(0, score_deltas_sum * 5)

        severity_bonus = {
            "positive": 15,
            "neutral": 5,
            "negative": 0,
            "critical": 0,
        }.get(evaluation.consequence.severity, 0)

        return max(5, base_xp + delta_bonus + severity_bonus)

    @staticmethod
    def apply_turn_scores(
        session: RoleplaySession,
        scores_delta: EvaluationScores,
        turn_xp: int,
    ) -> SessionScores:
        """Apply bounded deltas to session scores and recalculate composite financial instinct."""
        # Baseline start: if all scores are 0 on first turn, set baseline to 50
        if (
            session.critical_thinking == 0
            and session.risk_awareness == 0
            and session.impulse_control == 0
            and session.decision_making == 0
        ):
            session.critical_thinking = 50
            session.risk_awareness = 50
            session.impulse_control = 50
            session.decision_making = 50

        session.critical_thinking = clamp(
            session.critical_thinking + scores_delta.critical_thinking * 2
        )
        session.risk_awareness = clamp(
            session.risk_awareness + scores_delta.risk_awareness * 2
        )
        session.impulse_control = clamp(
            session.impulse_control + scores_delta.impulse_control * 2
        )
        session.decision_making = clamp(
            session.decision_making + scores_delta.decision_making * 2
        )

        composite = round(
            (
                session.critical_thinking
                + session.risk_awareness
                + session.impulse_control
                + session.decision_making
            )
            / 4
        )
        session.financial_instinct_score = clamp(composite)
        session.xp_earned += turn_xp

        return SessionScores(
            critical_thinking=session.critical_thinking,
            risk_awareness=session.risk_awareness,
            impulse_control=session.impulse_control,
            decision_making=session.decision_making,
            financial_instinct=session.financial_instinct_score,
        )

    @staticmethod
    def finalize_user_progression(
        user: User,
        session: RoleplaySession,
    ) -> UserProgressionUpdate:
        """Update persistent user level, XP, and financial instinct upon session completion."""
        xp_gained = session.xp_earned
        user.xp += xp_gained
        # Level formula: 100 XP per level
        new_level = max(1, (user.xp // 100) + 1)
        user.level = new_level

        # Financial instinct moving average
        session_instinct = float(session.financial_instinct_score)
        if float(user.financial_instinct) == 0.0:
            user.financial_instinct = round(session_instinct, 2)
        else:
            updated_instinct = (0.6 * float(user.financial_instinct)) + (0.4 * session_instinct)
            user.financial_instinct = round(min(100.0, max(0.0, updated_instinct)), 2)

        return UserProgressionUpdate(
            user_id=user.id,
            level=user.level,
            xp=user.xp,
            xp_gained=xp_gained,
            financial_instinct=float(user.financial_instinct),
        )


progression_service = ProgressionService()
