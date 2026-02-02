"""
Parent Interaction Manager
===========================

Manages turn-based conversations between Player Parent and AI Parent.
Handles scenario context, dialogue history, state updates, and
coordinates between the two parent agents.
"""

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
    """Phases within a single interaction turn."""
    WAITING_FOR_PLAYER = auto()
    PROCESSING_PLAYER_INPUT = auto()
    AI_THINKING = auto()
    AI_RESPONDING = auto()
    UPDATING_STATES = auto()
    TURN_COMPLETE = auto()


class InteractionMode(Enum):
    """Modes of interaction."""
    FREE_DIALOGUE = "free_dialogue"      # Open conversation
    CHOICE_BASED = "choice_based"        # Player picks from options
    SCENARIO_EVENT = "scenario_event"    # Scripted scenario moment
    REFLECTION = "reflection"            # Internal monologue/thoughts


@dataclass
class ScenarioContext:
    """
    Context for a specific scenario/day.
    
    Provides the setup information for a gameplay scenario.
    """
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
    """
    Coordinates interactions between Player and AI parents.
    
    Responsibilities:
    - Manage turn-based conversation flow
    - Maintain dialogue context and history
    - Coordinate state updates after each interaction
    - Apply rules and constraints
    - Handle scenario-specific logic
    
    Usage:
        manager = InteractionManager(player, ai_parent, state_manager)
        manager.start_scenario(scenario_context)
        
        # Player sends message
        response = manager.process_player_message("I'll handle the baby.")
        
        # Or player makes choice
        response = manager.process_player_choice("choice_1")
    """
    
    def __init__(
        self,
        player_parent: PlayerParent,
        ai_parent: AIParent,
        state_manager: StateManager,
        rule_engine: Optional[RuleEngine] = None,
        constraints: Optional[BehavioralConstraints] = None
    ):
        """
        Initialize the interaction manager.
        
        Args:
            player_parent: The player-controlled parent
            ai_parent: The AI-controlled parent
            state_manager: Central state manager
            rule_engine: Optional rule engine (default rules if not provided)
            constraints: Optional behavioral constraints
        """
        self.player = player_parent
        self.ai = ai_parent
        self.state_manager = state_manager
        
        # Initialize rules and constraints
        self.rule_engine = rule_engine or RuleEngine()
        if not rule_engine:
            for rule in create_default_rules():
                self.rule_engine.add_rule(rule)
        
        self.constraints = constraints or BehavioralConstraints()
        if not constraints:
            self.constraints.add_default_constraints()
        
        # Interaction state
        self._current_phase = TurnPhase.WAITING_FOR_PLAYER
        self._current_mode = InteractionMode.FREE_DIALOGUE
        self._current_scenario: Optional[ScenarioContext] = None
        self._dialogue_context = DialogueContext()
        self._turn_count = 0
        self._interaction_history: List[InteractionRecord] = []
        
        # Event system
        self._event_bus = get_event_bus()
        
        # Callbacks for external systems
        self._on_response_generated: Optional[Callable[[str], None]] = None
        self._on_state_updated: Optional[Callable[[Dict], None]] = None
    
    @property
    def current_phase(self) -> TurnPhase:
        """Get current turn phase."""
        return self._current_phase
    
    @property
    def current_mode(self) -> InteractionMode:
        """Get current interaction mode."""
        return self._current_mode
    
    @property
    def turn_count(self) -> int:
        """Get current turn count."""
        return self._turn_count
    
    def start_scenario(self, scenario: ScenarioContext) -> str:
        """
        Start a new scenario.
        
        Sets up the context and returns the scenario introduction.
        
        Args:
            scenario: The scenario context to start
            
        Returns:
            Scenario introduction text
        """
        self._current_scenario = scenario
        self._turn_count = 0
        
        # Reset dialogue context
        self._dialogue_context = DialogueContext(
            scenario_name=scenario.scenario_name,
            scenario_description=scenario.description,
            current_topic=scenario.scenario_name.lower().replace(" ", "_"),
            tension_level=scenario.stress_modifier,
            special_flags=scenario.special_flags,
        )
        
        # Apply scenario stress modifiers
        self.player.apply_scenario_context(
            scenario.scenario_name,
            stress_modifier=scenario.stress_modifier * 0.5
        )
        self.ai.add_stress(scenario.stress_modifier * 0.5)
        
        # Set mode based on whether choices are available
        if scenario.available_choices:
            self._current_mode = InteractionMode.CHOICE_BASED
        else:
            self._current_mode = InteractionMode.FREE_DIALOGUE
        
        self._current_phase = TurnPhase.WAITING_FOR_PLAYER
        
        # Publish event
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
        """Format the scenario introduction."""
        intro = f"=== {scenario.scenario_name} ===\n\n"
        intro += f"{scenario.description}\n"
        
        if scenario.available_choices:
            intro += "\nYour choices:\n"
            for i, choice in enumerate(scenario.available_choices, 1):
                intro += f"  {i}. {choice.get('text', choice.get('id'))}\n"
        
        return intro
    
    def process_player_message(self, message: str, context: dict = None) -> str:
        """
        Process a free-form message from the player.
        
        Args:
            message: Player's input text
            context: Optional context dict with scenario_key, choice_key, player_patterns
            
        Returns:
            AI parent's response
        """
        if not message or not message.strip():
            return ""
        
        self._current_phase = TurnPhase.PROCESSING_PLAYER_INPUT
        
        # Update dialogue context
        self._dialogue_context.player_message = message
        self._dialogue_context.player_state = self.player.get_state_summary()
        self._dialogue_context.ai_state = self.ai.get_state_summary()
        
        # Add scenario context if provided
        if context:
            self._dialogue_context.extra_context = context
        
        # Process through player agent
        self.player.process_input(message, self._dialogue_context)
        
        # Apply rules to current context
        rule_context = self._build_rule_context()
        rule_results = self.rule_engine.evaluate_all(rule_context)
        self._apply_rule_results(rule_results)
        
        # Generate AI response
        self._current_phase = TurnPhase.AI_THINKING
        self.ai.process_input(message, self._dialogue_context)
        
        self._current_phase = TurnPhase.AI_RESPONDING
        ai_response = self.ai.generate_response(self._dialogue_context, context=context)
        
        # Apply constraints to response
        is_valid, violations = self.constraints.check_response(ai_response)
        if not is_valid:
            ai_response = self.constraints.correct_response(ai_response)
        
        # Update states
        self._current_phase = TurnPhase.UPDATING_STATES
        self._update_states_after_exchange(message, ai_response)
        
        # Record interaction
        self._record_interaction(message, ai_response)
        
        self._turn_count += 1
        self._current_phase = TurnPhase.TURN_COMPLETE
        
        # Callback if set
        if self._on_response_generated:
            self._on_response_generated(ai_response)
        
        return ai_response
    
    def process_player_choice(self, choice_id: str) -> str:
        """
        Process a choice selection from the player.
        
        Args:
            choice_id: ID of the selected choice
            
        Returns:
            AI parent's response to the choice
        """
        if not self._current_scenario or not self._current_scenario.available_choices:
            return self.process_player_message(choice_id)
        
        # Find the choice
        choice = None
        for c in self._current_scenario.available_choices:
            if c.get("id") == choice_id or str(c.get("id")) == choice_id:
                choice = c
                break
        
        if not choice:
            # Try by index
            try:
                idx = int(choice_id) - 1
                if 0 <= idx < len(self._current_scenario.available_choices):
                    choice = self._current_scenario.available_choices[idx]
            except ValueError:
                pass
        
        if not choice:
            return "Invalid choice. Please try again."
        
        self._current_phase = TurnPhase.PROCESSING_PLAYER_INPUT
        
        # Extract choice data
        choice_text = choice.get("text", choice_id)
        category = choice.get("category", "general")
        emotional_impacts = choice.get("emotional_impacts", {})
        behavioral_tags = choice.get("tags", [])
        hidden_impacts = choice.get("hidden_impacts", {})
        
        # Convert emotional impacts to EmotionType keys
        typed_impacts = {}
        for emotion_str, value in emotional_impacts.items():
            try:
                typed_impacts[EmotionType(emotion_str)] = value
            except ValueError:
                pass
        
        # Register choice with player agent
        self.player.make_choice(
            choice_id=choice.get("id", choice_id),
            choice_text=choice_text,
            category=category,
            emotional_impacts=typed_impacts if typed_impacts else None,
            behavioral_tags=behavioral_tags
        )
        
        # Apply hidden impacts
        self._apply_hidden_impacts(hidden_impacts)
        
        # Update dialogue context
        self._dialogue_context.player_message = choice_text
        self._dialogue_context.player_state = self.player.get_state_summary()
        self._dialogue_context.ai_state = self.ai.get_state_summary()
        
        # Apply rules
        rule_context = self._build_rule_context()
        rule_context["choice_category"] = category
        rule_results = self.rule_engine.evaluate_all(rule_context)
        self._apply_rule_results(rule_results)
        
        # Generate AI response
        self._current_phase = TurnPhase.AI_THINKING
        
        # AI processes the choice as if player said it
        self.ai.process_input(choice_text, self._dialogue_context)
        
        self._current_phase = TurnPhase.AI_RESPONDING
        ai_response = self.ai.generate_response(self._dialogue_context)
        
        # Apply constraints
        is_valid, _ = self.constraints.check_response(ai_response)
        if not is_valid:
            ai_response = self.constraints.correct_response(ai_response)
        
        # Update states
        self._current_phase = TurnPhase.UPDATING_STATES
        self._update_states_after_exchange(choice_text, ai_response)
        
        # Record interaction
        self._record_interaction(choice_text, ai_response, is_choice=True)
        
        self._turn_count += 1
        self._current_phase = TurnPhase.TURN_COMPLETE
        
        if self._on_response_generated:
            self._on_response_generated(ai_response)
        
        return ai_response
    
    def _build_rule_context(self) -> Dict[str, Any]:
        """Build context dictionary for rule evaluation."""
        player_state = self.player.get_state_summary()
        ai_state = self.ai.get_state_summary()
        
        return {
            # Player state
            "player_stress": player_state.get("stress_level", 0),
            "player_valence": player_state.get("emotional_valence", 0),
            
            # AI state
            "stress_level": ai_state.get("stress_level", 0),
            "anger": self.ai.emotional_state.emotions.get(EmotionType.ANGER, 0),
            "sadness": self.ai.emotional_state.emotions.get(EmotionType.SADNESS, 0),
            "joy": self.ai.emotional_state.emotions.get(EmotionType.JOY, 0),
            "trust_emotion": self.ai.emotional_state.emotions.get(EmotionType.TRUST, 0.5),
            "emotional_valence": ai_state.get("emotional_valence", 0),
            
            # Personality
            "warmth": self.ai.personality.get_trait(EmotionType.TRUST) if hasattr(EmotionType, 'WARMTH') else 0.5,
            "strictness": 0.5,  # Would come from personality
            "patience": 0.5,
            
            # Relationship
            "trust_in_partner": self.ai._trust_in_partner,
            "disagreement_streak": self.ai._disagreement_streak,
            "agreement_streak": self.ai._agreement_streak,
            "conflict_count": len([r for r in self._interaction_history 
                                  if r.relationship_impact < 0]),
            
            # Message analysis (from last processed)
            "partner_sentiment": self._dialogue_context.player_state.get("emotional_valence", 0),
            "partner_valence": self._dialogue_context.player_state.get("emotional_valence", 0),
            "is_accusation": False,  # Would be set by message analysis
            "is_question": "?" in self._dialogue_context.player_message,
            "message_intensity": 0.5,  # Would be calculated
            
            # Scenario
            "tension_level": self._dialogue_context.tension_level,
            "turn_count": self._turn_count,
        }
    
    def _apply_rule_results(self, results: List[tuple]) -> None:
        """Apply rule evaluation results to agent states."""
        for rule_id, result in results:
            if not isinstance(result, dict):
                continue
            
            # Apply stress modifications
            if "reduce_stress" in result:
                self.ai.reduce_stress(result["reduce_stress"])
            
            # Apply emotion modifications
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
        """Apply hidden choice impacts."""
        # Relationship impacts
        if "relationship_impact" in impacts:
            delta = impacts["relationship_impact"]
            self.state_manager.update_relationship_quality(delta)
        
        # Trust impacts
        if "trust_impact" in impacts:
            self.ai._trust_in_partner = max(0, min(1, 
                self.ai._trust_in_partner + impacts["trust_impact"]
            ))
        
        # Stress impacts
        if "stress_impact" in impacts:
            if impacts["stress_impact"] > 0:
                self.ai.add_stress(impacts["stress_impact"])
                self.player.add_stress(impacts["stress_impact"] * 0.5)
            else:
                self.ai.reduce_stress(abs(impacts["stress_impact"]))
        
        # Flags
        if "set_flags" in impacts:
            for flag, value in impacts["set_flags"].items():
                self.state_manager.set_flag(flag, value)
    
    def _update_states_after_exchange(self, player_msg: str, ai_response: str) -> None:
        """Update both parent states after an exchange."""
        # Apply emotional decay (gradual return to baseline)
        self.player.apply_emotional_decay()
        self.ai.apply_emotional_decay()
        
        # Update tension based on interaction
        player_valence = self.player.emotional_state.get_valence()
        ai_valence = self.ai.emotional_state.get_valence()
        
        # If both are negative, tension increases
        if player_valence < 0 and ai_valence < 0:
            self._dialogue_context.tension_level = min(1.0, 
                self._dialogue_context.tension_level + 0.1)
        # If both are positive, tension decreases
        elif player_valence > 0.3 and ai_valence > 0.3:
            self._dialogue_context.tension_level = max(0.0,
                self._dialogue_context.tension_level - 0.1)
        
        # Callback
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
        """Record the interaction for history."""
        # Determine interaction type
        if self._dialogue_context.tension_level > 0.6:
            interaction_type = InteractionType.ARGUMENT
        elif is_choice:
            interaction_type = InteractionType.COLLABORATIVE_DECISION
        else:
            interaction_type = InteractionType.CASUAL_CONVERSATION
        
        # Calculate relationship impact
        player_valence = self.player.emotional_state.get_valence()
        ai_valence = self.ai.emotional_state.get_valence()
        avg_valence = (player_valence + ai_valence) / 2
        relationship_impact = avg_valence * 0.05  # Small incremental changes
        
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
        
        # Record learning outcome for AI
        # Quality based on relationship impact (normalized to 0-1, with 0.5 being neutral)
        outcome_quality = 0.5 + (relationship_impact * 5)  # relationship_impact is ~0.05 range
        outcome_quality = max(0.0, min(1.0, outcome_quality))  # Clamp to 0-1
        self.ai.learn_from_outcome(player_msg, ai_response, outcome_quality)
        
        # Publish event
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
        """Get recent dialogue history."""
        return self._dialogue_context.recent_history[-limit:]
    
    def get_interaction_summary(self) -> Dict[str, Any]:
        """Get summary of current interaction session."""
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
        """
        End the current scenario and return summary.
        
        Returns:
            Summary of the scenario outcome
        """
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
        
        # Publish event
        self._event_bus.publish(Event(
            event_type=EventType.INTERACTION_COMPLETED,
            source="interaction_manager",
            data=summary
        ))
        
        # Reset for next scenario
        self._current_scenario = None
        self._current_phase = TurnPhase.WAITING_FOR_PLAYER
        
        return summary
    
    def set_on_response_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for when AI generates a response."""
        self._on_response_generated = callback
    
    def set_on_state_update_callback(self, callback: Callable[[Dict], None]) -> None:
        """Set callback for when states are updated."""
        self._on_state_updated = callback
