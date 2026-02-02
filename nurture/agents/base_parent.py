"""
Base Parent Agent
==================

Abstract base class for all parent agents (player and AI).
Defines the common interface and shared functionality.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime

from nurture.core.data_structures import ParentState, EmotionalState, DialogueContext
from nurture.core.enums import ParentRole, EmotionType, InteractionType
from nurture.core.events import Event, EventType, get_event_bus
from nurture.memory.memory_store import MemoryStore, Memory
from nurture.core.enums import MemoryType


class BaseParent(ABC):
    """
    Abstract base class for parent agents.
    
    Defines the common interface that both PlayerParent and AIParent
    must implement. Provides shared functionality for:
    - State management
    - Emotional updates
    - Memory operations
    - Event publishing
    
    Subclasses must implement:
    - process_input(): Handle incoming messages
    - generate_response(): Produce responses
    """
    
    def __init__(self, state: ParentState, memory_store: Optional[MemoryStore] = None):
        """
        Initialize base parent.
        
        Args:
            state: The parent's state container
            memory_store: Optional memory store (created if not provided)
        """
        self.state = state
        self.memory = memory_store or MemoryStore(agent_id=state.id)
        self._event_bus = get_event_bus()
        self._input_log: List[Dict[str, Any]] = []
        self._output_log: List[Dict[str, Any]] = []
    
    @property
    def id(self) -> str:
        """Get agent ID."""
        return self.state.id
    
    @property
    def name(self) -> str:
        """Get agent name."""
        return self.state.name
    
    @property
    def role(self) -> ParentRole:
        """Get parent role."""
        return self.state.role
    
    @property
    def is_player(self) -> bool:
        """Check if this is the player-controlled parent."""
        return self.state.is_player
    
    @property
    def emotional_state(self) -> EmotionalState:
        """Get current emotional state."""
        return self.state.emotional_state
    
    @abstractmethod
    def process_input(self, message: str, context: Optional[DialogueContext] = None) -> None:
        """
        Process incoming input/message.
        
        Args:
            message: The input message
            context: Optional dialogue context
        """
        pass
    
    @abstractmethod
    def generate_response(self, context: Optional[DialogueContext] = None) -> str:
        """
        Generate a response.
        
        Args:
            context: Optional dialogue context
            
        Returns:
            Generated response string
        """
        pass
    
    def update_emotion(self, emotion: EmotionType, delta: float) -> None:
        """
        Update an emotional state.
        
        Args:
            emotion: The emotion to update
            delta: Change amount
        """
        old_value = self.emotional_state.emotions.get(emotion, 0.0)
        self.emotional_state.adjust_emotion(emotion, delta)
        new_value = self.emotional_state.emotions.get(emotion, 0.0)
        
        # Publish event
        self._event_bus.publish(Event(
            event_type=EventType.STATE_EMOTION_CHANGED,
            source=self.id,
            data={
                "emotion": emotion.value,
                "old_value": old_value,
                "new_value": new_value,
                "delta": delta,
            }
        ))
    
    def apply_emotional_impact(self, impacts: Dict[EmotionType, float]) -> None:
        """
        Apply multiple emotional impacts at once.
        
        Args:
            impacts: Dict mapping emotions to delta values
        """
        for emotion, delta in impacts.items():
            self.update_emotion(emotion, delta)
    
    def add_stress(self, amount: float) -> None:
        """
        Add stress to the parent.
        
        Args:
            amount: Stress amount to add (0.0-1.0)
        """
        self.emotional_state.stress_level = min(
            1.0, 
            self.emotional_state.stress_level + amount
        )
        self.update_emotion(EmotionType.STRESS, amount)
        
        # High stress affects other emotions
        if self.emotional_state.stress_level > 0.7:
            self.update_emotion(EmotionType.PATIENCE, -amount * 0.5)
            self.update_emotion(EmotionType.FRUSTRATION, amount * 0.3)
    
    def reduce_stress(self, amount: float) -> None:
        """
        Reduce stress from the parent.
        
        Args:
            amount: Stress amount to reduce
        """
        self.emotional_state.stress_level = max(
            0.0,
            self.emotional_state.stress_level - amount
        )
        self.update_emotion(EmotionType.STRESS, -amount)
        self.update_emotion(EmotionType.CALM, amount * 0.5)
    
    def create_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.INTERACTION,
        emotional_valence: Optional[float] = None,
        importance: float = 0.5,
        tags: Optional[set] = None,
        associated_agent_id: Optional[str] = None
    ) -> Memory:
        """
        Create a new memory from current context.
        
        Args:
            content: Memory content description
            memory_type: Type of memory
            emotional_valence: Emotional color (auto-calculated if None)
            importance: Memory importance
            tags: Categorical tags
            associated_agent_id: Related agent ID
            
        Returns:
            Created Memory object
        """
        # Auto-calculate emotional valence if not provided
        if emotional_valence is None:
            emotional_valence = self.emotional_state.get_valence()
        
        # Get emotional intensity from dominant emotion
        _, intensity = self.emotional_state.get_dominant_emotion()
        
        memory = self.memory.create_memory(
            content=content,
            memory_type=memory_type,
            emotional_valence=emotional_valence,
            emotional_intensity=intensity,
            importance=importance,
            tags=tags,
            associated_agent_id=associated_agent_id,
        )
        
        # Publish event
        self._event_bus.publish(Event(
            event_type=EventType.MEMORY_CREATED,
            source=self.id,
            data={
                "memory_id": memory.id,
                "content": content,
                "importance": importance,
            }
        ))
        
        return memory
    
    def recall_memories(self, tags: set, limit: int = 5) -> List[Memory]:
        """
        Recall memories by tags.
        
        Args:
            tags: Tags to search for
            limit: Maximum memories to retrieve
            
        Returns:
            List of matching memories
        """
        memories = self.memory.retrieve_by_tags(tags, limit)
        
        if memories:
            self._event_bus.publish(Event(
                event_type=EventType.MEMORY_RETRIEVED,
                source=self.id,
                data={
                    "tags": list(tags),
                    "count": len(memories),
                }
            ))
        
        return memories
    
    def apply_emotional_decay(self) -> None:
        """Apply natural emotional decay toward baseline."""
        self.emotional_state.apply_decay()
    
    def log_input(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log an input for history tracking."""
        self._input_log.append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "context": context,
        })
        # Keep only last 100 entries
        if len(self._input_log) > 100:
            self._input_log = self._input_log[-100:]
    
    def log_output(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log an output for history tracking."""
        self._output_log.append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "context": context,
        })
        if len(self._output_log) > 100:
            self._output_log = self._output_log[-100:]
    
    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current state.
        
        Returns:
            Dictionary with state summary
        """
        dom_emotion, dom_intensity = self.emotional_state.get_dominant_emotion()
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "is_player": self.is_player,
            "dominant_emotion": dom_emotion.value,
            "emotion_intensity": dom_intensity,
            "stress_level": self.emotional_state.stress_level,
            "emotional_valence": self.emotional_state.get_valence(),
            "relationship_quality": self.state.relationship_quality,
            "interaction_count": self.state.interaction_count,
        }
    
    def increment_interaction_count(self) -> None:
        """Increment the interaction counter."""
        self.state.interaction_count += 1
