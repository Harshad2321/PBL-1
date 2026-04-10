from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class PlayerChoice:
    choice_id: str
    text: str
    updates: Dict[str, Dict[str, float]]
    memory_tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "choice_id": self.choice_id,
            "text": self.text,
            "updates": self.updates,
            "memory_tags": self.memory_tags,
        }


@dataclass
class TimeBlockEvent:
    block_name: str
    scenario_text: str
    player_choices: List[PlayerChoice]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_name": self.block_name,
            "scenario_text": self.scenario_text,
            "player_choices": [choice.to_dict() for choice in self.player_choices],
        }


@dataclass
class DayEvent:
    act_number: int
    day_number: int
    title: str
    age_range: str
    time_blocks: Dict[str, TimeBlockEvent]

    def get_block(self, block_name: str) -> TimeBlockEvent:
        return self.time_blocks[block_name]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "act_number": self.act_number,
            "day_number": self.day_number,
            "title": self.title,
            "age_range": self.age_range,
            "time_blocks": {name: block.to_dict() for name, block in self.time_blocks.items()},
        }
