"""
Pattern Tracker
===============

Detects and tracks behavioral patterns over time to enable pattern-based
responses rather than reaction-based responses.

The PatternTracker monitors sequences of player actions within sliding time
windows to identify repeated behaviors. Patterns have more impact than
isolated actions, and pattern weights decay as they are broken by positive
behavior.

Key Features:
- Sliding time window analysis (default: 7 days)
- Minimum threshold for pattern recognition (default: 3 occurrences)
- Pattern weight decay (10% per day without occurrence)
- Pattern breaking through positive behavior (5 consecutive positive actions)

Example:
    tracker = PatternTracker()
    
    # Record actions
    tracker.record_action(PlayerAction(...), datetime.now())
    
    # Detect patterns
    patterns = tracker.detect_patterns(timedelta(days=7))
    
    # Check pattern frequency
    freq = tracker.get_pattern_frequency(PatternType.REPEATED_AVOIDANCE)
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from nurture.core.data_structures import PlayerAction, BehaviorPattern
from nurture.core.enums import ActionType, PatternType, ContextType


class PatternTracker:
    """
    Tracks and detects behavioral patterns over time.
    
    Monitors player actions within sliding time windows to identify
    repeated behaviors. Patterns are weighted and can be broken by
    sustained positive behavior.
    
    Attributes:
        action_history: List of all recorded actions with timestamps
        detected_patterns: Currently active patterns
        pattern_weights: Weight for each pattern type (0.0 to 1.0)
        positive_streak: Count of consecutive positive actions
        time_window: Time window for pattern detection (default: 7 days)
        min_occurrences: Minimum occurrences to form a pattern (default: 3)
        decay_rate: Daily decay rate for pattern weights (default: 0.1)
        break_threshold: Positive actions needed to break pattern (default: 5)
    """
    
    def __init__(
        self,
        time_window: timedelta = timedelta(days=7),
        min_occurrences: int = 3,
        decay_rate: float = 0.1,
        break_threshold: int = 5
    ):
        """
        Initialize pattern tracker.
        
        Args:
            time_window: Time window for pattern detection
            min_occurrences: Minimum occurrences to form a pattern
            decay_rate: Daily decay rate for pattern weights (0.0 to 1.0)
            break_threshold: Positive actions needed to break a pattern
        """
        self.action_history: List[PlayerAction] = []
        self.detected_patterns: Dict[PatternType, BehaviorPattern] = {}
        self.pattern_weights: Dict[PatternType, float] = defaultdict(lambda: 1.0)
        self.positive_streak: int = 0
        
        # Configuration
        self.time_window = time_window
        self.min_occurrences = min_occurrences
        self.decay_rate = decay_rate
        self.break_threshold = break_threshold
        
        # Pattern mapping: ActionType -> PatternType
        self._action_to_pattern_map = self._build_action_pattern_map()
    
    def _build_action_pattern_map(self) -> Dict[ActionType, PatternType]:
        """
        Build mapping from action types to pattern types.
        
        Returns:
            Dictionary mapping ActionType to PatternType
        """
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
        """
        Record a player action with timestamp for pattern analysis.
        
        Updates positive streak counter and adds action to history.
        
        Args:
            action: The player action to record
            timestamp: Optional timestamp (uses action.timestamp if not provided)
        
        Validates: Requirements 1.4
        """
        if timestamp is not None:
            action.timestamp = timestamp
        
        self.action_history.append(action)
        
        # Update positive streak
        if action.emotional_valence > 0.3:
            self.positive_streak += 1
        else:
            self.positive_streak = 0
        
        # Check if positive streak breaks any patterns
        if self.positive_streak >= self.break_threshold:
            self._break_negative_patterns()
    
    def _break_negative_patterns(self) -> None:
        """
        Reduce weight of negative patterns when positive streak is achieved.
        
        Validates: Requirements 1.5
        """
        negative_patterns = [
            PatternType.SPORADIC_INVOLVEMENT,
            PatternType.REPEATED_AVOIDANCE,
            PatternType.CONTROL_TAKING,
            PatternType.PUBLIC_UNDERMINING,
        ]
        
        for pattern_type in negative_patterns:
            if pattern_type in self.pattern_weights:
                # Reduce weight by 20% when pattern is broken
                self.pattern_weights[pattern_type] *= 0.8
                
                # Remove pattern if weight drops below threshold
                if self.pattern_weights[pattern_type] < 0.1:
                    self.pattern_weights[pattern_type] = 0.0
                    if pattern_type in self.detected_patterns:
                        del self.detected_patterns[pattern_type]
    
    def detect_patterns(self, time_window: Optional[timedelta] = None) -> List[BehaviorPattern]:
        """
        Identify repeated behavioral patterns within time window.
        
        Analyzes action history to find sequences of similar actions
        that occur repeatedly within the specified time window.
        
        Args:
            time_window: Time window to analyze (uses default if not provided)
        
        Returns:
            List of detected behavioral patterns
        
        Validates: Requirements 1.1, 1.2, 1.3, 1.4
        """
        if time_window is None:
            time_window = self.time_window
        
        cutoff_time = datetime.now() - time_window
        
        # Filter actions within time window
        recent_actions = [
            action for action in self.action_history
            if action.timestamp >= cutoff_time
        ]
        
        # Group actions by pattern type
        pattern_actions: Dict[PatternType, List[PlayerAction]] = defaultdict(list)
        
        for action in recent_actions:
            pattern_type = self._action_to_pattern_map.get(action.action_type)
            if pattern_type:
                pattern_actions[pattern_type].append(action)
        
        # Detect patterns with sufficient occurrences
        detected = []
        
        for pattern_type, actions in pattern_actions.items():
            if len(actions) >= self.min_occurrences:
                # Calculate frequency (actions per day)
                days = time_window.days if time_window.days > 0 else 1
                frequency = len(actions) / days
                
                # Get or create pattern
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
        
        # Apply temporal decay to pattern weights
        self._apply_temporal_decay()
        
        return detected
    
    def _apply_temporal_decay(self) -> None:
        """
        Apply time-based decay to pattern weights.
        
        Patterns that haven't occurred recently have their weights reduced.
        
        Validates: Requirements 1.5
        """
        now = datetime.now()
        
        for pattern_type, pattern in list(self.detected_patterns.items()):
            days_since_last = (now - pattern.last_seen).days
            
            if days_since_last > 0:
                # Apply exponential decay
                decay_factor = (1.0 - self.decay_rate) ** days_since_last
                pattern.weight *= decay_factor
                self.pattern_weights[pattern_type] = pattern.weight
                
                # Remove pattern if weight drops too low
                if pattern.weight < 0.1:
                    del self.detected_patterns[pattern_type]
                    self.pattern_weights[pattern_type] = 0.0
    
    def get_pattern_frequency(self, pattern_type: PatternType) -> float:
        """
        Calculate frequency of specific pattern type.
        
        Args:
            pattern_type: The pattern type to check
        
        Returns:
            Frequency as actions per day (0.0 if pattern not detected)
        
        Validates: Requirements 1.2
        """
        if pattern_type in self.detected_patterns:
            return self.detected_patterns[pattern_type].frequency
        return 0.0
    
    def break_pattern(self, pattern_type: PatternType) -> None:
        """
        Mark a negative pattern as broken by positive behavior.
        
        Reduces pattern weight and removes from detected patterns
        if weight drops below threshold.
        
        Args:
            pattern_type: The pattern type to break
        
        Validates: Requirements 1.5
        """
        if pattern_type in self.pattern_weights:
            # Reduce weight by 30% when explicitly broken
            self.pattern_weights[pattern_type] *= 0.7
            
            # Remove if weight too low
            if self.pattern_weights[pattern_type] < 0.1:
                self.pattern_weights[pattern_type] = 0.0
                if pattern_type in self.detected_patterns:
                    del self.detected_patterns[pattern_type]
    
    def get_pattern_weight(self, pattern_type: PatternType) -> float:
        """
        Get current weight of a pattern.
        
        Weight decreases as pattern is broken by positive behavior.
        
        Args:
            pattern_type: The pattern type to check
        
        Returns:
            Current weight (0.0 to 1.0)
        
        Validates: Requirements 1.5
        """
        return self.pattern_weights.get(pattern_type, 0.0)
    
    def get_all_patterns(self) -> List[BehaviorPattern]:
        """
        Get all currently detected patterns.
        
        Returns:
            List of all active behavioral patterns
        """
        return list(self.detected_patterns.values())
    
    def clear_history(self, before_date: Optional[datetime] = None) -> None:
        """
        Clear action history before a specific date.
        
        Useful for managing memory usage by removing old actions.
        
        Args:
            before_date: Clear actions before this date (clears all if None)
        """
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
        """
        Serialize pattern tracker state to dictionary.
        
        Returns:
            Dictionary containing all tracker state
        """
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
        """
        Deserialize pattern tracker state from dictionary.
        
        Args:
            data: Dictionary containing tracker state
        
        Returns:
            Restored PatternTracker instance
        """
        tracker = cls(
            time_window=timedelta(days=data.get("time_window_days", 7)),
            min_occurrences=data.get("min_occurrences", 3),
            decay_rate=data.get("decay_rate", 0.1),
            break_threshold=data.get("break_threshold", 5)
        )
        
        # Restore action history
        tracker.action_history = [
            PlayerAction.from_dict(action_data)
            for action_data in data.get("action_history", [])
        ]
        
        # Restore detected patterns
        tracker.detected_patterns = {
            PatternType(pt): BehaviorPattern.from_dict(pattern_data)
            for pt, pattern_data in data.get("detected_patterns", {}).items()
        }
        
        # Restore pattern weights
        tracker.pattern_weights = defaultdict(
            lambda: 1.0,
            {
                PatternType(pt): weight
                for pt, weight in data.get("pattern_weights", {}).items()
            }
        )
        
        tracker.positive_streak = data.get("positive_streak", 0)
        
        return tracker
