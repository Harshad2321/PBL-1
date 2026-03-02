from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from nurture.simulation.decision_engine import DecisionContext, DecisionEngine, ResponseType
from nurture.simulation.entities import AIParent, Child, Parent, Relationship
from nurture.simulation.event_catalog import EventCatalog, TIME_BLOCKS
from nurture.simulation.event_models import DayEvent, PlayerChoice, TimeBlockEvent
from nurture.simulation.memory_tags_store import MemoryTagsStore
from nurture.simulation.state_models import ConflictTone, MemoryTag, MemoryTags
from nurture.simulation.state_update_system import StateUpdateSystem


@dataclass
class SimulationPosition:
    act_number: int = 1
    day_number: int = 1
    block_index: int = 0


@dataclass
class GameEngine:
    player_parent: Parent
    ai_parent: AIParent
    child: Child
    relationship: Relationship
    event_catalog: EventCatalog = field(default_factory=EventCatalog)
    decision_engine: DecisionEngine = field(default_factory=DecisionEngine)
    state_update_system: StateUpdateSystem = field(default_factory=StateUpdateSystem)
    memory_tags: MemoryTags = field(default_factory=MemoryTags)
    memory_store: Optional[MemoryTagsStore] = None
    position: SimulationPosition = field(default_factory=SimulationPosition)
    is_finished: bool = False
    finish_reason: Optional[str] = None
    player_influence: float = 1.0
    emotional_impact_multiplier: float = 1.0
    long_term_flags: Dict[str, float] = field(default_factory=dict)
    act_one_locks: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def new_game(
        cls,
        player_role: str,
        player_name: str,
        ai_name: str,
        child_name: str,
        save_dir: str = "./saves",
    ) -> "GameEngine":
        player = Parent(name=player_name, role=player_role, is_player=True)
        ai = AIParent(name=ai_name, role="mother" if player_role.lower() == "father" else "father", is_player=False)
        child = Child(name=child_name)
        relationship = Relationship(parent_a_name=player_name, parent_b_name=ai_name)

        store = MemoryTagsStore(str(Path(save_dir) / "memory_tags.json"))

        return cls(
            player_parent=player,
            ai_parent=ai,
            child=child,
            relationship=relationship,
            memory_store=store,
            memory_tags=store.load(),
        )

    def get_current_day_event(self) -> DayEvent:
        return self.event_catalog.get_day_event(self.position.act_number, self.position.day_number)

    def get_current_time_block(self) -> TimeBlockEvent:
        day_event = self.get_current_day_event()
        return day_event.get_block(TIME_BLOCKS[self.position.block_index])

    def get_current_scenario_payload(self) -> Dict[str, Any]:
        day_event = self.get_current_day_event()
        time_block = self.get_current_time_block()
        return {
            "act": day_event.act_number,
            "day": day_event.day_number,
            "title": day_event.title,
            "age_range": day_event.age_range,
            "time_block": time_block.block_name,
            "scenario_text": time_block.scenario_text,
            "choices": [choice.to_dict() for choice in time_block.player_choices],
        }

    def process_player_choice(self, choice_id: str) -> Dict[str, Any]:
        if self.is_finished:
            return {"error": "Simulation has ended", "finish_reason": self.finish_reason}

        day_event = self.get_current_day_event()
        time_block = self.get_current_time_block()
        choice = self._resolve_choice(time_block.player_choices, choice_id)

        if not choice:
            return {"error": f"Invalid choice_id '{choice_id}' for this time block"}

        decision_context = DecisionContext(
            scenario_key=f"act_{day_event.act_number}_day_{day_event.day_number}_{time_block.block_name.lower()}",
            relationship=self.relationship.state,
            ai_parent=self.ai_parent.state,
            player_choice_id=choice.choice_id,
        )

        response_type = self.decision_engine.decide(decision_context)
        scaled_updates = self._scale_updates(choice.updates)

        update_trace = self.state_update_system.apply_interaction_updates(
            response_type=response_type,
            relationship_state=self.relationship.state,
            ai_parent_state=self.ai_parent.state,
            child_state=self.child.state,
            scenario_updates=scaled_updates,
        )
        applied_flags = self._apply_flags_from_updates(scaled_updates)
        if applied_flags:
            update_trace["flags"] = applied_flags

        interaction_record = {
            "act": day_event.act_number,
            "day": day_event.day_number,
            "title": day_event.title,
            "time_block": time_block.block_name,
            "choice_id": choice.choice_id,
            "choice_text": choice.text,
            "ai_response_type": response_type.value,
            "decision_snapshot": self.decision_engine.build_reasoning_snapshot(decision_context),
            "update_trace": update_trace,
        }
        self.relationship.log_interaction(interaction_record)
        self._record_memory_tags(day_event, choice, response_type)

        self._advance_position()
        self._evaluate_dynamic_end()
        self._persist_memory_tags()

        return {
            "interaction": interaction_record,
            "next": None if self.is_finished else self.get_current_scenario_payload(),
            "finished": self.is_finished,
            "finish_reason": self.finish_reason,
        }

    def export_state(self) -> Dict[str, Any]:
        return {
            "position": {
                "act_number": self.position.act_number,
                "day_number": self.position.day_number,
                "block_index": self.position.block_index,
            },
            "player": self.player_parent.to_dict(),
            "ai_parent": self.ai_parent.to_dict(),
            "child": self.child.to_dict(),
            "relationship": self.relationship.to_dict(),
            "memory_tags": self.memory_tags.to_dict(),
            "player_influence": self.player_influence,
            "emotional_impact_multiplier": self.emotional_impact_multiplier,
            "long_term_flags": self.long_term_flags,
            "act_one_locks": self.act_one_locks,
            "is_finished": self.is_finished,
            "finish_reason": self.finish_reason,
        }

    def _resolve_choice(self, choices: List[PlayerChoice], choice_id: str) -> Optional[PlayerChoice]:
        for choice in choices:
            if choice.choice_id == choice_id:
                return choice
        return None

    def _advance_position(self) -> None:
        self.position.block_index += 1
        if self.position.block_index < len(TIME_BLOCKS):
            return

        self.position.block_index = 0
        self.position.day_number += 1

        total_days = self.event_catalog.total_days(self.position.act_number)
        if self.position.day_number <= total_days:
            return

        self._on_act_completed(self.position.act_number)
        self.position.act_number += 1
        self.position.day_number = 1

        if self.position.act_number not in self.event_catalog.available_acts():
            self.is_finished = True
            self.finish_reason = "Configured content completed"

    def _on_act_completed(self, completed_act: int) -> None:
        if completed_act == 1:
            self.child.state.lock_attachment_style()
            self._lock_conflict_tone()
            self.relationship.state.relationship_trust_locked = True
            self.ai_parent.state.conflict_style = self.relationship.state.conflict_tone.value
            self.ai_parent.state.conflict_style_stability = min(
                1.0,
                self.ai_parent.state.conflict_style_stability + 0.25,
            )
            self.ai_parent.behavioral_baseline = {
                "supportiveness": self.ai_parent.state.supportiveness,
                "defensiveness": self.ai_parent.state.defensiveness,
                "stress_level": self.ai_parent.state.stress_level,
                "conflict_style": self.ai_parent.state.conflict_style,
            }
            self.act_one_locks = {
                "attachment_security_set": self.child.state.attachment_security,
                "conflict_intensity_baseline": self.relationship.state.conflict_intensity,
                "ai_conflict_style_stabilized": self.ai_parent.state.conflict_style,
                "relationship_trust_baseline_locked": self.relationship.state.trust,
                "long_term_flags_stored": dict(self.long_term_flags),
            }
            self.memory_tags.add(
                MemoryTag(
                    tag="act1_state_lock",
                    intensity=1.0,
                    source="system",
                    day=14,
                    act=1,
                    metadata=self.act_one_locks,
                )
            )
            self.player_influence = 0.85
            self.emotional_impact_multiplier = 1.15
        elif completed_act == 2:
            self.child.state.lock_archetype()
            self.act_one_locks = {
                "honesty_baseline_locked": self.child.state.honesty_baseline,
                "authority_structure_locked": self.relationship.state.authority_structure,
                "loyalty_bias_trajectory": self.child.state.loyalty_bias,
                "conflict_internalization_trajectory": self.child.state.conflict_internalization,
                "anxiety_baseline_locked": self.child.state.anxiety_baseline,
                "child_archetype": self.child.state.archetype.value if self.child.state.archetype else None,
            }
            self.memory_tags.add(
                MemoryTag(
                    tag="act2_state_lock",
                    intensity=1.0,
                    source="system",
                    day=14,
                    act=2,
                    metadata=self.act_one_locks,
                )
            )
            self.player_influence = 0.65
            self.emotional_impact_multiplier = 1.30

    def _lock_conflict_tone(self) -> None:
        relationship = self.relationship.state

        if relationship.trust > 0.68 and relationship.communication_openness > 0.62:
            relationship.conflict_tone = ConflictTone.COLLABORATIVE
        elif relationship.resentment > 0.65 and relationship.defensiveness > 0.60:
            relationship.conflict_tone = ConflictTone.VOLATILE
        elif relationship.communication_openness < 0.40:
            relationship.conflict_tone = ConflictTone.WITHDRAWN
        else:
            relationship.conflict_tone = ConflictTone.MIXED

    def _record_memory_tags(self, day_event: DayEvent, choice: PlayerChoice, response_type: ResponseType) -> None:
        for tag in choice.memory_tags:
            self.memory_tags.add(
                MemoryTag(
                    tag=tag,
                    intensity=0.5 if response_type == ResponseType.NEUTRAL else 0.7,
                    source="player_choice",
                    day=day_event.day_number,
                    act=day_event.act_number,
                    metadata={
                        "time_block": TIME_BLOCKS[self.position.block_index],
                        "choice_id": choice.choice_id,
                        "response_type": response_type.value,
                    },
                )
            )

    def _evaluate_dynamic_end(self) -> None:
        rs = self.relationship.state
        cs = self.child.state
        ai = self.ai_parent.state

        if rs.trust <= 0.10 and rs.resentment >= 0.90 and cs.emotional_safety <= 0.25:
            self.is_finished = True
            self.finish_reason = "Relationship collapse threshold reached"
            return

        if cs.conflict_internalization >= 0.92 and cs.self_worth <= 0.20:
            self.is_finished = True
            self.finish_reason = "Child distress threshold reached"
            return

        if ai.stress_level >= 0.95 and rs.communication_openness <= 0.20:
            self.is_finished = True
            self.finish_reason = "Co-parent regulation breakdown"

    def _persist_memory_tags(self) -> None:
        if self.memory_store:
            self.memory_store.save(self.memory_tags)

    def _apply_flags_from_updates(self, updates: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        flags = updates.get("flags", {})
        applied: Dict[str, float] = {}
        for flag_key, delta in flags.items():
            current_value = self.long_term_flags.get(flag_key, 0.0)
            new_value = current_value + delta
            self.long_term_flags[flag_key] = new_value
            applied[flag_key] = new_value
        return applied

    def _scale_updates(self, updates: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        scaled: Dict[str, Dict[str, float]] = {}
        for section, payload in updates.items():
            if section == "flags":
                scaled[section] = dict(payload)
                continue

            multiplier = self.player_influence if section == "relationship" else self.emotional_impact_multiplier
            scaled[section] = {key: value * multiplier for key, value in payload.items()}
        return scaled
