from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
from enum import Enum, auto
import uuid

class EventType(Enum):
    GAME_STARTED = auto()
    GAME_PAUSED = auto()
    GAME_RESUMED = auto()
    GAME_ENDED = auto()

    ROLE_SELECTED = auto()
    ROLES_ASSIGNED = auto()

    PLAYER_INPUT_RECEIVED = auto()
    PLAYER_CHOICE_MADE = auto()
    PLAYER_MESSAGE_SENT = auto()

    AI_RESPONSE_GENERATED = auto()
    AI_STRATEGY_SELECTED = auto()
    AI_EMOTION_UPDATED = auto()

    STATE_EMOTION_CHANGED = auto()
    STATE_RELATIONSHIP_CHANGED = auto()
    STATE_STRESS_CHANGED = auto()

    INTERACTION_STARTED = auto()
    INTERACTION_COMPLETED = auto()
    DIALOGUE_EXCHANGE = auto()

    MEMORY_CREATED = auto()
    MEMORY_RETRIEVED = auto()

    ERROR_OCCURRED = auto()
    WARNING_RAISED = auto()

@dataclass
class Event:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.GAME_STARTED
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

class EventBus:

    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._global_subscribers: List[Callable[[Event], None]] = []
        self._event_history: List[Event] = []
        self._history_enabled: bool = True
        self._max_history: int = 1000

    def subscribe(self, event_type: EventType,
                  handler: Callable[[Event], None]) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def subscribe_all(self, handler: Callable[[Event], None]) -> None:
        self._global_subscribers.append(handler)

    def unsubscribe(self, event_type: EventType,
                    handler: Callable[[Event], None]) -> bool:
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
                return True
            except ValueError:
                return False
        return False

    def publish(self, event: Event) -> None:
        if self._history_enabled:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history = self._event_history[-self._max_history:]

        for handler in self._global_subscribers:
            try:
                handler(event)
            except Exception as e:
                self._handle_error(event, e)

        if event.event_type in self._subscribers:
            for handler in self._subscribers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    self._handle_error(event, e)

    def _handle_error(self, event: Event, error: Exception) -> None:
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
        if event_type:
            filtered = [e for e in self._event_history
                       if e.event_type == event_type]
        else:
            filtered = self._event_history

        return list(reversed(filtered[-limit:]))

    def clear_history(self) -> None:
        self._event_history.clear()

_global_event_bus: Optional[EventBus] = None

def get_event_bus() -> EventBus:
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus

def reset_event_bus() -> None:
    global _global_event_bus
    _global_event_bus = None
