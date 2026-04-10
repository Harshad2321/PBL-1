from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from nurture.simulation.state_models import AIParentState, ChildState, RelationshipState


@dataclass
class Parent:
    name: str
    role: str
    is_player: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "is_player": self.is_player,
        }


@dataclass
class AIParent(Parent):
    state: AIParentState = field(default_factory=AIParentState)
    behavioral_baseline: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.is_player = False

    def apply_state_updates(self, updates: Dict[str, float]) -> None:
        self.state.apply_updates(updates)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update(
            {
                "state": self.state.to_dict(),
                "behavioral_baseline": self.behavioral_baseline,
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIParent":
        return cls(
            name=data["name"],
            role=data["role"],
            is_player=False,
            state=AIParentState.from_dict(data.get("state", {})),
            behavioral_baseline=data.get("behavioral_baseline", {}),
        )


@dataclass
class Child:
    name: str
    state: ChildState = field(default_factory=ChildState)

    def apply_state_updates(self, updates: Dict[str, float]) -> None:
        self.state.apply_updates(updates)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Child":
        return cls(
            name=data["name"],
            state=ChildState.from_dict(data.get("state", {})),
        )


@dataclass
class Relationship:
    parent_a_name: str
    parent_b_name: str
    state: RelationshipState = field(default_factory=RelationshipState)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)

    def apply_state_updates(self, updates: Dict[str, float]) -> None:
        self.state.apply_updates(updates)

    def log_interaction(self, interaction: Dict[str, Any]) -> None:
        self.interaction_history.append(interaction)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parent_a_name": self.parent_a_name,
            "parent_b_name": self.parent_b_name,
            "state": self.state.to_dict(),
            "interaction_history": self.interaction_history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relationship":
        return cls(
            parent_a_name=data["parent_a_name"],
            parent_b_name=data["parent_b_name"],
            state=RelationshipState.from_dict(data.get("state", {})),
            interaction_history=data.get("interaction_history", []),
        )
