from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime
from collections import defaultdict, OrderedDict
import uuid
import json
from pathlib import Path

from nurture.core.enums import MemoryType, EmotionType

@dataclass
class FastMemory:
    __slots__ = [
        'id', 'content', 'memory_type', 'timestamp',
        'emotional_valence', 'importance', 'tags',
        'access_count', 'agent_id', 'context'
    ]

    id: str
    content: str
    memory_type: MemoryType
    timestamp: float
    emotional_valence: float
    importance: float
    tags: frozenset
    access_count: int
    agent_id: Optional[str]
    context: Dict[str, Any]

    def __init__(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.INTERACTION,
        emotional_valence: float = 0.0,
        importance: float = 0.5,
        tags: Optional[Set[str]] = None,
        agent_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        timestamp: Optional[float] = None
    ):
        self.id = id or str(uuid.uuid4())[:8]
        self.content = content
        self.memory_type = memory_type
        self.timestamp = timestamp or datetime.now().timestamp()
        self.emotional_valence = emotional_valence
        self.importance = importance
        self.tags = frozenset(tags) if tags else frozenset()
        self.access_count = 0
        self.agent_id = agent_id
        self.context = context or {}

    @property
    def age_hours(self) -> float:
        return (datetime.now().timestamp() - self.timestamp) / 3600

    @property
    def retrieval_strength(self) -> float:
        recency = 1.0 / (1.0 + 0.01 * self.age_hours)
        access_boost = min(0.3, 0.03 * self.access_count)
        return (0.4 * self.importance + 0.4 * recency + 0.2 * abs(self.emotional_valence) + access_boost)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "timestamp": self.timestamp,
            "emotional_valence": self.emotional_valence,
            "importance": self.importance,
            "tags": list(self.tags),
            "access_count": self.access_count,
            "agent_id": self.agent_id,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FastMemory':
        return cls(
            id=data.get("id"),
            content=data.get("content", ""),
            memory_type=MemoryType(data.get("memory_type", "interaction")),
            timestamp=data.get("timestamp"),
            emotional_valence=data.get("emotional_valence", 0.0),
            importance=data.get("importance", 0.5),
            tags=set(data.get("tags", [])),
            agent_id=data.get("agent_id"),
            context=data.get("context", {}),
        )

class LRUCache:

    def __init__(self, max_size: int = 50):
        self._cache: OrderedDict[str, FastMemory] = OrderedDict()
        self._max_size = max_size

    def get(self, key: str) -> Optional[FastMemory]:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key: str, value: FastMemory) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
            self._cache[key] = value

    def invalidate(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()

class FastMemoryStore:

    def __init__(self, agent_id: str, max_capacity: int = 500, cache_size: int = 50):
        self.agent_id = agent_id
        self.max_capacity = max_capacity

        self._memories: Dict[str, FastMemory] = {}

        self._tag_index: Dict[str, Set[str]] = defaultdict(set)
        self._type_index: Dict[MemoryType, Set[str]] = defaultdict(set)
        self._emotion_index: Dict[str, Set[str]] = defaultdict(set)
        self._agent_index: Dict[str, Set[str]] = defaultdict(set)

        self._cache = LRUCache(cache_size)

        self._by_time: List[str] = []

    def add(self, memory: FastMemory) -> str:
        if len(self._memories) >= self.max_capacity:
            self._prune(count=self.max_capacity // 10)

        self._memories[memory.id] = memory

        for tag in memory.tags:
            self._tag_index[tag].add(memory.id)

        self._type_index[memory.memory_type].add(memory.id)

        if memory.emotional_valence > 0.2:
            self._emotion_index["positive"].add(memory.id)
        elif memory.emotional_valence < -0.2:
            self._emotion_index["negative"].add(memory.id)
        else:
            self._emotion_index["neutral"].add(memory.id)

        if memory.agent_id:
            self._agent_index[memory.agent_id].add(memory.id)

        self._insert_by_time(memory.id, memory.timestamp)

        return memory.id

    def _insert_by_time(self, memory_id: str, timestamp: float) -> None:
        if len(self._by_time) < 100:
            self._by_time.append(memory_id)
            self._by_time.sort(key=lambda mid: self._memories.get(mid, FastMemory("")).timestamp, reverse=True)
        else:
            left, right = 0, len(self._by_time)
            while left < right:
                mid = (left + right) // 2
                mid_mem = self._memories.get(self._by_time[mid])
                if mid_mem and mid_mem.timestamp > timestamp:
                    left = mid + 1
                else:
                    right = mid
            self._by_time.insert(left, memory_id)

    def create(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.INTERACTION,
        emotional_valence: float = 0.0,
        importance: float = 0.5,
        tags: Optional[Set[str]] = None,
        agent_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> FastMemory:
        memory = FastMemory(
            content=content,
            memory_type=memory_type,
            emotional_valence=emotional_valence,
            importance=importance,
            tags=tags,
            agent_id=agent_id,
            context=context
        )
        self.add(memory)
        return memory

    def get(self, memory_id: str) -> Optional[FastMemory]:
        cached = self._cache.get(memory_id)
        if cached:
            cached.access_count += 1
            return cached

        memory = self._memories.get(memory_id)
        if memory:
            memory.access_count += 1
            self._cache.put(memory_id, memory)
        return memory

    def get_by_tag(self, tag: str, limit: int = 10) -> List[FastMemory]:
        memory_ids = self._tag_index.get(tag, set())
        memories = [self._memories[mid] for mid in memory_ids if mid in self._memories]

        memories.sort(key=lambda m: m.retrieval_strength, reverse=True)

        for m in memories[:limit]:
            m.access_count += 1
            self._cache.put(m.id, m)

        return memories[:limit]

    def get_by_tags(self, tags: Set[str], match_all: bool = False, limit: int = 10) -> List[FastMemory]:
        if match_all:
            result_ids: Optional[Set[str]] = None
            for tag in tags:
                tag_ids = self._tag_index.get(tag, set())
                if result_ids is None:
                    result_ids = tag_ids.copy()
                else:
                    result_ids &= tag_ids
            memory_ids = result_ids or set()
        else:
            memory_ids = set()
            for tag in tags:
                memory_ids |= self._tag_index.get(tag, set())

        memories = [self._memories[mid] for mid in memory_ids if mid in self._memories]
        memories.sort(key=lambda m: m.retrieval_strength, reverse=True)

        for m in memories[:limit]:
            m.access_count += 1

        return memories[:limit]

    def get_by_type(self, memory_type: MemoryType, limit: int = 10) -> List[FastMemory]:
        memory_ids = self._type_index.get(memory_type, set())
        memories = [self._memories[mid] for mid in memory_ids if mid in self._memories]
        memories.sort(key=lambda m: m.timestamp, reverse=True)
        return memories[:limit]

    def get_by_emotion(
        self,
        min_valence: Optional[float] = None,
        max_valence: Optional[float] = None,
        limit: int = 10
    ) -> List[FastMemory]:
        if min_valence is not None and min_valence > 0.2:
            memory_ids = self._emotion_index.get("positive", set())
        elif max_valence is not None and max_valence < -0.2:
            memory_ids = self._emotion_index.get("negative", set())
        else:
            memory_ids = set(self._memories.keys())

        memories = []
        for mid in memory_ids:
            m = self._memories.get(mid)
            if m:
                if min_valence is not None and m.emotional_valence < min_valence:
                    continue
                if max_valence is not None and m.emotional_valence > max_valence:
                    continue
                memories.append(m)

        memories.sort(key=lambda m: abs(m.emotional_valence), reverse=True)
        return memories[:limit]

    def get_recent(self, count: int = 5) -> List[FastMemory]:
        result = []
        for mid in self._by_time[:count]:
            m = self._memories.get(mid)
            if m:
                result.append(m)
        return result

    def get_for_agent(self, agent_id: str, limit: int = 10) -> List[FastMemory]:
        memory_ids = self._agent_index.get(agent_id, set())
        memories = [self._memories[mid] for mid in memory_ids if mid in self._memories]
        memories.sort(key=lambda m: m.timestamp, reverse=True)
        return memories[:limit]

    def search(self, query: str, limit: int = 10) -> List[FastMemory]:
        query_lower = query.lower()
        matching = [m for m in self._memories.values() if query_lower in m.content.lower()]
        matching.sort(key=lambda m: m.retrieval_strength, reverse=True)
        return matching[:limit]

    def get_most_relevant(self, n: int = 5) -> List[FastMemory]:
        memories = list(self._memories.values())
        memories.sort(key=lambda m: m.retrieval_strength, reverse=True)
        return memories[:n]

    def _prune(self, count: int = 50) -> None:
        if len(self._memories) <= count:
            return

        sorted_mems = sorted(
            self._memories.values(),
            key=lambda m: m.retrieval_strength
        )

        to_remove = sorted_mems[:count]
        for memory in to_remove:
            self._remove(memory.id)

    def _remove(self, memory_id: str) -> None:
        memory = self._memories.pop(memory_id, None)
        if not memory:
            return

        for tag in memory.tags:
            self._tag_index[tag].discard(memory_id)

        self._type_index[memory.memory_type].discard(memory_id)

        if memory.emotional_valence > 0.2:
            self._emotion_index["positive"].discard(memory_id)
        elif memory.emotional_valence < -0.2:
            self._emotion_index["negative"].discard(memory_id)
        else:
            self._emotion_index["neutral"].discard(memory_id)

        if memory.agent_id:
            self._agent_index[memory.agent_id].discard(memory_id)

        try:
            self._by_time.remove(memory_id)
        except ValueError:
            pass

        self._cache.invalidate(memory_id)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_memories": len(self._memories),
            "unique_tags": len(self._tag_index),
            "positive_memories": len(self._emotion_index.get("positive", set())),
            "negative_memories": len(self._emotion_index.get("negative", set())),
            "neutral_memories": len(self._emotion_index.get("neutral", set())),
            "cache_size": len(self._cache._cache),
        }

    def save(self, filepath: Path) -> None:
        data = {
            "agent_id": self.agent_id,
            "max_capacity": self.max_capacity,
            "memories": [m.to_dict() for m in self._memories.values()],
        }
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f)

    @classmethod
    def load(cls, filepath: Path) -> 'FastMemoryStore':
        with open(filepath, 'r') as f:
            data = json.load(f)

        store = cls(
            agent_id=data["agent_id"],
            max_capacity=data.get("max_capacity", 500)
        )

        for mem_data in data.get("memories", []):
            memory = FastMemory.from_dict(mem_data)
            store.add(memory)

        return store

    def clear(self) -> None:
        self._memories.clear()
        self._tag_index.clear()
        self._type_index.clear()
        self._emotion_index.clear()
        self._agent_index.clear()
        self._by_time.clear()
        self._cache.clear()

    def __len__(self) -> int:
        return len(self._memories)

    def __contains__(self, memory_id: str) -> bool:
        return memory_id in self._memories
