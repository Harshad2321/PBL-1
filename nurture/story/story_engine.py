"""
Story Engine

Manages story progression, presents scenarios and choices,
and processes player decisions through the narrative.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
from pathlib import Path

from nurture.story.story_data import ACT_1, ActData, DayScenario


@dataclass
class StoryProgress:
    """Tracks player's position in the story."""
    current_act: str  # e.g., "ACT 1 — FOUNDATION"
    current_day: int  # 1-12 for Act 1
    total_acts_completed: int
    choices_made: Dict[str, str] = field(default_factory=dict)  # day_X: choice_id
    impacts_accumulated: List[str] = field(default_factory=list)  # hidden impacts
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "current_act": self.current_act,
            "current_day": self.current_day,
            "total_acts_completed": self.total_acts_completed,
            "choices_made": self.choices_made,
            "impacts_accumulated": self.impacts_accumulated,
        }


class StoryEngine:
    """Manages narrative progression and scenario delivery."""
    
    def __init__(self):
        """Initialize story engine with Act 1."""
        self.acts = [ACT_1]  # ACT 2-4 to be added later
        self.current_act_index = 0
        self.progress = StoryProgress(
            current_act=ACT_1.phase.value,
            current_day=1,
            total_acts_completed=0,
        )
    
    def get_current_scenario(self) -> DayScenario:
        """Get the scenario for the current day."""
        current_act = self.acts[self.current_act_index]
        # Days are 1-indexed, list is 0-indexed
        day_index = self.progress.current_day - 1
        return current_act.days[day_index]
    
    def get_scenario_presentation(self) -> Dict[str, Any]:
        """Get formatted scenario data for presentation to player."""
        scenario = self.get_current_scenario()
        current_act = self.acts[self.current_act_index]
        
        return {
            "act": self.progress.current_act,
            "day": self.progress.current_day,
            "total_days_in_act": current_act.total_days,
            "title": scenario.title,
            "description": scenario.description,
            "gameplay_time": scenario.gameplay_time,
            "scenario_text": scenario.scenario_text,
            "hidden_impact_intro": scenario.hidden_impact_intro,
            "choices": [
                {
                    "id": choice.choice_id,
                    "text": choice.text,
                }
                for choice in scenario.choices
            ]
        }
    
    def process_choice(self, choice_id: str) -> Dict[str, Any]:
        """
        Process player's choice and return impact information.
        
        Args:
            choice_id: The chosen option ID
            
        Returns:
            Dictionary with impacts, AI response, and progression info
        """
        scenario = self.get_current_scenario()
        
        # Find the chosen option
        chosen_choice = None
        for choice in scenario.choices:
            if choice.choice_id == choice_id:
                chosen_choice = choice
                break
        
        if not chosen_choice:
            return {
                "success": False,
                "error": f"Choice {choice_id} not found"
            }
        
        # Record the choice
        day_key = f"day_{self.progress.current_day}"
        self.progress.choices_made[day_key] = choice_id
        
        # Accumulate impacts
        self.progress.impacts_accumulated.extend(chosen_choice.hidden_impact)
        
        result = {
            "success": True,
            "choice_text": chosen_choice.text,
            "impact_description": chosen_choice.impact_description,
            "hidden_impacts": chosen_choice.hidden_impact,
            "day_completed": self.progress.current_day,
        }
        
        # Check if day should progress
        # (In full implementation, this might require solving a scenario or waiting)
        self.progress.current_day += 1
        current_act = self.acts[self.current_act_index]
        
        # Check if act is complete
        if self.progress.current_day > current_act.total_days:
            result["act_complete"] = True
            result["act_summary"] = self._generate_act_summary()
            # Don't auto-progress act; game will handle transition
            self.progress.current_day = current_act.total_days  # Reset to last day
        else:
            result["act_complete"] = False
            result["next_day_preview"] = self.acts[self.current_act_index].days[
                self.progress.current_day - 1
            ].title
        
        return result
    
    def can_progress_to_next_act(self) -> bool:
        """Check if current act is complete."""
        current_act = self.acts[self.current_act_index]
        return self.progress.current_day >= current_act.total_days
    
    def progress_to_next_act(self) -> bool:
        """Move to next act if available."""
        if self.current_act_index + 1 < len(self.acts):
            self.current_act_index += 1
            self.progress.total_acts_completed += 1
            next_act = self.acts[self.current_act_index]
            self.progress.current_act = next_act.phase.value
            self.progress.current_day = 1
            return True
        return False
    
    def _generate_act_summary(self) -> Dict[str, Any]:
        """Generate summary of completed act."""
        completed_act = self.acts[self.current_act_index]
        
        # Count choices by impact category
        impact_count = {}
        for impact in self.progress.impacts_accumulated:
            impact_count[impact] = impact_count.get(impact, 0) + 1
        
        # Find dominant patterns
        dominant_impacts = sorted(
            impact_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "act_name": completed_act.phase.value,
            "days_completed": completed_act.total_days,
            "total_impacts": len(self.progress.impacts_accumulated),
            "dominant_patterns": [impact for impact, count in dominant_impacts],
            "choices_breakdown": {
                day_key: choice_id
                for day_key, choice_id in self.progress.choices_made.items()
                if day_key.startswith("day_")
            }
        }
    
    def get_learning_tags_for_ai(self) -> Dict[str, float]:
        """
        Convert accumulated impacts into learning tags for AI adaptation.
        
        Returns:
            Dictionary of impact tags with confidence scores (0-1)
        """
        if not self.progress.impacts_accumulated:
            return {}
        
        # Count occurrences
        impact_count = {}
        for impact in self.progress.impacts_accumulated:
            impact_count[impact] = impact_count.get(impact, 0) + 1
        
        # Convert to confidence scores (0-1)
        max_count = max(impact_count.values())
        return {
            impact: count / max_count
            for impact, count in impact_count.items()
        }
    
    def save_progress(self, filepath: Path) -> bool:
        """Save story progress to file."""
        try:
            data = {
                "story_progress": self.progress.to_dict(),
                "timestamp": datetime.now().isoformat(),
            }
            filepath.write_text(json.dumps(data, indent=2))
            return True
        except Exception as e:
            print(f"Error saving story progress: {e}")
            return False
    
    def load_progress(self, filepath: Path) -> bool:
        """Load story progress from file."""
        try:
            data = json.loads(filepath.read_text())
            progress_data = data["story_progress"]
            
            self.progress = StoryProgress(
                current_act=progress_data["current_act"],
                current_day=progress_data["current_day"],
                total_acts_completed=progress_data["total_acts_completed"],
                choices_made=progress_data["choices_made"],
                impacts_accumulated=progress_data["impacts_accumulated"],
            )
            return True
        except Exception as e:
            print(f"Error loading story progress: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current story status."""
        current_act = self.acts[self.current_act_index]
        
        return {
            "act": self.progress.current_act,
            "current_act": self.current_act_index + 1,
            "day": self.progress.current_day,
            "current_day": self.progress.current_day,
            "total_days": current_act.total_days,
            "progress_percent": (self.progress.current_day / current_act.total_days) * 100,
            "acts_completed": self.progress.total_acts_completed,
            "total_acts": len(self.acts),
            "choices_made": len(self.progress.choices_made),
            "total_impacts": len(self.progress.impacts_accumulated),
        }
    
    def get_save_state(self) -> Dict[str, Any]:
        """Get story state for saving (serializable dict)."""
        return self.progress.to_dict()
    
    def load_save_state(self, state: Dict[str, Any]) -> bool:
        """Load story state from saved dict."""
        try:
            self.progress = StoryProgress(
                current_act=state.get("current_act", "ACT 1 — FOUNDATION (Age 0–3)"),
                current_day=state.get("current_day", 1),
                total_acts_completed=state.get("total_acts_completed", 0),
                choices_made=state.get("choices_made", []),
                impacts_accumulated=state.get("impacts_accumulated", []),
            )
            # Update act index based on current day
            self.current_act_index = min(state.get("total_acts_completed", 0), len(self.acts) - 1)
            return True
        except Exception as e:
            print(f"Error loading story state: {e}")
            return False
