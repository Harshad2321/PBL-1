from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum, auto

from nurture.agents.player_parent import PlayerParent
from nurture.agents.ai_parent import AIParent
from nurture.core.data_structures import (
    ParentState, DialogueContext, InteractionRecord
)
from nurture.core.enums import (
    ParentRole, EmotionType, InteractionType, MemoryType
)
from nurture.core.events import Event, EventType, get_event_bus
from nurture.memory.memory_store import MemoryStore
from nurture.memory.state_manager import StateManager
from nurture.rules.rule_engine import RuleEngine, create_default_rules
from nurture.rules.behavioral_constraints import BehavioralConstraints

class TurnPhase(Enum):
    WAITING_FOR_PLAYER = auto()
    PROCESSING_PLAYER_INPUT = auto()
    AI_THINKING = auto()
    AI_RESPONDING = auto()
    UPDATING_STATES = auto()
    TURN_COMPLETE = auto()

class InteractionMode(Enum):
    FREE_DIALOGUE = "free_dialogue"
    CHOICE_BASED = "choice_based"
    SCENARIO_EVENT = "scenario_event"
    REFLECTION = "reflection"

@dataclass
class ScenarioContext:
    scenario_id: str = ""
    scenario_name: str = ""
    description: str = ""
    day_number: int = 1
    act_number: int = 1
    stress_modifier: float = 0.0
    available_choices: List[Dict[str, Any]] = field(default_factory=list)
    hidden_impacts: Dict[str, Any] = field(default_factory=dict)
    special_flags: Dict[str, bool] = field(default_factory=dict)

class InteractionManager:

    def __init__(
        self,
        player_parent: PlayerParent,
        ai_parent: AIParent,
        state_manager: StateManager,
        rule_engine: Optional[RuleEngine] = None,
        constraints: Optional[BehavioralConstraints] = None
    ):
        self.player = player_parent
        self.ai = ai_parent
        self.state_manager = state_manager

        self.rule_engine = rule_engine or RuleEngine()
        if not rule_engine:
            for rule in create_default_rules():
                self.rule_engine.add_rule(rule)

        self.constraints = constraints or BehavioralConstraints()
        if not constraints:
            self.constraints.add_default_constraints()

        self._current_phase = TurnPhase.WAITING_FOR_PLAYER
        self._current_mode = InteractionMode.FREE_DIALOGUE
        self._current_scenario: Optional[ScenarioContext] = None
        self._dialogue_context = DialogueContext()
        self._turn_count = 0
        self._interaction_history: List[InteractionRecord] = []

        self._event_bus = get_event_bus()

        self._on_response_generated: Optional[Callable[[str], None]] = None
        self._on_state_updated: Optional[Callable[[Dict], None]] = None

    @property
    def current_phase(self) -> TurnPhase:
        return self._current_phase

    @property
    def current_mode(self) -> InteractionMode:
        return self._current_mode

    @property
    def turn_count(self) -> int:
        return self._turn_count

    def start_scenario(self, scenario: ScenarioContext) -> str:
        self._current_scenario = scenario
        self._turn_count = 0

        self._dialogue_context = DialogueContext(
            scenario_name=scenario.scenario_name,
            scenario_description=scenario.description,
            current_topic=scenario.scenario_name.lower().replace(" ", "_"),
            tension_level=scenario.stress_modifier,
            special_flags=scenario.special_flags,
        )

        self.player.apply_scenario_context(
            scenario.scenario_name,
            stress_modifier=scenario.stress_modifier * 0.5
        )
        self.ai.add_stress(scenario.stress_modifier * 0.5)

        if scenario.available_choices:
            self._current_mode = InteractionMode.CHOICE_BASED
        else:
            self._current_mode = InteractionMode.FREE_DIALOGUE

        self._current_phase = TurnPhase.WAITING_FOR_PLAYER

        self._event_bus.publish(Event(
            event_type=EventType.INTERACTION_STARTED,
            source="interaction_manager",
            data={
                "scenario_id": scenario.scenario_id,
                "scenario_name": scenario.scenario_name,
                "mode": self._current_mode.value,
            }
        ))

        return self._format_scenario_intro(scenario)

    def _format_scenario_intro(self, scenario: ScenarioContext) -> str:
        intro = f"=== {scenario.scenario_name} ===\n\n"
        intro += f"{scenario.description}\n"

        if scenario.available_choices:
            intro += "\nYour choices:\n"
            for i, choice in enumerate(scenario.available_choices, 1):
                intro += f"  {i}. {choice.get('text', choice.get('id'))}\n"

        return intro

    def process_player_message(self, message: str, context: dict = None) -> str:
        if not message or not message.strip():
            return ""

        self._current_phase = TurnPhase.PROCESSING_PLAYER_INPUT

        self._dialogue_context.player_message = message
        self._dialogue_context.player_state = self.player.get_state_summary()
        self._dialogue_context.ai_state = self.ai.get_state_summary()

        if context:
            self._dialogue_context.extra_context = context

        self.player.process_input(message, self._dialogue_context)

        rule_context = self._build_rule_context()
        rule_results = self.rule_engine.evaluate_all(rule_context)
        self._apply_rule_results(rule_results)

        self._current_phase = TurnPhase.AI_THINKING
        self.ai.process_input(message, self._dialogue_context)

        self._current_phase = TurnPhase.AI_RESPONDING
        ai_response = self.ai.generate_response(self._dialogue_context, context=context)

        is_valid, violations = self.constraints.check_response(ai_response)
        if not is_valid:
            ai_response = self.constraints.correct_response(ai_response)

        self._current_phase = TurnPhase.UPDATING_STATES
        self._update_states_after_exchange(message, ai_response)

        self._record_interaction(message, ai_response)

        self._turn_count += 1
        self._current_phase = TurnPhase.TURN_COMPLETE

        if self._on_response_generated:
            self._on_response_generated(ai_response)

        return ai_response

    def process_player_choice(self, choice_id: str) -> str:
        if not self._current_scenario or not self._current_scenario.available_choices:
            return self.process_player_message(choice_id)

        choice = None
        for c in self._current_scenario.available_choices:
            if c.get("id") == choice_id or str(c.get("id")) == choice_id:
                choice = c
                break

        if not choice:
            try:
                idx = int(choice_id) - 1
                if 0 <= idx < len(self._current_scenario.available_choices):
                    choice = self._current_scenario.available_choices[idx]
            except ValueError:
                pass

        if not choice:
            return "Invalid choice. Please try again."

        self._current_phase = TurnPhase.PROCESSING_PLAYER_INPUT

        choice_text = choice.get("text", choice_id)
        category = choice.get("category", "general")
        emotional_impacts = choice.get("emotional_impacts", {})
        behavioral_tags = choice.get("tags", [])
        hidden_impacts = choice.get("hidden_impacts", {})

        typed_impacts = {}
        for emotion_str, value in emotional_impacts.items():
            try:
                typed_impacts[EmotionType(emotion_str)] = value
            except ValueError:
                pass

        self.player.make_choice(
            choice_id=choice.get("id", choice_id),
            choice_text=choice_text,
            category=category,
            emotional_impacts=typed_impacts if typed_impacts else None,
            behavioral_tags=behavioral_tags
        )

        self._apply_hidden_impacts(hidden_impacts)

        self._dialogue_context.player_message = choice_text
        self._dialogue_context.player_state = self.player.get_state_summary()
        self._dialogue_context.ai_state = self.ai.get_state_summary()

        rule_context = self._build_rule_context()
        rule_context["choice_category"] = category
        rule_results = self.rule_engine.evaluate_all(rule_context)
        self._apply_rule_results(rule_results)

        self._current_phase = TurnPhase.AI_THINKING

        self.ai.process_input(choice_text, self._dialogue_context)

        self._current_phase = TurnPhase.AI_RESPONDING
        ai_response = self.ai.generate_response(self._dialogue_context)

        is_valid, _ = self.constraints.check_response(ai_response)
        if not is_valid:
            ai_response = self.constraints.correct_response(ai_response)

        self._current_phase = TurnPhase.UPDATING_STATES
        self._update_states_after_exchange(choice_text, ai_response)

        self._record_interaction(choice_text, ai_response, is_choice=True)

        self._turn_count += 1
        self._current_phase = TurnPhase.TURN_COMPLETE

        if self._on_response_generated:
            self._on_response_generated(ai_response)

        return ai_response

    def _build_rule_context(self) -> Dict[str, Any]:
        player_state = self.player.get_state_summary()
        ai_state = self.ai.get_state_summary()

        return {
            "player_stress": player_state.get("stress_level", 0),
            "player_valence": player_state.get("emotional_valence", 0),

            "stress_level": ai_state.get("stress_level", 0),
            "anger": self.ai.emotional_state.emotions.get(EmotionType.ANGER, 0),
            "sadness": self.ai.emotional_state.emotions.get(EmotionType.SADNESS, 0),
            "joy": self.ai.emotional_state.emotions.get(EmotionType.JOY, 0),
            "trust_emotion": self.ai.emotional_state.emotions.get(EmotionType.TRUST, 0.5),
            "emotional_valence": ai_state.get("emotional_valence", 0),

            "warmth": self.ai.personality.get_trait(EmotionType.TRUST) if hasattr(EmotionType, 'WARMTH') else 0.5,
            "strictness": 0.5,
            "patience": 0.5,

            "trust_in_partner": self.ai._trust_in_partner,
            "disagreement_streak": self.ai._disagreement_streak,
            "agreement_streak": self.ai._agreement_streak,
            "conflict_count": len([r for r in self._interaction_history
                                  if r.relationship_impact < 0]),

            "partner_sentiment": self._dialogue_context.player_state.get("emotional_valence", 0),
            "partner_valence": self._dialogue_context.player_state.get("emotional_valence", 0),
            "is_accusation": False,
            "is_question": "?" in self._dialogue_context.player_message,
            "message_intensity": 0.5,

            "tension_level": self._dialogue_context.tension_level,
            "turn_count": self._turn_count,
        }

    def _apply_rule_results(self, results: List[tuple]) -> None:
        for rule_id, result in results:
            if not isinstance(result, dict):
                continue

            if "reduce_stress" in result:
                self.ai.reduce_stress(result["reduce_stress"])

            for key, value in result.items():
                if key.endswith("_boost"):
                    emotion_name = key.replace("_boost", "")
                    try:
                        emotion = EmotionType(emotion_name)
                        self.ai.update_emotion(emotion, value)
                    except ValueError:
                        pass
                elif key.endswith("_reduction"):
                    emotion_name = key.replace("_reduction", "")
                    try:
                        emotion = EmotionType(emotion_name)
                        self.ai.update_emotion(emotion, -value)
                    except ValueError:
                        pass

    def _apply_hidden_impacts(self, impacts: Dict[str, Any]) -> None:
        if "relationship_impact" in impacts:
            delta = impacts["relationship_impact"]
            self.state_manager.update_relationship_quality(delta)

        if "trust_impact" in impacts:
            self.ai._trust_in_partner = max(0, min(1,
                self.ai._trust_in_partner + impacts["trust_impact"]
            ))

        if "stress_impact" in impacts:
            if impacts["stress_impact"] > 0:
                self.ai.add_stress(impacts["stress_impact"])
                self.player.add_stress(impacts["stress_impact"] * 0.5)
            else:
                self.ai.reduce_stress(abs(impacts["stress_impact"]))

        if "set_flags" in impacts:
            for flag, value in impacts["set_flags"].items():
                self.state_manager.set_flag(flag, value)

    def _update_states_after_exchange(self, player_msg: str, ai_response: str) -> None:
        self.player.apply_emotional_decay()
        self.ai.apply_emotional_decay()

        player_valence = self.player.emotional_state.get_valence()
        ai_valence = self.ai.emotional_state.get_valence()

        if player_valence < 0 and ai_valence < 0:
            self._dialogue_context.tension_level = min(1.0,
                self._dialogue_context.tension_level + 0.1)
        elif player_valence > 0.3 and ai_valence > 0.3:
            self._dialogue_context.tension_level = max(0.0,
                self._dialogue_context.tension_level - 0.1)

        if self._on_state_updated:
            self._on_state_updated({
                "player": self.player.get_state_summary(),
                "ai": self.ai.get_state_summary(),
                "tension": self._dialogue_context.tension_level,
            })

    def _record_interaction(
        self,
        player_msg: str,
        ai_response: str,
        is_choice: bool = False
    ) -> None:
        if self._dialogue_context.tension_level > 0.6:
            interaction_type = InteractionType.ARGUMENT
        elif is_choice:
            interaction_type = InteractionType.COLLABORATIVE_DECISION
        else:
            interaction_type = InteractionType.CASUAL_CONVERSATION

        player_valence = self.player.emotional_state.get_valence()
        ai_valence = self.ai.emotional_state.get_valence()
        avg_valence = (player_valence + ai_valence) / 2
        relationship_impact = avg_valence * 0.05

        record = InteractionRecord(
            interaction_type=interaction_type,
            initiator_id=self.player.id,
            responder_id=self.ai.id,
            initiator_message=player_msg,
            responder_message=ai_response,
            context={
                "scenario": self._current_scenario.scenario_name if self._current_scenario else None,
                "turn": self._turn_count,
                "tension": self._dialogue_context.tension_level,
            },
            emotional_impact={
                "player_valence": player_valence,
                "ai_valence": ai_valence,
            },
            relationship_impact=relationship_impact,
        )

        self._interaction_history.append(record)
        self.state_manager.record_interaction(record)

        outcome_quality = 0.5 + (relationship_impact * 5)
        outcome_quality = max(0.0, min(1.0, outcome_quality))
        self.ai.learn_from_outcome(player_msg, ai_response, outcome_quality)

        self._event_bus.publish(Event(
            event_type=EventType.DIALOGUE_EXCHANGE,
            source="interaction_manager",
            data={
                "turn": self._turn_count,
                "interaction_type": interaction_type.value,
                "relationship_impact": relationship_impact,
            }
        ))

    def get_dialogue_history(self, limit: int = 10) -> List[Dict[str, str]]:
        return self._dialogue_context.recent_history[-limit:]

    def get_interaction_summary(self) -> Dict[str, Any]:
        return {
            "scenario": self._current_scenario.scenario_name if self._current_scenario else None,
            "turn_count": self._turn_count,
            "mode": self._current_mode.value,
            "phase": self._current_phase.value,
            "tension_level": self._dialogue_context.tension_level,
            "player_state": self.player.get_state_summary(),
            "ai_state": self.ai.get_state_summary(),
            "relationship_quality": self.state_manager.session.metrics.get("relationship_quality", 0.7)
                                   if self.state_manager.session else 0.7,
        }

    def end_scenario(self) -> Dict[str, Any]:
        summary = {
            "scenario_name": self._current_scenario.scenario_name if self._current_scenario else None,
            "total_turns": self._turn_count,
            "final_tension": self._dialogue_context.tension_level,
            "player_final_state": self.player.get_state_summary(),
            "ai_final_state": self.ai.get_state_summary(),
            "interaction_count": len(self._interaction_history),
            "positive_interactions": sum(1 for r in self._interaction_history
                                        if r.relationship_impact > 0),
            "negative_interactions": sum(1 for r in self._interaction_history
                                        if r.relationship_impact < 0),
        }

        self._event_bus.publish(Event(
            event_type=EventType.INTERACTION_COMPLETED,
            source="interaction_manager",
            data=summary
        ))

        self._current_scenario = None
        self._current_phase = TurnPhase.WAITING_FOR_PLAYER

        return summary

    def set_on_response_callback(self, callback: Callable[[str], None]) -> None:
        self._on_response_generated = callback

    def set_on_state_update_callback(self, callback: Callable[[Dict], None]) -> None:
        self._on_state_updated = callback
