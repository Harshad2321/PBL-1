from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from nurture.simulation.decision_engine import ResponseType
from nurture.simulation.state_models import AIParentState, ChildState, RelationshipState


@dataclass
class UpdateBundle:
    relationship: Dict[str, float]
    ai_parent: Dict[str, float]
    child: Dict[str, float]


class StateUpdateSystem:

    RESPONSE_IMPACTS: Dict[ResponseType, UpdateBundle] = {
        ResponseType.COOPERATIVE: UpdateBundle(
            relationship={"trust": 0.04, "resentment": -0.03, "communication_openness": 0.03, "supportiveness": 0.03, "defensiveness": -0.02},
            ai_parent={"stress_level": -0.03, "supportiveness": 0.02, "defensiveness": -0.02, "emotional_safety": 0.02},
            child={"attachment_security": 0.02, "emotional_safety": 0.02, "self_worth": 0.01, "conflict_internalization": -0.01},
        ),
        ResponseType.CONFRONTATIONAL: UpdateBundle(
            relationship={"trust": -0.05, "resentment": 0.05, "communication_openness": -0.04, "supportiveness": -0.03, "defensiveness": 0.04},
            ai_parent={"stress_level": 0.04, "supportiveness": -0.03, "defensiveness": 0.03, "emotional_safety": -0.03},
            child={"attachment_security": -0.03, "emotional_safety": -0.04, "self_worth": -0.02, "conflict_internalization": 0.04},
        ),
        ResponseType.AVOIDANT: UpdateBundle(
            relationship={"trust": -0.02, "resentment": 0.03, "communication_openness": -0.05, "supportiveness": -0.02, "defensiveness": 0.01},
            ai_parent={"stress_level": 0.01, "supportiveness": -0.02, "defensiveness": 0.01, "emotional_safety": -0.01},
            child={"attachment_security": -0.02, "emotional_safety": -0.02, "self_worth": -0.01, "conflict_internalization": 0.03},
        ),
        ResponseType.SUPPORTIVE: UpdateBundle(
            relationship={"trust": 0.03, "resentment": -0.02, "communication_openness": 0.03, "supportiveness": 0.04, "defensiveness": -0.02},
            ai_parent={"stress_level": -0.02, "supportiveness": 0.03, "defensiveness": -0.01, "emotional_safety": 0.03},
            child={"attachment_security": 0.03, "emotional_safety": 0.03, "self_worth": 0.02, "conflict_internalization": -0.01},
        ),
        ResponseType.NEUTRAL: UpdateBundle(
            relationship={"trust": 0.0, "resentment": 0.0, "communication_openness": 0.0, "supportiveness": 0.0, "defensiveness": 0.0},
            ai_parent={"stress_level": 0.0, "supportiveness": 0.0, "defensiveness": 0.0, "emotional_safety": 0.0},
            child={"attachment_security": 0.0, "emotional_safety": 0.0, "self_worth": 0.0, "conflict_internalization": 0.0},
        ),
    }

    def apply_interaction_updates(
        self,
        response_type: ResponseType,
        relationship_state: RelationshipState,
        ai_parent_state: AIParentState,
        child_state: ChildState,
        scenario_updates: Dict[str, Dict[str, float]],
    ) -> Dict[str, Any]:
        base = self.RESPONSE_IMPACTS[response_type]

        relationship_updates = self._merge(base.relationship, scenario_updates.get("relationship", {}))
        ai_updates = self._merge(base.ai_parent, scenario_updates.get("ai_parent", {}))
        child_updates = self._merge(base.child, scenario_updates.get("child", {}))

        relationship_state.apply_updates(relationship_updates)
        ai_parent_state.apply_updates(ai_updates)
        child_state.apply_updates(child_updates)

        return {
            "response_type": response_type.value,
            "relationship_updates": relationship_updates,
            "ai_parent_updates": ai_updates,
            "child_updates": child_updates,
        }

    @staticmethod
    def _merge(base: Dict[str, float], scenario: Dict[str, float]) -> Dict[str, float]:
        merged = dict(base)
        for key, value in scenario.items():
            merged[key] = merged.get(key, 0.0) + value
        return merged
