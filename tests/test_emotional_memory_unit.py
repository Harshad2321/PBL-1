import pytest
from datetime import datetime, timedelta

from nurture.personality.emotional_memory import EmotionalMemorySystem
from nurture.core.data_structures import EmotionalImpact
from nurture.core.enums import EmotionType, ContextType, ContextCategory, PatternType

class TestEmotionalMemoryEdgeCases:

    def test_memory_capacity_overflow_and_pruning(self):
        memory_system = EmotionalMemorySystem(max_capacity=10)

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

        assert len(memory_system.memories) == 10

        timestamps = [m.timestamp for m in memory_system.memories]
        cutoff = base_time - timedelta(hours=10)
        assert all(t >= cutoff for t in timestamps)

    def test_recall_with_no_matching_memories(self):
        memory_system = EmotionalMemorySystem()

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

        recalled = memory_system.recall_similar(context=ContextType.PUBLIC)
        assert recalled == []

    def test_recall_with_no_memories_at_all(self):
        memory_system = EmotionalMemorySystem()

        recalled = memory_system.recall_similar()
        assert recalled == []

    def test_temporal_decay_application(self):
        memory_system = EmotionalMemorySystem()

        impact = EmotionalImpact(
            primary_emotion=EmotionType.TRUST,
            intensity=0.7,
            valence=0.6,
            context_category=ContextCategory.SUPPORT
        )

        recent_memory = memory_system.store_memory(
            interaction_id="recent",
            emotional_impact=impact,
            timestamp=datetime.now() - timedelta(hours=12)
        )

        week_memory = memory_system.store_memory(
            interaction_id="week",
            emotional_impact=impact,
            timestamp=datetime.now() - timedelta(days=5)
        )

        month_memory = memory_system.store_memory(
            interaction_id="month",
            emotional_impact=impact,
            timestamp=datetime.now() - timedelta(days=20)
        )

        old_memory = memory_system.store_memory(
            interaction_id="old",
            emotional_impact=impact,
            timestamp=datetime.now() - timedelta(days=45)
        )

        memory_system.apply_temporal_decay()

        assert recent_memory.weight == 1.0
        assert week_memory.weight == 0.8
        assert month_memory.weight == 0.5
        assert old_memory.weight < 0.3

    def test_get_emotional_association_empty(self):
        memory_system = EmotionalMemorySystem()

        association = memory_system.get_emotional_association(ContextCategory.SUPPORT)
        assert association == 0.0

    def test_get_emotional_association_accumulation(self):
        memory_system = EmotionalMemorySystem()

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

        support_assoc = memory_system.get_emotional_association(ContextCategory.SUPPORT)
        conflict_assoc = memory_system.get_emotional_association(ContextCategory.CONFLICT)

        assert support_assoc > 0
        assert conflict_assoc < 0
        assert abs(support_assoc - (0.6 * 5)) < 0.01
        assert abs(conflict_assoc - (-0.7 * 3)) < 0.01

    def test_recall_respects_context_filter(self):
        memory_system = EmotionalMemorySystem()

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

        public_memories = memory_system.recall_similar(context=ContextType.PUBLIC)
        assert len(public_memories) == 3
        assert all(m.context == ContextType.PUBLIC for m in public_memories)

        private_memories = memory_system.recall_similar(context=ContextType.PRIVATE)
        assert len(private_memories) == 5
        assert all(m.context == ContextType.PRIVATE for m in private_memories)

    def test_recall_respects_context_category_filter(self):
        memory_system = EmotionalMemorySystem()

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

        for category in categories:
            recalled = memory_system.recall_similar(context_category=category)
            assert len(recalled) == 3
            assert all(m.emotional_impact.context_category == category for m in recalled)

    def test_recall_sorted_by_weight(self):
        memory_system = EmotionalMemorySystem()

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

        recalled = memory_system.recall_similar(limit=10)

        weights = [m.weight for m in recalled]
        assert weights == sorted(weights, reverse=True)

    def test_get_recent_memories(self):
        memory_system = EmotionalMemorySystem()

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

        recent = memory_system.get_recent_memories(hours=12)

        assert len(recent) <= 5

        cutoff = datetime.now() - timedelta(hours=12)
        assert all(m.timestamp >= cutoff for m in recent)

    def test_get_memories_by_emotion(self):
        memory_system = EmotionalMemorySystem()

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

        trust_memories = memory_system.get_memories_by_emotion(EmotionType.TRUST)
        assert len(trust_memories) == 3
        assert all(m.emotional_impact.primary_emotion == EmotionType.TRUST for m in trust_memories)

    def test_get_memories_by_pattern(self):
        memory_system = EmotionalMemorySystem()

        impact = EmotionalImpact(
            primary_emotion=EmotionType.TRUST,
            intensity=0.5,
            valence=0.5,
            context_category=ContextCategory.SUPPORT
        )

        for i in range(3):
            memory_system.store_memory(
                interaction_id=f"presence_{i}",
                emotional_impact=impact,
                associated_patterns=[PatternType.CONSISTENT_PRESENCE]
            )

        for i in range(2):
            memory_system.store_memory(
                interaction_id=f"avoidance_{i}",
                emotional_impact=impact,
                associated_patterns=[PatternType.REPEATED_AVOIDANCE]
            )

        presence_memories = memory_system.get_memories_by_pattern(PatternType.CONSISTENT_PRESENCE)
        assert len(presence_memories) == 3

        avoidance_memories = memory_system.get_memories_by_pattern(PatternType.REPEATED_AVOIDANCE)
        assert len(avoidance_memories) == 2

    def test_get_average_valence(self):
        memory_system = EmotionalMemorySystem()

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

        avg = memory_system.get_average_valence(days=7)
        assert abs(avg - 0.8) < 0.01

    def test_get_average_valence_by_category(self):
        memory_system = EmotionalMemorySystem()

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

        support_avg = memory_system.get_average_valence(context_category=ContextCategory.SUPPORT)
        conflict_avg = memory_system.get_average_valence(context_category=ContextCategory.CONFLICT)

        assert abs(support_avg - 0.9) < 0.01
        assert abs(conflict_avg - (-0.6)) < 0.01

    def test_clear_old_memories(self):
        memory_system = EmotionalMemorySystem()

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

        removed = memory_system.clear_old_memories(days=180)

        assert removed > 0

        cutoff = datetime.now() - timedelta(days=180)
        assert all(m.timestamp >= cutoff for m in memory_system.memories)

    def test_get_memory_stats(self):
        memory_system = EmotionalMemorySystem()

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
        memory_system = EmotionalMemorySystem(max_capacity=500, decay_rate=0.1)

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

        data = memory_system.to_dict()

        assert 'memories' in data
        assert 'context_associations' in data
        assert 'max_capacity' in data
        assert 'decay_rate' in data

        assert data['max_capacity'] == 500
        assert data['decay_rate'] == 0.1
        assert len(data['memories']) == 10

        restored = EmotionalMemorySystem.from_dict(data)

        assert len(restored.memories) == 10
        assert restored.max_capacity == 500
        assert restored.decay_rate == 0.1
