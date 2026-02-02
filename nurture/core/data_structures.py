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
    ResponseStrategy, ConflictStyle, MemoryType
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
