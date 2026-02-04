"""
Core Data Structures for Nurture Simulation
============================================

This module defines the fundamental data structures for parent agents:
- State containers for emotions and personality
- Parent state tracking
- Interaction records

All structures use Python dataclasses for clean design with built-in
serialization support.

Design Principles:
1. Clear separation between mutable state and configuration
2. Rich documentation for all fields
3. Default factories for sensible initialization
4. Methods for common state operations
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import uuid

from nurture.core.enums import (
    EmotionType, PersonalityTrait, ParentRole, InteractionType,
    ResponseStrategy, ConflictStyle, MemoryType, ActionType,
    ContextType, ContextCategory, PatternType, WithdrawalLevel
)


# =============================================================================
# EMOTIONAL STATE
# =============================================================================

@dataclass
class EmotionalState:
    """
    Represents the current emotional state of a parent agent.
    
    Emotions are modeled as a vector of intensities (0.0 to 1.0) for each
    emotion type. The emotional state influences decision-making, dialogue
    generation, and relationship dynamics.
    
    Attributes:
        emotions: Dict mapping emotion types to intensity values (0.0-1.0)
        baseline_mood: Default emotional state when no events are active (-1 to 1)
        volatility: How quickly emotions change (0.0=stable, 1.0=volatile)
        regulation_capacity: Ability to manage emotions (0.0-1.0)
        stress_level: Current accumulated stress (0.0-1.0)
        last_updated: Timestamp of last state change
        
    Example:
        state = EmotionalState()
        state.update_emotion(EmotionType.JOY, 0.8)
        print(state.get_dominant_emotion())  # (EmotionType.JOY, 0.8)
    """
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
    baseline_mood: float = 0.5  # -1.0 (negative) to 1.0 (positive)
    volatility: float = 0.3     # How reactive to events
    regulation_capacity: float = 0.6  # Emotional self-control
    stress_level: float = 0.2
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_emotion(self, emotion: EmotionType, value: float) -> None:
        """
        Update a specific emotion value, clamped to [0, 1].
        
        Args:
            emotion: The emotion to update
            value: New value (will be clamped to 0.0-1.0)
        """
        self.emotions[emotion] = max(0.0, min(1.0, value))
        self.last_updated = datetime.now()
    
    def adjust_emotion(self, emotion: EmotionType, delta: float) -> None:
        """
        Adjust an emotion by a delta value.
        
        Args:
            emotion: The emotion to adjust
            delta: Change amount (positive or negative)
        """
        current = self.emotions.get(emotion, 0.0)
        self.update_emotion(emotion, current + delta)
    
    def get_dominant_emotion(self) -> Tuple[EmotionType, float]:
        """
        Get the emotion with highest intensity.
        
        Returns:
            Tuple of (EmotionType, intensity)
        """
        if not self.emotions:
            return (EmotionType.CALM, 0.5)
        return max(self.emotions.items(), key=lambda x: x[1])
    
    def get_valence(self) -> float:
        """
        Calculate overall emotional valence.
        
        Returns:
            Float from -1.0 (very negative) to 1.0 (very positive)
        """
        positive = EmotionType.get_positive_emotions()
        negative = EmotionType.get_negative_emotions()
        
        pos_sum = sum(self.emotions.get(e, 0) for e in positive)
        neg_sum = sum(self.emotions.get(e, 0) for e in negative)
        
        total = pos_sum + neg_sum
        if total == 0:
            return 0.0
        return (pos_sum - neg_sum) / max(len(positive), len(negative))
    
    def apply_decay(self, decay_rate: float = 0.1) -> None:
        """
        Apply emotional decay toward baseline.
        
        Over time, emotions naturally regress toward neutral states.
        Decay is influenced by regulation capacity.
        
        Args:
            decay_rate: Base rate of decay (0.0-1.0)
        """
        effective_decay = decay_rate * self.regulation_capacity
        
        for emotion in list(self.emotions.keys()):
            current = self.emotions[emotion]
            # Baseline is 0.5 for most emotions, lower for negative ones
            baseline = 0.1 if emotion in EmotionType.get_negative_emotions() else 0.4
            diff = current - baseline
            new_value = current - (diff * effective_decay)
            self.emotions[emotion] = max(0.0, min(1.0, new_value))
        
        # Decay stress separately
        self.stress_level = max(0.0, self.stress_level - (self.stress_level * effective_decay * 0.5))
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize emotional state to dictionary."""
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
        """Deserialize emotional state from dictionary."""
        emotions = {EmotionType(k): v for k, v in data.get("emotions", {}).items()}
        return cls(
            emotions=emotions,
            baseline_mood=data.get("baseline_mood", 0.5),
            volatility=data.get("volatility", 0.3),
            regulation_capacity=data.get("regulation_capacity", 0.6),
            stress_level=data.get("stress_level", 0.2),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat())),
        )


# =============================================================================
# PERSONALITY PROFILE
# =============================================================================

@dataclass
class PersonalityProfile:
    """
    Defines stable personality traits for a parent agent.
    
    Personality influences how agents interpret events, make decisions,
    and respond to situations. Traits are relatively stable but can
    shift slightly over extended periods.
    
    Attributes:
        traits: Dict mapping trait types to values (0.0-1.0)
        conflict_style: Default conflict handling pattern
        communication_style: Preferred way of communicating
        adaptability: How much personality can shift (0.0-1.0)
        
    Example:
        profile = PersonalityProfile.create_warm_patient()
        print(profile.get_trait(PersonalityTrait.WARMTH))  # 0.8
    """
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
        """Get value for a specific trait."""
        return self.traits.get(trait, 0.5)
    
    def set_trait(self, trait: PersonalityTrait, value: float) -> None:
        """Set a trait value, clamped to [0, 1]."""
        self.traits[trait] = max(0.0, min(1.0, value))
    
    def adjust_trait(self, trait: PersonalityTrait, delta: float) -> None:
        """
        Adjust a trait by delta, respecting adaptability.
        
        Larger adaptability allows larger changes.
        """
        max_change = self.adaptability * abs(delta)
        actual_change = max(-max_change, min(max_change, delta))
        current = self.get_trait(trait)
        self.set_trait(trait, current + actual_change)
    
    @classmethod
    def create_warm_patient(cls) -> 'PersonalityProfile':
        """Create a warm and patient personality profile."""
        profile = cls()
        profile.set_trait(PersonalityTrait.WARMTH, 0.8)
        profile.set_trait(PersonalityTrait.PATIENCE, 0.8)
        profile.set_trait(PersonalityTrait.STRICTNESS, 0.3)
        profile.set_trait(PersonalityTrait.EXPRESSIVENESS, 0.7)
        profile.conflict_style = ConflictStyle.ACCOMMODATING
        return profile
    
    @classmethod
    def create_strict_structured(cls) -> 'PersonalityProfile':
        """Create a strict and structured personality profile."""
        profile = cls()
        profile.set_trait(PersonalityTrait.STRICTNESS, 0.8)
        profile.set_trait(PersonalityTrait.WARMTH, 0.4)
        profile.set_trait(PersonalityTrait.PATIENCE, 0.5)
        profile.set_trait(PersonalityTrait.CONSCIENTIOUSNESS, 0.8)
        profile.conflict_style = ConflictStyle.COMPETITIVE
        return profile
    
    @classmethod
    def create_balanced(cls) -> 'PersonalityProfile':
        """Create a balanced personality profile."""
        return cls()  # Uses defaults
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize personality profile to dictionary."""
        return {
            "traits": {t.value: v for t, v in self.traits.items()},
            "conflict_style": self.conflict_style.value,
            "communication_style": self.communication_style,
            "adaptability": self.adaptability,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonalityProfile':
        """Deserialize personality profile from dictionary."""
        traits = {PersonalityTrait(k): v for k, v in data.get("traits", {}).items()}
        return cls(
            traits=traits,
            conflict_style=ConflictStyle(data.get("conflict_style", "collaborative")),
            communication_style=data.get("communication_style", "balanced"),
            adaptability=data.get("adaptability", 0.3),
        )


# =============================================================================
# PARENT STATE
# =============================================================================

@dataclass
class ParentState:
    """
    Complete state container for a parent agent.
    
    Combines identity, emotional state, personality, and behavioral tracking
    into a single unified state object.
    
    Attributes:
        id: Unique identifier for this parent
        role: Father or Mother
        name: Display name
        is_player: True if human-controlled, False if AI
        emotional_state: Current emotional state
        personality: Personality profile
        interaction_count: Total interactions
        relationship_quality: Quality of relationship with partner (0-1)
        behavioral_patterns: Tracked behavioral tendencies
        current_strategy: Current response strategy (AI only)
        
    Example:
        state = ParentState.create_player(ParentRole.FATHER, "John")
        state.emotional_state.adjust_emotion(EmotionType.STRESS, 0.2)
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: ParentRole = ParentRole.FATHER
    name: str = "Parent"
    is_player: bool = True
    emotional_state: EmotionalState = field(default_factory=EmotionalState)
    personality: PersonalityProfile = field(default_factory=PersonalityProfile)
    interaction_count: int = 0
    relationship_quality: float = 0.7  # With partner
    behavioral_patterns: Dict[str, float] = field(default_factory=dict)
    current_strategy: Optional[ResponseStrategy] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create_player(cls, role: ParentRole, name: str) -> 'ParentState':
        """
        Create a new player parent state.
        
        Args:
            role: Father or Mother
            name: Display name for the player
            
        Returns:
            New ParentState configured for player control
        """
        return cls(
            role=role,
            name=name,
            is_player=True,
            personality=PersonalityProfile(),  # Will be inferred from choices
        )
    
    @classmethod
    def create_ai(cls, role: ParentRole, name: str, 
                  personality: Optional[PersonalityProfile] = None) -> 'ParentState':
        """
        Create a new AI parent state.
        
        Args:
            role: Father or Mother
            name: Display name for the AI parent
            personality: Optional personality profile (defaults to balanced)
            
        Returns:
            New ParentState configured for AI control
        """
        return cls(
            role=role,
            name=name,
            is_player=False,
            personality=personality or PersonalityProfile.create_balanced(),
            current_strategy=ResponseStrategy.SUPPORTIVE,
        )
    
    def update_behavioral_pattern(self, pattern: str, value: float) -> None:
        """
        Update a behavioral pattern observation.
        
        Uses exponential moving average to smooth pattern tracking.
        """
        alpha = 0.3  # Learning rate
        current = self.behavioral_patterns.get(pattern, 0.5)
        self.behavioral_patterns[pattern] = current * (1 - alpha) + value * alpha
    
    def get_stress_modifier(self) -> float:
        """
        Get modifier based on current stress level.
        
        High stress reduces patience and increases negative reactions.
        
        Returns:
            Modifier from -0.3 (high stress) to 0.1 (low stress)
        """
        stress = self.emotional_state.stress_level
        return 0.1 - (stress * 0.4)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize parent state to dictionary."""
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
        """Deserialize parent state from dictionary."""
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


# =============================================================================
# INTERACTION RECORD
# =============================================================================

@dataclass
class InteractionRecord:
    """
    Record of a single interaction between parents.
    
    Used for logging, memory formation, and pattern analysis.
    
    Attributes:
        id: Unique identifier
        timestamp: When the interaction occurred
        interaction_type: Category of interaction
        initiator_id: ID of parent who initiated
        responder_id: ID of parent who responded
        initiator_message: What the initiator said/did
        responder_message: How the responder replied
        context: Additional context (scenario, day, etc.)
        emotional_impact: How this affected emotions
        relationship_impact: How this affected relationship
    """
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
        """Serialize interaction record to dictionary."""
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
        """Deserialize interaction record from dictionary."""
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


# =============================================================================
# DIALOGUE CONTEXT
# =============================================================================

@dataclass
class DialogueContext:
    """
    Context for dialogue generation.
    
    Provides all necessary information for generating contextually
    appropriate responses.
    
    Attributes:
        scenario_name: Current scenario/day name
        scenario_description: Description of current situation
        recent_history: Recent dialogue exchanges
        current_topic: Main topic of discussion
        tension_level: Current conflict/tension level (0-1)
        player_message: Latest message from player
        player_state: Current player emotional state summary
        ai_state: Current AI emotional state summary
        special_flags: Any special conditions active
    """
    scenario_name: str = ""
    scenario_description: str = ""
    recent_history: List[Dict[str, str]] = field(default_factory=list)
    current_topic: str = ""
    tension_level: float = 0.0
    player_message: str = ""
    player_state: Dict[str, Any] = field(default_factory=dict)
    ai_state: Dict[str, Any] = field(default_factory=dict)
    special_flags: Dict[str, bool] = field(default_factory=dict)
    extra_context: Dict[str, Any] = field(default_factory=dict)  # Scenario context for AI
    
    def add_exchange(self, speaker: str, message: str) -> None:
        """Add a dialogue exchange to history, keeping last 10."""
        self.recent_history.append({"speaker": speaker, "message": message})
        if len(self.recent_history) > 10:
            self.recent_history = self.recent_history[-10:]
    
    def get_formatted_history(self) -> str:
        """Get dialogue history as formatted string."""
        return "\n".join(
            f"{ex['speaker']}: {ex['message']}" 
            for ex in self.recent_history
        )


# =============================================================================
# MOTHER AI PERSONALITY SYSTEM DATA STRUCTURES
# =============================================================================

@dataclass
class PlayerAction:
    """
    Represents a single player action for pattern tracking.
    
    Actions are recorded with timestamps and context to enable
    pattern detection and trust dynamics calculations.
    
    Attributes:
        action_type: Type of action performed
        context: Whether action occurred in public or private
        emotional_valence: Emotional impact (-1.0 to 1.0)
        timestamp: When the action occurred
        metadata: Additional context-specific data
    """
    action_type: ActionType
    context: ContextType
    emotional_valence: float  # -1.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize player action to dictionary."""
        return {
            "action_type": self.action_type.value,
            "context": self.context.value,
            "emotional_valence": self.emotional_valence,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerAction':
        """Deserialize player action from dictionary."""
        return cls(
            action_type=ActionType(data["action_type"]),
            context=ContextType(data["context"]),
            emotional_valence=data["emotional_valence"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


@dataclass
class BehaviorPattern:
    """
    Represents a detected behavioral pattern.
    
    Patterns are sequences of similar actions that occur repeatedly
    within a time window. They have more impact than isolated actions.
    
    Attributes:
        pattern_type: Type of pattern detected
        occurrences: List of actions that form this pattern
        frequency: How often pattern occurs (actions per day)
        weight: Current weight of pattern (decreases as broken)
        first_seen: When pattern was first detected
        last_seen: When pattern last occurred
    """
    pattern_type: PatternType
    occurrences: List[PlayerAction] = field(default_factory=list)
    frequency: float = 0.0
    weight: float = 1.0  # Decreases as pattern is broken
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize behavior pattern to dictionary."""
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
        """Deserialize behavior pattern from dictionary."""
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
    """
    Represents the emotional impact of an interaction.
    
    Stores how an interaction made the Mother AI feel, not what was said.
    
    Attributes:
        primary_emotion: The dominant emotion felt
        intensity: How strongly the emotion was felt (0.0 to 1.0)
        valence: Overall positive/negative feeling (-1.0 to 1.0)
        context_category: Broader category of the interaction
    """
    primary_emotion: EmotionType
    intensity: float  # 0.0 to 1.0
    valence: float  # -1.0 (negative) to 1.0 (positive)
    context_category: ContextCategory
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize emotional impact to dictionary."""
        return {
            "primary_emotion": self.primary_emotion.value,
            "intensity": self.intensity,
            "valence": self.valence,
            "context_category": self.context_category.value,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionalImpact':
        """Deserialize emotional impact from dictionary."""
        return cls(
            primary_emotion=EmotionType(data["primary_emotion"]),
            intensity=data["intensity"],
            valence=data["valence"],
            context_category=ContextCategory(data["context_category"]),
        )


@dataclass
class EmotionalMemory:
    """
    A memory of how an interaction felt.
    
    Emotional memories store the feeling rather than verbatim content,
    and are weighted by recency for recall.
    
    Attributes:
        emotional_impact: How the interaction felt
        timestamp: When the interaction occurred
        context: Public or private context
        weight: Current weight (decreases with time)
        associated_patterns: Patterns active during this memory
    """
    emotional_impact: EmotionalImpact
    timestamp: datetime = field(default_factory=datetime.now)
    context: ContextType = ContextType.PRIVATE
    weight: float = 1.0  # Decreases with time
    associated_patterns: List[PatternType] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize emotional memory to dictionary."""
        return {
            "emotional_impact": self.emotional_impact.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "context": self.context.value,
            "weight": self.weight,
            "associated_patterns": [p.value for p in self.associated_patterns],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionalMemory':
        """Deserialize emotional memory from dictionary."""
        return cls(
            emotional_impact=EmotionalImpact.from_dict(data["emotional_impact"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            context=ContextType(data["context"]),
            weight=data.get("weight", 1.0),
            associated_patterns=[PatternType(p) for p in data.get("associated_patterns", [])],
        )


@dataclass
class ResponseModifiers:
    """
    Modifiers for response generation based on personality state.
    
    These values adjust how the Mother AI responds based on current
    trust, resentment, and emotional state.
    
    Attributes:
        response_length_multiplier: Multiplier for response length (0.3 to 1.0)
        initiation_probability: Probability of initiating interaction (0.0 to 1.0)
        cooperation_level: Willingness to cooperate (0.0 to 1.0)
        emotional_vulnerability: Willingness to be emotionally open (0.0 to 1.0)
        interpretation_bias: How to interpret ambiguous actions (-1.0 to 1.0)
    """
    response_length_multiplier: float = 1.0  # 0.3 to 1.0
    initiation_probability: float = 1.0  # 0.0 to 1.0
    cooperation_level: float = 1.0  # 0.0 to 1.0
    emotional_vulnerability: float = 1.0  # 0.0 to 1.0
    interpretation_bias: float = 0.0  # -1.0 (negative) to 1.0 (positive)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize response modifiers to dictionary."""
        return {
            "response_length_multiplier": self.response_length_multiplier,
            "initiation_probability": self.initiation_probability,
            "cooperation_level": self.cooperation_level,
            "emotional_vulnerability": self.emotional_vulnerability,
            "interpretation_bias": self.interpretation_bias,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResponseModifiers':
        """Deserialize response modifiers from dictionary."""
        return cls(
            response_length_multiplier=data.get("response_length_multiplier", 1.0),
            initiation_probability=data.get("initiation_probability", 1.0),
            cooperation_level=data.get("cooperation_level", 1.0),
            emotional_vulnerability=data.get("emotional_vulnerability", 1.0),
            interpretation_bias=data.get("interpretation_bias", 0.0),
        )


@dataclass
class RelationshipMetrics:
    """
    Comprehensive snapshot of relationship state.
    
    Tracks all key metrics that define the current state of the
    relationship between player and Mother AI.
    
    Attributes:
        trust_score: Trust level (0.0 to 100.0)
        resentment_score: Accumulated resentment (0.0 to 100.0)
        emotional_safety: Perceived emotional safety (0.0 to 100.0)
        parenting_unity: Alignment in parenting (0.0 to 100.0)
        player_reliability: How reliable player is perceived (0.0 to 1.0)
        cooperation_level: Current cooperation level (0.0 to 1.0)
        last_updated: When metrics were last updated
    """
    trust_score: float = 70.0  # 0.0 to 100.0
    resentment_score: float = 0.0  # 0.0 to 100.0
    emotional_safety: float = 70.0  # 0.0 to 100.0
    parenting_unity: float = 80.0  # 0.0 to 100.0
    player_reliability: float = 0.7  # 0.0 to 1.0
    cooperation_level: float = 1.0  # 0.0 to 1.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize relationship metrics to dictionary."""
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
        """Deserialize relationship metrics from dictionary."""
        return cls(
            trust_score=data.get("trust_score", 70.0),
            resentment_score=data.get("resentment_score", 0.0),
            emotional_safety=data.get("emotional_safety", 70.0),
            parenting_unity=data.get("parenting_unity", 80.0),
            player_reliability=data.get("player_reliability", 0.7),
            cooperation_level=data.get("cooperation_level", 1.0),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat())),
        )
