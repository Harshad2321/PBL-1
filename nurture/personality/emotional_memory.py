"""
Emotional Memory System
=======================

Stores how interactions made the Mother AI feel rather than verbatim content.

The EmotionalMemorySystem maintains a collection of emotional memories that
capture the feeling of interactions without storing exact dialogue. Memories
are weighted by recency and can be recalled based on context similarity.

Key Features:
- Stores emotional impact, not verbatim text
- Context-based categorization (support, conflict, parenting, intimacy)
- Temporal weighting (recent memories weighted more heavily)
- Automatic pruning when capacity exceeds 1000 entries
- Integration with existing MemoryStore

Example:
    memory_system = EmotionalMemorySystem()
    
    # Store a memory
    impact = EmotionalImpact(
        primary_emotion=EmotionType.DISAPPOINTMENT,
        intensity=0.7,
        valence=-0.6,
        context_category=ContextCategory.CONFLICT
    )
    memory_system.store_memory(interaction, impact)
    
    # Recall similar memories
    similar = memory_system.recall_similar(ContextType.PRIVATE, limit=5)
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from nurture.core.data_structures import EmotionalMemory, EmotionalImpact
from nurture.core.enums import ContextType, ContextCategory, EmotionType, PatternType


class EmotionalMemorySystem:
    """
    Manages emotional memories of interactions.
    
    Stores how interactions made the Mother AI feel, with temporal
    weighting and context-based retrieval. Memories are pruned when
    capacity is exceeded.
    
    Attributes:
        memories: List of all emotional memories
        context_associations: Accumulated emotional associations by context
        max_capacity: Maximum number of memories to store (default: 1000)
        decay_rate: Rate at which memory weights decay (default: 0.05 per day)
    """
    
    def __init__(
        self,
        max_capacity: int = 1000,
        decay_rate: float = 0.05
    ):
        """
        Initialize emotional memory system.
        
        Args:
            max_capacity: Maximum number of memories to store
            decay_rate: Daily decay rate for memory weights (0.0 to 1.0)
        """
        self.memories: List[EmotionalMemory] = []
        self.context_associations: Dict[ContextCategory, float] = defaultdict(float)
        self.max_capacity = max_capacity
        self.decay_rate = decay_rate
        
        # Temporal weighting thresholds
        self._weight_thresholds = {
            timedelta(hours=24): 1.0,      # < 24 hours: full weight
            timedelta(days=7): 0.8,        # 1-7 days: 80% weight
            timedelta(days=30): 0.5,       # 7-30 days: 50% weight
            timedelta(days=365): 0.3,      # > 30 days: 30% weight
        }
    
    def store_memory(
        self,
        interaction_id: str,
        emotional_impact: EmotionalImpact,
        context: ContextType = ContextType.PRIVATE,
        associated_patterns: Optional[List[PatternType]] = None,
        timestamp: Optional[datetime] = None
    ) -> EmotionalMemory:
        """
        Store emotional memory of an interaction.
        
        Stores the emotional impact without verbatim dialogue content.
        
        Args:
            interaction_id: Unique identifier for the interaction
            emotional_impact: How the interaction felt
            context: Public or private context
            associated_patterns: Patterns active during this memory
            timestamp: When the interaction occurred (defaults to now)
        
        Returns:
            The created EmotionalMemory
        
        Validates: Requirements 2.1, 2.2
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        if associated_patterns is None:
            associated_patterns = []
        
        # Create memory
        memory = EmotionalMemory(
            emotional_impact=emotional_impact,
            timestamp=timestamp,
            context=context,
            weight=1.0,  # Start with full weight
            associated_patterns=associated_patterns
        )
        
        self.memories.append(memory)
        
        # Update context associations
        self.context_associations[emotional_impact.context_category] += emotional_impact.valence
        
        # Prune if over capacity
        if len(self.memories) > self.max_capacity:
            self._prune_oldest_memories()
        
        return memory
    
    def _prune_oldest_memories(self) -> None:
        """
        Remove oldest memories when capacity is exceeded.
        
        Keeps the most recent memories up to max_capacity.
        """
        # Sort by timestamp (newest first)
        self.memories.sort(key=lambda m: m.timestamp, reverse=True)
        
        # Keep only max_capacity memories
        self.memories = self.memories[:self.max_capacity]
    
    def recall_similar(
        self,
        context: Optional[ContextType] = None,
        context_category: Optional[ContextCategory] = None,
        limit: int = 5
    ) -> List[EmotionalMemory]:
        """
        Recall memories from similar contexts, weighted by recency.
        
        Returns memories that match the specified context, with more
        recent memories weighted more heavily.
        
        Args:
            context: Filter by public/private context (optional)
            context_category: Filter by context category (optional)
            limit: Maximum number of memories to return
        
        Returns:
            List of relevant memories, sorted by weight (highest first)
        
        Validates: Requirements 2.3, 2.4
        """
        # Apply temporal decay to all memories
        self.apply_temporal_decay()
        
        # Filter memories by context
        filtered = self.memories
        
        if context is not None:
            filtered = [m for m in filtered if m.context == context]
        
        if context_category is not None:
            filtered = [
                m for m in filtered
                if m.emotional_impact.context_category == context_category
            ]
        
        # Sort by weight (recency-weighted)
        filtered.sort(key=lambda m: m.weight, reverse=True)
        
        return filtered[:limit]
    
    def get_emotional_association(
        self,
        context_category: ContextCategory
    ) -> float:
        """
        Get accumulated emotional association for a context type.
        
        Returns the sum of emotional valences for all memories in
        the specified context category.
        
        Args:
            context_category: The context category to check
        
        Returns:
            Accumulated emotional valence (can be positive or negative)
        
        Validates: Requirements 2.5
        """
        return self.context_associations.get(context_category, 0.0)
    
    def apply_temporal_decay(self) -> None:
        """
        Apply time-based decay to older memories.
        
        Memory weights decrease based on how long ago they occurred,
        following the temporal weighting thresholds.
        
        Validates: Requirements 2.4
        """
        now = datetime.now()
        
        for memory in self.memories:
            age = now - memory.timestamp
            
            # Determine weight based on age
            if age < timedelta(hours=24):
                memory.weight = 1.0
            elif age < timedelta(days=7):
                memory.weight = 0.8
            elif age < timedelta(days=30):
                memory.weight = 0.5
            else:
                memory.weight = 0.3
            
            # Apply additional exponential decay for very old memories
            if age > timedelta(days=30):
                days_over_30 = (age - timedelta(days=30)).days
                decay_factor = (1.0 - self.decay_rate) ** days_over_30
                memory.weight *= decay_factor
    
    def get_recent_memories(
        self,
        hours: int = 24,
        limit: Optional[int] = None
    ) -> List[EmotionalMemory]:
        """
        Get memories from the last N hours.
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of memories to return (optional)
        
        Returns:
            List of recent memories
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [m for m in self.memories if m.timestamp >= cutoff]
        recent.sort(key=lambda m: m.timestamp, reverse=True)
        
        if limit is not None:
            recent = recent[:limit]
        
        return recent
    
    def get_memories_by_emotion(
        self,
        emotion: EmotionType,
        limit: int = 10
    ) -> List[EmotionalMemory]:
        """
        Get memories associated with a specific emotion.
        
        Args:
            emotion: The emotion type to filter by
            limit: Maximum number of memories to return
        
        Returns:
            List of memories with the specified primary emotion
        """
        filtered = [
            m for m in self.memories
            if m.emotional_impact.primary_emotion == emotion
        ]
        filtered.sort(key=lambda m: m.timestamp, reverse=True)
        return filtered[:limit]
    
    def get_memories_by_pattern(
        self,
        pattern_type: PatternType,
        limit: int = 10
    ) -> List[EmotionalMemory]:
        """
        Get memories associated with a specific behavioral pattern.
        
        Args:
            pattern_type: The pattern type to filter by
            limit: Maximum number of memories to return
        
        Returns:
            List of memories associated with the pattern
        """
        filtered = [
            m for m in self.memories
            if pattern_type in m.associated_patterns
        ]
        filtered.sort(key=lambda m: m.timestamp, reverse=True)
        return filtered[:limit]
    
    def get_average_valence(
        self,
        context_category: Optional[ContextCategory] = None,
        days: int = 7
    ) -> float:
        """
        Get average emotional valence over recent period.
        
        Args:
            context_category: Filter by context category (optional)
            days: Number of days to look back
        
        Returns:
            Average valence (-1.0 to 1.0), or 0.0 if no memories
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent = [m for m in self.memories if m.timestamp >= cutoff]
        
        if context_category is not None:
            recent = [
                m for m in recent
                if m.emotional_impact.context_category == context_category
            ]
        
        if not recent:
            return 0.0
        
        total_valence = sum(m.emotional_impact.valence for m in recent)
        return total_valence / len(recent)
    
    def clear_old_memories(self, days: int = 365) -> int:
        """
        Remove memories older than specified days.
        
        Args:
            days: Remove memories older than this many days
        
        Returns:
            Number of memories removed
        """
        cutoff = datetime.now() - timedelta(days=days)
        initial_count = len(self.memories)
        
        self.memories = [m for m in self.memories if m.timestamp >= cutoff]
        
        return initial_count - len(self.memories)
    
    def get_memory_count(self) -> int:
        """Get total number of stored memories."""
        return len(self.memories)
    
    def get_memory_stats(self) -> Dict[str, any]:
        """
        Get statistics about stored memories.
        
        Returns:
            Dictionary with memory statistics
        """
        if not self.memories:
            return {
                "total_memories": 0,
                "average_valence": 0.0,
                "oldest_memory_age_days": 0,
                "newest_memory_age_hours": 0,
                "context_breakdown": {},
            }
        
        now = datetime.now()
        oldest = min(m.timestamp for m in self.memories)
        newest = max(m.timestamp for m in self.memories)
        
        # Count by context category
        context_counts = defaultdict(int)
        for memory in self.memories:
            context_counts[memory.emotional_impact.context_category.value] += 1
        
        return {
            "total_memories": len(self.memories),
            "average_valence": sum(m.emotional_impact.valence for m in self.memories) / len(self.memories),
            "oldest_memory_age_days": (now - oldest).days,
            "newest_memory_age_hours": (now - newest).total_seconds() / 3600,
            "context_breakdown": dict(context_counts),
        }
    
    def to_dict(self) -> Dict:
        """
        Serialize emotional memory system to dictionary.
        
        Returns:
            Dictionary containing all memory system state
        """
        return {
            "memories": [m.to_dict() for m in self.memories],
            "context_associations": {
                cat.value: val
                for cat, val in self.context_associations.items()
            },
            "max_capacity": self.max_capacity,
            "decay_rate": self.decay_rate,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EmotionalMemorySystem':
        """
        Deserialize emotional memory system from dictionary.
        
        Args:
            data: Dictionary containing memory system state
        
        Returns:
            Restored EmotionalMemorySystem instance
        """
        system = cls(
            max_capacity=data.get("max_capacity", 1000),
            decay_rate=data.get("decay_rate", 0.05)
        )
        
        # Restore memories
        system.memories = [
            EmotionalMemory.from_dict(m_data)
            for m_data in data.get("memories", [])
        ]
        
        # Restore context associations
        system.context_associations = defaultdict(
            float,
            {
                ContextCategory(cat): val
                for cat, val in data.get("context_associations", {}).items()
            }
        )
        
        return system
