from __future__ import annotations

import json
from pathlib import Path

from nurture.simulation.state_models import MemoryTags


class MemoryTagsStore:

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, memory_tags: MemoryTags) -> None:
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(memory_tags.to_dict(), file, indent=2)

    def load(self) -> MemoryTags:
        if not self.file_path.exists():
            return MemoryTags()

        with self.file_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return MemoryTags.from_dict(payload)
