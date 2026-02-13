from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, Optional, Tuple
from enum import Enum, auto

class RulePriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5

class RuleCategory(Enum):
    EMOTIONAL = "emotional"
    BEHAVIORAL = "behavioral"
    RELATIONSHIP = "relationship"
    RESPONSE = "response"
    SAFETY = "safety"
    LEARNING = "learning"

@dataclass
class Rule:
    id: str
    name: str
    description: str = ""
    category: RuleCategory = RuleCategory.BEHAVIORAL
    priority: RulePriority = RulePriority.MEDIUM
    condition: Callable[[Dict[str, Any]], bool] = field(default=lambda ctx: True)
    action: Callable[[Dict[str, Any]], Any] = field(default=lambda ctx: None)
    enabled: bool = True

    def evaluate(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        if not self.enabled:
            return (False, None)

        try:
            if self.condition(context):
                result = self.action(context)
                return (True, result)
            return (False, None)
        except Exception as e:
            print(f"Rule {self.id} evaluation error: {e}")
            return (False, None)

class RuleEngine:

    def __init__(self):
        self._rules: Dict[str, Rule] = {}
        self._rules_by_category: Dict[RuleCategory, List[str]] = {
            cat: [] for cat in RuleCategory
        }
        self._sorted_rules: List[Rule] = []
        self._needs_sort = True

    def add_rule(self, rule: Rule) -> None:
        self._rules[rule.id] = rule
        self._rules_by_category[rule.category].append(rule.id)
        self._needs_sort = True

    def remove_rule(self, rule_id: str) -> bool:
        if rule_id in self._rules:
            rule = self._rules[rule_id]
            del self._rules[rule_id]
            self._rules_by_category[rule.category].remove(rule_id)
            self._needs_sort = True
            return True
        return False

    def enable_rule(self, rule_id: str, enabled: bool = True) -> None:
        if rule_id in self._rules:
            self._rules[rule_id].enabled = enabled

    def get_rule(self, rule_id: str) -> Optional[Rule]:
        return self._rules.get(rule_id)

    def _ensure_sorted(self) -> None:
        if self._needs_sort:
            self._sorted_rules = sorted(
                self._rules.values(),
                key=lambda r: r.priority.value
            )
            self._needs_sort = False

    def evaluate_all(self, context: Dict[str, Any]) -> List[Tuple[str, Any]]:
        self._ensure_sorted()

        results = []
        for rule in self._sorted_rules:
            if rule.enabled:
                fired, result = rule.evaluate(context)
                if fired:
                    results.append((rule.id, result))

        return results

    def evaluate_category(
        self,
        category: RuleCategory,
        context: Dict[str, Any]
    ) -> List[Tuple[str, Any]]:
        results = []
        for rule_id in self._rules_by_category[category]:
            rule = self._rules[rule_id]
            if rule.enabled:
                fired, result = rule.evaluate(context)
                if fired:
                    results.append((rule_id, result))

        return results

    def evaluate_until_match(self, context: Dict[str, Any]) -> Optional[Tuple[str, Any]]:
        self._ensure_sorted()

        for rule in self._sorted_rules:
            if rule.enabled:
                fired, result = rule.evaluate(context)
                if fired:
                    return (rule.id, result)

        return None

    def apply_results(
        self,
        context: Dict[str, Any],
        results: List[Tuple[str, Any]]
    ) -> Dict[str, Any]:
        modified = context.copy()

        for rule_id, result in results:
            if isinstance(result, dict):
                modified.update(result)

        return modified

    def get_all_rules(self) -> List[Rule]:
        return list(self._rules.values())

    def get_rules_by_category(self, category: RuleCategory) -> List[Rule]:
        return [self._rules[rid] for rid in self._rules_by_category[category]]

    def clear(self) -> None:
        self._rules.clear()
        self._rules_by_category = {cat: [] for cat in RuleCategory}
        self._sorted_rules.clear()
        self._needs_sort = False

def create_default_rules() -> List[Rule]:
    rules = []


    rules.append(Rule(
        id="max_stress_limit",
        name="Maximum Stress Limit",
        description="Prevents stress from exceeding safe levels",
        category=RuleCategory.SAFETY,
        priority=RulePriority.CRITICAL,
        condition=lambda ctx: ctx.get("stress_level", 0) > 0.95,
        action=lambda ctx: {
            "stress_level": 0.95,
            "trigger_cooldown": True,
            "force_strategy": "avoidant"
        }
    ))

    rules.append(Rule(
        id="anger_limit",
        name="Anger Limit",
        description="Prevents anger from causing harmful responses",
        category=RuleCategory.SAFETY,
        priority=RulePriority.CRITICAL,
        condition=lambda ctx: ctx.get("anger", 0) > 0.9,
        action=lambda ctx: {
            "anger": 0.9,
            "block_aggressive_response": True,
            "suggest_pause": True
        }
    ))


    rules.append(Rule(
        id="high_stress_patience_reduction",
        name="Stress Reduces Patience",
        description="High stress levels reduce patience",
        category=RuleCategory.EMOTIONAL,
        priority=RulePriority.HIGH,
        condition=lambda ctx: ctx.get("stress_level", 0) > 0.6,
        action=lambda ctx: {
            "patience_modifier": -0.2,
            "irritability_boost": 0.1
        }
    ))

    rules.append(Rule(
        id="positive_feedback_boost",
        name="Positive Feedback Boost",
        description="Positive partner messages boost mood",
        category=RuleCategory.EMOTIONAL,
        priority=RulePriority.MEDIUM,
        condition=lambda ctx: ctx.get("partner_sentiment", 0) > 0.5,
        action=lambda ctx: {
            "joy_boost": 0.1,
            "trust_boost": 0.05,
            "reduce_stress": 0.05
        }
    ))

    rules.append(Rule(
        id="accusation_response",
        name="Accusation Emotional Response",
        description="Accusations trigger defensive emotions",
        category=RuleCategory.EMOTIONAL,
        priority=RulePriority.HIGH,
        condition=lambda ctx: ctx.get("is_accusation", False),
        action=lambda ctx: {
            "hurt_feeling": 0.15,
            "defensive_mode": True,
            "trust_reduction": 0.05
        }
    ))


    rules.append(Rule(
        id="conflict_escalation_prevention",
        name="Conflict Escalation Prevention",
        description="Prevent conflict from escalating too quickly",
        category=RuleCategory.BEHAVIORAL,
        priority=RulePriority.MEDIUM,
        condition=lambda ctx: (
            ctx.get("disagreement_streak", 0) > 2 and
            ctx.get("conflict_count", 0) > 3
        ),
        action=lambda ctx: {
            "prefer_deescalation": True,
            "strategy_boost": {"compromising": 0.3, "empathetic": 0.2},
            "strategy_penalty": {"challenging": 0.3, "assertive": 0.2}
        }
    ))

    rules.append(Rule(
        id="warmth_response_style",
        name="Warmth Influences Response",
        description="High warmth personality prefers supportive responses",
        category=RuleCategory.BEHAVIORAL,
        priority=RulePriority.MEDIUM,
        condition=lambda ctx: ctx.get("warmth", 0.5) > 0.7,
        action=lambda ctx: {
            "strategy_boost": {"supportive": 0.2, "empathetic": 0.2},
            "prefer_emotional_connection": True
        }
    ))

    rules.append(Rule(
        id="strict_response_style",
        name="Strictness Influences Response",
        description="High strictness prefers assertive responses",
        category=RuleCategory.BEHAVIORAL,
        priority=RulePriority.MEDIUM,
        condition=lambda ctx: ctx.get("strictness", 0.5) > 0.7,
        action=lambda ctx: {
            "strategy_boost": {"assertive": 0.2, "practical": 0.15},
            "prefer_direct_communication": True
        }
    ))


    rules.append(Rule(
        id="low_trust_caution",
        name="Low Trust Caution",
        description="Low trust leads to more cautious interactions",
        category=RuleCategory.RELATIONSHIP,
        priority=RulePriority.MEDIUM,
        condition=lambda ctx: ctx.get("trust_in_partner", 0.7) < 0.4,
        action=lambda ctx: {
            "guarded_response": True,
            "strategy_boost": {"avoidant": 0.15, "practical": 0.1},
            "reduce_vulnerability": True
        }
    ))

    rules.append(Rule(
        id="high_trust_openness",
        name="High Trust Openness",
        description="High trust enables more open communication",
        category=RuleCategory.RELATIONSHIP,
        priority=RulePriority.MEDIUM,
        condition=lambda ctx: ctx.get("trust_in_partner", 0.7) > 0.8,
        action=lambda ctx: {
            "open_communication": True,
            "strategy_boost": {"emotional": 0.1, "supportive": 0.1},
            "allow_vulnerability": True
        }
    ))

    rules.append(Rule(
        id="relationship_repair_opportunity",
        name="Relationship Repair Opportunity",
        description="After conflict, look for repair opportunities",
        category=RuleCategory.RELATIONSHIP,
        priority=RulePriority.LOW,
        condition=lambda ctx: (
            ctx.get("recent_conflict", False) and
            ctx.get("partner_sentiment", 0) > 0.3
        ),
        action=lambda ctx: {
            "repair_opportunity": True,
            "strategy_boost": {"empathetic": 0.3, "compromising": 0.2},
            "reduce_defensiveness": True
        }
    ))


    rules.append(Rule(
        id="match_emotional_intensity",
        name="Match Emotional Intensity",
        description="Response intensity should roughly match input",
        category=RuleCategory.RESPONSE,
        priority=RulePriority.MEDIUM,
        condition=lambda ctx: True,
        action=lambda ctx: {
            "target_intensity": ctx.get("message_intensity", 0.5) * 0.8 + 0.2
        }
    ))

    rules.append(Rule(
        id="question_requires_answer",
        name="Question Requires Answer",
        description="Questions should receive informative responses",
        category=RuleCategory.RESPONSE,
        priority=RulePriority.MEDIUM,
        condition=lambda ctx: ctx.get("is_question", False),
        action=lambda ctx: {
            "should_inform": True,
            "strategy_boost": {"practical": 0.2}
        }
    ))

    return rules
