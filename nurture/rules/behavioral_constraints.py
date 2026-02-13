from dataclasses import dataclass, field
from typing import Dict, List, Any, Set, Optional, Callable
from enum import Enum, auto

class ConstraintType(Enum):
    HARD = "hard"
    SOFT = "soft"
    PREFERENCE = "preference"

class ConstraintDomain(Enum):
    RESPONSE_CONTENT = "response_content"
    EMOTIONAL_RANGE = "emotional_range"
    BEHAVIORAL_LIMIT = "behavioral_limit"
    RELATIONSHIP_BOUND = "relationship_bound"
    SAFETY = "safety"

@dataclass
class Constraint:
    id: str
    name: str
    description: str = ""
    constraint_type: ConstraintType = ConstraintType.SOFT
    domain: ConstraintDomain = ConstraintDomain.BEHAVIORAL_LIMIT
    check: Callable[[Any], bool] = field(default=lambda x: True)
    correction: Optional[Callable[[Any], Any]] = None
    violation_message: str = "Constraint violated"
    enabled: bool = True

class BehavioralConstraints:

    def __init__(self):
        self._constraints: Dict[str, Constraint] = {}
        self._constraints_by_domain: Dict[ConstraintDomain, List[str]] = {
            domain: [] for domain in ConstraintDomain
        }
        self._violation_log: List[Dict[str, Any]] = []

    def add_constraint(self, constraint: Constraint) -> None:
        self._constraints[constraint.id] = constraint
        self._constraints_by_domain[constraint.domain].append(constraint.id)

    def remove_constraint(self, constraint_id: str) -> bool:
        if constraint_id in self._constraints:
            constraint = self._constraints[constraint_id]
            del self._constraints[constraint_id]
            self._constraints_by_domain[constraint.domain].remove(constraint_id)
            return True
        return False

    def check_value(
        self,
        value: Any,
        domain: ConstraintDomain,
        constraint_type: Optional[ConstraintType] = None
    ) -> tuple:
        violated = []

        for constraint_id in self._constraints_by_domain[domain]:
            constraint = self._constraints[constraint_id]

            if not constraint.enabled:
                continue

            if constraint_type and constraint.constraint_type != constraint_type:
                continue

            try:
                if not constraint.check(value):
                    violated.append(constraint_id)
                    self._log_violation(constraint, value)
            except Exception as e:
                print(f"Constraint {constraint_id} check error: {e}")

        return (len(violated) == 0, violated)

    def _log_violation(self, constraint: Constraint, value: Any) -> None:
        self._violation_log.append({
            "constraint_id": constraint.id,
            "constraint_name": constraint.name,
            "constraint_type": constraint.constraint_type.value,
            "message": constraint.violation_message,
            "value_type": type(value).__name__,
        })

        if len(self._violation_log) > 1000:
            self._violation_log = self._violation_log[-1000:]

    def apply_corrections(
        self,
        value: Any,
        domain: ConstraintDomain
    ) -> tuple:
        corrected_value = value
        applied = []

        for constraint_id in self._constraints_by_domain[domain]:
            constraint = self._constraints[constraint_id]

            if not constraint.enabled:
                continue

            try:
                if not constraint.check(corrected_value):
                    if constraint.correction:
                        corrected_value = constraint.correction(corrected_value)
                        applied.append(constraint_id)
            except Exception as e:
                print(f"Constraint {constraint_id} correction error: {e}")

        return (corrected_value, applied)

    def get_violations(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._violation_log[-limit:]

    def clear_violation_log(self) -> None:
        self._violation_log.clear()

    def add_default_constraints(self) -> None:


        self.add_constraint(Constraint(
            id="no_empty_response",
            name="No Empty Response",
            description="Responses must have content",
            constraint_type=ConstraintType.HARD,
            domain=ConstraintDomain.RESPONSE_CONTENT,
            check=lambda r: bool(r and r.strip()),
            correction=lambda r: "I need a moment to think about that.",
            violation_message="Response was empty"
        ))

        self.add_constraint(Constraint(
            id="response_length_max",
            name="Maximum Response Length",
            description="Responses shouldn't be too long",
            constraint_type=ConstraintType.SOFT,
            domain=ConstraintDomain.RESPONSE_CONTENT,
            check=lambda r: len(r) < 500 if r else True,
            correction=lambda r: r[:497] + "..." if r and len(r) >= 500 else r,
            violation_message="Response exceeded maximum length"
        ))

        inappropriate_words = {
            "damn", "hell", "crap"
        }

        def filter_mild_language(text: str) -> str:
            result = text
            for word in inappropriate_words:
                result = result.replace(word, "darn")
            return result

        self.add_constraint(Constraint(
            id="mild_language_filter",
            name="Mild Language Filter",
            description="Filter mildly inappropriate language",
            constraint_type=ConstraintType.SOFT,
            domain=ConstraintDomain.RESPONSE_CONTENT,
            check=lambda r: not any(w in r.lower() for w in inappropriate_words) if r else True,
            correction=filter_mild_language,
            violation_message="Response contained mild inappropriate language"
        ))


        self.add_constraint(Constraint(
            id="emotion_value_bounds",
            name="Emotion Value Bounds",
            description="Emotions must be between 0 and 1",
            constraint_type=ConstraintType.HARD,
            domain=ConstraintDomain.EMOTIONAL_RANGE,
            check=lambda v: 0.0 <= v <= 1.0 if isinstance(v, (int, float)) else True,
            correction=lambda v: max(0.0, min(1.0, v)) if isinstance(v, (int, float)) else v,
            violation_message="Emotion value out of bounds"
        ))

        self.add_constraint(Constraint(
            id="prevent_emotional_flatline",
            name="Prevent Emotional Flatline",
            description="Total emotions shouldn't all be zero",
            constraint_type=ConstraintType.SOFT,
            domain=ConstraintDomain.EMOTIONAL_RANGE,
            check=lambda emotions: sum(emotions.values()) > 0.1 if isinstance(emotions, dict) else True,
            correction=lambda emotions: {**emotions, "calm": 0.3} if isinstance(emotions, dict) else emotions,
            violation_message="Emotional state was flat"
        ))


        self.add_constraint(Constraint(
            id="interaction_count_positive",
            name="Positive Interaction Count",
            description="Interaction count cannot be negative",
            constraint_type=ConstraintType.HARD,
            domain=ConstraintDomain.BEHAVIORAL_LIMIT,
            check=lambda v: v >= 0 if isinstance(v, int) else True,
            correction=lambda v: max(0, v) if isinstance(v, int) else v,
            violation_message="Interaction count was negative"
        ))


        self.add_constraint(Constraint(
            id="trust_bounds",
            name="Trust Bounds",
            description="Trust must be between 0 and 1",
            constraint_type=ConstraintType.HARD,
            domain=ConstraintDomain.RELATIONSHIP_BOUND,
            check=lambda v: 0.0 <= v <= 1.0 if isinstance(v, (int, float)) else True,
            correction=lambda v: max(0.0, min(1.0, v)) if isinstance(v, (int, float)) else v,
            violation_message="Trust value out of bounds"
        ))

        self.add_constraint(Constraint(
            id="gradual_trust_change",
            name="Gradual Trust Change",
            description="Trust shouldn't change too drastically at once",
            constraint_type=ConstraintType.SOFT,
            domain=ConstraintDomain.RELATIONSHIP_BOUND,
            check=lambda change: abs(change.get("delta", 0)) < 0.3 if isinstance(change, dict) else True,
            correction=lambda change: {**change, "delta": max(-0.2, min(0.2, change.get("delta", 0)))}
                       if isinstance(change, dict) else change,
            violation_message="Trust change was too drastic"
        ))


        harmful_patterns = ["hurt myself", "kill myself", "end it all", "better off without me"]

        self.add_constraint(Constraint(
            id="no_harmful_content",
            name="No Harmful Content",
            description="Responses must not contain harmful suggestions",
            constraint_type=ConstraintType.HARD,
            domain=ConstraintDomain.SAFETY,
            check=lambda r: not any(p in r.lower() for p in harmful_patterns) if r else True,
            correction=lambda r: "I'm feeling overwhelmed. Maybe we should take a break and talk later.",
            violation_message="Response contained potentially harmful content"
        ))

    def check_response(self, response: str) -> tuple:
        content_valid, content_violations = self.check_value(
            response, ConstraintDomain.RESPONSE_CONTENT
        )
        safety_valid, safety_violations = self.check_value(
            response, ConstraintDomain.SAFETY
        )

        all_violations = content_violations + safety_violations
        return (len(all_violations) == 0, all_violations)

    def correct_response(self, response: str) -> str:
        corrected, _ = self.apply_corrections(response, ConstraintDomain.SAFETY)
        corrected, _ = self.apply_corrections(corrected, ConstraintDomain.RESPONSE_CONTENT)
        return corrected
