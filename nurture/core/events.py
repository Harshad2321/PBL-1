"""
Event System for Nurture Simulation
====================================

This module implements a lightweight event-driven architecture.
Events enable loose coupling between components and support:
- State change notifications
- Logging and debugging
- Future child agent observation hooks

Design Pattern: Observer/Pub-Sub with typed events
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
from enum import Enum, auto
import uuid


class EventType(Enum):
    """
    All event types in the parent simulation system.
    
    Events are grouped by category:
    - GAME_*: Game flow events
    - PLAYER_*: Player action events
    - AI_*: AI agent events
    - STATE_*: State change events
    - INTERACTION_*: Parent interaction events
    """
    # Game Flow Events
    GAME_STARTED = auto()
    GAME_PAUSED = auto()
    GAME_RESUMED = auto()
    GAME_ENDED = auto()
    
    # Role Events
    ROLE_SELECTED = auto()
    ROLES_ASSIGNED = auto()
    
    # Player Events
    PLAYER_INPUT_RECEIVED = auto()
    PLAYER_CHOICE_MADE = auto()
    PLAYER_MESSAGE_SENT = auto()
    
    # AI Parent Events
    AI_RESPONSE_GENERATED = auto()
    AI_STRATEGY_SELECTED = auto()
    AI_EMOTION_UPDATED = auto()
    
    # State Change Events
    STATE_EMOTION_CHANGED = auto()
    STATE_RELATIONSHIP_CHANGED = auto()
    STATE_STRESS_CHANGED = auto()
    
    # Interaction Events
    INTERACTION_STARTED = auto()
    INTERACTION_COMPLETED = auto()
    DIALOGUE_EXCHANGE = auto()
    
    # Memory Events
    MEMORY_CREATED = auto()
    MEMORY_RETRIEVED = auto()
    
    # System Events
    ERROR_OCCURRED = auto()
    WARNING_RAISED = auto()


@dataclass
class Event:
    """
    Base event class for all simulation events.
    
    Events carry data about something that happened in the simulation.
    They can be logged, processed by handlers, and used for debugging.
    
    Attributes:
        id: Unique event identifier
        event_type: Type of event
        timestamp: When the event occurred
        source: ID of component that triggered the event
        data: Event-specific payload data
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.GAME_STARTED
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


class EventBus:
    """
    Central event distribution system.
    
    The EventBus implements publish-subscribe pattern:
    - Publishers emit events without knowing receivers
    - Subscribers register handlers for specific event types
    - Events are processed synchronously
    
    Usage:
        bus = EventBus()
        bus.subscribe(EventType.PLAYER_MESSAGE_SENT, handle_message)
        bus.publish(Event(event_type=EventType.PLAYER_MESSAGE_SENT, data={"msg": "Hi"}))
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._global_subscribers: List[Callable[[Event], None]] = []
        self._event_history: List[Event] = []
        self._history_enabled: bool = True
        self._max_history: int = 1000
    
    def subscribe(self, event_type: EventType, 
                  handler: Callable[[Event], None]) -> None:
        """
        Subscribe a handler to a specific event type.
        
        Args:
            event_type: The type of event to listen for
            handler: Function that takes an Event and returns None
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def subscribe_all(self, handler: Callable[[Event], None]) -> None:
        """
        Subscribe a handler to ALL events.
        
        Useful for logging and debugging.
        """
        self._global_subscribers.append(handler)
    
    def unsubscribe(self, event_type: EventType, 
                    handler: Callable[[Event], None]) -> bool:
        """
        Remove a handler from an event type.
        
        Returns:
            True if handler was found and removed
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
                return True
            except ValueError:
                return False
        return False
    
    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: The event to publish
        """
        # Store in history
        if self._history_enabled:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history = self._event_history[-self._max_history:]
        
        # Notify global subscribers
        for handler in self._global_subscribers:
            try:
                handler(event)
            except Exception as e:
                self._handle_error(event, e)
        
        # Notify type-specific subscribers
        if event.event_type in self._subscribers:
            for handler in self._subscribers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    self._handle_error(event, e)
    
    def _handle_error(self, event: Event, error: Exception) -> None:
        """Handle errors in event handlers gracefully."""
        error_event = Event(
            event_type=EventType.ERROR_OCCURRED,
            data={
                "original_event_id": event.id,
                "error": str(error),
                "error_type": type(error).__name__
            }
        )
        self._event_history.append(error_event)
    
    def get_history(self, event_type: Optional[EventType] = None, 
                    limit: int = 50) -> List[Event]:
        """
        Get event history, optionally filtered by type.
        
        Returns:
            List of events, most recent first
        """
        if event_type:
            filtered = [e for e in self._event_history 
                       if e.event_type == event_type]
        else:
            filtered = self._event_history
        
        return list(reversed(filtered[-limit:]))
    
    def clear_history(self) -> None:
        """Clear the event history."""
        self._event_history.clear()


# Global event bus instance
_global_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """
    Get the global event bus instance.
    
    Returns:
        The global EventBus singleton
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def reset_event_bus() -> None:
    """Reset the global event bus (for testing)."""
    global _global_event_bus
    _global_event_bus = None
