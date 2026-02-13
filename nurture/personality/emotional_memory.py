from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from nurture.core.data_structures import EmotionalMemory, EmotionalImpact
from nurture.core.enums import ContextType, ContextCategory, EmotionType, PatternType

class EmotionalMemorySystem:

    def __init__(
        self,
        max_capacity: int = 1000,
        decay_rate: float = 0.05
    ):
        self.memories: List[EmotionalMemory] = []
        self.context_associations: Dict[ContextCategory, float] = defaultdict(float)
        self.max_capacity = max_capacity
        self.decay_rate = decay_rate

        self._weight_thresholds = {
            timedelta(hours=24): 1.0,
            timedelta(days=7): 0.8,
            timedelta(days=30): 0.5,
            timedelta(days=365): 0.3,
        }

    def store_memory(
        self,
        interaction_id: str,
        emotional_impact: EmotionalImpact,
        context: ContextType = ContextType.PRIVATE,
        associated_patterns: Optional[List[PatternType]] = None,
        timestamp: Optional[datetime] = None
    ) -> EmotionalMemory:
        if timestamp is None:
            timestamp = datetime.now()

        if associated_patterns is None:
            associated_patterns = []

        memory = EmotionalMemory(
            emotional_impact=emotional_impact,
            timestamp=timestamp,
            context=context,
            weight=1.0,
            associated_patterns=associated_patterns
        )

        self.memories.append(memory)

        self.context_associations[emotional_impact.context_category] += emotional_impact.valence

        if len(self.memories) > self.max_capacity:
            self._prune_oldest_memories()

        return memory

    def _prune_oldest_memories(self) -> None:
        self.memories.sort(key=lambda m: m.timestamp, reverse=True)

        self.memories = self.memories[:self.max_capacity]

    def recall_similar(
        self,
        context: Optional[ContextType] = None,
        context_category: Optional[ContextCategory] = None,
        limit: int = 5
    ) -> List[EmotionalMemory]:
        self.apply_temporal_decay()

        filtered = self.memories

        if context is not None:
            filtered = [m for m in filtered if m.context == context]

        if context_category is not None:
            filtered = [
                m for m in filtered
                if m.emotional_impact.context_category == context_category
            ]

        filtered.sort(key=lambda m: m.weight, reverse=True)

        return filtered[:limit]

    def get_emotional_association(
        self,
        context_category: ContextCategory
    ) -> float:
        return self.context_associations.get(context_category, 0.0)

    def apply_temporal_decay(self) -> None:
        now = datetime.now()

        for memory in self.memories:
            age = now - memory.timestamp

            if age < timedelta(hours=24):
                memory.weight = 1.0
            elif age < timedelta(days=7):
                memory.weight = 0.8
            elif age < timedelta(days=30):
                memory.weight = 0.5
            else:
                memory.weight = 0.3

            if age > timedelta(days=30):
                days_over_30 = (age - timedelta(days=30)).days
                decay_factor = (1.0 - self.decay_rate) ** days_over_30
                memory.weight *= decay_factor

    def get_recent_memories(
        self,
        hours: int = 24,
        limit: Optional[int] = None
    ) -> List[EmotionalMemory]:
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
        cutoff = datetime.now() - timedelta(days=days)
        initial_count = len(self.memories)

        self.memories = [m for m in self.memories if m.timestamp >= cutoff]

        return initial_count - len(self.memories)

    def get_memory_count(self) -> int:
        return len(self.memories)

    def get_memory_stats(self) -> Dict[str, any]:
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
        system = cls(
            max_capacity=data.get("max_capacity", 1000),
            decay_rate=data.get("decay_rate", 0.05)
        )

        system.memories = [
            EmotionalMemory.from_dict(m_data)
            for m_data in data.get("memories", [])
        ]

        system.context_associations = defaultdict(
            float,
            {
                ContextCategory(cat): val
                for cat, val in data.get("context_associations", {}).items()
            }
        )

        return system
