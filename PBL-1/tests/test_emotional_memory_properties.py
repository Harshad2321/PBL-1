"""
Property-based tests for EmotionalMemorySystem.

Tests emotional memory storage format, context categorization,
temporal weighting, and response adaptation.
"""
import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime, timedelta

from nurture.personality.emotional_memory import EmotionalMemorySystem
from nurture.core.data_structures import EmotionalImpact
from nurture.core.enums import EmotionType, ContextType, ContextCategory, PatternType


# Hypothesis strategies
@st.composite
def emotional_impact_strategy(draw, valence_range=(-1.0, 1.0)):
    """Generate random EmotionalImpact instances."""
    return EmotionalImpact(
        primary_emotion=draw(st.sampled_from(list(EmotionType))),
        intensity=draw(st.floats(min_value=0.0, max_value=1.0)),
        valence=draw(st.floats(min_value=valence_range[0], max_value=valence_range[1])),
        context_category=draw(st.sampled_from(list(ContextCategory)))
    )


@st.composite
def memory_entry_strategy(draw):
    """Generate random memory entry parameters."""
    return {
        'interaction_id': f"interaction_{draw(st.integers(min_value=1, max_value=10000))}",
        'emotional_impact': draw(emotional_impact_strategy()),
        'context': draw(st.sampled_from(list(ContextType))),
        'associated_patterns': draw(st.lists(st.sampled_from(list(PatternType)), max_size=3)),
        'timestamp': datetime.now() - timedelta(days=draw(st.integers(min_value=0, max_value=60)))
    }


# Property 4: Emotional memory storage format
# Validates: Requirements 2.1, 2.3

@given(st.lists(memory_entry_strategy(), min_size=1, max_size=50))
def test_emotional_memory_storage_format(memory_entries):
    """
    Property: For any interaction stored in emotional memory, the memory
    should contain emotional impact data (emotion type, intensity, valence,
    context category) but should not contain verbatim dialogue text.
    
    **Validates: Requirements 2.1, 2.3**
    """
    memory_system = EmotionalMemorySystem()
    
    # Store all memories
    for entry in memory_entries:
        memory = memory_system.store_memory(**entry)
        
        # Verify memory contains emotional impact data
        assert memory.emotional_impact is not None
        assert memory.emotional_impact.primary_emotion in EmotionType
        assert 0.0 <= memory.emotional_impact.intensity <= 1.0
        assert -1.0 <= memory.emotional_impact.valence <= 1.0
        assert memory.emotional_impact.context_category in ContextCategory
        
        # Verify memory has timestamp
        assert memory.timestamp is not None
        
        # Verify memory has context
        assert memory.context in ContextType
        
        # Verify no verbatim text is stored
        # (EmotionalMemory dataclass should not have a 'text' or 'dialogue' field)
        assert not hasattr(memory, 'text')
        assert not hasattr(memory, 'dialogue')
        assert not hasattr(memory, 'verbatim')
        assert not hasattr(memory, 'content')


# Property 5: Memory context categorization
# Validates: Requirements 2.2

@given(st.lists(memory_entry_strategy(), min_size=1, max_size=50))
def test_memory_context_categorization(memory_entries):
    """
    Property: For any emotional memory entry, it must be associated with
    exactly one valid context category (SUPPORT, CONFLICT, PARENTING, or INTIMACY).
    
    **Validates: Requirements 2.2**
    """
    memory_system = EmotionalMemorySystem()
    
    # Store all memories
    for entry in memory_entries:
        memory = memory_system.store_memory(**entry)
        
        # Verify exactly one context category
        assert memory.emotional_impact.context_category in ContextCategory
        
        # Verify it's one of the valid categories
        valid_categories = {
            ContextCategory.SUPPORT,
            ContextCategory.CONFLICT,
            ContextCategory.PARENTING,
            ContextCategory.INTIMACY
        }
        assert memory.emotional_impact.context_category in valid_categories


# Property 6: Temporal memory weighting
# Validates: Requirements 2.4

@given(
    st.integers(min_value=0, max_value=60),  # days_ago_1
    st.integers(min_value=0, max_value=60)   # days_ago_2
)
def test_temporal_memory_weighting(days_ago_1, days_ago_2):
    """
    Property: For any two emotional memories with the same emotional impact,
    the more recent memory should have a higher weight than the older memory,
    with weight decreasing according to the temporal decay function.
    
    **Validates: Requirements 2.4**
    """
    # Ensure memories have different ages
    assume(days_ago_1 != days_ago_2)
    
    memory_system = EmotionalMemorySystem()
    
    # Create identical emotional impacts
    impact = EmotionalImpact(
        primary_emotion=EmotionType.TRUST,
        intensity=0.7,
        valence=0.6,
        context_category=ContextCategory.SUPPORT
    )
    
    # Store two memories with different timestamps
    timestamp_1 = datetime.now() - timedelta(days=days_ago_1)
    timestamp_2 = datetime.now() - timedelta(days=days_ago_2)
    
    memory_1 = memory_system.store_memory(
        interaction_id="interaction_1",
        emotional_impact=impact,
        timestamp=timestamp_1
    )
    
    memory_2 = memory_system.store_memory(
        interaction_id="interaction_2",
        emotional_impact=impact,
        timestamp=timestamp_2
    )
    
    # Apply temporal decay
    memory_system.apply_temporal_decay()
    
    # More recent memory should have higher weight
    if days_ago_1 < days_ago_2:
        assert memory_1.weight >= memory_2.weight
    else:
        assert memory_2.weight >= memory_1.weight
    
    # Verify weight follows temporal decay function
    for memory, days_ago in [(memory_1, days_ago_1), (memory_2, days_ago_2)]:
        if days_ago < 1:
            assert memory.weight == 1.0
        elif days_ago < 7:
            assert memory.weight == 0.8
        elif days_ago < 30:
            assert memory.weight == 0.5
        else:
            # Should be 0.3 with additional exponential decay
            assert memory.weight <= 0.3


# Property 7: Response adaptation from emotional history
# Validates: Requirements 2.5

@given(
    st.lists(emotional_impact_strategy(valence_range=(0.5, 1.0)), min_size=5, max_size=20),  # positive
    st.lists(emotional_impact_strategy(valence_range=(-1.0, -0.5)), min_size=5, max_size=20)  # negative
)
def test_response_adaptation_from_emotional_history(positive_impacts, negative_impacts):
    """
    Property: For any situation type, responses generated after accumulating
    positive emotional associations should differ measurably from responses
    generated after accumulating negative emotional associations for that
    situation type.
    
    **Validates: Requirements 2.5**
    """
    # Test with positive emotional history
    positive_system = EmotionalMemorySystem()
    for i, impact in enumerate(positive_impacts):
        positive_system.store_memory(
            interaction_id=f"positive_{i}",
            emotional_impact=impact,
            timestamp=datetime.now() - timedelta(hours=i)
        )
    
    # Test with negative emotional history
    negative_system = EmotionalMemorySystem()
    for i, impact in enumerate(negative_impacts):
        negative_system.store_memory(
            interaction_id=f"negative_{i}",
            emotional_impact=impact,
            timestamp=datetime.now() - timedelta(hours=i)
        )
    
    # Get emotional associations for each context category
    for category in ContextCategory:
        positive_association = positive_system.get_emotional_association(category)
        negative_association = negative_system.get_emotional_association(category)
        
        # If both systems have memories in this category, associations should differ
        positive_memories = [m for m in positive_system.memories if m.emotional_impact.context_category == category]
        negative_memories = [m for m in negative_system.memories if m.emotional_impact.context_category == category]
        
        if positive_memories and negative_memories:
            # Positive system should have higher association than negative system
            assert positive_association > negative_association


# Additional property tests for edge cases

@given(st.integers(min_value=1, max_value=1500))
def test_memory_capacity_pruning(num_memories):
    """
    Property: When memory storage exceeds maximum capacity (1000),
    the system should prune oldest memories while keeping recent ones.
    """
    memory_system = EmotionalMemorySystem(max_capacity=1000)
    
    # Store many memories
    for i in range(num_memories):
        impact = EmotionalImpact(
            primary_emotion=EmotionType.TRUST,
            intensity=0.5,
            valence=0.5,
            context_category=ContextCategory.SUPPORT
        )
        memory_system.store_memory(
            interaction_id=f"interaction_{i}",
            emotional_impact=impact,
            timestamp=datetime.now() - timedelta(hours=num_memories - i)
        )
    
    # Should never exceed max capacity
    assert len(memory_system.memories) <= 1000
    
    if num_memories > 1000:
        # Should have pruned oldest memories
        assert len(memory_system.memories) == 1000
        
        # Most recent memories should be kept
        most_recent = memory_system.memories[0]
        assert most_recent.timestamp >= datetime.now() - timedelta(hours=1000)


@given(st.sampled_from(list(ContextType)), st.sampled_from(list(ContextCategory)))
def test_recall_with_no_matches(context, context_category):
    """
    Property: Recall query with no matching memories should return empty list.
    """
    memory_system = EmotionalMemorySystem()
    
    # Don't store any memories
    
    # Recall should return empty list
    recalled = memory_system.recall_similar(context=context, context_category=context_category)
    assert recalled == []


@given(st.lists(memory_entry_strategy(), min_size=1, max_size=50))
def test_recall_respects_limit(memory_entries):
    """
    Property: Recall should respect the limit parameter and return
    at most that many memories.
    """
    memory_system = EmotionalMemorySystem()
    
    # Store memories
    for entry in memory_entries:
        memory_system.store_memory(**entry)
    
    # Recall with various limits
    for limit in [1, 3, 5, 10]:
        recalled = memory_system.recall_similar(limit=limit)
        assert len(recalled) <= limit


@given(st.lists(memory_entry_strategy(), min_size=1, max_size=50))
def test_serialization_round_trip(memory_entries):
    """
    Property: Serializing and deserializing a memory system should
    preserve all memories and associations.
    """
    memory_system = EmotionalMemorySystem()
    
    # Store memories
    for entry in memory_entries:
        memory_system.store_memory(**entry)
    
    # Serialize
    data = memory_system.to_dict()
    
    # Deserialize
    restored_system = EmotionalMemorySystem.from_dict(data)
    
    # Should have same number of memories
    assert len(restored_system.memories) == len(memory_system.memories)
    
    # Should have same context associations
    for category in ContextCategory:
        original_assoc = memory_system.get_emotional_association(category)
        restored_assoc = restored_system.get_emotional_association(category)
        assert abs(original_assoc - restored_assoc) < 0.0001
