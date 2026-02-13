from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import random

from nurture.emotion.emotion_state import EmotionState
from nurture.emotion.perception import PerceptionResult, Sentiment, Intent, TriggerType

class ReactionMode(Enum):
    SUPPORTIVE = "supportive"
    DEFENSIVE = "defensive"
    CONFRONTATIONAL = "confrontational"
    COLD = "cold"
    WITHDRAWN = "withdrawn"
    COOPERATIVE = "cooperative"
    SARCASTIC = "sarcastic"
    VULNERABLE = "vulnerable"
    DISMISSIVE = "dismissive"
    HURT = "hurt"

@dataclass
class ReactionDecision:
    mode: ReactionMode
    intensity: float
    allowed_by_gate: bool
    emotion_deltas: Dict[str, float]
    reasoning: str

    def describe(self) -> str:
        return f"{self.mode.value} (intensity: {self.intensity:.1f}) - {self.reasoning}"

class EmotionGate:

    GATES = [
        (lambda e: e.anger > 0.7,
         [ReactionMode.SUPPORTIVE, ReactionMode.COOPERATIVE],
         "too angry to be supportive"),

        (lambda e: e.hurt > 0.7,
         [ReactionMode.SUPPORTIVE],
         "too hurt to be warm"),

        (lambda e: e.trust < 0.3,
         [ReactionMode.VULNERABLE],
         "trust too low to be vulnerable"),

        (lambda e: e.fatigue > 0.8,
         [ReactionMode.CONFRONTATIONAL],
         "too exhausted to fight"),

        (lambda e: e.empathy < 0.2,
         [ReactionMode.COOPERATIVE, ReactionMode.SUPPORTIVE],
         "empathy too low"),
    ]

    @classmethod
    def check(cls, emotion_state: EmotionState, mode: ReactionMode) -> Tuple[bool, str]:
        for condition, blocked_modes, reason in cls.GATES:
            if condition(emotion_state) and mode in blocked_modes:
                return False, reason
        return True, "allowed"

    @classmethod
    def get_allowed_modes(cls, emotion_state: EmotionState) -> List[ReactionMode]:
        allowed = []
        for mode in ReactionMode:
            is_allowed, _ = cls.check(emotion_state, mode)
            if is_allowed:
                allowed.append(mode)
        return allowed

class ReactionPolicy:

    REACTION_MAP = {
        (Sentiment.HOSTILE, Intent.ATTACK): [
            (ReactionMode.CONFRONTATIONAL, 0.4),
            (ReactionMode.HURT, 0.3),
            (ReactionMode.COLD, 0.2),
            (ReactionMode.WITHDRAWN, 0.1),
        ],

        (Sentiment.NEGATIVE, Intent.BLAME): [
            (ReactionMode.DEFENSIVE, 0.4),
            (ReactionMode.CONFRONTATIONAL, 0.3),
            (ReactionMode.HURT, 0.2),
            (ReactionMode.COLD, 0.1),
        ],

        (Sentiment.NEGATIVE, Intent.DISMISS): [
            (ReactionMode.HURT, 0.3),
            (ReactionMode.COLD, 0.3),
            (ReactionMode.SARCASTIC, 0.2),
            (ReactionMode.WITHDRAWN, 0.2),
        ],

        (Sentiment.NEUTRAL, Intent.WITHDRAW): [
            (ReactionMode.HURT, 0.3),
            (ReactionMode.COLD, 0.3),
            (ReactionMode.DISMISSIVE, 0.2),
            (ReactionMode.VULNERABLE, 0.2),
        ],

        (Sentiment.POSITIVE, Intent.APOLOGIZE): [
            (ReactionMode.COLD, 0.3),
            (ReactionMode.HURT, 0.3),
            (ReactionMode.COOPERATIVE, 0.2),
            (ReactionMode.SUPPORTIVE, 0.2),
        ],

        (Sentiment.POSITIVE, Intent.CONNECT): [
            (ReactionMode.COOPERATIVE, 0.4),
            (ReactionMode.SUPPORTIVE, 0.3),
            (ReactionMode.VULNERABLE, 0.2),
            (ReactionMode.COLD, 0.1),
        ],

        (Sentiment.NEUTRAL, Intent.QUESTION): [
            (ReactionMode.COOPERATIVE, 0.4),
            (ReactionMode.COLD, 0.3),
            (ReactionMode.DISMISSIVE, 0.2),
            (ReactionMode.SUPPORTIVE, 0.1),
        ],

        (Sentiment.NEUTRAL, Intent.NEUTRAL): [
            (ReactionMode.COLD, 0.3),
            (ReactionMode.COOPERATIVE, 0.3),
            (ReactionMode.DISMISSIVE, 0.2),
            (ReactionMode.SARCASTIC, 0.2),
        ],
    }

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
        pass

    def decide(
        self,
        emotion_state: EmotionState,
        perception: PerceptionResult
    ) -> ReactionDecision:
        key = (perception.sentiment, perception.intent)
        base_reactions = self.REACTION_MAP.get(
            key,
            self.REACTION_MAP[(Sentiment.NEUTRAL, Intent.NEUTRAL)]
        )

        mode_scores = {}
        for mode, base_weight in base_reactions:
            score = base_weight

            for emotion_name, mode_affinities in self.EMOTION_MODE_AFFINITY.items():
                if hasattr(emotion_state, emotion_name) and mode in mode_affinities:
                    emotion_value = getattr(emotion_state, emotion_name)
                    affinity = mode_affinities[mode]
                    score += emotion_value * affinity

            mode_scores[mode] = max(0, score)

        total = sum(mode_scores.values())
        if total > 0:
            mode_scores = {m: s/total for m, s in mode_scores.items()}

        modes = list(mode_scores.keys())
        weights = [mode_scores[m] for m in modes]

        weights = [w + random.uniform(0, 0.1) for w in weights]
        selected_mode = random.choices(modes, weights=weights, k=1)[0]

        allowed, gate_reason = EmotionGate.check(emotion_state, selected_mode)

        if not allowed:
            allowed_modes = EmotionGate.get_allowed_modes(emotion_state)
            if allowed_modes:
                allowed_scores = [(m, mode_scores.get(m, 0)) for m in allowed_modes]
                selected_mode = max(allowed_scores, key=lambda x: x[1])[0]

        intensity = self._calculate_intensity(emotion_state, perception)

        emotion_deltas = self._calculate_emotion_deltas(perception, selected_mode)

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
        intensity = perception.severity

        dom_emotion, dom_value = emotion_state.get_dominant_emotion()
        if dom_value > 0.6:
            intensity += 0.2

        if emotion_state.anger > 0.5:
            intensity += 0.1

        if emotion_state.fatigue > 0.7:
            intensity -= 0.2

        return max(0.2, min(1.0, intensity))

    def _calculate_emotion_deltas(
        self,
        perception: PerceptionResult,
        mode: ReactionMode
    ) -> Dict[str, float]:
        deltas = {}

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
        parts = []

        if perception.sentiment == Sentiment.HOSTILE:
            parts.append(f"hostile input detected")
        elif perception.intent == Intent.APOLOGIZE:
            parts.append(f"apology received")
        elif perception.intent == Intent.DISMISS:
            parts.append(f"feeling dismissed")

        dom_emotion, dom_value = emotion_state.get_dominant_emotion()
        if dom_value > 0.5:
            parts.append(f"high {dom_emotion}")

        parts.append(f"reacting {mode.value}")

        return "; ".join(parts) if parts else "default reaction"
