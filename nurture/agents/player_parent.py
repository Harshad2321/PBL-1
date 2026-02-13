from typing import Optional, List, Dict, Any
from datetime import datetime

from nurture.agents.base_parent import BaseParent
from nurture.core.data_structures import ParentState, DialogueContext
from nurture.core.enums import (
    ParentRole, EmotionType, InteractionType, MemoryType
)
from nurture.core.events import Event, EventType, get_event_bus
from nurture.memory.memory_store import MemoryStore

class PlayerParent(BaseParent):

    def __init__(self, state: ParentState, memory_store: Optional[MemoryStore] = None):
        super().__init__(state, memory_store)

        self._choice_history: List[Dict[str, Any]] = []
        self._message_history: List[Dict[str, Any]] = []
        self._behavioral_scores: Dict[str, float] = {
            "nurturing": 0.5,
            "disciplinary": 0.5,
            "avoidant": 0.3,
            "supportive": 0.5,
            "controlling": 0.3,
            "communicative": 0.5,
        }
        self._pending_input: Optional[str] = None
        self._last_choice_id: Optional[str] = None

    def process_input(self, message: str, context: Optional[DialogueContext] = None) -> None:
        if not message or not message.strip():
            return

        message = message.strip()

        self.log_input(message, {"context": context.__dict__ if context else None})

        self._message_history.append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "scenario": context.scenario_name if context else None,
            "emotional_state": self.emotional_state.get_valence(),
        })

        if context:
            context.add_exchange(self.name, message)

        self._pending_input = message

        self.increment_interaction_count()

        self._event_bus.publish(Event(
            event_type=EventType.PLAYER_MESSAGE_SENT,
            source=self.id,
            data={
                "message": message,
                "scenario": context.scenario_name if context else None,
            }
        ))

        self._analyze_message_sentiment(message)

    def _analyze_message_sentiment(self, message: str) -> None:
        message_lower = message.lower()

        positive_words = ["love", "happy", "glad", "thank", "appreciate",
                         "understand", "agree", "support", "help", "together"]
        negative_words = ["angry", "frustrated", "tired", "annoyed", "hate",
                         "can't", "won't", "never", "always", "fault"]
        stress_words = ["stressed", "overwhelmed", "exhausted", "busy",
                       "worried", "anxious"]

        pos_count = sum(1 for w in positive_words if w in message_lower)
        neg_count = sum(1 for w in negative_words if w in message_lower)
        stress_count = sum(1 for w in stress_words if w in message_lower)

        if pos_count > neg_count:
            self.update_emotion(EmotionType.JOY, 0.05 * pos_count)
            self.update_emotion(EmotionType.TRUST, 0.03 * pos_count)
        elif neg_count > pos_count:
            self.update_emotion(EmotionType.FRUSTRATION, 0.05 * neg_count)
            self.update_emotion(EmotionType.ANGER, 0.03 * neg_count)

        if stress_count > 0:
            self.add_stress(0.05 * stress_count)

    def generate_response(self, context: Optional[DialogueContext] = None) -> str:
        response = self._pending_input or ""
        self._pending_input = None

        if response:
            self.log_output(response)

        return response

    def make_choice(
        self,
        choice_id: str,
        choice_text: str = "",
        category: str = "general",
        emotional_impacts: Optional[Dict[EmotionType, float]] = None,
        behavioral_tags: Optional[List[str]] = None
    ) -> None:
        self._choice_history.append({
            "timestamp": datetime.now().isoformat(),
            "choice_id": choice_id,
            "choice_text": choice_text,
            "category": category,
            "emotional_state_before": self.emotional_state.get_valence(),
        })

        self._last_choice_id = choice_id

        self._update_behavioral_pattern(category, behavioral_tags or [])

        if emotional_impacts:
            self.apply_emotional_impact(emotional_impacts)

        self.create_memory(
            content=f"Made choice: {choice_text or choice_id}",
            memory_type=MemoryType.DECISION,
            importance=0.6,
            tags={category, "player_choice"},
        )

        self._event_bus.publish(Event(
            event_type=EventType.PLAYER_CHOICE_MADE,
            source=self.id,
            data={
                "choice_id": choice_id,
                "choice_text": choice_text,
                "category": category,
            }
        ))

    def _update_behavioral_pattern(self, category: str, tags: List[str]) -> None:
        learning_rate = 0.15

        if category in self._behavioral_scores:
            self._behavioral_scores[category] = min(1.0,
                self._behavioral_scores[category] + learning_rate)

        for tag in tags:
            if tag in self._behavioral_scores:
                self._behavioral_scores[tag] = min(1.0,
                    self._behavioral_scores[tag] + learning_rate * 0.5)

        for key in self._behavioral_scores:
            if key != category and key not in tags:
                self._behavioral_scores[key] = max(0.0,
                    self._behavioral_scores[key] - learning_rate * 0.1)

        self.state.behavioral_patterns = self._behavioral_scores.copy()

    def get_choice_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._choice_history[-limit:]

    def get_message_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._message_history[-limit:]

    def get_behavioral_profile(self) -> Dict[str, float]:
        return self._behavioral_scores.copy()

    def get_dominant_behavior(self) -> tuple:
        if not self._behavioral_scores:
            return ("balanced", 0.5)
        return max(self._behavioral_scores.items(), key=lambda x: x[1])

    def apply_scenario_context(
        self,
        scenario_name: str,
        stress_modifier: float = 0.0,
        emotional_preset: Optional[Dict[EmotionType, float]] = None
    ) -> None:
        if stress_modifier != 0:
            if stress_modifier > 0:
                self.add_stress(stress_modifier)
            else:
                self.reduce_stress(abs(stress_modifier))

        if emotional_preset:
            self.apply_emotional_impact(emotional_preset)

        self.create_memory(
            content=f"Started scenario: {scenario_name}",
            memory_type=MemoryType.INTERACTION,
            importance=0.4,
            tags={"scenario_start", scenario_name.lower().replace(" ", "_")},
        )

    def get_consistency_score(self) -> float:
        if len(self._choice_history) < 3:
            return 0.5

        categories = [c.get("category") for c in self._choice_history[-10:]]
        if not categories:
            return 0.5

        from collections import Counter
        counts = Counter(categories)
        total = len(categories)

        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                import math
                entropy -= p * math.log2(p)

        max_entropy = math.log2(max(len(counts), 1)) if counts else 1
        if max_entropy > 0:
            normalized = 1.0 - (entropy / max_entropy)
        else:
            normalized = 0.5

        return normalized

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.to_dict(),
            "choice_history": self._choice_history,
            "message_history": self._message_history,
            "behavioral_scores": self._behavioral_scores,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], memory_store: Optional[MemoryStore] = None) -> 'PlayerParent':
        state = ParentState.from_dict(data["state"])
        player = cls(state, memory_store)
        player._choice_history = data.get("choice_history", [])
        player._message_history = data.get("message_history", [])
        player._behavioral_scores = data.get("behavioral_scores", player._behavioral_scores)
        return player
