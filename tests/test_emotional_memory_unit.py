"""
Unit tests for EmotionalMemorySystem edge cases.

Tests memory capacity overflow, recall with no matches, temporal decay,
and other specific scenarios.
"""
import pytest
from datetime import datetime, timedelta

from nurture.personality.emotional_memory import EmotionalMemorySystem
from nurture.core.data_structures import EmotionalImpact
from nurture.core.enums import EmotionType, ContextType, ContextCategory, PatternType


class TestEmotionalMemoryEdgeCases:
    """Test edge cases and specific scenarios for EmotionalMemorySystem."""
    
    def test_memory_capacity_overflow_and_pruning(self):
        """
        Test that memory system correctly prunes oldest memories when
        capacity exceeds 1000 entries.
        """
        memory_system = EmotionalMemorySystem(max_capacity=10)  # Small capacity for testing
        
        # Store more memories than capacity
        base_time = datetime.now()
        for i in range(15):
            impact = EmotionalImpact(
                primary_emotion=EmotionType.TRUST,
                intensity=0.5,
                valence=0.5,
                context_category=ContextCategory.SUPPORT
            )
            memory_system.store_memory(
                interaction_id=f"interaction_{i}",
                emotional_impact=impact,
                timestamp=base_time - timedelta(hours=15 - i)
            )
        
        # Should have pruned to max capacity
        assert len(memory_system.memories) == 10
        
        # Most recent memories should be kept (last 10 out of 15)
        # The oldest should be from 10 hours ago (interaction_5)
        timestamps = [m.timestamp for m in memory_system.memories]
        cutoff = base_time - timedelta(hours=10)
        assert all(t >= cutoff for t in timestamps)
    
    def test_recall_with_no_matching_memories(self):
        """
        Test that recall returns empty list when no memories match
        the specified context.
        """
        memory_system = EmotionalMemorySystem()
        
        # Store only PRIVATE context memories
        for i in range(5):
            impact = EmotionalImpact(
                primary_emotion=EmotionType.TRUST,
                intensity=0.5,
                valence=0.5,
                context_category=ContextCategory.SUPPORT
            )
            memory_system.store_memory(
                interaction_id=f"interaction_{i}",
                emotional_impact=impact,
                context=ContextType.PRIVATE
            )
        
        # Recall PUBLIC context memories (should be empty)
        recalled = memory_system.recall_similar(context=ContextType.PUBLIC)
        assert recalled == []
    
    def test_recall_with_no_memories_at_all(self):
        """Test recall on empty memory system."""
        memory_system = EmotionalMemorySystem()
        
        recalled = memory_system.recall_similar()
        assert recalled == []
    
    def test_temporal_decay_application(self):
        """
        Test that temporal decay correctly reduces weights of older memories.
        """
        memory_system = EmotionalMemorySystem()
        
        # Store memories at different ages
        impact = EmotionalImpact(
            primary_emotion=EmotionType.TRUST,
            intensity=0.7,
            valence=0.6,
            context_category=ContextCategory.SUPPORT
        )
        
        # Recent memory (< 24 hours)
        recent_memory = memory_system.store_memory(
            interaction_id="recent",
            emotional_impact=impact,
            timestamp=datetime.now() - timedelta(hours=12)
        )
        
        # Week-old memory
        week_memory = memory_system.store_memory(
            interaction_id="week",
            emotional_impact=impact,
            timestamp=datetime.now() - timedelta(days=5)
        )
        
        # Month-old memory
        month_memory = memory_system.store_memory(
            interaction_id="month",
            emotional_impact=impact,
            timestamp=datetime.now() - timedelta(days=20)
        )
        
        # Old memory (> 30 days)
        old_memory = memory_system.store_memory(
            interaction_id="old",
            emotional_impact=impact,
            timestamp=datetime.now() - timedelta(days=45)
        )
        
        # Apply temporal decay
        memory_system.apply_temporal_decay()
        
        # Verify weights follow decay function
        assert recent_memory.weight == 1.0
        assert week_memory.weight == 0.8
        assert month_memory.weight == 0.5
        assert old_memory.weight < 0.3  # Should have additional exponential decay
    
    def test_get_emotional_association_empty(self):
        """Test getting emotional association when no memories exist."""
        memory_system = EmotionalMemorySystem()
        
        association = memory_system.get_emotional_association(ContextCategory.SUPPORT)
        assert association == 0.0
    
    def test_get_emotional_association_accumulation(self):
        """
        Test that emotional associations accumulate correctly across
        multiple memories.
        """
        memory_system = EmotionalMemorySystem()
        
        # Store multiple positive memories in SUPPORT category
        for i in range(5):
            impact = EmotionalImpact(
                primary_emotion=EmotionType.TRUST,
                intensity=0.7,
                valence=0.6,
                context_category=ContextCategory.SUPPORT
            )
            memory_system.store_memory(
                interaction_id=f"support_{i}",
                emotional_impact=impact
            )
        
        # Store negative memories in CONFLICT category
        for i in range(3):
            impact = EmotionalImpact(
                primary_emotion=EmotionType.RESENTMENT,
                intensity=0.8,
                valence=-0.7,
                context_category=ContextCategory.CONFLICT
            )
            memory_system.store_memory(
                interaction_id=f"conflict_{i}",
                emotional_impact=impact
            )
        
        # Check associations
        support_assoc = memory_system.get_emotional_association(ContextCategory.SUPPORT)
        conflict_assoc = memory_system.get_emotional_association(ContextCategory.CONFLICT)
        
        assert support_assoc > 0  # Positive association
        assert conflict_assoc < 0  # Negative association
        assert abs(support_assoc - (0.6 * 5)) < 0.01
        assert abs(conflict_assoc - (-0.7 * 3)) < 0.01
    
    def test_recall_respects_context_filter(self):
        """Test that recall correctly filters by context."""
        memory_system = EmotionalMemorySystem()
        
        # Store PUBLIC memories
        for i in range(3):
            impact = EmotionalImpact(
                primary_emotion=EmotionType.TRUST,
                intensity=0.5,
                valence=0.5,
                context_category=ContextCategory.PARENTING
            )
            memory_system.store_memory(
                interaction_id=f"public_{i}",
                emotional_impact=impact,
                context=ContextType.PUBLIC
            )
        
        # Store PRIVATE memories
        for i in range(5):
            impact = EmotionalImpact(
                primary_emotion=EmotionType.TRUST,
                intensity=0.5,
                valence=0.5,
                context_category=ContextCategory.INTIMACY
            )
            memory_system.store_memory(
                interaction_id=f"private_{i}",
                emotional_impact=impact,
                context=ContextType.PRIVATE
            )
        
        # Recall only PUBLIC
        public_memories = memory_system.recall_similar(context=ContextType.PUBLIC)
        assert len(public_memories) == 3
        assert all(m.context == ContextType.PUBLIC for m in public_memories)
        
        # Recall only PRIVATE
        private_memories = memory_system.recall_similar(context=ContextType.PRIVATE)
        assert len(private_memories) == 5
        assert all(m.context == ContextType.PRIVATE for m in private_memories)
    
    def test_recall_respects_context_category_filter(self):
        """Test that recall correctly filters by context category."""
        memory_system = EmotionalMemorySystem()
        
        # Store memories in different categories
        categories = [
            ContextCategory.SUPPORT,
            ContextCategory.CONFLICT,
            ContextCategory.PARENTING,
            ContextCategory.INTIMACY
        ]
        
        for category in categories:
            for i in range(3):
                impact = EmotionalImpact(
                    primary_emotion=EmotionType.TRUST,
                    intensity=0.5,
                    valence=0.5,
                    context_category=category
                )
                memory_system.store_memory(
                    interaction_id=f"{category.value}_{i}",
                    emotional_impact=impact
                )
        
        # Recall each category
        for category in categories:
            recalled = memory_system.recall_similar(context_category=category)
            assert len(recalled) == 3
            assert all(m.emotional_impact.context_category == category for m in recalled)
    
    def test_recall_sorted_by_weight(self):
        """Test that recall returns memories sorted by weight (recency)."""
        memory_system = EmotionalMemorySystem()
        
        # Store memories at different times
        for i in range(10):
            impact = EmotionalImpact(
                primary_emotion=EmotionType.TRUST,
                intensity=0.5,
                valence=0.5,
                context_category=ContextCategory.SUPPORT
            )
            memory_system.store_memory(
                interaction_id=f"memory_{i}",
                emotional_impact=impact,
                timestamp=datetime.now() - timedelta(days=i)
            )
        
        # Recall all memories
        recalled = memory_system.recall_similar(limit=10)
        
        # Should be sorted by weight (descending)
        weights = [m.weight for m in recalled]
        assert weights == sorted(weights, reverse=True)
    
    def test_get_recent_memories(self):
        """Test getting memories from last N hours."""
        memory_system = EmotionalMemorySystem()
        
        # Store memories at different times
        for i in range(10):
            impact = EmotionalImpact(
                primary_emotion=EmotionType.TRUST,
                intensity=0.5,
                valence=0.5,
                context_category=ContextCategory.SUPPORT
            )
            memory_system.store_memory(
                interaction_id=f"memory_{i}",
                emotional_impact=impact,
                timestamp=datetime.now() - timedelta(hours=i * 3)
            )
        
        # Get memories from last 12 hours
        recent = memory_system.get_recent_memories(hours=12)
        
        # Should have 5 memories (0, 3, 6, 9, 12 hours ago)
        assert len(recent) <= 5
        
        # All should be within 12 hours
        cutoff = datetime.now() - timedelta(hours=12)
        assert all(m.timestamp >= cutoff for m in recent)
    
    def test_get_memories_by_emotion(self):
        """Test filtering memories by emotion type."""
        memory_system = EmotionalMemorySystem()
        
        # Store memories with different emotions
        emotions = [EmotionType.TRUST, EmotionType.RESENTMENT, EmotionType.CONTENTMENT]
        
        for emotion in emotions:
            for i in range(3):
                impact = EmotionalImpact(
                    primary_emotion=emotion,
                    intensity=0.5,
                    valence=0.5,
                    context_category=ContextCategory.SUPPORT
                )
                memory_system.store_memory(
                    interaction_id=f"{emotion.value}_{i}",
                    emotional_impact=impact
                )
        
        # Get memories by emotion
        trust_memories = memory_system.get_memories_by_emotion(EmotionType.TRUST)
        assert len(trust_memories) == 3
        assert all(m.emotional_impact.primary_emotion == EmotionType.TRUST for m in trust_memories)
    
    def test_get_memories_by_pattern(self):
        """Test filtering memories by associated pattern."""
        memory_system = EmotionalMemorySystem()
        
        # Store memories with different patterns
        impact = EmotionalImpact(
            primary_emotion=EmotionType.TRUST,
            intensity=0.5,
            valence=0.5,
            context_category=ContextCategory.SUPPORT
        )
        
        # Memories with CONSISTENT_PRESENCE pattern
        for i in range(3):
            memory_system.store_memory(
                interaction_id=f"presence_{i}",
                emotional_impact=impact,
                associated_patterns=[PatternType.CONSISTENT_PRESENCE]
            )
        
        # Memories with REPEATED_AVOIDANCE pattern
        for i in range(2):
            memory_system.store_memory(
                interaction_id=f"avoidance_{i}",
                emotional_impact=impact,
                associated_patterns=[PatternType.REPEATED_AVOIDANCE]
            )
        
        # Get memories by pattern
        presence_memories = memory_system.get_memories_by_pattern(PatternType.CONSISTENT_PRESENCE)
        assert len(presence_memories) == 3
        
        avoidance_memories = memory_system.get_memories_by_pattern(PatternType.REPEATED_AVOIDANCE)
        assert len(avoidance_memories) == 2
    
    def test_get_average_valence(self):
        """Test calculating average valence over recent period."""
        memory_system = EmotionalMemorySystem()
        
        # Store positive memories
        for i in range(5):
            impact = EmotionalImpact(
                primary_emotion=EmotionType.TRUST,
                intensity=0.7,
                valence=0.8,
                context_category=ContextCategory.SUPPORT
            )
            memory_system.store_memory(
                interaction_id=f"positive_{i}",
                emotional_impact=impact,
                timestamp=datetime.now() - timedelta(days=i)
            )
        
        # Average should be 0.8
        avg = memory_system.get_average_valence(days=7)
        assert abs(avg - 0.8) < 0.01
    
    def test_get_average_valence_by_category(self):
        """Test calculating average valence filtered by category."""
        memory_system = EmotionalMemorySystem()
        
        # Store positive SUPPORT memories
        for i in range(3):
            impact = EmotionalImpact(
                primary_emotion=EmotionType.TRUST,
                intensity=0.7,
                valence=0.9,
                context_category=ContextCategory.SUPPORT
            )
            memory_system.store_memory(
                interaction_id=f"support_{i}",
                emotional_impact=impact
            )
        
        # Store negative CONFLICT memories
        for i in range(3):
            impact = EmotionalImpact(
                primary_emotion=EmotionType.RESENTMENT,
                intensity=0.7,
                valence=-0.6,
                context_category=ContextCategory.CONFLICT
            )
            memory_system.store_memory(
                interaction_id=f"conflict_{i}",
                emotional_impact=impact
            )
        
        # Check averages by category
        support_avg = memory_system.get_average_valence(context_category=ContextCategory.SUPPORT)
        conflict_avg = memory_system.get_average_valence(context_category=ContextCategory.CONFLICT)
        
        assert abs(support_avg - 0.9) < 0.01
        assert abs(conflict_avg - (-0.6)) < 0.01
    
    def test_clear_old_memories(self):
        """Test removing memories older than specified days."""
        memory_system = EmotionalMemorySystem()
        
        # Store memories at different ages
        for i in range(10):
            impact = EmotionalImpact(
                primary_emotion=EmotionType.TRUST,
                intensity=0.5,
                valence=0.5,
                context_category=ContextCategory.SUPPORT
            )
            memory_system.store_memory(
                interaction_id=f"memory_{i}",
                emotional_impact=impact,
                timestamp=datetime.now() - timedelta(days=i * 40)
            )
        
        # Clear memories older than 180 days
        removed = memory_system.clear_old_memories(days=180)
        
        # Should have removed some memories
        assert removed > 0
        
        # Remaining memories should be within 180 days
        cutoff = datetime.now() - timedelta(days=180)
        assert all(m.timestamp >= cutoff for m in memory_system.memories)
    
    def test_get_memory_stats(self):
        """Test getting memory statistics."""
        memory_system = EmotionalMemorySystem()
        
        # Store some memories
        for i in range(5):
            impact = EmotionalImpact(
                primary_emotion=EmotionType.TRUST,
                intensity=0.5,
                valence=0.6,
                context_category=ContextCategory.SUPPORT
            )
            memory_system.store_memory(
                interaction_id=f"memory_{i}",
                emotional_impact=impact,
                timestamp=datetime.now() - timedelta(days=i)
            )
        
        stats = memory_system.get_memory_stats()
        
        assert stats['total_memories'] == 5
        assert abs(stats['average_valence'] - 0.6) < 0.01
        assert stats['oldest_memory_age_days'] >= 4
        assert 'context_breakdown' in stats
    
    def test_serialization_preserves_all_data(self):
        """Test that serialization preserves all memory system data."""
        memory_system = EmotionalMemorySystem(max_capacity=500, decay_rate=0.1)
        
        # Store memories
        for i in range(10):
            impact = EmotionalImpact(
                primary_emotion=EmotionType.TRUST,
                intensity=0.5,
                valence=0.6,
                context_category=ContextCategory.SUPPORT
            )
            memory_system.store_memory(
                interaction_id=f"memory_{i}",
                emotional_impact=impact,
                associated_patterns=[PatternType.CONSISTENT_PRESENCE]
            )
        
        # Serialize
        data = memory_system.to_dict()
        
        # Verify all fields present
        assert 'memories' in data
        assert 'context_associations' in data
        assert 'max_capacity' in data
        assert 'decay_rate' in data
        
        assert data['max_capacity'] == 500
        assert data['decay_rate'] == 0.1
        assert len(data['memories']) == 10
        
        # Deserialize
        restored = EmotionalMemorySystem.from_dict(data)
        
        assert len(restored.memories) == 10
        assert restored.max_capacity == 500
        assert restored.decay_rate == 0.1
