"""
Unit tests for PatternTracker edge cases.

Tests specific scenarios and boundary conditions.
"""
import pytest
from datetime import datetime, timedelta

from nurture.personality.pattern_tracker import PatternTracker
from nurture.core.data_structures import PlayerAction
from nurture.core.enums import ActionType, ContextType, PatternType


def test_empty_time_window():
    """Test pattern detection with no actions in time window."""
    tracker = PatternTracker()
    
    # Add old actions outside time window
    old_action = PlayerAction(
        action_type=ActionType.CONFLICT_AVOID,
        context=ContextType.PRIVATE,
        emotional_valence=-0.5,
        timestamp=datetime.now() - timedelta(days=30)
    )
    tracker.record_action(old_action)
    
    # Detect patterns with 7-day window
    patterns = tracker.detect_patterns()
    
    # Should not detect patterns from old actions
    assert len(patterns) == 0


def test_insufficient_data_exactly_two_actions():
    """Test that exactly 2 actions don't form a pattern (need 3)."""
    tracker = PatternTracker(min_occurrences=3)
    
    # Add exactly 2 actions
    for i in range(2):
        action = PlayerAction(
            action_type=ActionType.CONTROL_TAKING,
            context=ContextType.PRIVATE,
            emotional_valence=-0.6,
            timestamp=datetime.now() - timedelta(hours=i)
        )
        tracker.record_action(action)
    
    patterns = tracker.detect_patterns()
    
    # Should not detect pattern with only 2 occurrences
    pattern_types = [p.pattern_type for p in patterns]
    assert PatternType.CONTROL_TAKING not in pattern_types


def test_pattern_weight_decay_over_time():
    """Test that pattern weight decays correctly over multiple days."""
    tracker = PatternTracker(min_occurrences=3, decay_rate=0.1)
    
    # Create a pattern 5 days ago
    old_timestamp = datetime.now() - timedelta(days=5)
    for i in range(4):
        action = PlayerAction(
            action_type=ActionType.CONFLICT_AVOID,
            context=ContextType.PRIVATE,
            emotional_valence=-0.5,
            timestamp=old_timestamp - timedelta(hours=i)
        )
        tracker.record_action(action)
    
    # Detect patterns (applies decay)
    patterns = tracker.detect_patterns()
    
    # Get weight
    weight = tracker.get_pattern_weight(PatternType.REPEATED_AVOIDANCE)
    
    # Weight should be decayed: (1.0 - 0.1)^5 = 0.59049
    expected_weight = (1.0 - 0.1) ** 5
    assert abs(weight - expected_weight) < 0.01


def test_pattern_removed_when_weight_too_low():
    """Test that patterns are removed when weight drops below 0.1."""
    tracker = PatternTracker(min_occurrences=3, decay_rate=0.3)
    
    # Create a pattern 10 days ago (will decay heavily)
    old_timestamp = datetime.now() - timedelta(days=10)
    for i in range(4):
        action = PlayerAction(
            action_type=ActionType.CONFLICT_AVOID,
            context=ContextType.PRIVATE,
            emotional_valence=-0.5,
            timestamp=old_timestamp - timedelta(hours=i)
        )
        tracker.record_action(action)
    
    # Detect patterns (applies decay)
    patterns = tracker.detect_patterns()
    
    # Weight should be very low: (1.0 - 0.3)^10 = 0.0282
    # Pattern should be removed
    weight = tracker.get_pattern_weight(PatternType.REPEATED_AVOIDANCE)
    assert weight < 0.1 or weight == 0.0


def test_positive_streak_breaks_pattern():
    """Test that 5 consecutive positive actions break negative patterns."""
    tracker = PatternTracker(min_occurrences=3, break_threshold=5)
    
    # Establish negative pattern
    for i in range(4):
        action = PlayerAction(
            action_type=ActionType.CONTROL_TAKING,
            context=ContextType.PRIVATE,
            emotional_valence=-0.6,
            timestamp=datetime.now() - timedelta(days=3-i)
        )
        tracker.record_action(action)
    
    # Get initial weight
    patterns = tracker.detect_patterns()
    initial_weight = tracker.get_pattern_weight(PatternType.CONTROL_TAKING)
    assert initial_weight > 0
    
    # Add 5 positive actions
    for i in range(5):
        action = PlayerAction(
            action_type=ActionType.EMPATHY_SHOWN,
            context=ContextType.PRIVATE,
            emotional_valence=0.7,
            timestamp=datetime.now()
        )
        tracker.record_action(action)
    
    # Weight should be reduced
    final_weight = tracker.get_pattern_weight(PatternType.CONTROL_TAKING)
    assert final_weight < initial_weight


def test_clear_history_removes_all_data():
    """Test that clear_history removes all actions and patterns."""
    tracker = PatternTracker()
    
    # Add some actions
    for i in range(5):
        action = PlayerAction(
            action_type=ActionType.CONFLICT_AVOID,
            context=ContextType.PRIVATE,
            emotional_valence=-0.5,
            timestamp=datetime.now() - timedelta(hours=i)
        )
        tracker.record_action(action)
    
    # Detect patterns
    patterns = tracker.detect_patterns()
    assert len(patterns) > 0
    
    # Clear history
    tracker.clear_history()
    
    # Everything should be cleared
    assert len(tracker.action_history) == 0
    assert len(tracker.detected_patterns) == 0
    assert tracker.positive_streak == 0


def test_clear_history_before_date():
    """Test that clear_history can remove only old actions."""
    tracker = PatternTracker()
    
    # Add old actions
    for i in range(3):
        action = PlayerAction(
            action_type=ActionType.CONFLICT_AVOID,
            context=ContextType.PRIVATE,
            emotional_valence=-0.5,
            timestamp=datetime.now() - timedelta(days=10+i)
        )
        tracker.record_action(action)
    
    # Add recent actions
    for i in range(3):
        action = PlayerAction(
            action_type=ActionType.EMPATHY_SHOWN,
            context=ContextType.PRIVATE,
            emotional_valence=0.6,
            timestamp=datetime.now() - timedelta(hours=i)
        )
        tracker.record_action(action)
    
    # Clear actions older than 5 days
    cutoff = datetime.now() - timedelta(days=5)
    tracker.clear_history(before_date=cutoff)
    
    # Should only have recent actions
    assert len(tracker.action_history) == 3
    assert all(a.timestamp >= cutoff for a in tracker.action_history)


def test_serialization_roundtrip():
    """Test that tracker state can be serialized and restored."""
    tracker = PatternTracker()
    
    # Add some actions and detect patterns
    for i in range(4):
        action = PlayerAction(
            action_type=ActionType.PARENTING_PRESENT,
            context=ContextType.PRIVATE,
            emotional_valence=0.6,
            timestamp=datetime.now() - timedelta(hours=i)
        )
        tracker.record_action(action)
    
    patterns = tracker.detect_patterns()
    
    # Serialize
    data = tracker.to_dict()
    
    # Deserialize
    restored = PatternTracker.from_dict(data)
    
    # Verify state is preserved
    assert len(restored.action_history) == len(tracker.action_history)
    assert len(restored.detected_patterns) == len(tracker.detected_patterns)
    assert restored.positive_streak == tracker.positive_streak
    assert restored.time_window == tracker.time_window
    assert restored.min_occurrences == tracker.min_occurrences


def test_multiple_pattern_types_detected():
    """Test that multiple different patterns can be detected simultaneously."""
    tracker = PatternTracker(min_occurrences=3)
    
    # Add actions for multiple patterns
    for i in range(4):
        # Conflict avoidance pattern
        tracker.record_action(PlayerAction(
            action_type=ActionType.CONFLICT_AVOID,
            context=ContextType.PRIVATE,
            emotional_valence=-0.5,
            timestamp=datetime.now() - timedelta(hours=i*2)
        ))
        
        # Control taking pattern
        tracker.record_action(PlayerAction(
            action_type=ActionType.CONTROL_TAKING,
            context=ContextType.PRIVATE,
            emotional_valence=-0.6,
            timestamp=datetime.now() - timedelta(hours=i*2+1)
        ))
    
    patterns = tracker.detect_patterns()
    pattern_types = [p.pattern_type for p in patterns]
    
    # Should detect both patterns
    assert PatternType.REPEATED_AVOIDANCE in pattern_types
    assert PatternType.CONTROL_TAKING in pattern_types
    assert len(patterns) >= 2


def test_pattern_frequency_calculation_accuracy():
    """Test that pattern frequency is calculated correctly."""
    tracker = PatternTracker(time_window=timedelta(days=7), min_occurrences=3)
    
    # Add exactly 7 actions over 7 days (1 per day)
    for i in range(7):
        action = PlayerAction(
            action_type=ActionType.PARENTING_PRESENT,
            context=ContextType.PRIVATE,
            emotional_valence=0.6,
            timestamp=datetime.now() - timedelta(days=i)
        )
        tracker.record_action(action)
    
    patterns = tracker.detect_patterns()
    
    # Find the pattern
    presence_pattern = next(
        (p for p in patterns if p.pattern_type == PatternType.CONSISTENT_PRESENCE),
        None
    )
    
    assert presence_pattern is not None
    # Frequency should be 7 actions / 7 days = 1.0
    assert abs(presence_pattern.frequency - 1.0) < 0.01


def test_break_pattern_explicitly():
    """Test the explicit break_pattern method."""
    tracker = PatternTracker(min_occurrences=3)
    
    # Establish a pattern
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
    
    # Explicitly break the pattern
    tracker.break_pattern(PatternType.REPEATED_AVOIDANCE)
    
    # Weight should be reduced
    final_weight = tracker.get_pattern_weight(PatternType.REPEATED_AVOIDANCE)
    assert final_weight < initial_weight
