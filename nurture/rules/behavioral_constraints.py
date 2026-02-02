"""
Behavioral Constraints for Nurture Simulation
==============================================

Defines hard and soft constraints on agent behavior to ensure
appropriate, realistic, and safe interactions.

Constraints are different from rules:
- Rules suggest modifications based on conditions
- Constraints enforce limits and filter inappropriate content
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Set, Optional, Callable
from enum import Enum, auto


class ConstraintType(Enum):
    """Types of behavioral constraints."""
    HARD = "hard"      # Must never be violated
    SOFT = "soft"      # Should generally be followed
    PREFERENCE = "preference"  # Nice to have


class ConstraintDomain(Enum):
    """Domains that constraints apply to."""
    RESPONSE_CONTENT = "response_content"
    EMOTIONAL_RANGE = "emotional_range"
    BEHAVIORAL_LIMIT = "behavioral_limit"
    RELATIONSHIP_BOUND = "relationship_bound"
    SAFETY = "safety"


@dataclass
class Constraint:
    """
    A behavioral constraint that limits agent actions.
    
    Constraints define boundaries that agents should not cross.
    They can filter, modify, or block behaviors and responses.
    
    Attributes:
        id: Unique constraint identifier
        name: Human-readable name
        description: What this constraint does
        constraint_type: Hard, soft, or preference
        domain: What aspect of behavior it constrains
        check: Function(value) -> bool (True if constraint is satisfied)
        correction: Optional function to correct violations
        violation_message: Message to log on violation
    """
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
    """
    Manager for behavioral constraints.
    
    Features:
    - Register and manage constraints
    - Check values against constraints
    - Apply corrections for violations
    - Report constraint status
    
    Usage:
        constraints = BehavioralConstraints()
        constraints.add_default_constraints()
        
        is_valid = constraints.check_response(response_text)
        if not is_valid:
            response_text = constraints.correct_response(response_text)
    """
    
    def __init__(self):
        """Initialize the constraint manager."""
        self._constraints: Dict[str, Constraint] = {}
        self._constraints_by_domain: Dict[ConstraintDomain, List[str]] = {
            domain: [] for domain in ConstraintDomain
        }
        self._violation_log: List[Dict[str, Any]] = []
    
    def add_constraint(self, constraint: Constraint) -> None:
        """Add a constraint to the manager."""
        self._constraints[constraint.id] = constraint
        self._constraints_by_domain[constraint.domain].append(constraint.id)
    
    def remove_constraint(self, constraint_id: str) -> bool:
        """Remove a constraint."""
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
        """
        Check a value against all constraints in a domain.
        
        Args:
            value: Value to check
            domain: Domain of constraints to check
            constraint_type: Optional filter by constraint type
            
        Returns:
            Tuple of (all_passed, list of violated constraint IDs)
        """
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
        """Log a constraint violation."""
        self._violation_log.append({
            "constraint_id": constraint.id,
            "constraint_name": constraint.name,
            "constraint_type": constraint.constraint_type.value,
            "message": constraint.violation_message,
            "value_type": type(value).__name__,
        })
        
        # Keep log bounded
        if len(self._violation_log) > 1000:
            self._violation_log = self._violation_log[-1000:]
    
    def apply_corrections(
        self, 
        value: Any, 
        domain: ConstraintDomain
    ) -> tuple:
        """
        Apply corrections for any violated constraints.
        
        Args:
            value: Value to check and correct
            domain: Domain of constraints
            
        Returns:
            Tuple of (corrected_value, list of applied corrections)
        """
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
        """Get recent constraint violations."""
        return self._violation_log[-limit:]
    
    def clear_violation_log(self) -> None:
        """Clear the violation log."""
        self._violation_log.clear()
    
    def add_default_constraints(self) -> None:
        """Add the default set of behavioral constraints."""
        
        # === RESPONSE CONTENT CONSTRAINTS ===
        
        # No empty responses
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
        
        # Response length limits
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
        
        # No inappropriate language (basic filter)
        inappropriate_words = {
            "damn", "hell", "crap"  # Mild - could be expanded or configured
        }
        
        def filter_mild_language(text: str) -> str:
            """Replace mild inappropriate words."""
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
        
        # === EMOTIONAL RANGE CONSTRAINTS ===
        
        # Emotion value bounds
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
        
        # Prevent emotional flatline
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
        
        # === BEHAVIORAL CONSTRAINTS ===
        
        # Interaction count sanity
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
        
        # === RELATIONSHIP CONSTRAINTS ===
        
        # Trust bounds
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
        
        # Prevent instant trust collapse
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
        
        # === SAFETY CONSTRAINTS ===
        
        # No self-harm content
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
        """
        Convenience method to check a response string.
        
        Args:
            response: Response text to check
            
        Returns:
            Tuple of (is_valid, list of violations)
        """
        # Check both content and safety
        content_valid, content_violations = self.check_value(
            response, ConstraintDomain.RESPONSE_CONTENT
        )
        safety_valid, safety_violations = self.check_value(
            response, ConstraintDomain.SAFETY
        )
        
        all_violations = content_violations + safety_violations
        return (len(all_violations) == 0, all_violations)
    
    def correct_response(self, response: str) -> str:
        """
        Convenience method to correct a response string.
        
        Args:
            response: Response text to correct
            
        Returns:
            Corrected response
        """
        # Apply safety corrections first (HARD constraints)
        corrected, _ = self.apply_corrections(response, ConstraintDomain.SAFETY)
        # Then content corrections
        corrected, _ = self.apply_corrections(corrected, ConstraintDomain.RESPONSE_CONTENT)
        return corrected
