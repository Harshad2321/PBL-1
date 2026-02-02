"""
Fast Memory System for Nurture Simulation
==========================================

High-performance memory storage with O(1) lookups using indexing.
Designed for fast retrieval during real-time conversations.

Features:
- Hash-based indexing for instant tag/type lookups
- LRU cache for frequently accessed memories
- Efficient importance-based pruning
- Optimized for conversation flow
"""

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
    """
    Optimized memory unit with minimal overhead.
    
    Uses __slots__ for memory efficiency.
    """
    __slots__ = [
        'id', 'content', 'memory_type', 'timestamp', 
        'emotional_valence', 'importance', 'tags',
        'access_count', 'agent_id', 'context'
    ]
    
    id: str
    content: str
    memory_type: MemoryType
    timestamp: float  # Unix timestamp for fast comparison
    emotional_valence: float
    importance: float
    tags: frozenset  # Immutable for hashing
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
        self.id = id or str(uuid.uuid4())[:8]  # Shorter IDs for speed
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
        """Get age in hours."""
        return (datetime.now().timestamp() - self.timestamp) / 3600
    
    @property
    def retrieval_strength(self) -> float:
        """Fast retrieval strength calculation."""
        recency = 1.0 / (1.0 + 0.01 * self.age_hours)
        access_boost = min(0.3, 0.03 * self.access_count)
        return (0.4 * self.importance + 0.4 * recency + 0.2 * abs(self.emotional_valence) + access_boost)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
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
        """Deserialize from dictionary."""
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
    """Simple LRU cache for frequently accessed memories."""
    
    def __init__(self, max_size: int = 50):
        self._cache: OrderedDict[str, FastMemory] = OrderedDict()
        self._max_size = max_size
    
    def get(self, key: str) -> Optional[FastMemory]:
        """Get item and move to end (most recent)."""
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None
    
    def put(self, key: str, value: FastMemory) -> None:
        """Add item, evict oldest if over capacity."""
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
            self._cache[key] = value
    
    def invalidate(self, key: str) -> None:
        """Remove item from cache."""
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cached items."""
        self._cache.clear()


class FastMemoryStore:
    """
    High-performance memory store with O(1) lookups.
    
    Uses multiple indexes for fast retrieval:
    - Tag index: tag -> set of memory IDs
    - Type index: memory_type -> set of memory IDs
    - Emotion index: positive/negative/neutral -> set of memory IDs
    - Agent index: agent_id -> set of memory IDs
    
    Features:
    - O(1) tag/type lookups
    - LRU cache for hot memories
    - Efficient pruning
    - Fast serialization
    """
    
    def __init__(self, agent_id: str, max_capacity: int = 500, cache_size: int = 50):
        """
        Initialize fast memory store.
        
        Args:
            agent_id: Owner agent ID
            max_capacity: Maximum memories to store
            cache_size: Size of LRU cache for hot memories
        """
        self.agent_id = agent_id
        self.max_capacity = max_capacity
        
        # Primary storage
        self._memories: Dict[str, FastMemory] = {}
        
        # Indexes for O(1) lookup
        self._tag_index: Dict[str, Set[str]] = defaultdict(set)
        self._type_index: Dict[MemoryType, Set[str]] = defaultdict(set)
        self._emotion_index: Dict[str, Set[str]] = defaultdict(set)  # positive/negative/neutral
        self._agent_index: Dict[str, Set[str]] = defaultdict(set)
        
        # LRU cache for frequently accessed
        self._cache = LRUCache(cache_size)
        
        # Sorted list for recency queries (maintained on insert)
        self._by_time: List[str] = []  # Memory IDs sorted by timestamp
    
    def add(self, memory: FastMemory) -> str:
        """
        Add a memory with automatic indexing.
        
        Args:
            memory: Memory to add
            
        Returns:
            Memory ID
        """
        # Check capacity
        if len(self._memories) >= self.max_capacity:
            self._prune(count=self.max_capacity // 10)  # Remove 10%
        
        # Store memory
        self._memories[memory.id] = memory
        
        # Update indexes
        for tag in memory.tags:
            self._tag_index[tag].add(memory.id)
        
        self._type_index[memory.memory_type].add(memory.id)
        
        # Emotion index
        if memory.emotional_valence > 0.2:
            self._emotion_index["positive"].add(memory.id)
        elif memory.emotional_valence < -0.2:
            self._emotion_index["negative"].add(memory.id)
        else:
            self._emotion_index["neutral"].add(memory.id)
        
        if memory.agent_id:
            self._agent_index[memory.agent_id].add(memory.id)
        
        # Insert into sorted time list (binary insert for efficiency)
        self._insert_by_time(memory.id, memory.timestamp)
        
        return memory.id
    
    def _insert_by_time(self, memory_id: str, timestamp: float) -> None:
        """Binary insert into sorted time list."""
        # For small lists, append and sort is fine
        if len(self._by_time) < 100:
            self._by_time.append(memory_id)
            self._by_time.sort(key=lambda mid: self._memories.get(mid, FastMemory("")).timestamp, reverse=True)
        else:
            # Binary search insert
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
        """Create and add a new memory."""
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
        """Get memory by ID with caching."""
        # Check cache first
        cached = self._cache.get(memory_id)
        if cached:
            cached.access_count += 1
            return cached
        
        # Get from storage
        memory = self._memories.get(memory_id)
        if memory:
            memory.access_count += 1
            self._cache.put(memory_id, memory)
        return memory
    
    def get_by_tag(self, tag: str, limit: int = 10) -> List[FastMemory]:
        """
        O(1) lookup by tag.
        
        Args:
            tag: Tag to search
            limit: Maximum results
            
        Returns:
            List of memories sorted by relevance
        """
        memory_ids = self._tag_index.get(tag, set())
        memories = [self._memories[mid] for mid in memory_ids if mid in self._memories]
        
        # Sort by retrieval strength
        memories.sort(key=lambda m: m.retrieval_strength, reverse=True)
        
        # Update access counts
        for m in memories[:limit]:
            m.access_count += 1
            self._cache.put(m.id, m)
        
        return memories[:limit]
    
    def get_by_tags(self, tags: Set[str], match_all: bool = False, limit: int = 10) -> List[FastMemory]:
        """
        Get memories matching tags.
        
        Args:
            tags: Tags to match
            match_all: If True, memory must have ALL tags. If False, ANY tag.
            limit: Maximum results
        """
        if match_all:
            # Intersection of all tag indexes
            result_ids: Optional[Set[str]] = None
            for tag in tags:
                tag_ids = self._tag_index.get(tag, set())
                if result_ids is None:
                    result_ids = tag_ids.copy()
                else:
                    result_ids &= tag_ids
            memory_ids = result_ids or set()
        else:
            # Union of tag indexes
            memory_ids = set()
            for tag in tags:
                memory_ids |= self._tag_index.get(tag, set())
        
        memories = [self._memories[mid] for mid in memory_ids if mid in self._memories]
        memories.sort(key=lambda m: m.retrieval_strength, reverse=True)
        
        for m in memories[:limit]:
            m.access_count += 1
        
        return memories[:limit]
    
    def get_by_type(self, memory_type: MemoryType, limit: int = 10) -> List[FastMemory]:
        """O(1) lookup by memory type."""
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
        """Get memories by emotional valence range."""
        # Use emotion index for broad filtering
        if min_valence is not None and min_valence > 0.2:
            memory_ids = self._emotion_index.get("positive", set())
        elif max_valence is not None and max_valence < -0.2:
            memory_ids = self._emotion_index.get("negative", set())
        else:
            # Need to check all
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
        """Get most recent memories - O(1) using sorted list."""
        result = []
        for mid in self._by_time[:count]:
            m = self._memories.get(mid)
            if m:
                result.append(m)
        return result
    
    def get_for_agent(self, agent_id: str, limit: int = 10) -> List[FastMemory]:
        """Get memories involving specific agent."""
        memory_ids = self._agent_index.get(agent_id, set())
        memories = [self._memories[mid] for mid in memory_ids if mid in self._memories]
        memories.sort(key=lambda m: m.timestamp, reverse=True)
        return memories[:limit]
    
    def search(self, query: str, limit: int = 10) -> List[FastMemory]:
        """Text search in memory contents."""
        query_lower = query.lower()
        matching = [m for m in self._memories.values() if query_lower in m.content.lower()]
        matching.sort(key=lambda m: m.retrieval_strength, reverse=True)
        return matching[:limit]
    
    def get_most_relevant(self, n: int = 5) -> List[FastMemory]:
        """Get most relevant memories overall."""
        memories = list(self._memories.values())
        memories.sort(key=lambda m: m.retrieval_strength, reverse=True)
        return memories[:n]
    
    def _prune(self, count: int = 50) -> None:
        """Remove least relevant memories."""
        if len(self._memories) <= count:
            return
        
        # Sort by retrieval strength
        sorted_mems = sorted(
            self._memories.values(),
            key=lambda m: m.retrieval_strength
        )
        
        # Remove lowest scoring
        to_remove = sorted_mems[:count]
        for memory in to_remove:
            self._remove(memory.id)
    
    def _remove(self, memory_id: str) -> None:
        """Remove a memory and clean up indexes."""
        memory = self._memories.pop(memory_id, None)
        if not memory:
            return
        
        # Clean indexes
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
        
        # Remove from time list
        try:
            self._by_time.remove(memory_id)
        except ValueError:
            pass
        
        # Invalidate cache
        self._cache.invalidate(memory_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory store statistics."""
        return {
            "total_memories": len(self._memories),
            "unique_tags": len(self._tag_index),
            "positive_memories": len(self._emotion_index.get("positive", set())),
            "negative_memories": len(self._emotion_index.get("negative", set())),
            "neutral_memories": len(self._emotion_index.get("neutral", set())),
            "cache_size": len(self._cache._cache),
        }
    
    def save(self, filepath: Path) -> None:
        """Save to JSON file."""
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
        """Load from JSON file."""
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
        """Clear all memories and indexes."""
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
