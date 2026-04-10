"""
Property-based tests for TrustDynamicsEngine.

Tests asymmetric trust dynamics, diminishing returns, withdrawal states,
resentment accumulation, and apology effectiveness.
"""
import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime, timedelta

from nurture.personality.trust_dynamics import TrustDynamicsEngine
from nurture.core.enums import ContextType, WithdrawalLevel, ActionType


# Property 8: Asymmetric trust dynamics
# Validates: Requirements 3.1, 3.2

@given(
    magnitude=st.floats(min_value=1.0, max_value=5.0)
)
def test_asymmetric_trust_dynamics(magnitude):
    """
    Property: Trust erosion should be approximately 2x faster than trust building.
    Using BASE_TRUST_INCREASE (+2.0) vs BASE_TRUST_DECREASE (-4.0).
    
    **Validates: Requirements 3.1, 3.2**
    """
    engine = TrustDynamicsEngine(initial_trust=60.0)
    
    # Apply positive change using BASE_TRUST_INCREASE
    positive_change = engine.update_trust(TrustDynamicsEngine.BASE_TRUST_INCREASE)
    
    # Reset
    engine2 = TrustDynamicsEngine(initial_trust=60.0)
    
    # Apply negative change using BASE_TRUST_DECREASE
    negative_change = engine2.update_trust(-TrustDynamicsEngine.BASE_TRUST_DECREASE)
    
    # Negative should have ~2x impact
    ratio = abs(negative_change) / abs(positive_change)
    assert 1.8 <= ratio <= 2.2, f"Expected ~2x ratio, got {ratio} (positive: {positive_change}, negative: {negative_change})"


# Property 9: Diminishing returns on rapid positive actions
# Validates: Requirements 3.3

@given(st.integers(min_value=2, max_value=10))
def test_diminishing_returns_on_rapid_positive_actions(num_actions):
    """
    Property: For any sequence of positive actions occurring within a 1-hour window,
    each subsequent action should have reduced effectiveness, with the second and
    later actions having at most 50% of the first action's trust impact.
    
    **Validates: Requirements 3.3**
    """
    engine = TrustDynamicsEngine(initial_trust=60.0)
    
    base_time = datetime.now()
    changes = []
    
    # Perform rapid positive actions within 1-hour window
    for i in range(num_actions):
        timestamp = base_time + timedelta(minutes=i * 5)  # 5 minutes apart
        change = engine.update_trust(2.0, timestamp=timestamp)
        changes.append(change)
    
    # First action should have full impact
    assert changes[0] > 0
    
    # Subsequent actions should have reduced impact (50% or less)
    for i in range(1, len(changes)):
        assert changes[i] <= changes[0] * 0.5 + 0.01  # Small tolerance


# Property 10: Withdrawal state transition
# Validates: Requirements 3.4

@given(st.floats(min_value=0.0, max_value=100.0))
def test_withdrawal_state_transition(trust_score):
    """
    Property: For any trust score that falls below 50.0, the system should
    enter withdrawal state, and for any trust score that rises above 50.0
    from withdrawal, the system should exit withdrawal state.
    
    **Validates: Requirements 3.4**
    """
    engine = TrustDynamicsEngine(initial_trust=trust_score)
    
    if trust_score < 50.0:
        assert engine.is_in_withdrawal() is True
        assert engine.get_withdrawal_level() != WithdrawalLevel.NONE
    else:
        assert engine.is_in_withdrawal() is False
        assert engine.get_withdrawal_level() == WithdrawalLevel.NONE


# Property 11: High trust resilience
# Validates: Requirements 3.5

@given(negative_delta=st.floats(min_value=-5.0, max_value=-1.0))
def test_high_trust_resilience(negative_delta):
    """
    Property: For any negative interaction occurring when trust score is above 70.0,
    the trust decrease should be reduced by at least 30% compared to the same
    interaction at lower trust levels.
    
    **Validates: Requirements 3.5**
    """
    # High trust scenario
    high_trust_engine = TrustDynamicsEngine(initial_trust=75.0)
    high_trust_change = high_trust_engine.update_trust(negative_delta)
    
    # Low trust scenario
    low_trust_engine = TrustDynamicsEngine(initial_trust=50.0)
    low_trust_change = low_trust_engine.update_trust(negative_delta)
    
    # High trust should have less negative impact
    assert abs(high_trust_change) < abs(low_trust_change)
    
    # Should be reduced by at least 30%
    reduction_ratio = abs(high_trust_change) / abs(low_trust_change)
    assert reduction_ratio <= 0.7 + 0.05  # 70% or less (with small tolerance)


# Property 12: Pattern-based resentment accumulation
# Validates: Requirements 4.1

@given(st.integers(min_value=1, max_value=10))
def test_pattern_based_resentment_accumulation(num_incidents):
    """
    Property: For any detected negative behavioral pattern, resentment score
    should increase more than for isolated negative actions, with pattern-based
    increases being at least 5x larger than single-incident increases.
    
    **Validates: Requirements 4.1**
    """
    # Pattern-based resentment
    pattern_engine = TrustDynamicsEngine()
    pattern_changes = []
    for _ in range(num_incidents):
        change = pattern_engine.update_resentment(delta=1.0, is_pattern=True)
        pattern_changes.append(change)
    
    # Single incident resentment
    single_engine = TrustDynamicsEngine()
    single_changes = []
    for _ in range(num_incidents):
        change = single_engine.update_resentment(delta=1.0, is_pattern=False)
        single_changes.append(change)
    
    # Pattern should accumulate much faster (at least 5x)
    total_pattern = sum(pattern_changes)
    total_single = sum(single_changes)
    
    if total_single > 0:
        ratio = total_pattern / total_single
        assert ratio >= 5.0, f"Expected at least 5x ratio, got {ratio}"


# Property 14: Slow resentment decay
# Validates: Requirements 4.4

@given(days=st.floats(min_value=1.0, max_value=30.0))
def test_slow_resentment_decay(days):
    """
    Property: For any sustained positive behavioral pattern, resentment score
    should decrease at a rate significantly slower than trust score increases,
    with resentment decay being at most 25% of trust increase rate.
    
    **Validates: Requirements 4.4**
    """
    engine = TrustDynamicsEngine(initial_resentment=50.0, initial_trust=60.0)
    
    # Track trust increases
    trust_before = engine.get_trust_score()
    engine.update_trust(2.0)  # Positive action
    trust_increase = engine.get_trust_score() - trust_before
    
    # Apply resentment decay
    resentment_before = engine.get_resentment_score()
    resentment_decay = engine.apply_resentment_decay(days_elapsed=days)
    
    # Resentment decay rate should be much slower
    # Trust increases at 2.0 per action, resentment decays at 0.5 per day
    # So resentment decay should be at most 25% of trust increase rate
    if trust_increase > 0:
        decay_per_day = resentment_decay / days
        assert decay_per_day <= trust_increase * 0.25 + 0.1  # Small tolerance


# Property 15: Resentment impact on trust recovery
# Validates: Requirements 4.5

@given(positive_delta=st.floats(min_value=1.0, max_value=5.0))
def test_resentment_impact_on_trust_recovery(positive_delta):
    """
    Property: For any trust recovery attempt when resentment score exceeds 50.0,
    the trust increase should be reduced by at least 50% compared to the same
    actions at low resentment.
    
    **Validates: Requirements 4.5**
    """
    # High resentment scenario
    high_resentment_engine = TrustDynamicsEngine(initial_trust=40.0, initial_resentment=60.0)
    high_resentment_change = high_resentment_engine.update_trust(positive_delta)
    
    # Low resentment scenario
    low_resentment_engine = TrustDynamicsEngine(initial_trust=40.0, initial_resentment=20.0)
    low_resentment_change = low_resentment_engine.update_trust(positive_delta)
    
    # High resentment should reduce trust recovery
    assert high_resentment_change < low_resentment_change
    
    # Should be reduced by at least 50%
    if low_resentment_change > 0:
        ratio = high_resentment_change / low_resentment_change
        assert ratio <= 0.5 + 0.05  # 50% or less (with small tolerance)


# Property 18: Apology tracking
# Validates: Requirements 6.1

@given(
    behavior_type=st.sampled_from([
        ActionType.CONFLICT_AVOID,
        ActionType.CONTROL_TAKING,
        ActionType.PARENTING_ABSENT
    ])
)
def test_apology_tracking(behavior_type):
    """
    Property: For any apology action, the system should record the apology
    with its associated behavior type and timestamp.
    
    **Validates: Requirements 6.1**
    """
    engine = TrustDynamicsEngine()
    
    # Record apology
    engine.record_apology(behavior_type, apology_type="genuine")
    
    # Should be tracked
    assert behavior_type in engine.apology_records
    assert engine.apology_records[behavior_type].behavior_type == behavior_type
    assert engine.apology_records[behavior_type].timestamp is not None


# Property 19: Apology effectiveness decay
# Validates: Requirements 6.2, 6.3

@given(
    behavior_type=st.sampled_from([ActionType.CONFLICT_AVOID, ActionType.CONTROL_TAKING]),
    num_recurrences=st.integers(min_value=1, max_value=5)
)
def test_apology_effectiveness_decay(behavior_type, num_recurrences):
    """
    Property: For any behavior type, if the player apologizes for that behavior
    and then repeats it, the apology effectiveness for that behavior type should
    decrease by at least 0.2, with a minimum effectiveness of 0.1.
    
    **Validates: Requirements 6.2, 6.3**
    """
    engine = TrustDynamicsEngine()
    
    # Record initial apology
    engine.record_apology(behavior_type, apology_type="genuine")
    initial_effectiveness = engine.get_apology_effectiveness(behavior_type)
    
    # Record recurrences
    for _ in range(num_recurrences):
        engine.record_behavior_recurrence(behavior_type)
    
    # Check effectiveness decay
    final_effectiveness = engine.get_apology_effectiveness(behavior_type)
    
    # Should have decayed
    assert final_effectiveness < initial_effectiveness
    
    # Should not go below minimum
    assert final_effectiveness >= 0.1
    
    # Should decay by at least 0.2 per recurrence (up to minimum)
    expected_decay = min(initial_effectiveness - 0.1, num_recurrences * 0.2)
    actual_decay = initial_effectiveness - final_effectiveness
    assert actual_decay >= expected_decay - 0.05  # Small tolerance


# Property 20: Apology effectiveness recovery
# Validates: Requirements 6.4

@given(weeks_elapsed=st.integers(min_value=1, max_value=10))
def test_apology_effectiveness_recovery(weeks_elapsed):
    """
    Property: For any behavior type with reduced apology effectiveness,
    sustained behavioral change (no recurrence for 7+ days) should gradually
    restore effectiveness at a rate of approximately 0.1 per week.
    
    **Validates: Requirements 6.4**
    """
    engine = TrustDynamicsEngine()
    behavior_type = ActionType.CONFLICT_AVOID
    
    # Record apology and recurrence to reduce effectiveness
    engine.record_apology(behavior_type)
    engine.record_behavior_recurrence(behavior_type)
    
    reduced_effectiveness = engine.get_apology_effectiveness(behavior_type)
    
    # Simulate time passing without recurrence
    past_time = datetime.now() - timedelta(weeks=weeks_elapsed)
    engine.apology_records[behavior_type].last_recurrence = past_time
    
    # Check recovery
    recovered_effectiveness = engine.get_apology_effectiveness(behavior_type)
    
    # Should have recovered
    if weeks_elapsed >= 1:
        assert recovered_effectiveness > reduced_effectiveness
        
        # Recovery should be approximately 0.1 per week
        expected_recovery = min(0.1 * weeks_elapsed, 1.0 - reduced_effectiveness)
        actual_recovery = recovered_effectiveness - reduced_effectiveness
        assert abs(actual_recovery - expected_recovery) < 0.15  # Tolerance


# Property 21: Apology type differentiation
# Validates: Requirements 6.5

@given(st.sampled_from(["defensive", "generic", "genuine", "action_oriented"]))
def test_apology_type_differentiation(apology_type):
    """
    Property: For any set of different apology types (defensive, genuine,
    action-oriented), the trust impact should vary according to type, with
    action-oriented apologies having at least 3x the impact of defensive apologies.
    
    **Validates: Requirements 6.5**
    """
    engine = TrustDynamicsEngine()
    behavior_type = ActionType.CONFLICT_AVOID
    
    # Get effectiveness for this apology type
    effectiveness = engine.get_apology_effectiveness(behavior_type, apology_type)
    
    # Check expected ranges
    if apology_type == "defensive":
        assert 0.25 <= effectiveness <= 0.35
    elif apology_type == "generic":
        assert 0.45 <= effectiveness <= 0.55
    elif apology_type == "genuine":
        assert 0.95 <= effectiveness <= 1.05
    elif apology_type == "action_oriented":
        assert 1.45 <= effectiveness <= 1.55
    
    # Verify action-oriented is at least 3x defensive
    defensive_effectiveness = engine.get_apology_effectiveness(behavior_type, "defensive")
    action_effectiveness = engine.get_apology_effectiveness(behavior_type, "action_oriented")
    
    ratio = action_effectiveness / defensive_effectiveness
    assert ratio >= 3.0, f"Expected at least 3x ratio, got {ratio}"


# Additional property tests for edge cases

@given(st.floats(min_value=-10.0, max_value=10.0))
def test_trust_score_clamping(delta):
    """
    Property: Trust score should always stay within valid range [0.0, 100.0].
    """
    # Test at boundaries
    engine_low = TrustDynamicsEngine(initial_trust=5.0)
    engine_low.update_trust(delta)
    assert 0.0 <= engine_low.get_trust_score() <= 100.0
    
    engine_high = TrustDynamicsEngine(initial_trust=95.0)
    engine_high.update_trust(delta)
    assert 0.0 <= engine_high.get_trust_score() <= 100.0


@given(st.floats(min_value=-10.0, max_value=10.0))
def test_resentment_score_clamping(delta):
    """
    Property: Resentment score should always stay within valid range [0.0, 100.0].
    """
    # Test at boundaries
    engine_low = TrustDynamicsEngine(initial_resentment=5.0)
    engine_low.update_resentment(delta)
    assert 0.0 <= engine_low.get_resentment_score() <= 100.0
    
    engine_high = TrustDynamicsEngine(initial_resentment=95.0)
    engine_high.update_resentment(delta)
    assert 0.0 <= engine_high.get_resentment_score() <= 100.0


@given(st.sampled_from([ContextType.PUBLIC, ContextType.PRIVATE]))
def test_public_context_multiplier(context):
    """
    Property: Public context should have 2x impact compared to private context.
    """
    public_engine = TrustDynamicsEngine(initial_trust=60.0)
    public_change = public_engine.update_trust(2.0, context=ContextType.PUBLIC)
    
    private_engine = TrustDynamicsEngine(initial_trust=60.0)
    private_change = private_engine.update_trust(2.0, context=ContextType.PRIVATE)
    
    # Public should be approximately 2x private
    if context == ContextType.PUBLIC:
        ratio = abs(public_change) / abs(private_change)
        assert 1.9 <= ratio <= 2.1


@given(st.lists(st.booleans(), min_size=1, max_size=20))
def test_serialization_round_trip(action_sequence):
    """
    Property: Serializing and deserializing should preserve all state.
    """
    engine = TrustDynamicsEngine()
    
    # Perform some actions
    for is_positive in action_sequence:
        if is_positive:
            engine.update_trust(2.0)
        else:
            engine.update_resentment(1.0, is_pattern=False)
    
    # Serialize
    data = engine.to_dict()
    
    # Deserialize
    restored = TrustDynamicsEngine.from_dict(data)
    
    # Should match
    assert abs(restored.get_trust_score() - engine.get_trust_score()) < 0.01
    assert abs(restored.get_resentment_score() - engine.get_resentment_score()) < 0.01
    assert restored.is_in_withdrawal() == engine.is_in_withdrawal()
