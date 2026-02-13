from enum import Enum, IntEnum, auto
from typing import List

class ParentRole(Enum):
    FATHER = "father"
    MOTHER = "mother"

    def get_opposite(self) -> 'ParentRole':
        return ParentRole.MOTHER if self == ParentRole.FATHER else ParentRole.FATHER

    def get_display_name(self) -> str:
        return self.value.capitalize()

class EmotionType(Enum):
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"

    TRUST = "trust"
    LOVE = "love"
    GUILT = "guilt"
    SHAME = "shame"
    PRIDE = "pride"

    ANXIETY = "anxiety"
    FRUSTRATION = "frustration"
    CONTENTMENT = "contentment"
    RESENTMENT = "resentment"
    CALM = "calm"
    STRESS = "stress"

    @classmethod
    def get_positive_emotions(cls) -> List['EmotionType']:
        return [cls.JOY, cls.TRUST, cls.LOVE, cls.PRIDE, cls.CONTENTMENT, cls.CALM]

    @classmethod
    def get_negative_emotions(cls) -> List['EmotionType']:
        return [cls.SADNESS, cls.ANGER, cls.FEAR, cls.GUILT, cls.SHAME,
                cls.ANXIETY, cls.FRUSTRATION, cls.RESENTMENT, cls.STRESS]

class PersonalityTrait(Enum):
    STRICTNESS = "strictness"
    WARMTH = "warmth"
    PATIENCE = "patience"
    FLEXIBILITY = "flexibility"
    EXPRESSIVENESS = "expressiveness"

    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"

class InteractionType(Enum):
    CASUAL_CONVERSATION = "casual_conversation"
    SERIOUS_DISCUSSION = "serious_discussion"
    ARGUMENT = "argument"
    RECONCILIATION = "reconciliation"
    PLANNING = "planning"
    SUPPORT = "support"
    CRITICISM = "criticism"
    PRAISE = "praise"

    SHARED_ACTIVITY = "shared_activity"
    INDEPENDENT_DECISION = "independent_decision"
    COLLABORATIVE_DECISION = "collaborative_decision"
    CONFLICT_RESOLUTION = "conflict_resolution"

class ResponseStrategy(Enum):
    SUPPORTIVE = "supportive"
    CHALLENGING = "challenging"
    COMPROMISING = "compromising"
    AVOIDANT = "avoidant"
    ASSERTIVE = "assertive"
    EMPATHETIC = "empathetic"
    PRACTICAL = "practical"
    EMOTIONAL = "emotional"

class ConflictStyle(Enum):
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"
    AVOIDANT = "avoidant"
    ACCOMMODATING = "accommodating"
    COMPROMISING = "compromising"

class EventSeverity(IntEnum):
    TRIVIAL = 1
    MINOR = 2
    MODERATE = 3
    SIGNIFICANT = 4
    MAJOR = 5

class MemoryType(Enum):
    INTERACTION = "interaction"
    EMOTIONAL = "emotional"
    DECISION = "decision"
    CONFLICT = "conflict"
    POSITIVE = "positive"
    PATTERN = "pattern"

class ActionType(Enum):
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
    PUBLIC = "public"
    PRIVATE = "private"

class ContextCategory(Enum):
    SUPPORT = "support"
    CONFLICT = "conflict"
    PARENTING = "parenting"
    INTIMACY = "intimacy"

class PatternType(Enum):
    CONSISTENT_PRESENCE = "consistent_presence"
    SPORADIC_INVOLVEMENT = "sporadic_involvement"
    REPEATED_AVOIDANCE = "repeated_avoidance"
    CONTROL_TAKING = "control_taking"
    EMPATHETIC_SUPPORT = "empathetic_support"
    PUBLIC_UNITY = "public_unity"
    PUBLIC_UNDERMINING = "public_undermining"

class WithdrawalLevel(IntEnum):
    NONE = 0
    MILD = 1
    MODERATE = 2
    SEVERE = 3
