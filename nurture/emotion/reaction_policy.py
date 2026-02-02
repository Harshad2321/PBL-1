"""
Reaction Policy Module
=======================

Maps emotional state + perception to reaction modes.
Includes emotion gates to prevent unrealistic responses.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import random

from nurture.emotion.emotion_state import EmotionState
from nurture.emotion.perception import PerceptionResult, Sentiment, Intent, TriggerType


class ReactionMode(Enum):
    """Possible reaction modes for the parent agent."""
    SUPPORTIVE = "supportive"       # Warm, understanding, helpful
    DEFENSIVE = "defensive"         # Protecting self, justifying
    CONFRONTATIONAL = "confrontational"  # Challenging, fighting back
    COLD = "cold"                   # Distant, minimal engagement
    WITHDRAWN = "withdrawn"         # Shutting down, not talking
    COOPERATIVE = "cooperative"     # Working together, problem-solving
    SARCASTIC = "sarcastic"         # Biting humor, passive-aggressive
    VULNERABLE = "vulnerable"       # Open about pain, emotional
    DISMISSIVE = "dismissive"       # Not taking seriously
    HURT = "hurt"                   # Expressing pain directly


@dataclass
class ReactionDecision:
    """Result of the reaction policy decision."""
    mode: ReactionMode
    intensity: float  # 0-1, how strong the reaction
    allowed_by_gate: bool  # Whether emotion gate approved this
    emotion_deltas: Dict[str, float]  # How this reaction affects emotions
    reasoning: str  # Why this mode was chosen
    
    def describe(self) -> str:
        """Human-readable description."""
        return f"{self.mode.value} (intensity: {self.intensity:.1f}) - {self.reasoning}"


class EmotionGate:
    """
    Prevents emotionally inconsistent responses.
    
    Rules:
    - Can't be supportive when furious
    - Can't be cheerful when deeply hurt
    - Can't fully trust after betrayal
    - Fatigue limits emotional range
    """
    
    # Blocked combinations: (condition, blocked_modes, reason)
    GATES = [
        # High anger blocks supportive/cooperative
        (lambda e: e.anger > 0.7, 
         [ReactionMode.SUPPORTIVE, ReactionMode.COOPERATIVE],
         "too angry to be supportive"),
        
        # Deep hurt blocks cheerful support
        (lambda e: e.hurt > 0.7,
         [ReactionMode.SUPPORTIVE],
         "too hurt to be warm"),
        
        # Low trust blocks vulnerability
        (lambda e: e.trust < 0.3,
         [ReactionMode.VULNERABLE],
         "trust too low to be vulnerable"),
        
        # Extreme fatigue limits confrontation
        (lambda e: e.fatigue > 0.8,
         [ReactionMode.CONFRONTATIONAL],
         "too exhausted to fight"),
        
        # Low empathy blocks cooperative mode
        (lambda e: e.empathy < 0.2,
         [ReactionMode.COOPERATIVE, ReactionMode.SUPPORTIVE],
         "empathy too low"),
    ]
    
    @classmethod
    def check(cls, emotion_state: EmotionState, mode: ReactionMode) -> Tuple[bool, str]:
        """
        Check if a reaction mode is allowed given emotional state.
        
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        for condition, blocked_modes, reason in cls.GATES:
            if condition(emotion_state) and mode in blocked_modes:
                return False, reason
        return True, "allowed"
    
    @classmethod
    def get_allowed_modes(cls, emotion_state: EmotionState) -> List[ReactionMode]:
        """Get all reaction modes allowed by current emotional state."""
        allowed = []
        for mode in ReactionMode:
            is_allowed, _ = cls.check(emotion_state, mode)
            if is_allowed:
                allowed.append(mode)
        return allowed


class ReactionPolicy:
    """
    Determines reaction mode based on emotional state and perception.
    
    Uses a combination of:
    - Current emotional state
    - Perceived input characteristics
    - Emotion gates for consistency
    """
    
    # Mapping from (sentiment, intent) to base reaction modes
    # Format: (sentiment, intent) -> [(mode, weight), ...]
    REACTION_MAP = {
        # Hostile/attacking input
        (Sentiment.HOSTILE, Intent.ATTACK): [
            (ReactionMode.CONFRONTATIONAL, 0.4),
            (ReactionMode.HURT, 0.3),
            (ReactionMode.COLD, 0.2),
            (ReactionMode.WITHDRAWN, 0.1),
        ],
        
        # Blame
        (Sentiment.NEGATIVE, Intent.BLAME): [
            (ReactionMode.DEFENSIVE, 0.4),
            (ReactionMode.CONFRONTATIONAL, 0.3),
            (ReactionMode.HURT, 0.2),
            (ReactionMode.COLD, 0.1),
        ],
        
        # Dismissal
        (Sentiment.NEGATIVE, Intent.DISMISS): [
            (ReactionMode.HURT, 0.3),
            (ReactionMode.COLD, 0.3),
            (ReactionMode.SARCASTIC, 0.2),
            (ReactionMode.WITHDRAWN, 0.2),
        ],
        
        # Withdrawal/avoidance
        (Sentiment.NEUTRAL, Intent.WITHDRAW): [
            (ReactionMode.HURT, 0.3),
            (ReactionMode.COLD, 0.3),
            (ReactionMode.DISMISSIVE, 0.2),
            (ReactionMode.VULNERABLE, 0.2),
        ],
        
        # Apology
        (Sentiment.POSITIVE, Intent.APOLOGIZE): [
            (ReactionMode.COLD, 0.3),  # Don't immediately forgive
            (ReactionMode.HURT, 0.3),
            (ReactionMode.COOPERATIVE, 0.2),
            (ReactionMode.SUPPORTIVE, 0.2),
        ],
        
        # Connection attempt
        (Sentiment.POSITIVE, Intent.CONNECT): [
            (ReactionMode.COOPERATIVE, 0.4),
            (ReactionMode.SUPPORTIVE, 0.3),
            (ReactionMode.VULNERABLE, 0.2),
            (ReactionMode.COLD, 0.1),  # Sometimes still guarded
        ],
        
        # Neutral question
        (Sentiment.NEUTRAL, Intent.QUESTION): [
            (ReactionMode.COOPERATIVE, 0.4),
            (ReactionMode.COLD, 0.3),
            (ReactionMode.DISMISSIVE, 0.2),
            (ReactionMode.SUPPORTIVE, 0.1),
        ],
        
        # Default
        (Sentiment.NEUTRAL, Intent.NEUTRAL): [
            (ReactionMode.COLD, 0.3),
            (ReactionMode.COOPERATIVE, 0.3),
            (ReactionMode.DISMISSIVE, 0.2),
            (ReactionMode.SARCASTIC, 0.2),
        ],
    }
    
    # Emotion influence on mode selection
    # High value -> mode more likely
    EMOTION_MODE_AFFINITY = {
        'anger': {
            ReactionMode.CONFRONTATIONAL: 0.4,
            ReactionMode.SARCASTIC: 0.3,
            ReactionMode.COLD: 0.2,
            ReactionMode.SUPPORTIVE: -0.5,
        },
        'hurt': {
            ReactionMode.HURT: 0.5,
            ReactionMode.VULNERABLE: 0.3,
            ReactionMode.WITHDRAWN: 0.3,
            ReactionMode.COLD: 0.2,
        },
        'fatigue': {
            ReactionMode.WITHDRAWN: 0.4,
            ReactionMode.COLD: 0.3,
            ReactionMode.DISMISSIVE: 0.3,
            ReactionMode.CONFRONTATIONAL: -0.3,
        },
        'trust': {
            ReactionMode.SUPPORTIVE: 0.3,
            ReactionMode.COOPERATIVE: 0.3,
            ReactionMode.VULNERABLE: 0.2,
        },
        'empathy': {
            ReactionMode.SUPPORTIVE: 0.4,
            ReactionMode.COOPERATIVE: 0.3,
            ReactionMode.VULNERABLE: 0.2,
        },
    }
    
    def __init__(self):
        """Initialize the reaction policy."""
        pass
    
    def decide(
        self, 
        emotion_state: EmotionState, 
        perception: PerceptionResult
    ) -> ReactionDecision:
        """
        Decide on a reaction mode given emotional state and perception.
        
        Args:
            emotion_state: Current emotional state
            perception: Analysis of user input
            
        Returns:
            ReactionDecision with mode, intensity, and effects
        """
        # Get base reaction probabilities from map
        key = (perception.sentiment, perception.intent)
        base_reactions = self.REACTION_MAP.get(
            key, 
            self.REACTION_MAP[(Sentiment.NEUTRAL, Intent.NEUTRAL)]
        )
        
        # Calculate weighted scores for each mode
        mode_scores = {}
        for mode, base_weight in base_reactions:
            score = base_weight
            
            # Apply emotion influences
            for emotion_name, mode_affinities in self.EMOTION_MODE_AFFINITY.items():
                if hasattr(emotion_state, emotion_name) and mode in mode_affinities:
                    emotion_value = getattr(emotion_state, emotion_name)
                    affinity = mode_affinities[mode]
                    score += emotion_value * affinity
            
            mode_scores[mode] = max(0, score)
        
        # Normalize scores
        total = sum(mode_scores.values())
        if total > 0:
            mode_scores = {m: s/total for m, s in mode_scores.items()}
        
        # Select mode (weighted random for variety)
        modes = list(mode_scores.keys())
        weights = [mode_scores[m] for m in modes]
        
        # Add small randomness
        weights = [w + random.uniform(0, 0.1) for w in weights]
        selected_mode = random.choices(modes, weights=weights, k=1)[0]
        
        # Check emotion gate
        allowed, gate_reason = EmotionGate.check(emotion_state, selected_mode)
        
        # If blocked, select next best allowed mode
        if not allowed:
            allowed_modes = EmotionGate.get_allowed_modes(emotion_state)
            if allowed_modes:
                # Pick best scoring allowed mode
                allowed_scores = [(m, mode_scores.get(m, 0)) for m in allowed_modes]
                selected_mode = max(allowed_scores, key=lambda x: x[1])[0]
        
        # Calculate intensity based on emotion extremity and perception severity
        intensity = self._calculate_intensity(emotion_state, perception)
        
        # Determine emotion deltas from this interaction
        emotion_deltas = self._calculate_emotion_deltas(perception, selected_mode)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(emotion_state, perception, selected_mode)
        
        return ReactionDecision(
            mode=selected_mode,
            intensity=intensity,
            allowed_by_gate=allowed,
            emotion_deltas=emotion_deltas,
            reasoning=reasoning,
        )
    
    def _calculate_intensity(
        self, 
        emotion_state: EmotionState, 
        perception: PerceptionResult
    ) -> float:
        """Calculate reaction intensity."""
        # Base on perception severity
        intensity = perception.severity
        
        # Modify by emotional extremity
        dom_emotion, dom_value = emotion_state.get_dominant_emotion()
        if dom_value > 0.6:
            intensity += 0.2
        
        # High anger increases intensity
        if emotion_state.anger > 0.5:
            intensity += 0.1
        
        # High fatigue decreases intensity
        if emotion_state.fatigue > 0.7:
            intensity -= 0.2
        
        return max(0.2, min(1.0, intensity))
    
    def _calculate_emotion_deltas(
        self, 
        perception: PerceptionResult,
        mode: ReactionMode
    ) -> Dict[str, float]:
        """Calculate how emotions should change after this interaction."""
        deltas = {}
        
        # Effects of perception
        if TriggerType.INSULT in perception.triggers:
            deltas['anger'] = 0.2
            deltas['hurt'] = 0.3
            deltas['trust'] = -0.2
        
        if TriggerType.BLAME in perception.triggers:
            deltas['anger'] = 0.15
            deltas['hurt'] = 0.1
            deltas['stress'] = 0.1
        
        if TriggerType.AFFECTION in perception.triggers:
            deltas['hurt'] = -0.1
            deltas['trust'] = 0.05
            deltas['love'] = 0.05
        
        if TriggerType.EMPATHY in perception.triggers:
            deltas['stress'] = -0.1
            deltas['trust'] = 0.1
            deltas['empathy'] = 0.1
        
        if TriggerType.DISMISSAL in perception.triggers:
            deltas['hurt'] = 0.15
            deltas['anger'] = 0.1
            deltas['empathy'] = -0.1
        
        if perception.intent == Intent.APOLOGIZE:
            deltas['anger'] = -0.1
            deltas['hurt'] = -0.05
        
        # Effects of reacting
        if mode == ReactionMode.CONFRONTATIONAL:
            deltas['stress'] = deltas.get('stress', 0) + 0.1
            deltas['fatigue'] = deltas.get('fatigue', 0) + 0.1
        
        if mode == ReactionMode.WITHDRAWN:
            deltas['empathy'] = deltas.get('empathy', 0) - 0.05
        
        if mode == ReactionMode.SUPPORTIVE:
            deltas['empathy'] = deltas.get('empathy', 0) + 0.05
        
        return deltas
    
    def _generate_reasoning(
        self,
        emotion_state: EmotionState,
        perception: PerceptionResult,
        mode: ReactionMode
    ) -> str:
        """Generate human-readable reasoning for the decision."""
        parts = []
        
        # Perception basis
        if perception.sentiment == Sentiment.HOSTILE:
            parts.append(f"hostile input detected")
        elif perception.intent == Intent.APOLOGIZE:
            parts.append(f"apology received")
        elif perception.intent == Intent.DISMISS:
            parts.append(f"feeling dismissed")
        
        # Emotion basis
        dom_emotion, dom_value = emotion_state.get_dominant_emotion()
        if dom_value > 0.5:
            parts.append(f"high {dom_emotion}")
        
        # Mode choice
        parts.append(f"reacting {mode.value}")
        
        return "; ".join(parts) if parts else "default reaction"
