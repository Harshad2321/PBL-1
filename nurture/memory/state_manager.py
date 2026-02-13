from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json
import uuid

from nurture.core.data_structures import ParentState, InteractionRecord
from nurture.core.enums import ParentRole
from nurture.memory.memory_store import MemoryStore

@dataclass
class GameSession:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    last_saved: Optional[datetime] = None
    player_parent: Optional[ParentState] = None
    ai_parent: Optional[ParentState] = None
    interaction_history: List[InteractionRecord] = field(default_factory=list)
    current_scenario: str = ""
    current_day: int = 1
    current_act: int = 1
    flags: Dict[str, bool] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "last_saved": self.last_saved.isoformat() if self.last_saved else None,
            "player_parent": self.player_parent.to_dict() if self.player_parent else None,
            "ai_parent": self.ai_parent.to_dict() if self.ai_parent else None,
            "interaction_history": [i.to_dict() for i in self.interaction_history],
            "current_scenario": self.current_scenario,
            "current_day": self.current_day,
            "current_act": self.current_act,
            "flags": self.flags,
            "metrics": self.metrics,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameSession':
        session = cls(
            id=data.get("id", str(uuid.uuid4())),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            current_scenario=data.get("current_scenario", ""),
            current_day=data.get("current_day", 1),
            current_act=data.get("current_act", 1),
            flags=data.get("flags", {}),
            metrics=data.get("metrics", {}),
        )

        if data.get("last_saved"):
            session.last_saved = datetime.fromisoformat(data["last_saved"])

        if data.get("player_parent"):
            session.player_parent = ParentState.from_dict(data["player_parent"])

        if data.get("ai_parent"):
            session.ai_parent = ParentState.from_dict(data["ai_parent"])

        session.interaction_history = [
            InteractionRecord.from_dict(i)
            for i in data.get("interaction_history", [])
        ]

        return session

class StateManager:

    def __init__(self, save_directory: Optional[Path] = None):
        if save_directory is None:
            self.save_directory = Path("./saves")
        elif isinstance(save_directory, str):
            self.save_directory = Path(save_directory)
        else:
            self.save_directory = save_directory
        self.save_directory.mkdir(parents=True, exist_ok=True)

        self.session: Optional[GameSession] = None
        self.player_memory: Optional[MemoryStore] = None
        self.ai_memory: Optional[MemoryStore] = None
        self._state_history: List[Dict[str, Any]] = []
        self._max_history = 50

    def initialize_session(
        self,
        player_role: ParentRole,
        player_name: str,
        ai_name: Optional[str] = None
    ) -> GameSession:
        ai_role = ParentRole.get_opposite(player_role)

        if not ai_name:
            ai_name = "Sarah" if ai_role == ParentRole.MOTHER else "Michael"

        player_parent = ParentState.create_player(player_role, player_name)
        ai_parent = ParentState.create_ai(ai_role, ai_name)

        self.player_memory = MemoryStore(agent_id=player_parent.id)
        self.ai_memory = MemoryStore(agent_id=ai_parent.id)

        self.session = GameSession(
            player_parent=player_parent,
            ai_parent=ai_parent,
        )

        self.session.metrics = {
            "relationship_quality": 0.7,
            "communication_score": 0.5,
            "conflict_count": 0,
            "positive_interactions": 0,
            "negative_interactions": 0,
        }

        return self.session

    def get_player_state(self) -> Optional[ParentState]:
        return self.session.player_parent if self.session else None

    def get_ai_state(self) -> Optional[ParentState]:
        return self.session.ai_parent if self.session else None

    def record_interaction(self, record: InteractionRecord) -> None:
        if self.session:
            self.session.interaction_history.append(record)

            if record.relationship_impact > 0:
                self.session.metrics["positive_interactions"] = \
                    self.session.metrics.get("positive_interactions", 0) + 1
            elif record.relationship_impact < 0:
                self.session.metrics["negative_interactions"] = \
                    self.session.metrics.get("negative_interactions", 0) + 1

    def snapshot_state(self) -> None:
        if self.session:
            snapshot = self.session.to_dict()
            self._state_history.append(snapshot)

            if len(self._state_history) > self._max_history:
                self._state_history = self._state_history[-self._max_history:]

    def get_recent_interactions(self, count: int = 5) -> List[InteractionRecord]:
        if self.session:
            return self.session.interaction_history[-count:]
        return []

    def update_relationship_quality(self, delta: float) -> None:
        if self.session:
            current = self.session.metrics.get("relationship_quality", 0.7)
            self.session.metrics["relationship_quality"] = max(0.0, min(1.0, current + delta))

            if self.session.player_parent:
                self.session.player_parent.relationship_quality = \
                    self.session.metrics["relationship_quality"]
            if self.session.ai_parent:
                self.session.ai_parent.relationship_quality = \
                    self.session.metrics["relationship_quality"]

    def set_flag(self, flag: str, value: bool) -> None:
        if self.session:
            self.session.flags[flag] = value

    def get_flag(self, flag: str, default: bool = False) -> bool:
        if self.session:
            return self.session.flags.get(flag, default)
        return default

    def save_game(self, slot_name: str) -> Path:
        if not self.session:
            raise ValueError("No active session to save")

        self.session.last_saved = datetime.now()

        save_path = self.save_directory / f"{slot_name}.json"
        with open(save_path, 'w') as f:
            json.dump(self.session.to_dict(), f, indent=2)

        if self.player_memory:
            self.player_memory.save_to_file(
                self.save_directory / f"{slot_name}_player_memory.json"
            )
        if self.ai_memory:
            self.ai_memory.save_to_file(
                self.save_directory / f"{slot_name}_ai_memory.json"
            )

        return save_path

    def load_game(self, slot_name: str) -> GameSession:
        save_path = self.save_directory / f"{slot_name}.json"

        if not save_path.exists():
            raise FileNotFoundError(f"Save file not found: {save_path}")

        with open(save_path, 'r') as f:
            data = json.load(f)

        self.session = GameSession.from_dict(data)

        player_memory_path = self.save_directory / f"{slot_name}_player_memory.json"
        if player_memory_path.exists():
            self.player_memory = MemoryStore.load_from_file(player_memory_path)

        ai_memory_path = self.save_directory / f"{slot_name}_ai_memory.json"
        if ai_memory_path.exists():
            self.ai_memory = MemoryStore.load_from_file(ai_memory_path)

        return self.session

    def list_saves(self) -> List[Dict[str, Any]]:
        saves = []
        for save_file in self.save_directory.glob("*.json"):
            if "_memory" not in save_file.name:
                try:
                    with open(save_file, 'r') as f:
                        data = json.load(f)
                    saves.append({
                        "slot_name": save_file.stem,
                        "created_at": data.get("created_at"),
                        "last_saved": data.get("last_saved"),
                        "current_day": data.get("current_day", 1),
                        "current_act": data.get("current_act", 1),
                    })
                except (json.JSONDecodeError, IOError):
                    continue

        return sorted(saves, key=lambda x: x.get("last_saved") or "", reverse=True)

    def delete_save(self, slot_name: str) -> bool:
        try:
            save_path = self.save_directory / f"{slot_name}.json"
            if save_path.exists():
                save_path.unlink()

            for suffix in ["_player_memory.json", "_ai_memory.json"]:
                memory_path = self.save_directory / f"{slot_name}{suffix}"
                if memory_path.exists():
                    memory_path.unlink()

            return True
        except IOError:
            return False
