from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from nurture.core.enums import ContextType, WithdrawalLevel, ActionType

@dataclass
class ApologyRecord:
    behavior_type: ActionType
    timestamp: datetime
    is_genuine: bool
    effectiveness: float = 1.0
    recurrence_count: int = 0
    last_recurrence: Optional[datetime] = None

class TrustDynamicsEngine:

    BASE_TRUST_INCREASE = 2.0
    BASE_TRUST_DECREASE = 4.0
    DIMINISHING_RETURNS_WINDOW = timedelta(hours=1)
    DIMINISHING_RETURNS_MULTIPLIER = 0.5

    WITHDRAWAL_THRESHOLD = 50.0
    CRITICAL_THRESHOLD = 30.0
    HIGH_TRUST_THRESHOLD = 70.0
    HIGH_TRUST_RESILIENCE = 0.7

    PUBLIC_CONTEXT_MULTIPLIER = 2.0

    PATTERN_RESENTMENT_INCREASE = 3.0
    SINGLE_INCIDENT_RESENTMENT = 0.5
    RESENTMENT_DECAY_RATE = 0.5

    RESENTMENT_RESPONSE_THRESHOLD = 30.0
    RESENTMENT_INITIATION_THRESHOLD = 50.0
    RESENTMENT_COOPERATION_THRESHOLD = 70.0
    RESENTMENT_TRUST_IMPACT_THRESHOLD = 50.0

    INITIAL_APOLOGY_EFFECTIVENESS = 1.0
    APOLOGY_DECAY_PER_RECURRENCE = 0.2
    MIN_APOLOGY_EFFECTIVENESS = 0.1
    APOLOGY_RECOVERY_RATE = 0.1
    APOLOGY_RECOVERY_PERIOD = timedelta(days=7)

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
        self.trust_score = max(0.0, min(100.0, initial_trust))
        self.resentment_score = max(0.0, min(100.0, initial_resentment))

        self.last_positive_action_time: Optional[datetime] = None
        self.last_resentment_decay_time: Optional[datetime] = None

        self.apology_records: Dict[ActionType, ApologyRecord] = {}

        self._positive_action_count_in_window = 0
        self._positive_action_window_start: Optional[datetime] = None

    def update_trust(
        self,
        delta: float,
        context: ContextType = ContextType.PRIVATE,
        timestamp: Optional[datetime] = None
    ) -> float:
        if timestamp is None:
            timestamp = datetime.now()

        if context == ContextType.PUBLIC:
            delta *= self.PUBLIC_CONTEXT_MULTIPLIER

        if delta > 0:
            if self._is_within_diminishing_returns_window(timestamp):
                self._positive_action_count_in_window += 1
                if self._positive_action_count_in_window > 1:
                    delta *= self.DIMINISHING_RETURNS_MULTIPLIER
            else:
                self._positive_action_window_start = timestamp
                self._positive_action_count_in_window = 1

            if self.resentment_score > self.RESENTMENT_TRUST_IMPACT_THRESHOLD:
                delta *= 0.5

            self.last_positive_action_time = timestamp

        else:
            if self.trust_score > self.HIGH_TRUST_THRESHOLD:
                delta *= self.HIGH_TRUST_RESILIENCE

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
        if timestamp is None:
            timestamp = datetime.now()

        if is_pattern and delta > 0:
            delta = self.PATTERN_RESENTMENT_INCREASE
        elif delta > 0:
            delta = self.SINGLE_INCIDENT_RESENTMENT

        old_resentment = self.resentment_score
        self.resentment_score = max(0.0, min(100.0, self.resentment_score + delta))

        actual_change = self.resentment_score - old_resentment
        return actual_change

    def apply_resentment_decay(
        self,
        days_elapsed: float = 1.0
    ) -> float:
        if self.last_positive_action_time is None:
            return 0.0

        decay = self.RESENTMENT_DECAY_RATE * days_elapsed
        old_resentment = self.resentment_score
        self.resentment_score = max(0.0, self.resentment_score - decay)

        return old_resentment - self.resentment_score

    def get_trust_score(self) -> float:
        return self.trust_score

    def get_resentment_score(self) -> float:
        return self.resentment_score

    def is_in_withdrawal(self) -> bool:
        return self.trust_score < self.WITHDRAWAL_THRESHOLD

    def get_withdrawal_level(self) -> WithdrawalLevel:
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
        if timestamp is None:
            timestamp = datetime.now()

        if behavior_type not in self.apology_records:
            self.apology_records[behavior_type] = ApologyRecord(
                behavior_type=behavior_type,
                timestamp=timestamp,
                is_genuine=(apology_type in ["genuine", "action_oriented"]),
                effectiveness=self.INITIAL_APOLOGY_EFFECTIVENESS
            )
        else:
            record = self.apology_records[behavior_type]
            record.timestamp = timestamp
            record.is_genuine = (apology_type in ["genuine", "action_oriented"])

    def record_behavior_recurrence(
        self,
        behavior_type: ActionType,
        timestamp: Optional[datetime] = None
    ) -> None:
        if timestamp is None:
            timestamp = datetime.now()

        if behavior_type in self.apology_records:
            record = self.apology_records[behavior_type]
            record.recurrence_count += 1
            record.last_recurrence = timestamp

            record.effectiveness = max(
                self.MIN_APOLOGY_EFFECTIVENESS,
                record.effectiveness - self.APOLOGY_DECAY_PER_RECURRENCE
            )

    def get_apology_effectiveness(
        self,
        behavior_type: ActionType,
        apology_type: str = "genuine"
    ) -> float:
        type_multiplier = self.APOLOGY_TYPE_MULTIPLIERS.get(
            apology_type,
            self.APOLOGY_TYPE_MULTIPLIERS["genuine"]
        )

        if behavior_type not in self.apology_records:
            return type_multiplier

        record = self.apology_records[behavior_type]

        if record.last_recurrence:
            time_since_recurrence = datetime.now() - record.last_recurrence
            weeks_elapsed = time_since_recurrence.days / 7.0

            if weeks_elapsed >= 1.0:
                recovery = self.APOLOGY_RECOVERY_RATE * int(weeks_elapsed)
                record.effectiveness = min(
                    self.INITIAL_APOLOGY_EFFECTIVENESS,
                    record.effectiveness + recovery
                )

        return record.effectiveness * type_multiplier

    def _is_within_diminishing_returns_window(self, timestamp: datetime) -> bool:
        if self._positive_action_window_start is None:
            return False

        return (timestamp - self._positive_action_window_start) < self.DIMINISHING_RETURNS_WINDOW

    def get_response_length_multiplier(self) -> float:
        withdrawal_level = self.get_withdrawal_level()

        if withdrawal_level == WithdrawalLevel.NONE:
            return 1.0
        elif withdrawal_level == WithdrawalLevel.MILD:
            return 0.7
        elif withdrawal_level == WithdrawalLevel.MODERATE:
            return 0.5
        else:
            return 0.3

    def get_initiation_probability(self) -> float:
        if self.trust_score > self.HIGH_TRUST_THRESHOLD:
            return 1.0
        elif self.trust_score > 40.0:
            return (self.trust_score - 40.0) / 30.0
        else:
            return 0.1

    def get_cooperation_level(self) -> float:
        if self.resentment_score < self.RESENTMENT_RESPONSE_THRESHOLD:
            return 1.0
        elif self.resentment_score < self.RESENTMENT_INITIATION_THRESHOLD:
            return 0.7
        elif self.resentment_score < self.RESENTMENT_COOPERATION_THRESHOLD:
            return 0.4
        else:
            return 0.2

    def to_dict(self) -> Dict:
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
        engine = cls(
            initial_trust=data.get("trust_score", 60.0),
            initial_resentment=data.get("resentment_score", 10.0)
        )

        if data.get("last_positive_action_time"):
            engine.last_positive_action_time = datetime.fromisoformat(data["last_positive_action_time"])
        if data.get("last_resentment_decay_time"):
            engine.last_resentment_decay_time = datetime.fromisoformat(data["last_resentment_decay_time"])

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

        engine._positive_action_count_in_window = data.get("_positive_action_count_in_window", 0)
        if data.get("_positive_action_window_start"):
            engine._positive_action_window_start = datetime.fromisoformat(data["_positive_action_window_start"])

        return engine
