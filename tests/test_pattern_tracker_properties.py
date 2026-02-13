import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime, timedelta

from nurture.personality.pattern_tracker import PatternTracker
from nurture.core.data_structures import PlayerAction
from nurture.core.enums import ActionType, ContextType, PatternType

@st.composite
def player_action_strategy(draw, action_type=None, valence_range=(-1.0, 1.0)):
    if action_type is None:
        action_type = draw(st.sampled_from(list(ActionType)))

    return PlayerAction(
        action_type=action_type,
        context=draw(st.sampled_from(list(ContextType))),
        emotional_valence=draw(st.floats(min_value=valence_range[0], max_value=valence_range[1])),
        timestamp=datetime.now() - timedelta(days=draw(st.integers(min_value=0, max_value=6))),
        metadata={}
    )

@given(st.lists(player_action_strategy(), min_size=1, max_size=20))
def test_pattern_tracking_completeness(actions):
    tracker = PatternTracker()

    for action in actions:
        tracker.record_action(action)

    assert len(tracker.action_history) == len(actions)

    for i, action in enumerate(actions):
        stored_action = tracker.action_history[i]
        assert stored_action.action_type == action.action_type
        assert stored_action.context == action.context
        assert abs(stored_action.emotional_valence - action.emotional_valence) < 0.0001
        assert stored_action.timestamp is not None

@given(st.integers(min_value=1, max_value=7))
def test_pattern_based_trust_impact(num_repetitions):
    tracker = PatternTracker(min_occurrences=3)

    for i in range(num_repetitions):
        action = PlayerAction(
            action_type=ActionType.CONFLICT_AVOID,
            context=ContextType.PRIVATE,
            emotional_valence=-0.5,
            timestamp=datetime.now() - timedelta(days=i)
        )
        tracker.record_action(action)

    patterns = tracker.detect_patterns()

    if num_repetitions >= 3:
        assert len(patterns) > 0

        pattern_types = [p.pattern_type for p in patterns]
        assert PatternType.REPEATED_AVOIDANCE in pattern_types

        avoidance_pattern = next(p for p in patterns if p.pattern_type == PatternType.REPEATED_AVOIDANCE)
        assert avoidance_pattern.frequency > 0
        assert len(avoidance_pattern.occurrences) == num_repetitions
    else:
        pattern_types = [p.pattern_type for p in patterns]
        assert PatternType.REPEATED_AVOIDANCE not in pattern_types

@given(st.integers(min_value=5, max_value=10))
def test_pattern_weight_decay(num_positive_actions):
    tracker = PatternTracker(min_occurrences=3, break_threshold=5)

    for i in range(4):
        action = PlayerAction(
            action_type=ActionType.CONTROL_TAKING,
            context=ContextType.PRIVATE,
            emotional_valence=-0.6,
            timestamp=datetime.now() - timedelta(days=6-i)
        )
        tracker.record_action(action)

    patterns = tracker.detect_patterns()
    assert len(patterns) > 0

    initial_weight = tracker.get_pattern_weight(PatternType.CONTROL_TAKING)
    assert initial_weight > 0

    for i in range(num_positive_actions):
        action = PlayerAction(
            action_type=ActionType.EMPATHY_SHOWN,
            context=ContextType.PRIVATE,
            emotional_valence=0.7,
            timestamp=datetime.now()
        )
        tracker.record_action(action)

    if num_positive_actions >= 5:
        final_weight = tracker.get_pattern_weight(PatternType.CONTROL_TAKING)
        assert final_weight < initial_weight

@given(st.lists(player_action_strategy(), min_size=0, max_size=2))
def test_insufficient_data_no_patterns(actions):
    tracker = PatternTracker(min_occurrences=3)

    for action in actions:
        tracker.record_action(action)

    patterns = tracker.detect_patterns()

    assert all(len(p.occurrences) >= 3 for p in patterns)

@given(st.integers(min_value=1, max_value=30))
def test_temporal_decay_reduces_weight(days_old):
    tracker = PatternTracker(min_occurrences=3, decay_rate=0.1)

    old_timestamp = datetime.now() - timedelta(days=days_old)
    for i in range(4):
        action = PlayerAction(
            action_type=ActionType.CONFLICT_AVOID,
            context=ContextType.PRIVATE,
            emotional_valence=-0.5,
            timestamp=old_timestamp - timedelta(hours=i)
        )
        tracker.record_action(action)

    patterns = tracker.detect_patterns()

    if days_old <= 7:
        pattern_types = [p.pattern_type for p in patterns]
        if PatternType.REPEATED_AVOIDANCE in pattern_types:
            weight = tracker.get_pattern_weight(PatternType.REPEATED_AVOIDANCE)

            expected_max_weight = (1.0 - 0.1) ** days_old
            assert weight <= expected_max_weight + 0.01

@given(st.integers(min_value=3, max_value=10))
def test_pattern_frequency_calculation(num_actions):
    tracker = PatternTracker(time_window=timedelta(days=7), min_occurrences=3)

    for i in range(num_actions):
        action = PlayerAction(
            action_type=ActionType.PARENTING_PRESENT,
            context=ContextType.PRIVATE,
            emotional_valence=0.6,
            timestamp=datetime.now() - timedelta(days=i % 7)
        )
        tracker.record_action(action)

    patterns = tracker.detect_patterns()

    if num_actions >= 3:
        pattern_types = [p.pattern_type for p in patterns]
        if PatternType.CONSISTENT_PRESENCE in pattern_types:
            pattern = next(p for p in patterns if p.pattern_type == PatternType.CONSISTENT_PRESENCE)

            expected_frequency = num_actions / 7.0
            assert abs(pattern.frequency - expected_frequency) < 0.2
