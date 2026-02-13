from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from nurture.core.data_structures import PlayerAction, BehaviorPattern
from nurture.core.enums import ActionType, PatternType, ContextType

class PatternTracker:

    def __init__(
        self,
        time_window: timedelta = timedelta(days=7),
        min_occurrences: int = 3,
        decay_rate: float = 0.1,
        break_threshold: int = 5
    ):
        self.action_history: List[PlayerAction] = []
        self.detected_patterns: Dict[PatternType, BehaviorPattern] = {}
        self.pattern_weights: Dict[PatternType, float] = defaultdict(lambda: 1.0)
        self.positive_streak: int = 0

        self.time_window = time_window
        self.min_occurrences = min_occurrences
        self.decay_rate = decay_rate
        self.break_threshold = break_threshold

        self._action_to_pattern_map = self._build_action_pattern_map()

    def _build_action_pattern_map(self) -> Dict[ActionType, PatternType]:
        return {
            ActionType.PARENTING_PRESENT: PatternType.CONSISTENT_PRESENCE,
            ActionType.PARENTING_ABSENT: PatternType.SPORADIC_INVOLVEMENT,
            ActionType.CONFLICT_AVOID: PatternType.REPEATED_AVOIDANCE,
            ActionType.CONTROL_TAKING: PatternType.CONTROL_TAKING,
            ActionType.EMPATHY_SHOWN: PatternType.EMPATHETIC_SUPPORT,
            ActionType.PUBLIC_SUPPORT: PatternType.PUBLIC_UNITY,
            ActionType.PUBLIC_CONTRADICTION: PatternType.PUBLIC_UNDERMINING,
        }

    def record_action(self, action: PlayerAction, timestamp: Optional[datetime] = None) -> None:
        if timestamp is not None:
            action.timestamp = timestamp

        self.action_history.append(action)

        if action.emotional_valence > 0.3:
            self.positive_streak += 1
        else:
            self.positive_streak = 0

        if self.positive_streak >= self.break_threshold:
            self._break_negative_patterns()

    def _break_negative_patterns(self) -> None:
        negative_patterns = [
            PatternType.SPORADIC_INVOLVEMENT,
            PatternType.REPEATED_AVOIDANCE,
            PatternType.CONTROL_TAKING,
            PatternType.PUBLIC_UNDERMINING,
        ]

        for pattern_type in negative_patterns:
            if pattern_type in self.pattern_weights:
                self.pattern_weights[pattern_type] *= 0.8

                if self.pattern_weights[pattern_type] < 0.1:
                    self.pattern_weights[pattern_type] = 0.0
                    if pattern_type in self.detected_patterns:
                        del self.detected_patterns[pattern_type]

    def detect_patterns(self, time_window: Optional[timedelta] = None) -> List[BehaviorPattern]:
        if time_window is None:
            time_window = self.time_window

        cutoff_time = datetime.now() - time_window

        recent_actions = [
            action for action in self.action_history
            if action.timestamp >= cutoff_time
        ]

        pattern_actions: Dict[PatternType, List[PlayerAction]] = defaultdict(list)

        for action in recent_actions:
            pattern_type = self._action_to_pattern_map.get(action.action_type)
            if pattern_type:
                pattern_actions[pattern_type].append(action)

        detected = []

        for pattern_type, actions in pattern_actions.items():
            if len(actions) >= self.min_occurrences:
                days = time_window.days if time_window.days > 0 else 1
                frequency = len(actions) / days

                if pattern_type in self.detected_patterns:
                    pattern = self.detected_patterns[pattern_type]
                    pattern.occurrences = actions
                    pattern.frequency = frequency
                    pattern.last_seen = actions[-1].timestamp
                else:
                    pattern = BehaviorPattern(
                        pattern_type=pattern_type,
                        occurrences=actions,
                        frequency=frequency,
                        weight=self.pattern_weights[pattern_type],
                        first_seen=actions[0].timestamp,
                        last_seen=actions[-1].timestamp
                    )
                    self.detected_patterns[pattern_type] = pattern

                detected.append(pattern)

        self._apply_temporal_decay()

        return detected

    def _apply_temporal_decay(self) -> None:
        now = datetime.now()

        for pattern_type, pattern in list(self.detected_patterns.items()):
            days_since_last = (now - pattern.last_seen).days

            if days_since_last > 0:
                decay_factor = (1.0 - self.decay_rate) ** days_since_last
                pattern.weight *= decay_factor
                self.pattern_weights[pattern_type] = pattern.weight

                if pattern.weight < 0.1:
                    del self.detected_patterns[pattern_type]
                    self.pattern_weights[pattern_type] = 0.0

    def get_pattern_frequency(self, pattern_type: PatternType) -> float:
        if pattern_type in self.detected_patterns:
            return self.detected_patterns[pattern_type].frequency
        return 0.0

    def break_pattern(self, pattern_type: PatternType) -> None:
        if pattern_type in self.pattern_weights:
            self.pattern_weights[pattern_type] *= 0.7

            if self.pattern_weights[pattern_type] < 0.1:
                self.pattern_weights[pattern_type] = 0.0
                if pattern_type in self.detected_patterns:
                    del self.detected_patterns[pattern_type]

    def get_pattern_weight(self, pattern_type: PatternType) -> float:
        return self.pattern_weights.get(pattern_type, 0.0)

    def get_all_patterns(self) -> List[BehaviorPattern]:
        return list(self.detected_patterns.values())

    def clear_history(self, before_date: Optional[datetime] = None) -> None:
        if before_date is None:
            self.action_history.clear()
            self.detected_patterns.clear()
            self.pattern_weights.clear()
            self.positive_streak = 0
        else:
            self.action_history = [
                action for action in self.action_history
                if action.timestamp >= before_date
            ]

    def to_dict(self) -> Dict:
        return {
            "action_history": [action.to_dict() for action in self.action_history],
            "detected_patterns": {
                pt.value: pattern.to_dict()
                for pt, pattern in self.detected_patterns.items()
            },
            "pattern_weights": {
                pt.value: weight
                for pt, weight in self.pattern_weights.items()
            },
            "positive_streak": self.positive_streak,
            "time_window_days": self.time_window.days,
            "min_occurrences": self.min_occurrences,
            "decay_rate": self.decay_rate,
            "break_threshold": self.break_threshold,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'PatternTracker':
        tracker = cls(
            time_window=timedelta(days=data.get("time_window_days", 7)),
            min_occurrences=data.get("min_occurrences", 3),
            decay_rate=data.get("decay_rate", 0.1),
            break_threshold=data.get("break_threshold", 5)
        )

        tracker.action_history = [
            PlayerAction.from_dict(action_data)
            for action_data in data.get("action_history", [])
        ]

        tracker.detected_patterns = {
            PatternType(pt): BehaviorPattern.from_dict(pattern_data)
            for pt, pattern_data in data.get("detected_patterns", {}).items()
        }

        tracker.pattern_weights = defaultdict(
            lambda: 1.0,
            {
                PatternType(pt): weight
                for pt, weight in data.get("pattern_weights", {}).items()
            }
        )

        tracker.positive_streak = data.get("positive_streak", 0)

        return tracker
