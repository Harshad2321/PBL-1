from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime
import uuid
import json
from pathlib import Path

from nurture.core.enums import MemoryType, EmotionType

@dataclass
class Memory:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    memory_type: MemoryType = MemoryType.INTERACTION
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    emotional_valence: float = 0.0
    emotional_intensity: float = 0.5
    associated_agent_id: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    importance: float = 0.5
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    decay_resistance: float = 0.5
    context: Dict[str, Any] = field(default_factory=dict)

    def calculate_retrieval_strength(self) -> float:
        now = datetime.now()
        age_hours = (now - self.timestamp).total_seconds() / 3600
        recency_factor = 1.0 / (1.0 + 0.01 * age_hours)

        access_factor = min(1.0, 0.5 + 0.05 * self.access_count)

        strength = (
            0.25 * recency_factor +
            0.30 * self.emotional_intensity +
            0.20 * access_factor +
            0.25 * self.importance
        ) * self.decay_resistance

        return min(1.0, max(0.0, strength))

    def access(self) -> None:
        self.access_count += 1
        self.last_accessed = datetime.now()
        self.decay_resistance = min(1.0, self.decay_resistance + 0.02)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "emotional_valence": self.emotional_valence,
            "emotional_intensity": self.emotional_intensity,
            "associated_agent_id": self.associated_agent_id,
            "tags": list(self.tags),
            "importance": self.importance,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "decay_resistance": self.decay_resistance,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            memory_type=MemoryType(data.get("memory_type", "interaction")),
            content=data.get("content", ""),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            emotional_valence=data.get("emotional_valence", 0.0),
            emotional_intensity=data.get("emotional_intensity", 0.5),
            associated_agent_id=data.get("associated_agent_id"),
            tags=set(data.get("tags", [])),
            importance=data.get("importance", 0.5),
            access_count=data.get("access_count", 0),
            last_accessed=datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else None,
            decay_resistance=data.get("decay_resistance", 0.5),
            context=data.get("context", {}),
        )

class MemoryStore:

    def __init__(self, agent_id: str, max_capacity: int = 500):
        self.agent_id = agent_id
        self.max_capacity = max_capacity
        self.memories: List[Memory] = []
        self._importance_threshold = 0.2

    def add_memory(self, memory: Memory) -> None:
        self.memories.append(memory)

        if len(self.memories) > self.max_capacity:
            self._prune_memories()

    def create_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.INTERACTION,
        emotional_valence: float = 0.0,
        emotional_intensity: float = 0.5,
        tags: Optional[Set[str]] = None,
        importance: float = 0.5,
        associated_agent_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Memory:
        memory = Memory(
            memory_type=memory_type,
            content=content,
            emotional_valence=emotional_valence,
            emotional_intensity=emotional_intensity,
            tags=tags or set(),
            importance=importance,
            associated_agent_id=associated_agent_id,
            context=context or {},
        )
        self.add_memory(memory)
        return memory

    def _prune_memories(self) -> None:
        scored = [(m, m.importance * m.decay_resistance * m.calculate_retrieval_strength())
                  for m in self.memories]
        scored.sort(key=lambda x: x[1], reverse=True)
        self.memories = [m for m, _ in scored[:self.max_capacity]]

    def retrieve_by_tags(self, tags: Set[str], limit: int = 10) -> List[Memory]:
        matching = [m for m in self.memories if m.tags & tags]
        matching.sort(key=lambda m: m.importance * m.calculate_retrieval_strength(),
                     reverse=True)

        for m in matching[:limit]:
            m.access()

        return matching[:limit]

    def retrieve_by_emotion(
        self,
        valence_range: Tuple[float, float],
        limit: int = 10
    ) -> List[Memory]:
        min_val, max_val = valence_range
        matching = [m for m in self.memories
                   if min_val <= m.emotional_valence <= max_val]
        matching.sort(key=lambda m: m.emotional_intensity, reverse=True)

        for m in matching[:limit]:
            m.access()

        return matching[:limit]

    def retrieve_by_type(self, memory_type: MemoryType, limit: int = 10) -> List[Memory]:
        matching = [m for m in self.memories if m.memory_type == memory_type]
        matching.sort(key=lambda m: m.timestamp, reverse=True)

        for m in matching[:limit]:
            m.access()

        return matching[:limit]

    def get_recent(self, count: int = 5) -> List[Memory]:
        sorted_memories = sorted(self.memories,
                                key=lambda m: m.timestamp, reverse=True)
        return sorted_memories[:count]

    def get_related_to_agent(self, agent_id: str, limit: int = 10) -> List[Memory]:
        matching = [m for m in self.memories
                   if m.associated_agent_id == agent_id]
        matching.sort(key=lambda m: m.timestamp, reverse=True)
        return matching[:limit]

    def get_pattern_summary(self, tag: str) -> Dict[str, Any]:
        tagged = [m for m in self.memories if tag in m.tags]
        if not tagged:
            return {
                "count": 0,
                "avg_valence": 0.0,
                "avg_intensity": 0.0,
                "trend": "neutral"
            }

        avg_valence = sum(m.emotional_valence for m in tagged) / len(tagged)
        avg_intensity = sum(m.emotional_intensity for m in tagged) / len(tagged)

        tagged.sort(key=lambda m: m.timestamp, reverse=True)
        if len(tagged) >= 4:
            recent = tagged[:len(tagged)//2]
            older = tagged[len(tagged)//2:]
            recent_val = sum(m.emotional_valence for m in recent) / len(recent)
            older_val = sum(m.emotional_valence for m in older) / len(older)
            if recent_val > older_val + 0.1:
                trend = "improving"
            elif recent_val < older_val - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "count": len(tagged),
            "avg_valence": avg_valence,
            "avg_intensity": avg_intensity,
            "trend": trend,
        }

    def search(self, query: str, limit: int = 10) -> List[Memory]:
        query_lower = query.lower()
        matching = [m for m in self.memories
                   if query_lower in m.content.lower()]
        matching.sort(key=lambda m: m.calculate_retrieval_strength(), reverse=True)
        return matching[:limit]

    def save_to_file(self, filepath: Path) -> None:
        data = {
            "agent_id": self.agent_id,
            "max_capacity": self.max_capacity,
            "memories": [m.to_dict() for m in self.memories],
        }
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: Path) -> 'MemoryStore':
        with open(filepath, 'r') as f:
            data = json.load(f)

        store = cls(
            agent_id=data["agent_id"],
            max_capacity=data.get("max_capacity", 500)
        )
        store.memories = [Memory.from_dict(m) for m in data.get("memories", [])]
        return store

    def clear(self) -> None:
        self.memories.clear()

    def __len__(self) -> int:
        return len(self.memories)
