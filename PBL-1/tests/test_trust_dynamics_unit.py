"""
Unit tests for TrustDynamicsEngine edge cases.

These tests validate specific edge cases and boundary conditions
that complement the property-based tests.
"""

import pytest
from datetime import datetime, timedelta

from nurture.personality.trust_dynamics import TrustDynamicsEngine
from nurture.core.enums import ContextType, WithdrawalLevel, ActionType


class TestTrustScoreClamping:
    """Test trust score stays within valid range [0.0, 100.0]."""
    
    def test_trust_cannot_exceed_100(self):
        """Trust score should be clamped at 100.0."""
        engine = TrustDynamicsEngine(initial_trust=95.0)
        
        # Try to push trust above 100
        engine.update_trust(delta=10.0)
        
        assert engine.get_trust_score() == 100.0
    
    def test_trust_cannot_go_below_0(self):
        """Trust score should be clamped at 0.0."""
        engine = TrustDynamicsEngine(initial_trust=5.0)
        
        # Try to push trust below 0
        engine.update_trust(delta=-10.0)
        
        assert engine.get_trust_score() == 0.0
    
    def test_initial_trust_clamped_on_construction(self):
        """Initial trust should be clamped to valid range."""
        engine_high = TrustDynamicsEngine(initial_trust=150.0)
        assert engine_high.get_trust_score() == 100.0
        
        engine_low = TrustDynamicsEngine(initial_trust=-50.0)
        assert engine_low.get_trust_score() == 0.0


class TestResentmentScoreClamping:
    """Test resentment score stays within valid range [0.0, 100.0]."""
    
    def test_resentment_cannot_exceed_100(self):
        """Resentment score should be clamped at 100.0."""
        engine = TrustDynamicsEngine(initial_resentment=98.0)
        
        # Try to push resentment above 100 (pattern adds 3.0)
        engine.update_resentment(delta=5.0, is_pattern=True)
        
        assert engine.get_resentment_score() == 100.0
    
    def test_resentment_cannot_go_below_0(self):
        """Resentment score should be clamped at 0.0."""
        engine = TrustDynamicsEngine(initial_resentment=1.0)
        
        # Try to push resentment below 0
        engine.update_resentment(delta=-5.0)
        
        assert engine.get_resentment_score() == 0.0
    
    def test_initial_resentment_clamped_on_construction(self):
        """Initial resentment should be clamped to valid range."""
        engine_high = TrustDynamicsEngine(initial_resentment=150.0)
        assert engine_high.get_resentment_score() == 100.0
        
        engine_low = TrustDynamicsEngine(initial_resentment=-50.0)
        assert engine_low.get_resentment_score() == 0.0


class TestWithdrawalThresholdBoundaries:
    """Test withdrawal state transitions at exact threshold boundaries."""
    
    def test_withdrawal_at_exact_threshold(self):
        """At trust=50.0, should NOT be in withdrawal (>= threshold)."""
        engine = TrustDynamicsEngine(initial_trust=50.0)
        
        assert not engine.is_in_withdrawal()
        assert engine.get_withdrawal_level() == WithdrawalLevel.NONE
    
    def test_withdrawal_just_below_threshold(self):
        """At trust=49.9, should be in withdrawal."""
        engine = TrustDynamicsEngine(initial_trust=49.9)
        
        assert engine.is_in_withdrawal()
        assert engine.get_withdrawal_level() == WithdrawalLevel.MILD
    
    def test_mild_withdrawal_boundary(self):
        """Test MILD withdrawal at trust=40.0."""
        engine = TrustDynamicsEngine(initial_trust=40.0)
        
        assert engine.is_in_withdrawal()
        assert engine.get_withdrawal_level() == WithdrawalLevel.MILD
    
    def test_moderate_withdrawal_boundary(self):
        """Test MODERATE withdrawal at trust=30.0."""
        engine = TrustDynamicsEngine(initial_trust=30.0)
        
        assert engine.is_in_withdrawal()
        assert engine.get_withdrawal_level() == WithdrawalLevel.MODERATE
    
    def test_severe_withdrawal_boundary(self):
        """Test SEVERE withdrawal at trust=29.9."""
        engine = TrustDynamicsEngine(initial_trust=29.9)
        
        assert engine.is_in_withdrawal()
        assert engine.get_withdrawal_level() == WithdrawalLevel.SEVERE
    
    def test_severe_withdrawal_at_zero(self):
        """Test SEVERE withdrawal at trust=0.0."""
        engine = TrustDynamicsEngine(initial_trust=0.0)
        
        assert engine.is_in_withdrawal()
        assert engine.get_withdrawal_level() == WithdrawalLevel.SEVERE


class TestApologyEffectivenessMinimum:
    """Test apology effectiveness has minimum value."""
    
    def test_effectiveness_has_minimum_floor(self):
        """Apology effectiveness should not go below MIN_APOLOGY_EFFECTIVENESS."""
        engine = TrustDynamicsEngine()
        
        # Record apology
        engine.record_apology(ActionType.EMPATHY_LACKING, apology_type="genuine")
        
        # Record many recurrences to try to push effectiveness below minimum
        for _ in range(10):
            engine.record_behavior_recurrence(ActionType.EMPATHY_LACKING)
        
        effectiveness = engine.get_apology_effectiveness(
            ActionType.EMPATHY_LACKING,
            apology_type="genuine"
        )
        
        assert effectiveness >= TrustDynamicsEngine.MIN_APOLOGY_EFFECTIVENESS
    
    def test_defensive_apology_minimum(self):
        """Defensive apology effectiveness should respect minimum."""
        engine = TrustDynamicsEngine()
        
        engine.record_apology(ActionType.CONFLICT_AVOID, apology_type="defensive")
        
        # Record many recurrences
        for _ in range(10):
            engine.record_behavior_recurrence(ActionType.CONFLICT_AVOID)
        
        effectiveness = engine.get_apology_effectiveness(
            ActionType.CONFLICT_AVOID,
            apology_type="defensive"
        )
        
        # Should be at least MIN * defensive_multiplier
        min_expected = TrustDynamicsEngine.MIN_APOLOGY_EFFECTIVENESS * 0.3
        assert effectiveness >= min_expected
    
    def test_no_apology_record_returns_type_multiplier(self):
        """Without apology record, should return type multiplier."""
        engine = TrustDynamicsEngine()
        
        # No apology recorded for this behavior
        effectiveness = engine.get_apology_effectiveness(
            ActionType.EMPATHY_LACKING,
            apology_type="genuine"
        )
        
        assert effectiveness == 1.0  # genuine type multiplier
    
    def test_action_oriented_apology_maximum(self):
        """Action-oriented apology should have highest multiplier."""
        engine = TrustDynamicsEngine()
        
        engine.record_apology(ActionType.CONFLICT_AVOID, apology_type="action_oriented")
        
        effectiveness = engine.get_apology_effectiveness(
            ActionType.CONFLICT_AVOID,
            apology_type="action_oriented"
        )
        
        assert effectiveness == 1.5  # action_oriented multiplier


class TestResponseModifiers:
    """Test response modifier calculations at boundaries."""
    
    def test_response_length_at_boundaries(self):
        """Test response length multiplier at each withdrawal level."""
        # No withdrawal
        engine_none = TrustDynamicsEngine(initial_trust=50.0)
        assert engine_none.get_response_length_multiplier() == 1.0
        
        # Mild withdrawal
        engine_mild = TrustDynamicsEngine(initial_trust=45.0)
        assert engine_mild.get_response_length_multiplier() == 0.7
        
        # Moderate withdrawal
        engine_moderate = TrustDynamicsEngine(initial_trust=35.0)
        assert engine_moderate.get_response_length_multiplier() == 0.5
        
        # Severe withdrawal
        engine_severe = TrustDynamicsEngine(initial_trust=20.0)
        assert engine_severe.get_response_length_multiplier() == 0.3
    
    def test_initiation_probability_at_boundaries(self):
        """Test initiation probability at trust boundaries."""
        # High trust (>70)
        engine_high = TrustDynamicsEngine(initial_trust=75.0)
        assert engine_high.get_initiation_probability() == 1.0
        
        # Low trust (<40)
        engine_low = TrustDynamicsEngine(initial_trust=30.0)
        assert engine_low.get_initiation_probability() == 0.1
        
        # Mid trust (40-70)
        engine_mid = TrustDynamicsEngine(initial_trust=55.0)
        prob = engine_mid.get_initiation_probability()
        assert 0.1 < prob < 1.0
    
    def test_cooperation_level_at_boundaries(self):
        """Test cooperation level at resentment boundaries."""
        # Low resentment (<30)
        engine_low = TrustDynamicsEngine(initial_resentment=20.0)
        assert engine_low.get_cooperation_level() == 1.0
        
        # Mid-low resentment (30-50)
        engine_mid_low = TrustDynamicsEngine(initial_resentment=40.0)
        assert engine_mid_low.get_cooperation_level() == 0.7
        
        # Mid-high resentment (50-70)
        engine_mid_high = TrustDynamicsEngine(initial_resentment=60.0)
        assert engine_mid_high.get_cooperation_level() == 0.4
        
        # High resentment (>70)
        engine_high = TrustDynamicsEngine(initial_resentment=80.0)
        assert engine_high.get_cooperation_level() == 0.2


class TestResentmentDecay:
    """Test resentment decay edge cases."""
    
    def test_decay_without_positive_actions(self):
        """Resentment should not decay without positive actions."""
        engine = TrustDynamicsEngine(initial_resentment=50.0)
        
        # Try to apply decay without any positive actions
        decay = engine.apply_resentment_decay(days_elapsed=5.0)
        
        assert decay == 0.0
        assert engine.get_resentment_score() == 50.0
    
    def test_decay_with_positive_actions(self):
        """Resentment should decay after positive actions."""
        engine = TrustDynamicsEngine(initial_resentment=50.0)
        
        # Record a positive action
        engine.update_trust(delta=2.0)
        
        # Apply decay
        decay = engine.apply_resentment_decay(days_elapsed=1.0)
        
        assert decay == 0.5  # RESENTMENT_DECAY_RATE
        assert engine.get_resentment_score() == 49.5
    
    def test_decay_cannot_go_negative(self):
        """Resentment decay should not push score below 0."""
        engine = TrustDynamicsEngine(initial_resentment=0.2)
        
        # Record a positive action
        engine.update_trust(delta=2.0)
        
        # Apply large decay
        decay = engine.apply_resentment_decay(days_elapsed=10.0)
        
        assert engine.get_resentment_score() == 0.0


class TestDiminishingReturnsWindow:
    """Test diminishing returns time window edge cases."""
    
    def test_rapid_positive_actions_within_window(self):
        """Multiple positive actions within 1 hour should have diminishing returns."""
        engine = TrustDynamicsEngine(initial_trust=50.0)
        
        now = datetime.now()
        
        # First action - full impact
        change1 = engine.update_trust(delta=2.0, timestamp=now)
        
        # Second action 30 minutes later - diminished
        change2 = engine.update_trust(delta=2.0, timestamp=now + timedelta(minutes=30))
        
        # Second change should be smaller due to diminishing returns
        assert change2 < change1
    
    def test_positive_actions_outside_window(self):
        """Positive actions >1 hour apart should have full impact."""
        engine = TrustDynamicsEngine(initial_trust=50.0)
        
        now = datetime.now()
        
        # First action
        change1 = engine.update_trust(delta=2.0, timestamp=now)
        
        # Second action 2 hours later - full impact
        change2 = engine.update_trust(delta=2.0, timestamp=now + timedelta(hours=2))
        
        # Both changes should be equal
        assert abs(change1 - change2) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
