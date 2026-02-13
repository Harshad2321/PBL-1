from dataclasses import dataclass, field
from typing import Dict, Optional
import random

@dataclass
class EmotionState:
    anger: float = 0.2
    stress: float = 0.4
    fatigue: float = 0.3
    trust: float = 0.6
    empathy: float = 0.5
    hurt: float = 0.2
    love: float = 0.7

    _baselines: Dict[str, float] = field(default_factory=lambda: {
        'anger': 0.2,
        'stress': 0.3,
        'fatigue': 0.3,
        'trust': 0.5,
        'empathy': 0.5,
        'hurt': 0.2,
        'love': 0.6,
    })

    _decay_rates: Dict[str, float] = field(default_factory=lambda: {
        'anger': 0.1,
        'stress': 0.05,
        'fatigue': 0.02,
        'trust': 0.02,
        'empathy': 0.05,
        'hurt': 0.08,
        'love': 0.01,
    })

    def __post_init__(self):
        self._clamp_all()

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, value))

    def _clamp_all(self):
        self.anger = self._clamp(self.anger)
        self.stress = self._clamp(self.stress)
        self.fatigue = self._clamp(self.fatigue)
        self.trust = self._clamp(self.trust)
        self.empathy = self._clamp(self.empathy)
        self.hurt = self._clamp(self.hurt)
        self.love = self._clamp(self.love)

    def update(self, deltas: Dict[str, float]) -> None:
        for emotion, delta in deltas.items():
            if hasattr(self, emotion):
                current = getattr(self, emotion)
                setattr(self, emotion, self._clamp(current + delta))

        self._apply_interactions()

    def _apply_interactions(self):
        if self.anger > 0.7:
            self.empathy = self._clamp(self.empathy - 0.1)

        if self.fatigue > 0.7:
            self.stress = self._clamp(self.stress + 0.05)

        if self.hurt > 0.6:
            self.trust = self._clamp(self.trust - 0.05)

        if self.trust < 0.3:
            self.empathy = self._clamp(self.empathy - 0.05)

        if self.love > 0.7 and self.anger > 0.5:
            self.anger = self._clamp(self.anger - 0.05)

    def decay_toward_baseline(self):
        for emotion, baseline in self._baselines.items():
            if hasattr(self, emotion):
                current = getattr(self, emotion)
                decay_rate = self._decay_rates.get(emotion, 0.05)

                if current > baseline:
                    new_value = current - decay_rate
                    setattr(self, emotion, max(baseline, new_value))
                elif current < baseline:
                    new_value = current + decay_rate
                    setattr(self, emotion, min(baseline, new_value))

    def get_dominant_emotion(self) -> tuple:
        emotions = {
            'anger': self.anger,
            'stress': self.stress,
            'fatigue': self.fatigue,
            'hurt': self.hurt,
        }

        weighted = {}
        for emotion, value in emotions.items():
            baseline = self._baselines.get(emotion, 0.5)
            deviation = abs(value - baseline)
            weighted[emotion] = (value, deviation)

        dominant = max(weighted.items(), key=lambda x: x[1][0])
        return dominant[0], dominant[1][0]

    def get_emotional_valence(self) -> float:
        positive = (self.trust + self.empathy + self.love) / 3
        negative = (self.anger + self.stress + self.hurt) / 3
        return positive - negative

    def get_state_summary(self) -> Dict[str, float]:
        return {
            'anger': round(self.anger, 2),
            'stress': round(self.stress, 2),
            'fatigue': round(self.fatigue, 2),
            'trust': round(self.trust, 2),
            'empathy': round(self.empathy, 2),
            'hurt': round(self.hurt, 2),
            'love': round(self.love, 2),
            'valence': round(self.get_emotional_valence(), 2),
        }

    def describe(self) -> str:
        descriptions = []

        if self.anger > 0.7:
            descriptions.append("furious")
        elif self.anger > 0.5:
            descriptions.append("angry")
        elif self.anger > 0.3:
            descriptions.append("irritated")

        if self.stress > 0.7:
            descriptions.append("overwhelmed")
        elif self.stress > 0.5:
            descriptions.append("stressed")

        if self.fatigue > 0.7:
            descriptions.append("exhausted")
        elif self.fatigue > 0.5:
            descriptions.append("tired")

        if self.hurt > 0.7:
            descriptions.append("deeply hurt")
        elif self.hurt > 0.5:
            descriptions.append("hurt")

        if self.trust < 0.3:
            descriptions.append("distrustful")

        if self.empathy < 0.3:
            descriptions.append("closed off")

        if not descriptions:
            if self.get_emotional_valence() > 0.2:
                descriptions.append("okay")
            else:
                descriptions.append("neutral")

        return ", ".join(descriptions)

    def copy(self) -> 'EmotionState':
        return EmotionState(
            anger=self.anger,
            stress=self.stress,
            fatigue=self.fatigue,
            trust=self.trust,
            empathy=self.empathy,
            hurt=self.hurt,
            love=self.love,
        )

class EmotionPresets:

    @staticmethod
    def calm() -> EmotionState:
        return EmotionState(
            anger=0.1, stress=0.2, fatigue=0.2,
            trust=0.7, empathy=0.7, hurt=0.1, love=0.8
        )

    @staticmethod
    def stressed_new_parent() -> EmotionState:
        return EmotionState(
            anger=0.3, stress=0.6, fatigue=0.7,
            trust=0.5, empathy=0.4, hurt=0.3, love=0.7
        )

    @staticmethod
    def betrayed() -> EmotionState:
        return EmotionState(
            anger=0.7, stress=0.6, fatigue=0.5,
            trust=0.2, empathy=0.2, hurt=0.8, love=0.4
        )

    @staticmethod
    def exhausted() -> EmotionState:
        return EmotionState(
            anger=0.4, stress=0.7, fatigue=0.9,
            trust=0.4, empathy=0.3, hurt=0.4, love=0.5
        )

    @staticmethod
    def loving() -> EmotionState:
        return EmotionState(
            anger=0.1, stress=0.3, fatigue=0.3,
            trust=0.8, empathy=0.8, hurt=0.1, love=0.9
        )
