"""
Enumerations for the Nurture Simulation System
===============================================

This module defines all enumeration types used throughout the simulation,
providing type-safe constants for roles, emotions, traits, and interaction types.

Design Philosophy:
- Each enum represents a distinct conceptual domain
- Values support both categorical and ordinal usage patterns
- Clear naming for readability and maintainability
"""

from enum import Enum, IntEnum, auto
from typing import List


class ParentRole(Enum):
    """
    Parent role in the family simulation.
    
    The player selects one role, and the AI automatically takes the other.
    Role affects dialogue style, societal expectations, and some scenarios.
    """
    FATHER = "father"
    MOTHER = "mother"
    
    def get_opposite(self) -> 'ParentRole':
        """Get the opposite parent role."""
        return ParentRole.MOTHER if self == ParentRole.FATHER else ParentRole.FATHER
    
    def get_display_name(self) -> str:
        """Get human-readable name for the role."""
        return self.value.capitalize()


class EmotionType(Enum):
    """
    Primary emotional states that parent agents can experience.
    
    These emotions form the basis of the emotional state model and
    influence decision-making, memory formation, and dialogue tone.
    
    Categories:
    - Basic: Primary emotions (joy, sadness, anger, fear)
    - Social: Relationship emotions (trust, love, guilt)
    - Complex: Derived emotions (frustration, contentment)
    """
    # Basic emotions
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    
    # Social emotions
    TRUST = "trust"
    LOVE = "love"
    GUILT = "guilt"
    SHAME = "shame"
    PRIDE = "pride"
    
    # Complex emotions
    ANXIETY = "anxiety"
    FRUSTRATION = "frustration"
    CONTENTMENT = "contentment"
    RESENTMENT = "resentment"
    CALM = "calm"
    STRESS = "stress"
    
    @classmethod
    def get_positive_emotions(cls) -> List['EmotionType']:
        """Return list of positive emotions."""
        return [cls.JOY, cls.TRUST, cls.LOVE, cls.PRIDE, cls.CONTENTMENT, cls.CALM]
    
    @classmethod
    def get_negative_emotions(cls) -> List['EmotionType']:
        """Return list of negative emotions."""
        return [cls.SADNESS, cls.ANGER, cls.FEAR, cls.GUILT, cls.SHAME, 
                cls.ANXIETY, cls.FRUSTRATION, cls.RESENTMENT, cls.STRESS]


class PersonalityTrait(Enum):
    """
    Personality traits for parent agents.
    
    AI Parent has stable trait values that influence behavior.
    Player Parent's traits are inferred from their choices.
    
    Trait dimensions are designed for parenting contexts:
    - Strictness: How rule-focused vs permissive
    - Warmth: Emotional expressiveness and affection
    - Patience: Tolerance for stress and delay
    - Flexibility: Adaptability to change
    - Expressiveness: Communication openness
    """
    # Core parenting traits
    STRICTNESS = "strictness"
    WARMTH = "warmth"
    PATIENCE = "patience"
    FLEXIBILITY = "flexibility"
    EXPRESSIVENESS = "expressiveness"
    
    # Big Five personality traits (for deeper modeling)
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"


class InteractionType(Enum):
    """
    Types of interactions between parents.
    
    Each interaction type has different effects on emotional states
    and relationship dynamics.
    """
    # Dialogue types
    CASUAL_CONVERSATION = "casual_conversation"
    SERIOUS_DISCUSSION = "serious_discussion"
    ARGUMENT = "argument"
    RECONCILIATION = "reconciliation"
    PLANNING = "planning"
    SUPPORT = "support"
    CRITICISM = "criticism"
    PRAISE = "praise"
    
    # Action types
    SHARED_ACTIVITY = "shared_activity"
    INDEPENDENT_DECISION = "independent_decision"
    COLLABORATIVE_DECISION = "collaborative_decision"
    CONFLICT_RESOLUTION = "conflict_resolution"


class ResponseStrategy(Enum):
    """
    AI Parent response strategies.
    
    The AI Parent selects a strategy based on its emotional state,
    personality, and the current context.
    """
    SUPPORTIVE = "supportive"          # Agree and validate
    CHALLENGING = "challenging"        # Disagree respectfully
    COMPROMISING = "compromising"      # Find middle ground
    AVOIDANT = "avoidant"              # Deflect or change subject
    ASSERTIVE = "assertive"            # State position firmly
    EMPATHETIC = "empathetic"          # Focus on feelings
    PRACTICAL = "practical"            # Focus on solutions
    EMOTIONAL = "emotional"            # Express feelings strongly


class ConflictStyle(Enum):
    """
    Patterns of handling interpersonal conflict.
    
    These styles emerge from interaction patterns and influence
    how disagreements are approached.
    """
    COLLABORATIVE = "collaborative"    # Seek win-win solutions
    COMPETITIVE = "competitive"        # Win at all costs
    AVOIDANT = "avoidant"              # Dodge confrontation
    ACCOMMODATING = "accommodating"    # Yield to keep peace
    COMPROMISING = "compromising"      # Meet in the middle


class EventSeverity(IntEnum):
    """
    Severity levels for events, affecting memory formation and emotional impact.
    
    Higher severity events create stronger memories and have
    greater influence on agent states.
    """
    TRIVIAL = 1          # Minor, easily forgotten
    MINOR = 2            # Noticeable but not significant
    MODERATE = 3         # Meaningful, forms memories
    SIGNIFICANT = 4      # Important, lasting impact
    MAJOR = 5            # Life-altering, permanent memories


class MemoryType(Enum):
    """
    Types of memories stored by parent agents.
    
    Different memory types have different retention rates,
    retrieval patterns, and influence on decision-making.
    """
    INTERACTION = "interaction"        # Conversations and exchanges
    EMOTIONAL = "emotional"            # Strong emotional moments
    DECISION = "decision"              # Choices made
    CONFLICT = "conflict"              # Disagreements
    POSITIVE = "positive"              # Good experiences
    PATTERN = "pattern"                # Learned behavioral patterns


class ActionType(Enum):
    """
    Types of player actions tracked by the Mother AI personality system.
    
    These actions are monitored for pattern detection and influence
    trust dynamics, resentment accumulation, and relationship state.
    """
    SUPPORT = "support"
    CONFLICT_ENGAGE = "conflict_engage"
    CONFLICT_AVOID = "conflict_avoid"
    PARENTING_PRESENT = "parenting_present"
    PARENTING_ABSENT = "parenting_absent"
    CONTROL_TAKING = "control_taking"
    EMPATHY_SHOWN = "empathy_shown"
    EMPATHY_LACKING = "empathy_lacking"
    PUBLIC_SUPPORT = "public_support"
    PUBLIC_CONTRADICTION = "public_contradiction"
    APOLOGY = "apology"
    STRESS_ACKNOWLEDGE = "stress_acknowledge"
    STRESS_IGNORE = "stress_ignore"


class ContextType(Enum):
    """
    Context in which an interaction occurs.
    
    Public context (in front of child or others) has different
    impact than private context (between partners alone).
    """
    PUBLIC = "public"      # In front of child or others
    PRIVATE = "private"    # Between player and Mother AI alone


class ContextCategory(Enum):
    """
    Categorical grouping of interaction contexts for emotional memory.
    
    Used to associate emotional memories with broader themes.
    """
    SUPPORT = "support"
    CONFLICT = "conflict"
    PARENTING = "parenting"
    INTIMACY = "intimacy"


class PatternType(Enum):
    """
    Types of behavioral patterns detected over time.
    
    Patterns are identified when actions repeat within time windows
    and influence trust, resentment, and relationship dynamics.
    """
    CONSISTENT_PRESENCE = "consistent_presence"
    SPORADIC_INVOLVEMENT = "sporadic_involvement"
    REPEATED_AVOIDANCE = "repeated_avoidance"
    CONTROL_TAKING = "control_taking"
    EMPATHETIC_SUPPORT = "empathetic_support"
    PUBLIC_UNITY = "public_unity"
    PUBLIC_UNDERMINING = "public_undermining"


class WithdrawalLevel(IntEnum):
    """
    Severity levels of emotional withdrawal state.
    
    Higher withdrawal levels result in reduced engagement,
    shorter responses, and less emotional vulnerability.
    """
    NONE = 0       # Trust > 50
    MILD = 1       # Trust 40-50
    MODERATE = 2   # Trust 30-40
    SEVERE = 3     # Trust < 30
