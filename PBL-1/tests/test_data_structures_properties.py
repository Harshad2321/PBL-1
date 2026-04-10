"""
Property-based tests for Mother AI data structures.

Tests that all data structures can be serialized and deserialized
without data loss, validating complete state persistence.
"""
import pytest
from hypothesis import given, strategies as st
from datetime import datetime, timedelta

from nurture.core.data_structures import (
    PlayerAction, BehaviorPattern, EmotionalImpact, EmotionalMemory,
    ResponseModifiers, RelationshipMetrics
)
from nurture.core.enums import (
    ActionType, ContextType, ContextCategory, PatternType,
    EmotionType, WithdrawalLevel
)


# Hypothesis strategies for generating test data
@st.composite
def player_action_strategy(draw):
    """Generate random PlayerAction instances."""
    return PlayerAction(
        action_type=draw(st.sampled_from(list(ActionType))),
        context=draw(st.sampled_from(list(ContextType))),
        emotional_valence=draw(st.floats(min_value=-1.0, max_value=1.0)),
        timestamp=datetime.now() - timedelta(days=draw(st.integers(min_value=0, max_value=30))),
        metadata=draw(st.dictionaries(st.text(min_size=1, max_size=10), st.text(min_size=1, max_size=20), max_size=3))
    )


@st.composite
def behavior_pattern_strategy(draw):
    """Generate random BehaviorPattern instances."""
    num_occurrences = draw(st.integers(min_value=0, max_value=10))
    occurrences = [draw(player_action_strategy()) for _ in range(num_occurrences)]
    
    return BehaviorPattern(
        pattern_type=draw(st.sampled_from(list(PatternType))),
        occurrences=occurrences,
        frequency=draw(st.floats(min_value=0.0, max_value=10.0)),
        weight=draw(st.floats(min_value=0.0, max_value=1.0)),
        first_seen=datetime.now() - timedelta(days=draw(st.integers(min_value=1, max_value=30))),
        last_seen=datetime.now() - timedelta(days=draw(st.integers(min_value=0, max_value=5)))
    )


@st.composite
def emotional_impact_strategy(draw):
    """Generate random EmotionalImpact instances."""
    return EmotionalImpact(
        primary_emotion=draw(st.sampled_from(list(EmotionType))),
        intensity=draw(st.floats(min_value=0.0, max_value=1.0)),
        valence=draw(st.floats(min_value=-1.0, max_value=1.0)),
        context_category=draw(st.sampled_from(list(ContextCategory)))
    )


@st.composite
def emotional_memory_strategy(draw):
    """Generate random EmotionalMemory instances."""
    num_patterns = draw(st.integers(min_value=0, max_value=5))
    patterns = [draw(st.sampled_from(list(PatternType))) for _ in range(num_patterns)]
    
    return EmotionalMemory(
        emotional_impact=draw(emotional_impact_strategy()),
        timestamp=datetime.now() - timedelta(days=draw(st.integers(min_value=0, max_value=30))),
        context=draw(st.sampled_from(list(ContextType))),
        weight=draw(st.floats(min_value=0.0, max_value=1.0)),
        associated_patterns=patterns
    )


@st.composite
def response_modifiers_strategy(draw):
    """Generate random ResponseModifiers instances."""
    return ResponseModifiers(
        response_length_multiplier=draw(st.floats(min_value=0.3, max_value=1.0)),
        initiation_probability=draw(st.floats(min_value=0.0, max_value=1.0)),
        cooperation_level=draw(st.floats(min_value=0.0, max_value=1.0)),
        emotional_vulnerability=draw(st.floats(min_value=0.0, max_value=1.0)),
        interpretation_bias=draw(st.floats(min_value=-1.0, max_value=1.0))
    )


@st.composite
def relationship_metrics_strategy(draw):
    """Generate random RelationshipMetrics instances."""
    return RelationshipMetrics(
        trust_score=draw(st.floats(min_value=0.0, max_value=100.0)),
        resentment_score=draw(st.floats(min_value=0.0, max_value=100.0)),
        emotional_safety=draw(st.floats(min_value=0.0, max_value=100.0)),
        parenting_unity=draw(st.floats(min_value=0.0, max_value=100.0)),
        player_reliability=draw(st.floats(min_value=0.0, max_value=1.0)),
        cooperation_level=draw(st.floats(min_value=0.0, max_value=1.0)),
        last_updated=datetime.now() - timedelta(days=draw(st.integers(min_value=0, max_value=30)))
    )


# Property 46: Complete state persistence
# Validates: Requirements 15.1, 15.3

@given(player_action_strategy())
def test_player_action_serialization_roundtrip(action):
    """
    Property: For any PlayerAction, serialization followed by deserialization
    should produce an equivalent object.
    
    Validates Requirements 15.1, 15.3: State persistence and consistency.
    """
    # Serialize
    serialized = action.to_dict()
    
    # Deserialize
    restored = PlayerAction.from_dict(serialized)
    
    # Verify equivalence
    assert restored.action_type == action.action_type
    assert restored.context == action.context
    assert abs(restored.emotional_valence - action.emotional_valence) < 0.0001
    assert restored.metadata == action.metadata
    # Timestamps may have microsecond differences, check within 1 second
    assert abs((restored.timestamp - action.timestamp).total_seconds()) < 1.0


@given(behavior_pattern_strategy())
def test_behavior_pattern_serialization_roundtrip(pattern):
    """
    Property: For any BehaviorPattern, serialization followed by deserialization
    should produce an equivalent object.
    
    Validates Requirements 15.1, 15.3: State persistence and consistency.
    """
    # Serialize
    serialized = pattern.to_dict()
    
    # Deserialize
    restored = BehaviorPattern.from_dict(serialized)
    
    # Verify equivalence
    assert restored.pattern_type == pattern.pattern_type
    assert len(restored.occurrences) == len(pattern.occurrences)
    assert abs(restored.frequency - pattern.frequency) < 0.0001
    assert abs(restored.weight - pattern.weight) < 0.0001
    assert abs((restored.first_seen - pattern.first_seen).total_seconds()) < 1.0
    assert abs((restored.last_seen - pattern.last_seen).total_seconds()) < 1.0


@given(emotional_impact_strategy())
def test_emotional_impact_serialization_roundtrip(impact):
    """
    Property: For any EmotionalImpact, serialization followed by deserialization
    should produce an equivalent object.
    
    Validates Requirements 15.1, 15.3: State persistence and consistency.
    """
    # Serialize
    serialized = impact.to_dict()
    
    # Deserialize
    restored = EmotionalImpact.from_dict(serialized)
    
    # Verify equivalence
    assert restored.primary_emotion == impact.primary_emotion
    assert abs(restored.intensity - impact.intensity) < 0.0001
    assert abs(restored.valence - impact.valence) < 0.0001
    assert restored.context_category == impact.context_category


@given(emotional_memory_strategy())
def test_emotional_memory_serialization_roundtrip(memory):
    """
    Property: For any EmotionalMemory, serialization followed by deserialization
    should produce an equivalent object.
    
    Validates Requirements 15.1, 15.3: State persistence and consistency.
    """
    # Serialize
    serialized = memory.to_dict()
    
    # Deserialize
    restored = EmotionalMemory.from_dict(serialized)
    
    # Verify equivalence
    assert restored.emotional_impact.primary_emotion == memory.emotional_impact.primary_emotion
    assert restored.context == memory.context
    assert abs(restored.weight - memory.weight) < 0.0001
    assert restored.associated_patterns == memory.associated_patterns
    assert abs((restored.timestamp - memory.timestamp).total_seconds()) < 1.0


@given(response_modifiers_strategy())
def test_response_modifiers_serialization_roundtrip(modifiers):
    """
    Property: For any ResponseModifiers, serialization followed by deserialization
    should produce an equivalent object.
    
    Validates Requirements 15.1, 15.3: State persistence and consistency.
    """
    # Serialize
    serialized = modifiers.to_dict()
    
    # Deserialize
    restored = ResponseModifiers.from_dict(serialized)
    
    # Verify equivalence
    assert abs(restored.response_length_multiplier - modifiers.response_length_multiplier) < 0.0001
    assert abs(restored.initiation_probability - modifiers.initiation_probability) < 0.0001
    assert abs(restored.cooperation_level - modifiers.cooperation_level) < 0.0001
    assert abs(restored.emotional_vulnerability - modifiers.emotional_vulnerability) < 0.0001
    assert abs(restored.interpretation_bias - modifiers.interpretation_bias) < 0.0001


@given(relationship_metrics_strategy())
def test_relationship_metrics_serialization_roundtrip(metrics):
    """
    Property: For any RelationshipMetrics, serialization followed by deserialization
    should produce an equivalent object.
    
    Validates Requirements 15.1, 15.3: State persistence and consistency.
    """
    # Serialize
    serialized = metrics.to_dict()
    
    # Deserialize
    restored = RelationshipMetrics.from_dict(serialized)
    
    # Verify equivalence
    assert abs(restored.trust_score - metrics.trust_score) < 0.0001
    assert abs(restored.resentment_score - metrics.resentment_score) < 0.0001
    assert abs(restored.emotional_safety - metrics.emotional_safety) < 0.0001
    assert abs(restored.parenting_unity - metrics.parenting_unity) < 0.0001
    assert abs(restored.player_reliability - metrics.player_reliability) < 0.0001
    assert abs(restored.cooperation_level - metrics.cooperation_level) < 0.0001
    assert abs((restored.last_updated - metrics.last_updated).total_seconds()) < 1.0
