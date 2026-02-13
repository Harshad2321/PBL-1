import pytest
from datetime import datetime, timedelta

from nurture.personality.trust_dynamics import TrustDynamicsEngine
from nurture.core.enums import ContextType, WithdrawalLevel, ActionType

class TestTrustScoreClamping:

    def test_trust_cannot_exceed_100(self):
        engine = TrustDynamicsEngine(initial_trust=95.0)

        engine.update_trust(delta=10.0)

        assert engine.get_trust_score() == 100.0

    def test_trust_cannot_go_below_0(self):
        engine = TrustDynamicsEngine(initial_trust=5.0)

        engine.update_trust(delta=-10.0)

        assert engine.get_trust_score() == 0.0

    def test_initial_trust_clamped_on_construction(self):
        engine_high = TrustDynamicsEngine(initial_trust=150.0)
        assert engine_high.get_trust_score() == 100.0

        engine_low = TrustDynamicsEngine(initial_trust=-50.0)
        assert engine_low.get_trust_score() == 0.0

class TestResentmentScoreClamping:

    def test_resentment_cannot_exceed_100(self):
        engine = TrustDynamicsEngine(initial_resentment=98.0)

        engine.update_resentment(delta=5.0, is_pattern=True)

        assert engine.get_resentment_score() == 100.0

    def test_resentment_cannot_go_below_0(self):
        engine = TrustDynamicsEngine(initial_resentment=1.0)

        engine.update_resentment(delta=-5.0)

        assert engine.get_resentment_score() == 0.0

    def test_initial_resentment_clamped_on_construction(self):
        engine_high = TrustDynamicsEngine(initial_resentment=150.0)
        assert engine_high.get_resentment_score() == 100.0

        engine_low = TrustDynamicsEngine(initial_resentment=-50.0)
        assert engine_low.get_resentment_score() == 0.0

class TestWithdrawalThresholdBoundaries:

    def test_withdrawal_at_exact_threshold(self):
        engine = TrustDynamicsEngine(initial_trust=50.0)

        assert not engine.is_in_withdrawal()
        assert engine.get_withdrawal_level() == WithdrawalLevel.NONE

    def test_withdrawal_just_below_threshold(self):
        engine = TrustDynamicsEngine(initial_trust=49.9)

        assert engine.is_in_withdrawal()
        assert engine.get_withdrawal_level() == WithdrawalLevel.MILD

    def test_mild_withdrawal_boundary(self):
        engine = TrustDynamicsEngine(initial_trust=40.0)

        assert engine.is_in_withdrawal()
        assert engine.get_withdrawal_level() == WithdrawalLevel.MILD

    def test_moderate_withdrawal_boundary(self):
        engine = TrustDynamicsEngine(initial_trust=30.0)

        assert engine.is_in_withdrawal()
        assert engine.get_withdrawal_level() == WithdrawalLevel.MODERATE

    def test_severe_withdrawal_boundary(self):
        engine = TrustDynamicsEngine(initial_trust=29.9)

        assert engine.is_in_withdrawal()
        assert engine.get_withdrawal_level() == WithdrawalLevel.SEVERE

    def test_severe_withdrawal_at_zero(self):
        engine = TrustDynamicsEngine(initial_trust=0.0)

        assert engine.is_in_withdrawal()
        assert engine.get_withdrawal_level() == WithdrawalLevel.SEVERE

class TestApologyEffectivenessMinimum:

    def test_effectiveness_has_minimum_floor(self):
        engine = TrustDynamicsEngine()

        engine.record_apology(ActionType.EMPATHY_LACKING, apology_type="genuine")

        for _ in range(10):
            engine.record_behavior_recurrence(ActionType.EMPATHY_LACKING)

        effectiveness = engine.get_apology_effectiveness(
            ActionType.EMPATHY_LACKING,
            apology_type="genuine"
        )

        assert effectiveness >= TrustDynamicsEngine.MIN_APOLOGY_EFFECTIVENESS

    def test_defensive_apology_minimum(self):
        engine = TrustDynamicsEngine()

        engine.record_apology(ActionType.CONFLICT_AVOID, apology_type="defensive")

        for _ in range(10):
            engine.record_behavior_recurrence(ActionType.CONFLICT_AVOID)

        effectiveness = engine.get_apology_effectiveness(
            ActionType.CONFLICT_AVOID,
            apology_type="defensive"
        )

        min_expected = TrustDynamicsEngine.MIN_APOLOGY_EFFECTIVENESS * 0.3
        assert effectiveness >= min_expected

    def test_no_apology_record_returns_type_multiplier(self):
        engine = TrustDynamicsEngine()

        effectiveness = engine.get_apology_effectiveness(
            ActionType.EMPATHY_LACKING,
            apology_type="genuine"
        )

        assert effectiveness == 1.0

    def test_action_oriented_apology_maximum(self):
        engine = TrustDynamicsEngine()

        engine.record_apology(ActionType.CONFLICT_AVOID, apology_type="action_oriented")

        effectiveness = engine.get_apology_effectiveness(
            ActionType.CONFLICT_AVOID,
            apology_type="action_oriented"
        )

        assert effectiveness == 1.5

class TestResponseModifiers:

    def test_response_length_at_boundaries(self):
        engine_none = TrustDynamicsEngine(initial_trust=50.0)
        assert engine_none.get_response_length_multiplier() == 1.0

        engine_mild = TrustDynamicsEngine(initial_trust=45.0)
        assert engine_mild.get_response_length_multiplier() == 0.7

        engine_moderate = TrustDynamicsEngine(initial_trust=35.0)
        assert engine_moderate.get_response_length_multiplier() == 0.5

        engine_severe = TrustDynamicsEngine(initial_trust=20.0)
        assert engine_severe.get_response_length_multiplier() == 0.3

    def test_initiation_probability_at_boundaries(self):
        engine_high = TrustDynamicsEngine(initial_trust=75.0)
        assert engine_high.get_initiation_probability() == 1.0

        engine_low = TrustDynamicsEngine(initial_trust=30.0)
        assert engine_low.get_initiation_probability() == 0.1

        engine_mid = TrustDynamicsEngine(initial_trust=55.0)
        prob = engine_mid.get_initiation_probability()
        assert 0.1 < prob < 1.0

    def test_cooperation_level_at_boundaries(self):
        engine_low = TrustDynamicsEngine(initial_resentment=20.0)
        assert engine_low.get_cooperation_level() == 1.0

        engine_mid_low = TrustDynamicsEngine(initial_resentment=40.0)
        assert engine_mid_low.get_cooperation_level() == 0.7

        engine_mid_high = TrustDynamicsEngine(initial_resentment=60.0)
        assert engine_mid_high.get_cooperation_level() == 0.4

        engine_high = TrustDynamicsEngine(initial_resentment=80.0)
        assert engine_high.get_cooperation_level() == 0.2

class TestResentmentDecay:

    def test_decay_without_positive_actions(self):
        engine = TrustDynamicsEngine(initial_resentment=50.0)

        decay = engine.apply_resentment_decay(days_elapsed=5.0)

        assert decay == 0.0
        assert engine.get_resentment_score() == 50.0

    def test_decay_with_positive_actions(self):
        engine = TrustDynamicsEngine(initial_resentment=50.0)

        engine.update_trust(delta=2.0)

        decay = engine.apply_resentment_decay(days_elapsed=1.0)

        assert decay == 0.5
        assert engine.get_resentment_score() == 49.5

    def test_decay_cannot_go_negative(self):
        engine = TrustDynamicsEngine(initial_resentment=0.2)

        engine.update_trust(delta=2.0)

        decay = engine.apply_resentment_decay(days_elapsed=10.0)

        assert engine.get_resentment_score() == 0.0

class TestDiminishingReturnsWindow:

    def test_rapid_positive_actions_within_window(self):
        engine = TrustDynamicsEngine(initial_trust=50.0)

        now = datetime.now()

        change1 = engine.update_trust(delta=2.0, timestamp=now)

        change2 = engine.update_trust(delta=2.0, timestamp=now + timedelta(minutes=30))

        assert change2 < change1

    def test_positive_actions_outside_window(self):
        engine = TrustDynamicsEngine(initial_trust=50.0)

        now = datetime.now()

        change1 = engine.update_trust(delta=2.0, timestamp=now)

        change2 = engine.update_trust(delta=2.0, timestamp=now + timedelta(hours=2))

        assert abs(change1 - change2) < 0.01

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
