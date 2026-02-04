"""
Property-based tests for PatternTracker.

Tests pattern detection, weight decay, and pattern-based trust impact.
"""
import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime, timedelta

from nurture.personality.pattern_tracker import PatternTracker
from nurture.core.data_structures import PlayerAction
from nurture.core.enums import ActionType, ContextType, PatternType


# Hypothesis strategies
@st.composite
def player_action_strategy(draw, action_type=None, valence_range=(-1.0, 1.0)):
    """Generate random PlayerAction instances."""
    if action_type is None:
        action_type = draw(st.sampled_from(list(ActionType)))
    
    return PlayerAction(
        action_type=action_type,
        context=draw(st.sampled_from(list(ContextType))),
        emotional_valence=draw(st.floats(min_value=valence_range[0], max_value=valence_range[1])),
        timestamp=datetime.now() - timedelta(days=draw(st.integers(min_value=0, max_value=6))),
        metadata={}
    )


# Property 3: Pattern tracking completeness
# Validates: Requirements 1.4

@given(st.lists(player_action_strategy(), min_size=1, max_size=20))
def test_pattern_tracking_completeness(actions):
    """
    Property: For any player action recorded, the system should store it
    with a timestamp and make it available for pattern detection queries.
    
    Validates Requirements 1.4: Pattern tracking completeness.
    """
    tracker = PatternTracker()
    
    # Record all actions
    for action in actions:
        tracker.record_action(action)
    
    # Verify all actions are stored
    assert len(tracker.action_history) == len(actions)
    
    # Verify each action is retrievable
    for i, action in enumerate(actions):
        stored_action = tracker.action_history[i]
        assert stored_action.action_type == action.action_type
        assert stored_action.context == action.context
        assert abs(stored_action.emotional_valence - action.emotional_valence) < 0.0001
        assert stored_action.timestamp is not None


# Property 1: Pattern-based trust impact
# Validates: Requirements 1.1, 1.2, 1.3

@given(st.integers(min_value=1, max_value=7))
def test_pattern_based_trust_impact(num_repetitions):
    """
    Property: For any sequence of player actions, the trust score change
    should be proportional to pattern frequency rather than individual
    action count, where repeated negative actions within a time window
    decrease trust more than isolated incidents.
    
    Validates Requirements 1.1, 1.2, 1.3: Pattern-based response.
    """
    tracker = PatternTracker(min_occurrences=3)
    
    # Create repeated negative actions (conflict avoidance) within time window
    for i in range(num_repetitions):
        action = PlayerAction(
            action_type=ActionType.CONFLICT_AVOID,
            context=ContextType.PRIVATE,
            emotional_valence=-0.5,
            timestamp=datetime.now() - timedelta(days=i)
        )
        tracker.record_action(action)
    
    # Detect patterns
    patterns = tracker.detect_patterns()
    
    if num_repetitions >= 3:
        # Should detect a pattern
        assert len(patterns) > 0
        
        # Pattern should be REPEATED_AVOIDANCE
        pattern_types = [p.pattern_type for p in patterns]
        assert PatternType.REPEATED_AVOIDANCE in pattern_types
        
        # Pattern frequency should be proportional to repetitions
        avoidance_pattern = next(p for p in patterns if p.pattern_type == PatternType.REPEATED_AVOIDANCE)
        assert avoidance_pattern.frequency > 0
        # All actions should be within the 7-day window
        assert len(avoidance_pattern.occurrences) == num_repetitions
    else:
        # Should not detect a pattern with < 3 occurrences
        pattern_types = [p.pattern_type for p in patterns]
        assert PatternType.REPEATED_AVOIDANCE not in pattern_types


# Property 2: Pattern weight decay
# Validates: Requirements 1.5

@given(st.integers(min_value=5, max_value=10))
def test_pattern_weight_decay(num_positive_actions):
    """
    Property: For any established negative behavioral pattern, introducing
    consistent positive behavior should reduce the pattern's weight over time,
    with weight decreasing by at least 10% per day without pattern recurrence.
    
    Validates Requirements 1.5: Pattern weight decay.
    """
    tracker = PatternTracker(min_occurrences=3, break_threshold=5)
    
    # Establish a negative pattern (control taking)
    for i in range(4):
        action = PlayerAction(
            action_type=ActionType.CONTROL_TAKING,
            context=ContextType.PRIVATE,
            emotional_valence=-0.6,
            timestamp=datetime.now() - timedelta(days=6-i)
        )
        tracker.record_action(action)
    
    # Detect the pattern
    patterns = tracker.detect_patterns()
    assert len(patterns) > 0
    
    # Get initial weight
    initial_weight = tracker.get_pattern_weight(PatternType.CONTROL_TAKING)
    assert initial_weight > 0
    
    # Introduce positive actions
    for i in range(num_positive_actions):
        action = PlayerAction(
            action_type=ActionType.EMPATHY_SHOWN,
            context=ContextType.PRIVATE,
            emotional_valence=0.7,
            timestamp=datetime.now()
        )
        tracker.record_action(action)
    
    # Weight should decrease after positive streak
    if num_positive_actions >= 5:
        final_weight = tracker.get_pattern_weight(PatternType.CONTROL_TAKING)
        assert final_weight < initial_weight


# Additional property tests for edge cases

@given(st.lists(player_action_strategy(), min_size=0, max_size=2))
def test_insufficient_data_no_patterns(actions):
    """
    Property: With fewer than min_occurrences actions of the same type,
    no pattern should be detected.
    """
    tracker = PatternTracker(min_occurrences=3)
    
    for action in actions:
        tracker.record_action(action)
    
    patterns = tracker.detect_patterns()
    
    # Should not detect patterns with insufficient data
    assert all(len(p.occurrences) >= 3 for p in patterns)


@given(st.integers(min_value=1, max_value=30))
def test_temporal_decay_reduces_weight(days_old):
    """
    Property: Patterns that haven't occurred recently should have
    reduced weight due to temporal decay.
    """
    tracker = PatternTracker(min_occurrences=3, decay_rate=0.1)
    
    # Create a pattern in the past
    old_timestamp = datetime.now() - timedelta(days=days_old)
    for i in range(4):
        action = PlayerAction(
            action_type=ActionType.CONFLICT_AVOID,
            context=ContextType.PRIVATE,
            emotional_valence=-0.5,
            timestamp=old_timestamp - timedelta(hours=i)
        )
        tracker.record_action(action)
    
    # Detect patterns (this applies temporal decay)
    patterns = tracker.detect_patterns()
    
    if days_old <= 7:
        # Pattern should still be detected within time window
        pattern_types = [p.pattern_type for p in patterns]
        if PatternType.REPEATED_AVOIDANCE in pattern_types:
            weight = tracker.get_pattern_weight(PatternType.REPEATED_AVOIDANCE)
            
            # Weight should decay exponentially with time
            expected_max_weight = (1.0 - 0.1) ** days_old
            assert weight <= expected_max_weight + 0.01  # Small tolerance for floating point


@given(st.integers(min_value=3, max_value=10))
def test_pattern_frequency_calculation(num_actions):
    """
    Property: Pattern frequency should be calculated as actions per day
    within the time window.
    """
    tracker = PatternTracker(time_window=timedelta(days=7), min_occurrences=3)
    
    # Create actions spread over 7 days
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
            
            # Frequency should be approximately num_actions / 7 days
            expected_frequency = num_actions / 7.0
            assert abs(pattern.frequency - expected_frequency) < 0.2  # Allow some tolerance
