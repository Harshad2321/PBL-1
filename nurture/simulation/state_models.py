from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


class AttachmentStyle(str, Enum):
    SECURE = "secure"
    ANXIOUS = "anxious"
    AVOIDANT = "avoidant"
    DISORGANIZED = "disorganized"
    UNLOCKED = "unlocked"


class ConflictTone(str, Enum):
    COLLABORATIVE = "collaborative"
    VOLATILE = "volatile"
    WITHDRAWN = "withdrawn"
    MIXED = "mixed"


class ChildArchetype(str, Enum):
    ANXIOUS = "anxious"
    DEFIANT = "defiant"
    WITHDRAWN = "withdrawn"
    BALANCED = "balanced"


@dataclass
class RelationshipState:
    trust: float = 0.60
    resentment: float = 0.10
    communication_openness: float = 0.55
    emotional_closeness: float = 0.55
    supportiveness: float = 0.55
    defensiveness: float = 0.20
    reliability: float = 0.55
    bond_strength: float = 0.55
    authority_structure: float = 0.50
    forgiveness_rate: float = 0.50
    conflict_intensity: float = 0.30
    relationship_trust_locked: bool = False
    conflict_tone: ConflictTone = ConflictTone.MIXED

    def apply_updates(self, updates: Dict[str, float]) -> None:
        for key, delta in updates.items():
            if not hasattr(self, key):
                continue
            current = getattr(self, key)
            if isinstance(current, float):
                setattr(self, key, _clamp(current + delta))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trust": self.trust,
            "resentment": self.resentment,
            "communication_openness": self.communication_openness,
            "emotional_closeness": self.emotional_closeness,
            "supportiveness": self.supportiveness,
            "defensiveness": self.defensiveness,
            "reliability": self.reliability,
            "bond_strength": self.bond_strength,
            "authority_structure": self.authority_structure,
            "forgiveness_rate": self.forgiveness_rate,
            "conflict_intensity": self.conflict_intensity,
            "relationship_trust_locked": self.relationship_trust_locked,
            "conflict_tone": self.conflict_tone.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelationshipState":
        return cls(
            trust=data.get("trust", 0.60),
            resentment=data.get("resentment", 0.10),
            communication_openness=data.get("communication_openness", 0.55),
            emotional_closeness=data.get("emotional_closeness", 0.55),
            supportiveness=data.get("supportiveness", 0.55),
            defensiveness=data.get("defensiveness", 0.20),
            reliability=data.get("reliability", 0.55),
            bond_strength=data.get("bond_strength", 0.55),
            authority_structure=data.get("authority_structure", 0.50),
            forgiveness_rate=data.get("forgiveness_rate", 0.50),
            conflict_intensity=data.get("conflict_intensity", 0.30),
            relationship_trust_locked=data.get("relationship_trust_locked", False),
            conflict_tone=ConflictTone(data.get("conflict_tone", ConflictTone.MIXED.value)),
        )


@dataclass
class AIParentState:
    stress_level: float = 0.30
    supportiveness: float = 0.55
    defensiveness: float = 0.25
    emotional_safety: float = 0.60
    emotional_availability: float = 0.55
    conflict_style_stability: float = 0.20
    conflict_style: str = "mixed"
    baseline_flexibility: float = 0.50
    adaptation_momentum: float = 0.0

    def apply_updates(self, updates: Dict[str, float]) -> None:
        for key, delta in updates.items():
            if not hasattr(self, key):
                continue
            current = getattr(self, key)
            if isinstance(current, float):
                setattr(self, key, _clamp(current + delta))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stress_level": self.stress_level,
            "supportiveness": self.supportiveness,
            "defensiveness": self.defensiveness,
            "emotional_safety": self.emotional_safety,
            "emotional_availability": self.emotional_availability,
            "conflict_style_stability": self.conflict_style_stability,
            "conflict_style": self.conflict_style,
            "baseline_flexibility": self.baseline_flexibility,
            "adaptation_momentum": self.adaptation_momentum,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIParentState":
        return cls(
            stress_level=data.get("stress_level", 0.30),
            supportiveness=data.get("supportiveness", 0.55),
            defensiveness=data.get("defensiveness", 0.25),
            emotional_safety=data.get("emotional_safety", 0.60),
            emotional_availability=data.get("emotional_availability", 0.55),
            conflict_style_stability=data.get("conflict_style_stability", 0.20),
            conflict_style=data.get("conflict_style", "mixed"),
            baseline_flexibility=data.get("baseline_flexibility", 0.50),
            adaptation_momentum=data.get("adaptation_momentum", 0.0),
        )


@dataclass
class ChildState:
    age_years: int = 0
    attachment_security: float = 0.60
    emotional_safety: float = 0.60
    self_worth: float = 0.60
    conflict_internalization: float = 0.10
    emotional_imprint: float = 0.10
    child_presence_baseline: float = 0.50
    caregiving_trust: float = 0.55
    anxiety_baseline: float = 0.10
    honesty_baseline: float = 0.60
    loyalty_bias: float = 0.50
    withdrawal_pattern: float = 0.10
    manipulation_tendency: float = 0.10
    emotional_expression: float = 0.55
    attachment_style: AttachmentStyle = AttachmentStyle.UNLOCKED
    attachment_locked: bool = False
    archetype: Optional[ChildArchetype] = None
    archetype_locked: bool = False

    def apply_updates(self, updates: Dict[str, float]) -> None:
        for key, delta in updates.items():
            if not hasattr(self, key):
                continue
            current = getattr(self, key)
            if isinstance(current, float):
                setattr(self, key, _clamp(current + delta))

    def lock_attachment_style(self) -> None:
        if self.attachment_locked:
            return

        if self.attachment_security >= 0.70 and self.emotional_safety >= 0.65:
            self.attachment_style = AttachmentStyle.SECURE
        elif self.attachment_security < 0.45 and self.conflict_internalization > 0.60:
            self.attachment_style = AttachmentStyle.DISORGANIZED
        elif self.attachment_security < 0.50:
            self.attachment_style = AttachmentStyle.AVOIDANT
        else:
            self.attachment_style = AttachmentStyle.ANXIOUS

        self.attachment_locked = True

    def lock_archetype(self) -> None:
        if self.archetype_locked:
            return

        if self.anxiety_baseline >= 0.65 and self.emotional_expression < 0.50:
            self.archetype = ChildArchetype.ANXIOUS
        elif self.manipulation_tendency >= 0.60 and self.honesty_baseline < 0.50:
            self.archetype = ChildArchetype.DEFIANT
        elif self.withdrawal_pattern >= 0.65 and self.emotional_expression < 0.40:
            self.archetype = ChildArchetype.WITHDRAWN
        else:
            self.archetype = ChildArchetype.BALANCED

        self.archetype_locked = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "age_years": self.age_years,
            "attachment_security": self.attachment_security,
            "emotional_safety": self.emotional_safety,
            "self_worth": self.self_worth,
            "conflict_internalization": self.conflict_internalization,
            "emotional_imprint": self.emotional_imprint,
            "child_presence_baseline": self.child_presence_baseline,
            "caregiving_trust": self.caregiving_trust,
            "anxiety_baseline": self.anxiety_baseline,
            "honesty_baseline": self.honesty_baseline,
            "loyalty_bias": self.loyalty_bias,
            "withdrawal_pattern": self.withdrawal_pattern,
            "manipulation_tendency": self.manipulation_tendency,
            "emotional_expression": self.emotional_expression,
            "attachment_style": self.attachment_style.value,
            "attachment_locked": self.attachment_locked,
            "archetype": self.archetype.value if self.archetype else None,
            "archetype_locked": self.archetype_locked,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChildState":
        archetype_value = data.get("archetype")
        return cls(
            age_years=data.get("age_years", 0),
            attachment_security=data.get("attachment_security", 0.60),
            emotional_safety=data.get("emotional_safety", 0.60),
            self_worth=data.get("self_worth", 0.60),
            conflict_internalization=data.get("conflict_internalization", 0.10),
            emotional_imprint=data.get("emotional_imprint", 0.10),
            child_presence_baseline=data.get("child_presence_baseline", 0.50),
            caregiving_trust=data.get("caregiving_trust", 0.55),
            anxiety_baseline=data.get("anxiety_baseline", 0.10),
            honesty_baseline=data.get("honesty_baseline", 0.60),
            loyalty_bias=data.get("loyalty_bias", 0.50),
            withdrawal_pattern=data.get("withdrawal_pattern", 0.10),
            manipulation_tendency=data.get("manipulation_tendency", 0.10),
            emotional_expression=data.get("emotional_expression", 0.55),
            attachment_style=AttachmentStyle(data.get("attachment_style", AttachmentStyle.UNLOCKED.value)),
            attachment_locked=data.get("attachment_locked", False),
            archetype=ChildArchetype(archetype_value) if archetype_value else None,
            archetype_locked=data.get("archetype_locked", False),
        )


@dataclass
class MemoryTag:
    tag: str
    intensity: float
    source: str
    day: int
    act: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tag": self.tag,
            "intensity": _clamp(self.intensity),
            "source": self.source,
            "day": self.day,
            "act": self.act,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryTag":
        return cls(
            tag=data["tag"],
            intensity=data.get("intensity", 0.5),
            source=data.get("source", "system"),
            day=data.get("day", 1),
            act=data.get("act", 1),
            metadata=data.get("metadata", {}),
        )


@dataclass
class MemoryTags:
    entries: List[MemoryTag] = field(default_factory=list)

    def add(self, memory_tag: MemoryTag) -> None:
        self.entries.append(memory_tag)

    def recent(self, limit: int = 10) -> List[MemoryTag]:
        return self.entries[-limit:]

    def to_dict(self) -> Dict[str, Any]:
        return {"entries": [entry.to_dict() for entry in self.entries]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryTags":
        entries = [MemoryTag.from_dict(item) for item in data.get("entries", [])]
        return cls(entries=entries)
