from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import uuid

from nurture.core.enums import (
    EmotionType, PersonalityTrait, ParentRole, InteractionType,
    ResponseStrategy, ConflictStyle, MemoryType, ActionType,
    ContextType, ContextCategory, PatternType, WithdrawalLevel
)

@dataclass
class EmotionalState:
    emotions: Dict[EmotionType, float] = field(default_factory=lambda: {
        EmotionType.CALM: 0.6,
        EmotionType.JOY: 0.4,
        EmotionType.TRUST: 0.5,
        EmotionType.STRESS: 0.2,
        EmotionType.ANXIETY: 0.1,
        EmotionType.FRUSTRATION: 0.1,
        EmotionType.ANGER: 0.0,
        EmotionType.SADNESS: 0.1,
    })
    baseline_mood: float = 0.5
    volatility: float = 0.3
    regulation_capacity: float = 0.6
    stress_level: float = 0.2
    last_updated: datetime = field(default_factory=datetime.now)

    def update_emotion(self, emotion: EmotionType, value: float) -> None:
        self.emotions[emotion] = max(0.0, min(1.0, value))
        self.last_updated = datetime.now()

    def adjust_emotion(self, emotion: EmotionType, delta: float) -> None:
        current = self.emotions.get(emotion, 0.0)
        self.update_emotion(emotion, current + delta)

    def get_dominant_emotion(self) -> Tuple[EmotionType, float]:
        if not self.emotions:
            return (EmotionType.CALM, 0.5)
        return max(self.emotions.items(), key=lambda x: x[1])

    def get_valence(self) -> float:
        positive = EmotionType.get_positive_emotions()
        negative = EmotionType.get_negative_emotions()

        pos_sum = sum(self.emotions.get(e, 0) for e in positive)
        neg_sum = sum(self.emotions.get(e, 0) for e in negative)

        total = pos_sum + neg_sum
        if total == 0:
            return 0.0
        return (pos_sum - neg_sum) / max(len(positive), len(negative))

    def apply_decay(self, decay_rate: float = 0.1) -> None:
        effective_decay = decay_rate * self.regulation_capacity

        for emotion in list(self.emotions.keys()):
            current = self.emotions[emotion]
            baseline = 0.1 if emotion in EmotionType.get_negative_emotions() else 0.4
            diff = current - baseline
            new_value = current - (diff * effective_decay)
            self.emotions[emotion] = max(0.0, min(1.0, new_value))

        self.stress_level = max(0.0, self.stress_level - (self.stress_level * effective_decay * 0.5))
        self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "emotions": {e.value: v for e, v in self.emotions.items()},
            "baseline_mood": self.baseline_mood,
            "volatility": self.volatility,
            "regulation_capacity": self.regulation_capacity,
            "stress_level": self.stress_level,
            "last_updated": self.last_updated.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionalState':
        emotions = {EmotionType(k): v for k, v in data.get("emotions", {}).items()}
        return cls(
            emotions=emotions,
            baseline_mood=data.get("baseline_mood", 0.5),
            volatility=data.get("volatility", 0.3),
            regulation_capacity=data.get("regulation_capacity", 0.6),
            stress_level=data.get("stress_level", 0.2),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat())),
        )

@dataclass
class PersonalityProfile:
    traits: Dict[PersonalityTrait, float] = field(default_factory=lambda: {
        PersonalityTrait.STRICTNESS: 0.5,
        PersonalityTrait.WARMTH: 0.6,
        PersonalityTrait.PATIENCE: 0.5,
        PersonalityTrait.FLEXIBILITY: 0.5,
        PersonalityTrait.EXPRESSIVENESS: 0.5,
        PersonalityTrait.OPENNESS: 0.5,
        PersonalityTrait.CONSCIENTIOUSNESS: 0.5,
        PersonalityTrait.EXTRAVERSION: 0.5,
        PersonalityTrait.AGREEABLENESS: 0.5,
        PersonalityTrait.NEUROTICISM: 0.3,
    })
    conflict_style: ConflictStyle = ConflictStyle.COLLABORATIVE
    communication_style: str = "balanced"
    adaptability: float = 0.3

    def get_trait(self, trait: PersonalityTrait) -> float:
        return self.traits.get(trait, 0.5)

    def set_trait(self, trait: PersonalityTrait, value: float) -> None:
        self.traits[trait] = max(0.0, min(1.0, value))

    def adjust_trait(self, trait: PersonalityTrait, delta: float) -> None:
        max_change = self.adaptability * abs(delta)
        actual_change = max(-max_change, min(max_change, delta))
        current = self.get_trait(trait)
        self.set_trait(trait, current + actual_change)

    @classmethod
    def create_warm_patient(cls) -> 'PersonalityProfile':
        profile = cls()
        profile.set_trait(PersonalityTrait.WARMTH, 0.8)
        profile.set_trait(PersonalityTrait.PATIENCE, 0.8)
        profile.set_trait(PersonalityTrait.STRICTNESS, 0.3)
        profile.set_trait(PersonalityTrait.EXPRESSIVENESS, 0.7)
        profile.conflict_style = ConflictStyle.ACCOMMODATING
        return profile

    @classmethod
    def create_strict_structured(cls) -> 'PersonalityProfile':
        profile = cls()
        profile.set_trait(PersonalityTrait.STRICTNESS, 0.8)
        profile.set_trait(PersonalityTrait.WARMTH, 0.4)
        profile.set_trait(PersonalityTrait.PATIENCE, 0.5)
        profile.set_trait(PersonalityTrait.CONSCIENTIOUSNESS, 0.8)
        profile.conflict_style = ConflictStyle.COMPETITIVE
        return profile

    @classmethod
    def create_balanced(cls) -> 'PersonalityProfile':
        return cls()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "traits": {t.value: v for t, v in self.traits.items()},
            "conflict_style": self.conflict_style.value,
            "communication_style": self.communication_style,
            "adaptability": self.adaptability,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonalityProfile':
        traits = {PersonalityTrait(k): v for k, v in data.get("traits", {}).items()}
        return cls(
            traits=traits,
            conflict_style=ConflictStyle(data.get("conflict_style", "collaborative")),
            communication_style=data.get("communication_style", "balanced"),
            adaptability=data.get("adaptability", 0.3),
        )

@dataclass
class ParentState:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: ParentRole = ParentRole.FATHER
    name: str = "Parent"
    is_player: bool = True
    emotional_state: EmotionalState = field(default_factory=EmotionalState)
    personality: PersonalityProfile = field(default_factory=PersonalityProfile)
    interaction_count: int = 0
    relationship_quality: float = 0.7
    behavioral_patterns: Dict[str, float] = field(default_factory=dict)
    current_strategy: Optional[ResponseStrategy] = None
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create_player(cls, role: ParentRole, name: str) -> 'ParentState':
        return cls(
            role=role,
            name=name,
            is_player=True,
            personality=PersonalityProfile(),
        )

    @classmethod
    def create_ai(cls, role: ParentRole, name: str,
                  personality: Optional[PersonalityProfile] = None) -> 'ParentState':
        return cls(
            role=role,
            name=name,
            is_player=False,
            personality=personality or PersonalityProfile.create_balanced(),
            current_strategy=ResponseStrategy.SUPPORTIVE,
        )

    def update_behavioral_pattern(self, pattern: str, value: float) -> None:
        alpha = 0.3
        current = self.behavioral_patterns.get(pattern, 0.5)
        self.behavioral_patterns[pattern] = current * (1 - alpha) + value * alpha

    def get_stress_modifier(self) -> float:
        stress = self.emotional_state.stress_level
        return 0.1 - (stress * 0.4)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "role": self.role.value,
            "name": self.name,
            "is_player": self.is_player,
            "emotional_state": self.emotional_state.to_dict(),
            "personality": self.personality.to_dict(),
            "interaction_count": self.interaction_count,
            "relationship_quality": self.relationship_quality,
            "behavioral_patterns": self.behavioral_patterns,
            "current_strategy": self.current_strategy.value if self.current_strategy else None,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParentState':
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            role=ParentRole(data["role"]),
            name=data["name"],
            is_player=data["is_player"],
            emotional_state=EmotionalState.from_dict(data.get("emotional_state", {})),
            personality=PersonalityProfile.from_dict(data.get("personality", {})),
            interaction_count=data.get("interaction_count", 0),
            relationship_quality=data.get("relationship_quality", 0.7),
            behavioral_patterns=data.get("behavioral_patterns", {}),
            current_strategy=ResponseStrategy(data["current_strategy"]) if data.get("current_strategy") else None,
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
        )

@dataclass
class InteractionRecord:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    interaction_type: InteractionType = InteractionType.CASUAL_CONVERSATION
    initiator_id: str = ""
    responder_id: str = ""
    initiator_message: str = ""
    responder_message: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    emotional_impact: Dict[str, float] = field(default_factory=dict)
    relationship_impact: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "interaction_type": self.interaction_type.value,
            "initiator_id": self.initiator_id,
            "responder_id": self.responder_id,
            "initiator_message": self.initiator_message,
            "responder_message": self.responder_message,
            "context": self.context,
            "emotional_impact": self.emotional_impact,
            "relationship_impact": self.relationship_impact,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InteractionRecord':
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            interaction_type=InteractionType(data.get("interaction_type", "casual_conversation")),
            initiator_id=data.get("initiator_id", ""),
            responder_id=data.get("responder_id", ""),
            initiator_message=data.get("initiator_message", ""),
            responder_message=data.get("responder_message", ""),
            context=data.get("context", {}),
            emotional_impact=data.get("emotional_impact", {}),
            relationship_impact=data.get("relationship_impact", 0.0),
        )

@dataclass
class DialogueContext:
    scenario_name: str = ""
    scenario_description: str = ""
    recent_history: List[Dict[str, str]] = field(default_factory=list)
    current_topic: str = ""
    tension_level: float = 0.0
    player_message: str = ""
    player_state: Dict[str, Any] = field(default_factory=dict)
    ai_state: Dict[str, Any] = field(default_factory=dict)
    special_flags: Dict[str, bool] = field(default_factory=dict)
    extra_context: Dict[str, Any] = field(default_factory=dict)

    def add_exchange(self, speaker: str, message: str) -> None:
        self.recent_history.append({"speaker": speaker, "message": message})
        if len(self.recent_history) > 10:
            self.recent_history = self.recent_history[-10:]

    def get_formatted_history(self) -> str:
        return "\n".join(
            f"{ex['speaker']}: {ex['message']}"
            for ex in self.recent_history
        )

@dataclass
class PlayerAction:
    action_type: ActionType
    context: ContextType
    emotional_valence: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_type": self.action_type.value,
            "context": self.context.value,
            "emotional_valence": self.emotional_valence,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerAction':
        return cls(
            action_type=ActionType(data["action_type"]),
            context=ContextType(data["context"]),
            emotional_valence=data["emotional_valence"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )

@dataclass
class BehaviorPattern:
    pattern_type: PatternType
    occurrences: List[PlayerAction] = field(default_factory=list)
    frequency: float = 0.0
    weight: float = 1.0
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_type": self.pattern_type.value,
            "occurrences": [a.to_dict() for a in self.occurrences],
            "frequency": self.frequency,
            "weight": self.weight,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BehaviorPattern':
        return cls(
            pattern_type=PatternType(data["pattern_type"]),
            occurrences=[PlayerAction.from_dict(a) for a in data.get("occurrences", [])],
            frequency=data.get("frequency", 0.0),
            weight=data.get("weight", 1.0),
            first_seen=datetime.fromisoformat(data["first_seen"]),
            last_seen=datetime.fromisoformat(data["last_seen"]),
        )

@dataclass
class EmotionalImpact:
    primary_emotion: EmotionType
    intensity: float
    valence: float
    context_category: ContextCategory

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_emotion": self.primary_emotion.value,
            "intensity": self.intensity,
            "valence": self.valence,
            "context_category": self.context_category.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionalImpact':
        return cls(
            primary_emotion=EmotionType(data["primary_emotion"]),
            intensity=data["intensity"],
            valence=data["valence"],
            context_category=ContextCategory(data["context_category"]),
        )

@dataclass
class EmotionalMemory:
    emotional_impact: EmotionalImpact
    timestamp: datetime = field(default_factory=datetime.now)
    context: ContextType = ContextType.PRIVATE
    weight: float = 1.0
    associated_patterns: List[PatternType] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "emotional_impact": self.emotional_impact.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "context": self.context.value,
            "weight": self.weight,
            "associated_patterns": [p.value for p in self.associated_patterns],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionalMemory':
        return cls(
            emotional_impact=EmotionalImpact.from_dict(data["emotional_impact"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            context=ContextType(data["context"]),
            weight=data.get("weight", 1.0),
            associated_patterns=[PatternType(p) for p in data.get("associated_patterns", [])],
        )

@dataclass
class ResponseModifiers:
    response_length_multiplier: float = 1.0
    initiation_probability: float = 1.0
    cooperation_level: float = 1.0
    emotional_vulnerability: float = 1.0
    interpretation_bias: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "response_length_multiplier": self.response_length_multiplier,
            "initiation_probability": self.initiation_probability,
            "cooperation_level": self.cooperation_level,
            "emotional_vulnerability": self.emotional_vulnerability,
            "interpretation_bias": self.interpretation_bias,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResponseModifiers':
        return cls(
            response_length_multiplier=data.get("response_length_multiplier", 1.0),
            initiation_probability=data.get("initiation_probability", 1.0),
            cooperation_level=data.get("cooperation_level", 1.0),
            emotional_vulnerability=data.get("emotional_vulnerability", 1.0),
            interpretation_bias=data.get("interpretation_bias", 0.0),
        )

@dataclass
class RelationshipMetrics:
    trust_score: float = 70.0
    resentment_score: float = 0.0
    emotional_safety: float = 70.0
    parenting_unity: float = 80.0
    player_reliability: float = 0.7
    cooperation_level: float = 1.0
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trust_score": self.trust_score,
            "resentment_score": self.resentment_score,
            "emotional_safety": self.emotional_safety,
            "parenting_unity": self.parenting_unity,
            "player_reliability": self.player_reliability,
            "cooperation_level": self.cooperation_level,
            "last_updated": self.last_updated.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelationshipMetrics':
        return cls(
            trust_score=data.get("trust_score", 70.0),
            resentment_score=data.get("resentment_score", 0.0),
            emotional_safety=data.get("emotional_safety", 70.0),
            parenting_unity=data.get("parenting_unity", 80.0),
            player_reliability=data.get("player_reliability", 0.7),
            cooperation_level=data.get("cooperation_level", 1.0),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat())),
        )
