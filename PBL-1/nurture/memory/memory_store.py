"""
Memory Store for Nurture Simulation
====================================

This module provides memory storage and retrieval for parent agents.
Memories enable learning from past interactions and pattern recognition.

Design:
- Each memory has importance and decay resistance
- Memories can be tagged for categorical retrieval
- Emotional associations strengthen memory retention
- Supports both episodic (specific events) and semantic (patterns) memories
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime
import uuid
import json
from pathlib import Path

from nurture.core.enums import MemoryType, EmotionType


@dataclass
class Memory:
    """
    A single memory unit stored by a parent agent.
    
    Memories capture interactions, emotional responses, and patterns
    that influence future behavior and decision-making.
    
    Attributes:
        id: Unique identifier
        memory_type: Category (interaction, emotional, decision, etc.)
        content: Description or summary of the memory
        timestamp: When the memory was formed
        emotional_valence: Emotional color (-1.0 to 1.0)
        emotional_intensity: Strength of emotional association (0.0-1.0)
        associated_agent_id: ID of other agent involved
        tags: Categorical tags for retrieval
        importance: How significant this memory is (0.0-1.0)
        access_count: Number of times retrieved
        last_accessed: When last retrieved
        decay_resistance: Resistance to forgetting (0.0-1.0)
        context: Additional contextual information
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    memory_type: MemoryType = MemoryType.INTERACTION
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    emotional_valence: float = 0.0  # -1 to 1
    emotional_intensity: float = 0.5  # 0 to 1
    associated_agent_id: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    importance: float = 0.5
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    decay_resistance: float = 0.5
    context: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_retrieval_strength(self) -> float:
        """
        Calculate how easily this memory can be retrieved.
        
        Based on:
        - Recency (more recent = stronger)
        - Emotional intensity (stronger emotions = stronger memory)
        - Access frequency (more access = stronger)
        - Importance
        
        Returns:
            Retrieval strength from 0.0 to 1.0
        """
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
        """Record an access to this memory."""
        self.access_count += 1
        self.last_accessed = datetime.now()
        # Accessing memories increases their retention
        self.decay_resistance = min(1.0, self.decay_resistance + 0.02)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize memory to dictionary."""
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
        """Deserialize memory from dictionary."""
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
    """
    Memory storage and retrieval system for a parent agent.
    
    Features:
    - Capacity limits with importance-based pruning
    - Tag-based and emotional retrieval
    - Pattern recognition across memories
    - Persistence to disk
    
    Usage:
        store = MemoryStore(agent_id="parent_1")
        store.add_memory(Memory(content="Had an argument", emotional_valence=-0.5))
        conflicts = store.retrieve_by_tags({"conflict", "argument"})
    """
    
    def __init__(self, agent_id: str, max_capacity: int = 500):
        """
        Initialize memory store.
        
        Args:
            agent_id: ID of the agent this store belongs to
            max_capacity: Maximum memories to retain
        """
        self.agent_id = agent_id
        self.max_capacity = max_capacity
        self.memories: List[Memory] = []
        self._importance_threshold = 0.2
    
    def add_memory(self, memory: Memory) -> None:
        """
        Add a memory to the store.
        
        If over capacity, prunes least important memories.
        
        Args:
            memory: The memory to add
        """
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
        """
        Create and add a new memory.
        
        Convenience method that creates a Memory and adds it to the store.
        
        Returns:
            The created Memory object
        """
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
        """Remove least important memories when over capacity."""
        # Calculate composite score for each memory
        scored = [(m, m.importance * m.decay_resistance * m.calculate_retrieval_strength()) 
                  for m in self.memories]
        scored.sort(key=lambda x: x[1], reverse=True)
        self.memories = [m for m, _ in scored[:self.max_capacity]]
    
    def retrieve_by_tags(self, tags: Set[str], limit: int = 10) -> List[Memory]:
        """
        Retrieve memories matching any of the given tags.
        
        Args:
            tags: Set of tags to match
            limit: Maximum memories to return
            
        Returns:
            List of matching memories, sorted by importance
        """
        matching = [m for m in self.memories if m.tags & tags]
        matching.sort(key=lambda m: m.importance * m.calculate_retrieval_strength(), 
                     reverse=True)
        
        # Record access
        for m in matching[:limit]:
            m.access()
        
        return matching[:limit]
    
    def retrieve_by_emotion(
        self, 
        valence_range: Tuple[float, float], 
        limit: int = 10
    ) -> List[Memory]:
        """
        Retrieve memories within an emotional valence range.
        
        Args:
            valence_range: (min, max) valence values
            limit: Maximum memories to return
            
        Returns:
            List of matching memories
        """
        min_val, max_val = valence_range
        matching = [m for m in self.memories 
                   if min_val <= m.emotional_valence <= max_val]
        matching.sort(key=lambda m: m.emotional_intensity, reverse=True)
        
        for m in matching[:limit]:
            m.access()
        
        return matching[:limit]
    
    def retrieve_by_type(self, memory_type: MemoryType, limit: int = 10) -> List[Memory]:
        """Retrieve memories of a specific type."""
        matching = [m for m in self.memories if m.memory_type == memory_type]
        matching.sort(key=lambda m: m.timestamp, reverse=True)
        
        for m in matching[:limit]:
            m.access()
        
        return matching[:limit]
    
    def get_recent(self, count: int = 5) -> List[Memory]:
        """
        Get most recent memories.
        
        Args:
            count: Number of memories to return
            
        Returns:
            List of most recent memories
        """
        sorted_memories = sorted(self.memories, 
                                key=lambda m: m.timestamp, reverse=True)
        return sorted_memories[:count]
    
    def get_related_to_agent(self, agent_id: str, limit: int = 10) -> List[Memory]:
        """Get memories involving a specific agent."""
        matching = [m for m in self.memories 
                   if m.associated_agent_id == agent_id]
        matching.sort(key=lambda m: m.timestamp, reverse=True)
        return matching[:limit]
    
    def get_pattern_summary(self, tag: str) -> Dict[str, Any]:
        """
        Analyze patterns in memories with a given tag.
        
        Returns statistics about emotional trends and frequency.
        
        Args:
            tag: Tag to analyze
            
        Returns:
            Dictionary with pattern statistics
        """
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
        
        # Determine trend based on recent vs older memories
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
        """
        Simple text search in memory contents.
        
        Args:
            query: Text to search for (case-insensitive)
            limit: Maximum results
            
        Returns:
            List of matching memories
        """
        query_lower = query.lower()
        matching = [m for m in self.memories 
                   if query_lower in m.content.lower()]
        matching.sort(key=lambda m: m.calculate_retrieval_strength(), reverse=True)
        return matching[:limit]
    
    def save_to_file(self, filepath: Path) -> None:
        """
        Save memory store to JSON file.
        
        Args:
            filepath: Path to save file
        """
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
        """
        Load memory store from JSON file.
        
        Args:
            filepath: Path to load file
            
        Returns:
            Loaded MemoryStore instance
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        store = cls(
            agent_id=data["agent_id"],
            max_capacity=data.get("max_capacity", 500)
        )
        store.memories = [Memory.from_dict(m) for m in data.get("memories", [])]
        return store
    
    def clear(self) -> None:
        """Clear all memories."""
        self.memories.clear()
    
    def __len__(self) -> int:
        """Return number of memories stored."""
        return len(self.memories)
