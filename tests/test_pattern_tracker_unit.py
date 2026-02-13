import pytest
from datetime import datetime, timedelta

from nurture.personality.pattern_tracker import PatternTracker
from nurture.core.data_structures import PlayerAction
from nurture.core.enums import ActionType, ContextType, PatternType

def test_empty_time_window():
    tracker = PatternTracker()

    old_action = PlayerAction(
        action_type=ActionType.CONFLICT_AVOID,
        context=ContextType.PRIVATE,
        emotional_valence=-0.5,
        timestamp=datetime.now() - timedelta(days=30)
    )
    tracker.record_action(old_action)

    patterns = tracker.detect_patterns()

    assert len(patterns) == 0

def test_insufficient_data_exactly_two_actions():
    tracker = PatternTracker(min_occurrences=3)

    for i in range(2):
        action = PlayerAction(
            action_type=ActionType.CONTROL_TAKING,
            context=ContextType.PRIVATE,
            emotional_valence=-0.6,
            timestamp=datetime.now() - timedelta(hours=i)
        )
        tracker.record_action(action)

    patterns = tracker.detect_patterns()

    pattern_types = [p.pattern_type for p in patterns]
    assert PatternType.CONTROL_TAKING not in pattern_types

def test_pattern_weight_decay_over_time():
    tracker = PatternTracker(min_occurrences=3, decay_rate=0.1)

    old_timestamp = datetime.now() - timedelta(days=5)
    for i in range(4):
        action = PlayerAction(
            action_type=ActionType.CONFLICT_AVOID,
            context=ContextType.PRIVATE,
            emotional_valence=-0.5,
            timestamp=old_timestamp - timedelta(hours=i)
        )
        tracker.record_action(action)

    patterns = tracker.detect_patterns()

    weight = tracker.get_pattern_weight(PatternType.REPEATED_AVOIDANCE)

    expected_weight = (1.0 - 0.1) ** 5
    assert abs(weight - expected_weight) < 0.01

def test_pattern_removed_when_weight_too_low():
    tracker = PatternTracker(min_occurrences=3, decay_rate=0.3)

    old_timestamp = datetime.now() - timedelta(days=10)
    for i in range(4):
        action = PlayerAction(
            action_type=ActionType.CONFLICT_AVOID,
            context=ContextType.PRIVATE,
            emotional_valence=-0.5,
            timestamp=old_timestamp - timedelta(hours=i)
        )
        tracker.record_action(action)

    patterns = tracker.detect_patterns()

    weight = tracker.get_pattern_weight(PatternType.REPEATED_AVOIDANCE)
    assert weight < 0.1 or weight == 0.0

def test_positive_streak_breaks_pattern():
    tracker = PatternTracker(min_occurrences=3, break_threshold=5)

    for i in range(4):
        action = PlayerAction(
            action_type=ActionType.CONTROL_TAKING,
            context=ContextType.PRIVATE,
            emotional_valence=-0.6,
            timestamp=datetime.now() - timedelta(days=3-i)
        )
        tracker.record_action(action)

    patterns = tracker.detect_patterns()
    initial_weight = tracker.get_pattern_weight(PatternType.CONTROL_TAKING)
    assert initial_weight > 0

    for i in range(5):
        action = PlayerAction(
            action_type=ActionType.EMPATHY_SHOWN,
            context=ContextType.PRIVATE,
            emotional_valence=0.7,
            timestamp=datetime.now()
        )
        tracker.record_action(action)

    final_weight = tracker.get_pattern_weight(PatternType.CONTROL_TAKING)
    assert final_weight < initial_weight

def test_clear_history_removes_all_data():
    tracker = PatternTracker()

    for i in range(5):
        action = PlayerAction(
            action_type=ActionType.CONFLICT_AVOID,
            context=ContextType.PRIVATE,
            emotional_valence=-0.5,
            timestamp=datetime.now() - timedelta(hours=i)
        )
        tracker.record_action(action)

    patterns = tracker.detect_patterns()
    assert len(patterns) > 0

    tracker.clear_history()

    assert len(tracker.action_history) == 0
    assert len(tracker.detected_patterns) == 0
    assert tracker.positive_streak == 0

def test_clear_history_before_date():
    tracker = PatternTracker()

    for i in range(3):
        action = PlayerAction(
            action_type=ActionType.CONFLICT_AVOID,
            context=ContextType.PRIVATE,
            emotional_valence=-0.5,
            timestamp=datetime.now() - timedelta(days=10+i)
        )
        tracker.record_action(action)

    for i in range(3):
        action = PlayerAction(
            action_type=ActionType.EMPATHY_SHOWN,
            context=ContextType.PRIVATE,
            emotional_valence=0.6,
            timestamp=datetime.now() - timedelta(hours=i)
        )
        tracker.record_action(action)

    cutoff = datetime.now() - timedelta(days=5)
    tracker.clear_history(before_date=cutoff)

    assert len(tracker.action_history) == 3
    assert all(a.timestamp >= cutoff for a in tracker.action_history)

def test_serialization_roundtrip():
    tracker = PatternTracker()

    for i in range(4):
        action = PlayerAction(
            action_type=ActionType.PARENTING_PRESENT,
            context=ContextType.PRIVATE,
            emotional_valence=0.6,
            timestamp=datetime.now() - timedelta(hours=i)
        )
        tracker.record_action(action)

    patterns = tracker.detect_patterns()

    data = tracker.to_dict()

    restored = PatternTracker.from_dict(data)

    assert len(restored.action_history) == len(tracker.action_history)
    assert len(restored.detected_patterns) == len(tracker.detected_patterns)
    assert restored.positive_streak == tracker.positive_streak
    assert restored.time_window == tracker.time_window
    assert restored.min_occurrences == tracker.min_occurrences

def test_multiple_pattern_types_detected():
    tracker = PatternTracker(min_occurrences=3)

    for i in range(4):
        tracker.record_action(PlayerAction(
            action_type=ActionType.CONFLICT_AVOID,
            context=ContextType.PRIVATE,
            emotional_valence=-0.5,
            timestamp=datetime.now() - timedelta(hours=i*2)
        ))

        tracker.record_action(PlayerAction(
            action_type=ActionType.CONTROL_TAKING,
            context=ContextType.PRIVATE,
            emotional_valence=-0.6,
            timestamp=datetime.now() - timedelta(hours=i*2+1)
        ))

    patterns = tracker.detect_patterns()
    pattern_types = [p.pattern_type for p in patterns]

    assert PatternType.REPEATED_AVOIDANCE in pattern_types
    assert PatternType.CONTROL_TAKING in pattern_types
    assert len(patterns) >= 2

def test_pattern_frequency_calculation_accuracy():
    tracker = PatternTracker(time_window=timedelta(days=7), min_occurrences=3)

    for i in range(7):
        action = PlayerAction(
            action_type=ActionType.PARENTING_PRESENT,
            context=ContextType.PRIVATE,
            emotional_valence=0.6,
            timestamp=datetime.now() - timedelta(days=i)
        )
        tracker.record_action(action)

    patterns = tracker.detect_patterns()

    presence_pattern = next(
        (p for p in patterns if p.pattern_type == PatternType.CONSISTENT_PRESENCE),
        None
    )

    assert presence_pattern is not None
    assert abs(presence_pattern.frequency - 1.0) < 0.01

def test_break_pattern_explicitly():
    tracker = PatternTracker(min_occurrences=3)

    for i in range(4):
        action = PlayerAction(
            action_type=ActionType.CONFLICT_AVOID,
            context=ContextType.PRIVATE,
            emotional_valence=-0.5,
            timestamp=datetime.now() - timedelta(hours=i)
        )
        tracker.record_action(action)

    patterns = tracker.detect_patterns()
    initial_weight = tracker.get_pattern_weight(PatternType.REPEATED_AVOIDANCE)
    assert initial_weight > 0

    tracker.break_pattern(PatternType.REPEATED_AVOIDANCE)

    final_weight = tracker.get_pattern_weight(PatternType.REPEATED_AVOIDANCE)
    assert final_weight < initial_weight
