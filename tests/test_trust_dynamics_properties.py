import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime, timedelta

from nurture.personality.trust_dynamics import TrustDynamicsEngine
from nurture.core.enums import ContextType, WithdrawalLevel, ActionType

@given(
    magnitude=st.floats(min_value=1.0, max_value=5.0)
)
def test_asymmetric_trust_dynamics(magnitude):
    engine = TrustDynamicsEngine(initial_trust=60.0)

    positive_change = engine.update_trust(TrustDynamicsEngine.BASE_TRUST_INCREASE)

    engine2 = TrustDynamicsEngine(initial_trust=60.0)

    negative_change = engine2.update_trust(-TrustDynamicsEngine.BASE_TRUST_DECREASE)

    ratio = abs(negative_change) / abs(positive_change)
    assert 1.8 <= ratio <= 2.2, f"Expected ~2x ratio, got {ratio} (positive: {positive_change}, negative: {negative_change})"

@given(st.integers(min_value=2, max_value=10))
def test_diminishing_returns_on_rapid_positive_actions(num_actions):
    engine = TrustDynamicsEngine(initial_trust=60.0)

    base_time = datetime.now()
    changes = []

    for i in range(num_actions):
        timestamp = base_time + timedelta(minutes=i * 5)
        change = engine.update_trust(2.0, timestamp=timestamp)
        changes.append(change)

    assert changes[0] > 0

    for i in range(1, len(changes)):
        assert changes[i] <= changes[0] * 0.5 + 0.01

@given(st.floats(min_value=0.0, max_value=100.0))
def test_withdrawal_state_transition(trust_score):
    engine = TrustDynamicsEngine(initial_trust=trust_score)

    if trust_score < 50.0:
        assert engine.is_in_withdrawal() is True
        assert engine.get_withdrawal_level() != WithdrawalLevel.NONE
    else:
        assert engine.is_in_withdrawal() is False
        assert engine.get_withdrawal_level() == WithdrawalLevel.NONE

@given(negative_delta=st.floats(min_value=-5.0, max_value=-1.0))
def test_high_trust_resilience(negative_delta):
    high_trust_engine = TrustDynamicsEngine(initial_trust=75.0)
    high_trust_change = high_trust_engine.update_trust(negative_delta)

    low_trust_engine = TrustDynamicsEngine(initial_trust=50.0)
    low_trust_change = low_trust_engine.update_trust(negative_delta)

    assert abs(high_trust_change) < abs(low_trust_change)

    reduction_ratio = abs(high_trust_change) / abs(low_trust_change)
    assert reduction_ratio <= 0.7 + 0.05

@given(st.integers(min_value=1, max_value=10))
def test_pattern_based_resentment_accumulation(num_incidents):
    pattern_engine = TrustDynamicsEngine()
    pattern_changes = []
    for _ in range(num_incidents):
        change = pattern_engine.update_resentment(delta=1.0, is_pattern=True)
        pattern_changes.append(change)

    single_engine = TrustDynamicsEngine()
    single_changes = []
    for _ in range(num_incidents):
        change = single_engine.update_resentment(delta=1.0, is_pattern=False)
        single_changes.append(change)

    total_pattern = sum(pattern_changes)
    total_single = sum(single_changes)

    if total_single > 0:
        ratio = total_pattern / total_single
        assert ratio >= 5.0, f"Expected at least 5x ratio, got {ratio}"

@given(days=st.floats(min_value=1.0, max_value=30.0))
def test_slow_resentment_decay(days):
    engine = TrustDynamicsEngine(initial_resentment=50.0, initial_trust=60.0)

    trust_before = engine.get_trust_score()
    engine.update_trust(2.0)
    trust_increase = engine.get_trust_score() - trust_before

    resentment_before = engine.get_resentment_score()
    resentment_decay = engine.apply_resentment_decay(days_elapsed=days)

    if trust_increase > 0:
        decay_per_day = resentment_decay / days
        assert decay_per_day <= trust_increase * 0.25 + 0.1

@given(positive_delta=st.floats(min_value=1.0, max_value=5.0))
def test_resentment_impact_on_trust_recovery(positive_delta):
    high_resentment_engine = TrustDynamicsEngine(initial_trust=40.0, initial_resentment=60.0)
    high_resentment_change = high_resentment_engine.update_trust(positive_delta)

    low_resentment_engine = TrustDynamicsEngine(initial_trust=40.0, initial_resentment=20.0)
    low_resentment_change = low_resentment_engine.update_trust(positive_delta)

    assert high_resentment_change < low_resentment_change

    if low_resentment_change > 0:
        ratio = high_resentment_change / low_resentment_change
        assert ratio <= 0.5 + 0.05

@given(
    behavior_type=st.sampled_from([
        ActionType.CONFLICT_AVOID,
        ActionType.CONTROL_TAKING,
        ActionType.PARENTING_ABSENT
    ])
)
def test_apology_tracking(behavior_type):
    engine = TrustDynamicsEngine()

    engine.record_apology(behavior_type, apology_type="genuine")

    assert behavior_type in engine.apology_records
    assert engine.apology_records[behavior_type].behavior_type == behavior_type
    assert engine.apology_records[behavior_type].timestamp is not None

@given(
    behavior_type=st.sampled_from([ActionType.CONFLICT_AVOID, ActionType.CONTROL_TAKING]),
    num_recurrences=st.integers(min_value=1, max_value=5)
)
def test_apology_effectiveness_decay(behavior_type, num_recurrences):
    engine = TrustDynamicsEngine()

    engine.record_apology(behavior_type, apology_type="genuine")
    initial_effectiveness = engine.get_apology_effectiveness(behavior_type)

    for _ in range(num_recurrences):
        engine.record_behavior_recurrence(behavior_type)

    final_effectiveness = engine.get_apology_effectiveness(behavior_type)

    assert final_effectiveness < initial_effectiveness

    assert final_effectiveness >= 0.1

    expected_decay = min(initial_effectiveness - 0.1, num_recurrences * 0.2)
    actual_decay = initial_effectiveness - final_effectiveness
    assert actual_decay >= expected_decay - 0.05

@given(weeks_elapsed=st.integers(min_value=1, max_value=10))
def test_apology_effectiveness_recovery(weeks_elapsed):
    engine = TrustDynamicsEngine()
    behavior_type = ActionType.CONFLICT_AVOID

    engine.record_apology(behavior_type)
    engine.record_behavior_recurrence(behavior_type)

    reduced_effectiveness = engine.get_apology_effectiveness(behavior_type)

    past_time = datetime.now() - timedelta(weeks=weeks_elapsed)
    engine.apology_records[behavior_type].last_recurrence = past_time

    recovered_effectiveness = engine.get_apology_effectiveness(behavior_type)

    if weeks_elapsed >= 1:
        assert recovered_effectiveness > reduced_effectiveness

        expected_recovery = min(0.1 * weeks_elapsed, 1.0 - reduced_effectiveness)
        actual_recovery = recovered_effectiveness - reduced_effectiveness
        assert abs(actual_recovery - expected_recovery) < 0.15

@given(st.sampled_from(["defensive", "generic", "genuine", "action_oriented"]))
def test_apology_type_differentiation(apology_type):
    engine = TrustDynamicsEngine()
    behavior_type = ActionType.CONFLICT_AVOID

    effectiveness = engine.get_apology_effectiveness(behavior_type, apology_type)

    if apology_type == "defensive":
        assert 0.25 <= effectiveness <= 0.35
    elif apology_type == "generic":
        assert 0.45 <= effectiveness <= 0.55
    elif apology_type == "genuine":
        assert 0.95 <= effectiveness <= 1.05
    elif apology_type == "action_oriented":
        assert 1.45 <= effectiveness <= 1.55

    defensive_effectiveness = engine.get_apology_effectiveness(behavior_type, "defensive")
    action_effectiveness = engine.get_apology_effectiveness(behavior_type, "action_oriented")

    ratio = action_effectiveness / defensive_effectiveness
    assert ratio >= 3.0, f"Expected at least 3x ratio, got {ratio}"

@given(st.floats(min_value=-10.0, max_value=10.0))
def test_trust_score_clamping(delta):
    engine_low = TrustDynamicsEngine(initial_trust=5.0)
    engine_low.update_trust(delta)
    assert 0.0 <= engine_low.get_trust_score() <= 100.0

    engine_high = TrustDynamicsEngine(initial_trust=95.0)
    engine_high.update_trust(delta)
    assert 0.0 <= engine_high.get_trust_score() <= 100.0

@given(st.floats(min_value=-10.0, max_value=10.0))
def test_resentment_score_clamping(delta):
    engine_low = TrustDynamicsEngine(initial_resentment=5.0)
    engine_low.update_resentment(delta)
    assert 0.0 <= engine_low.get_resentment_score() <= 100.0

    engine_high = TrustDynamicsEngine(initial_resentment=95.0)
    engine_high.update_resentment(delta)
    assert 0.0 <= engine_high.get_resentment_score() <= 100.0

@given(st.sampled_from([ContextType.PUBLIC, ContextType.PRIVATE]))
def test_public_context_multiplier(context):
    public_engine = TrustDynamicsEngine(initial_trust=60.0)
    public_change = public_engine.update_trust(2.0, context=ContextType.PUBLIC)

    private_engine = TrustDynamicsEngine(initial_trust=60.0)
    private_change = private_engine.update_trust(2.0, context=ContextType.PRIVATE)

    if context == ContextType.PUBLIC:
        ratio = abs(public_change) / abs(private_change)
        assert 1.9 <= ratio <= 2.1

@given(st.lists(st.booleans(), min_size=1, max_size=20))
def test_serialization_round_trip(action_sequence):
    engine = TrustDynamicsEngine()

    for is_positive in action_sequence:
        if is_positive:
            engine.update_trust(2.0)
        else:
            engine.update_resentment(1.0, is_pattern=False)

    data = engine.to_dict()

    restored = TrustDynamicsEngine.from_dict(data)

    assert abs(restored.get_trust_score() - engine.get_trust_score()) < 0.01
    assert abs(restored.get_resentment_score() - engine.get_resentment_score()) < 0.01
    assert restored.is_in_withdrawal() == engine.is_in_withdrawal()
