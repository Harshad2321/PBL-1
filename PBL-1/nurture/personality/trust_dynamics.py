"""
Trust Dynamics Engine
=====================

Manages trust score, resentment score, and calculates derived states.

The TrustDynamicsEngine implements the core relationship dynamics:
- Asymmetric trust (builds slowly, erodes fast)
- Pattern-based resentment accumulation
- Withdrawal states based on trust thresholds
- Apology effectiveness tracking

Key Features:
- Trust builds at +2.0 per positive interaction
- Trust erodes at -4.0 per negative interaction (2x faster)
- Diminishing returns on rapid positive actions
- High trust provides resilience against negative interactions
- Resentment accumulates from patterns, not single incidents
- Apology effectiveness decays with repeated behavior

Example:
    engine = TrustDynamicsEngine()
    
    # Positive interaction
    engine.update_trust(delta=2.0, context=ContextType.PRIVATE)
    
    # Negative interaction (erodes faster)
    engine.update_trust(delta=-4.0, context=ContextType.PUBLIC)  # 2x in public
    
    # Pattern-based resentment
    engine.update_resentment(delta=3.0, is_pattern=True)
    
    # Check withdrawal state
    if engine.is_in_withdrawal():
        print(f"Withdrawal level: {engine.get_withdrawal_level()}")
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from nurture.core.enums import ContextType, WithdrawalLevel, ActionType


@dataclass
class ApologyRecord:
    """Record of an apology for a specific behavior."""
    behavior_type: ActionType
    timestamp: datetime
    is_genuine: bool
    effectiveness: float = 1.0
    recurrence_count: int = 0
    last_recurrence: Optional[datetime] = None


class TrustDynamicsEngine:
    """
    Manages trust score, resentment score, and derived states.
    
    Implements asymmetric trust dynamics where trust builds slowly
    but erodes quickly, with pattern-based resentment and withdrawal
    states.
    
    Attributes:
        trust_score: Current trust level (0.0 to 100.0)
        resentment_score: Current resentment level (0.0 to 100.0)
        last_positive_action_time: Timestamp of last positive action
        apology_records: Tracking of apologies and their effectiveness
    """
    
    # Trust dynamics constants
    BASE_TRUST_INCREASE = 2.0
    BASE_TRUST_DECREASE = 4.0  # 2x faster erosion
    DIMINISHING_RETURNS_WINDOW = timedelta(hours=1)
    DIMINISHING_RETURNS_MULTIPLIER = 0.5
    
    # Trust thresholds
    WITHDRAWAL_THRESHOLD = 50.0
    CRITICAL_THRESHOLD = 30.0
    HIGH_TRUST_THRESHOLD = 70.0
    HIGH_TRUST_RESILIENCE = 0.7  # Negative interactions have 70% impact
    
    # Context multipliers
    PUBLIC_CONTEXT_MULTIPLIER = 2.0
    
    # Resentment dynamics constants
    PATTERN_RESENTMENT_INCREASE = 3.0
    SINGLE_INCIDENT_RESENTMENT = 0.5
    RESENTMENT_DECAY_RATE = 0.5  # Per day with positive interactions
    
    # Resentment thresholds
    RESENTMENT_RESPONSE_THRESHOLD = 30.0
    RESENTMENT_INITIATION_THRESHOLD = 50.0
    RESENTMENT_COOPERATION_THRESHOLD = 70.0
    RESENTMENT_TRUST_IMPACT_THRESHOLD = 50.0
    
    # Apology effectiveness
    INITIAL_APOLOGY_EFFECTIVENESS = 1.0
    APOLOGY_DECAY_PER_RECURRENCE = 0.2
    MIN_APOLOGY_EFFECTIVENESS = 0.1
    APOLOGY_RECOVERY_RATE = 0.1  # Per week
    APOLOGY_RECOVERY_PERIOD = timedelta(days=7)
    
    # Apology type multipliers
    APOLOGY_TYPE_MULTIPLIERS = {
        "defensive": 0.3,
        "generic": 0.5,
        "genuine": 1.0,
        "action_oriented": 1.5,
    }
    
    def __init__(
        self,
        initial_trust: float = 60.0,
        initial_resentment: float = 10.0
    ):
        """
        Initialize trust dynamics engine.
        
        Args:
            initial_trust: Starting trust score (default: 60.0)
            initial_resentment: Starting resentment score (default: 10.0)
        """
        self.trust_score = max(0.0, min(100.0, initial_trust))
        self.resentment_score = max(0.0, min(100.0, initial_resentment))
        
        self.last_positive_action_time: Optional[datetime] = None
        self.last_resentment_decay_time: Optional[datetime] = None
        
        self.apology_records: Dict[ActionType, ApologyRecord] = {}
        
        # Track positive action streak for diminishing returns
        self._positive_action_count_in_window = 0
        self._positive_action_window_start: Optional[datetime] = None
    
    def update_trust(
        self,
        delta: float,
        context: ContextType = ContextType.PRIVATE,
        timestamp: Optional[datetime] = None
    ) -> float:
        """
        Update trust score with context-based multipliers.
        
        Implements:
        - Asymmetric trust dynamics (erosion 2x faster than building)
        - Diminishing returns on rapid positive actions
        - Public context multiplier (2x impact)
        - High trust resilience (negative actions have less impact)
        - Resentment impact on trust recovery
        
        Args:
            delta: Base trust change amount
            context: PUBLIC or PRIVATE context
            timestamp: When the action occurred (defaults to now)
        
        Returns:
            Actual trust change applied
        
        Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 4.5
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Apply context multiplier
        if context == ContextType.PUBLIC:
            delta *= self.PUBLIC_CONTEXT_MULTIPLIER
        
        # Handle positive trust changes
        if delta > 0:
            # Check for diminishing returns
            if self._is_within_diminishing_returns_window(timestamp):
                self._positive_action_count_in_window += 1
                if self._positive_action_count_in_window > 1:
                    delta *= self.DIMINISHING_RETURNS_MULTIPLIER
            else:
                # Start new window
                self._positive_action_window_start = timestamp
                self._positive_action_count_in_window = 1
            
            # Resentment reduces trust recovery
            if self.resentment_score > self.RESENTMENT_TRUST_IMPACT_THRESHOLD:
                delta *= 0.5
            
            self.last_positive_action_time = timestamp
        
        # Handle negative trust changes
        else:
            # High trust provides resilience
            if self.trust_score > self.HIGH_TRUST_THRESHOLD:
                delta *= self.HIGH_TRUST_RESILIENCE
        
        # Apply trust change
        old_trust = self.trust_score
        self.trust_score = max(0.0, min(100.0, self.trust_score + delta))
        
        actual_change = self.trust_score - old_trust
        return actual_change
    
    def update_resentment(
        self,
        delta: float,
        is_pattern: bool = False,
        timestamp: Optional[datetime] = None
    ) -> float:
        """
        Update resentment score, with higher impact for patterns.
        
        Implements:
        - Pattern-based accumulation (3.0 per pattern)
        - Single incident accumulation (0.5 per incident)
        - Slow decay with positive interactions
        
        Args:
            delta: Base resentment change
            is_pattern: Whether this is from a detected pattern
            timestamp: When the action occurred (defaults to now)
        
        Returns:
            Actual resentment change applied
        
        Validates: Requirements 4.1, 4.4
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Patterns have much higher impact
        if is_pattern and delta > 0:
            delta = self.PATTERN_RESENTMENT_INCREASE
        elif delta > 0:
            delta = self.SINGLE_INCIDENT_RESENTMENT
        
        # Apply resentment change
        old_resentment = self.resentment_score
        self.resentment_score = max(0.0, min(100.0, self.resentment_score + delta))
        
        actual_change = self.resentment_score - old_resentment
        return actual_change
    
    def apply_resentment_decay(
        self,
        days_elapsed: float = 1.0
    ) -> float:
        """
        Apply time-based resentment decay.
        
        Resentment decays slowly with positive interactions.
        
        Args:
            days_elapsed: Number of days since last decay
        
        Returns:
            Amount of resentment decay applied
        
        Validates: Requirements 4.4
        """
        if self.last_positive_action_time is None:
            return 0.0
        
        decay = self.RESENTMENT_DECAY_RATE * days_elapsed
        old_resentment = self.resentment_score
        self.resentment_score = max(0.0, self.resentment_score - decay)
        
        return old_resentment - self.resentment_score
    
    def get_trust_score(self) -> float:
        """Get current trust score (0.0 to 100.0)."""
        return self.trust_score
    
    def get_resentment_score(self) -> float:
        """Get current resentment score (0.0 to 100.0)."""
        return self.resentment_score
    
    def is_in_withdrawal(self) -> bool:
        """
        Check if Mother AI is in withdrawal state.
        
        Withdrawal occurs when trust falls below 50.0.
        
        Returns:
            True if in withdrawal state
        
        Validates: Requirements 3.4, 5.1
        """
        return self.trust_score < self.WITHDRAWAL_THRESHOLD
    
    def get_withdrawal_level(self) -> WithdrawalLevel:
        """
        Get current withdrawal severity level.
        
        Returns:
            WithdrawalLevel enum value
        
        Validates: Requirements 5.1, 5.2, 5.3
        """
        if self.trust_score >= self.WITHDRAWAL_THRESHOLD:
            return WithdrawalLevel.NONE
        elif self.trust_score >= 40.0:
            return WithdrawalLevel.MILD
        elif self.trust_score >= self.CRITICAL_THRESHOLD:
            return WithdrawalLevel.MODERATE
        else:
            return WithdrawalLevel.SEVERE
    
    def record_apology(
        self,
        behavior_type: ActionType,
        apology_type: str = "genuine",
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Record an apology and update effectiveness tracking.
        
        Args:
            behavior_type: The behavior being apologized for
            apology_type: Type of apology (defensive, generic, genuine, action_oriented)
            timestamp: When the apology occurred (defaults to now)
        
        Validates: Requirements 6.1, 6.5
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Get or create apology record
        if behavior_type not in self.apology_records:
            self.apology_records[behavior_type] = ApologyRecord(
                behavior_type=behavior_type,
                timestamp=timestamp,
                is_genuine=(apology_type in ["genuine", "action_oriented"]),
                effectiveness=self.INITIAL_APOLOGY_EFFECTIVENESS
            )
        else:
            # Update existing record
            record = self.apology_records[behavior_type]
            record.timestamp = timestamp
            record.is_genuine = (apology_type in ["genuine", "action_oriented"])
    
    def record_behavior_recurrence(
        self,
        behavior_type: ActionType,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Record that apologized-for behavior recurred, reducing apology effectiveness.
        
        Args:
            behavior_type: The behavior that recurred
            timestamp: When the recurrence happened (defaults to now)
        
        Validates: Requirements 6.2, 6.3
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        if behavior_type in self.apology_records:
            record = self.apology_records[behavior_type]
            record.recurrence_count += 1
            record.last_recurrence = timestamp
            
            # Decay effectiveness
            record.effectiveness = max(
                self.MIN_APOLOGY_EFFECTIVENESS,
                record.effectiveness - self.APOLOGY_DECAY_PER_RECURRENCE
            )
    
    def get_apology_effectiveness(
        self,
        behavior_type: ActionType,
        apology_type: str = "genuine"
    ) -> float:
        """
        Get effectiveness multiplier for apologies about specific behavior.
        
        Effectiveness starts at 1.0 and decays with repeated behavior.
        Can recover over time with sustained behavioral change.
        
        Args:
            behavior_type: The behavior being apologized for
            apology_type: Type of apology (defensive, generic, genuine, action_oriented)
        
        Returns:
            Effectiveness multiplier (0.1 to 1.5)
        
        Validates: Requirements 6.2, 6.3, 6.4, 6.5
        """
        # Get base effectiveness from apology type
        type_multiplier = self.APOLOGY_TYPE_MULTIPLIERS.get(
            apology_type,
            self.APOLOGY_TYPE_MULTIPLIERS["genuine"]
        )
        
        # Check if there's a history for this behavior
        if behavior_type not in self.apology_records:
            return type_multiplier
        
        record = self.apology_records[behavior_type]
        
        # Apply recovery if enough time has passed without recurrence
        if record.last_recurrence:
            time_since_recurrence = datetime.now() - record.last_recurrence
            weeks_elapsed = time_since_recurrence.days / 7.0
            
            if weeks_elapsed >= 1.0:
                # Gradual recovery
                recovery = self.APOLOGY_RECOVERY_RATE * int(weeks_elapsed)
                record.effectiveness = min(
                    self.INITIAL_APOLOGY_EFFECTIVENESS,
                    record.effectiveness + recovery
                )
        
        return record.effectiveness * type_multiplier
    
    def _is_within_diminishing_returns_window(self, timestamp: datetime) -> bool:
        """Check if timestamp is within diminishing returns window."""
        if self._positive_action_window_start is None:
            return False
        
        return (timestamp - self._positive_action_window_start) < self.DIMINISHING_RETURNS_WINDOW
    
    def get_response_length_multiplier(self) -> float:
        """
        Calculate response length multiplier based on withdrawal state.
        
        Returns:
            Multiplier from 0.3 (severe withdrawal) to 1.0 (no withdrawal)
        
        Validates: Requirements 5.1, 5.2
        """
        withdrawal_level = self.get_withdrawal_level()
        
        if withdrawal_level == WithdrawalLevel.NONE:
            return 1.0
        elif withdrawal_level == WithdrawalLevel.MILD:
            return 0.7
        elif withdrawal_level == WithdrawalLevel.MODERATE:
            return 0.5
        else:  # SEVERE
            return 0.3
    
    def get_initiation_probability(self) -> float:
        """
        Calculate probability of initiating interaction based on trust.
        
        Returns:
            Probability from 0.0 to 1.0
        
        Validates: Requirements 5.3, 13.1, 13.2, 13.3
        """
        if self.trust_score > self.HIGH_TRUST_THRESHOLD:
            return 1.0  # Baseline frequency
        elif self.trust_score > 40.0:
            # Proportionally reduced
            return (self.trust_score - 40.0) / 30.0
        else:
            return 0.1  # Minimal frequency
    
    def get_cooperation_level(self) -> float:
        """
        Calculate cooperation level based on resentment.
        
        Returns:
            Cooperation level from 0.0 to 1.0
        
        Validates: Requirements 5.4
        """
        if self.resentment_score < self.RESENTMENT_RESPONSE_THRESHOLD:
            return 1.0
        elif self.resentment_score < self.RESENTMENT_INITIATION_THRESHOLD:
            return 0.7
        elif self.resentment_score < self.RESENTMENT_COOPERATION_THRESHOLD:
            return 0.4
        else:
            return 0.2  # Minimal cooperation
    
    def to_dict(self) -> Dict:
        """
        Serialize trust dynamics engine to dictionary.
        
        Returns:
            Dictionary containing all engine state
        """
        return {
            "trust_score": self.trust_score,
            "resentment_score": self.resentment_score,
            "last_positive_action_time": self.last_positive_action_time.isoformat() if self.last_positive_action_time else None,
            "last_resentment_decay_time": self.last_resentment_decay_time.isoformat() if self.last_resentment_decay_time else None,
            "apology_records": {
                behavior.value: {
                    "behavior_type": record.behavior_type.value,
                    "timestamp": record.timestamp.isoformat(),
                    "is_genuine": record.is_genuine,
                    "effectiveness": record.effectiveness,
                    "recurrence_count": record.recurrence_count,
                    "last_recurrence": record.last_recurrence.isoformat() if record.last_recurrence else None,
                }
                for behavior, record in self.apology_records.items()
            },
            "_positive_action_count_in_window": self._positive_action_count_in_window,
            "_positive_action_window_start": self._positive_action_window_start.isoformat() if self._positive_action_window_start else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TrustDynamicsEngine':
        """
        Deserialize trust dynamics engine from dictionary.
        
        Args:
            data: Dictionary containing engine state
        
        Returns:
            Restored TrustDynamicsEngine instance
        """
        engine = cls(
            initial_trust=data.get("trust_score", 60.0),
            initial_resentment=data.get("resentment_score", 10.0)
        )
        
        # Restore timestamps
        if data.get("last_positive_action_time"):
            engine.last_positive_action_time = datetime.fromisoformat(data["last_positive_action_time"])
        if data.get("last_resentment_decay_time"):
            engine.last_resentment_decay_time = datetime.fromisoformat(data["last_resentment_decay_time"])
        
        # Restore apology records
        for behavior_str, record_data in data.get("apology_records", {}).items():
            behavior_type = ActionType(record_data["behavior_type"])
            engine.apology_records[behavior_type] = ApologyRecord(
                behavior_type=behavior_type,
                timestamp=datetime.fromisoformat(record_data["timestamp"]),
                is_genuine=record_data["is_genuine"],
                effectiveness=record_data["effectiveness"],
                recurrence_count=record_data["recurrence_count"],
                last_recurrence=datetime.fromisoformat(record_data["last_recurrence"]) if record_data.get("last_recurrence") else None
            )
        
        # Restore window tracking
        engine._positive_action_count_in_window = data.get("_positive_action_count_in_window", 0)
        if data.get("_positive_action_window_start"):
            engine._positive_action_window_start = datetime.fromisoformat(data["_positive_action_window_start"])
        
        return engine
