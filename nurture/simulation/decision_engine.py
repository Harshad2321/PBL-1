from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict

from nurture.simulation.state_models import AIParentState, RelationshipState


class ResponseType(str, Enum):
    COOPERATIVE = "cooperative"
    CONFRONTATIONAL = "confrontational"
    AVOIDANT = "avoidant"
    SUPPORTIVE = "supportive"
    NEUTRAL = "neutral"


@dataclass
class DecisionContext:
    scenario_key: str
    relationship: RelationshipState
    ai_parent: AIParentState
    player_choice_id: str


class DecisionEngine:

    def decide(self, context: DecisionContext) -> ResponseType:
        rs = context.relationship
        ai = context.ai_parent

        if rs.trust >= 0.72 and rs.communication_openness >= 0.65 and ai.stress_level <= 0.35:
            return ResponseType.COOPERATIVE

        if rs.resentment >= 0.65 or ai.defensiveness >= 0.70:
            return ResponseType.CONFRONTATIONAL

        if ai.stress_level >= 0.75 and rs.communication_openness < 0.50:
            return ResponseType.AVOIDANT

        if rs.supportiveness >= 0.62 and ai.emotional_safety >= 0.60:
            return ResponseType.SUPPORTIVE

        return ResponseType.NEUTRAL

    def build_reasoning_snapshot(self, context: DecisionContext) -> Dict[str, float]:
        return {
            "trust": context.relationship.trust,
            "resentment": context.relationship.resentment,
            "stress_level": context.ai_parent.stress_level,
            "communication_openness": context.relationship.communication_openness,
            "supportiveness": context.relationship.supportiveness,
            "defensiveness": context.ai_parent.defensiveness,
        }
