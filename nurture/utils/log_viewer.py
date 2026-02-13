import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class LogViewer:

    def __init__(self, save_directory: str = "./saves"):
        self.save_directory = Path(save_directory)

    def load_session(self, slot_name: str = "autosave") -> Optional[Dict[str, Any]]:
        save_path = self.save_directory / f"{slot_name}.json"
        if not save_path.exists():
            return None
        with open(save_path, 'r') as f:
            return json.load(f)

    def get_all_interactions(self, slot_name: str = "autosave") -> List[Dict[str, Any]]:
        data = self.load_session(slot_name)
        if not data:
            return []
        return data.get("interaction_history", [])

    def get_player_info(self, data: Dict[str, Any]) -> Dict[str, str]:
        player = data.get("player_parent", {})
        ai = data.get("ai_parent", {})
        return {
            "player_name": player.get("name", "Unknown"),
            "player_role": player.get("role", "unknown"),
            "player_id": player.get("id", ""),
            "ai_name": ai.get("name", "Unknown"),
            "ai_role": ai.get("role", "unknown"),
            "ai_id": ai.get("id", ""),
        }

    def format_timestamp(self, ts_str: str) -> str:
        try:
            dt = datetime.fromisoformat(ts_str)
            return dt.strftime("%b %d, %Y %I:%M:%S %p")
        except (ValueError, TypeError):
            return ts_str

    def display_full_log(self, slot_name: str = "autosave") -> None:
        data = self.load_session(slot_name)
        if not data:
            print(f"\n  No save file found for slot '{slot_name}'.")
            return

        info = self.get_player_info(data)
        interactions = data.get("interaction_history", [])
        metrics = data.get("metrics", {})

        print(f"\n{'='*70}")
        print(f"  FULL GAME LOG - {slot_name}")
        print(f"{'='*70}")

        print(f"\n  Session ID:    {data.get('id', 'N/A')}")
        print(f"  Created:       {self.format_timestamp(data.get('created_at', ''))}")
        print(f"  Last Saved:    {self.format_timestamp(data.get('last_saved', ''))}")
        print(f"  Progress:      Act {data.get('current_act', 1)}, Day {data.get('current_day', 1)}")
        print(f"  Player:        {info['player_name']} ({info['player_role'].title()})")
        print(f"  AI Partner:    {info['ai_name']} ({info['ai_role'].title()})")

        print(f"\n{'─'*70}")
        print(f"  RELATIONSHIP METRICS")
        print(f"{'─'*70}")
        for key, value in metrics.items():
            label = key.replace("_", " ").title()
            if isinstance(value, float):
                bar = self._progress_bar(value, max_val=1.0)
                print(f"  {label:<30} {bar} {value:.2f}")
            else:
                print(f"  {label:<30} {value}")

        print(f"\n{'─'*70}")
        print(f"  STORY CHOICES")
        print(f"{'─'*70}")
        story_state = data.get("flags", {}).get("story_state", {})
        choices = story_state.get("choices_made", {})
        impacts = story_state.get("impacts_accumulated", [])

        if choices:
            for day, choice in choices.items():
                day_label = day.replace("_", " ").title()
                print(f"  {day_label}: {choice}")
        else:
            print("  No story choices recorded yet.")

        if impacts:
            print(f"\n  Accumulated Impacts:")
            for impact in impacts:
                print(f"    - {impact.replace('_', ' ').title()}")

        print(f"\n{'─'*70}")
        print(f"  CONVERSATION LOG ({len(interactions)} interactions)")
        print(f"{'─'*70}")

        if not interactions:
            print("\n  No interactions recorded yet.\n")
            return

        player_name = info['player_name']
        ai_name = info['ai_name']
        player_id = info['player_id']

        for i, interaction in enumerate(interactions, 1):
            ts = self.format_timestamp(interaction.get("timestamp", ""))
            itype = interaction.get("interaction_type", "unknown").replace("_", " ").title()

            is_player_initiator = interaction.get("initiator_id") == player_id

            if is_player_initiator:
                speaker1 = player_name
                speaker2 = ai_name
            else:
                speaker1 = ai_name
                speaker2 = player_name

            msg1 = interaction.get("initiator_message", "")
            msg2 = interaction.get("responder_message", "")

            emotional = interaction.get("emotional_impact", {})
            rel_impact = interaction.get("relationship_impact", 0.0)

            print(f"\n  [{i}] {ts}  |  Type: {itype}")
            print(f"  {'─'*60}")

            if msg1:
                print(f"  {speaker1}: {msg1}")
            if msg2:
                print(f"  {speaker2}: {msg2}")

            impact_parts = []
            if emotional.get("player_valence") is not None:
                pv = emotional["player_valence"]
                impact_parts.append(f"Player mood: {'+' if pv > 0 else ''}{pv:.3f}")
            if emotional.get("ai_valence") is not None:
                av = emotional["ai_valence"]
                impact_parts.append(f"AI mood: {'+' if av > 0 else ''}{av:.3f}")
            if rel_impact != 0:
                impact_parts.append(f"Relationship: {'+' if rel_impact > 0 else ''}{rel_impact:.4f}")

            if impact_parts:
                print(f"  Impact: {' | '.join(impact_parts)}")

        print(f"\n{'─'*70}")
        print(f"  EMOTIONAL STATE SNAPSHOT")
        print(f"{'─'*70}")

        for label, parent_key in [("Player", "player_parent"), ("AI Partner", "ai_parent")]:
            parent = data.get(parent_key, {})
            emotions = parent.get("emotional_state", {}).get("emotions", {})
            stress = parent.get("emotional_state", {}).get("stress_level", 0)
            if emotions:
                print(f"\n  {label} ({parent.get('name', 'Unknown')}):")
                for emo, val in emotions.items():
                    bar = self._progress_bar(val)
                    print(f"    {emo.title():<15} {bar} {val:.2f}")
                print(f"    {'Stress':<15} {self._progress_bar(stress)} {stress:.2f}")

        print(f"\n{'='*70}")
        print(f"  END OF LOG")
        print(f"{'='*70}\n")

    def display_conversation_only(self, slot_name: str = "autosave") -> None:
        data = self.load_session(slot_name)
        if not data:
            print(f"\n  No save file found for slot '{slot_name}'.")
            return

        info = self.get_player_info(data)
        interactions = data.get("interaction_history", [])
        player_name = info['player_name']
        ai_name = info['ai_name']
        player_id = info['player_id']

        print(f"\n{'='*70}")
        print(f"  CONVERSATION HISTORY")
        print(f"{'='*70}")

        if not interactions:
            print("\n  No conversations recorded.\n")
            return

        for interaction in interactions:
            ts = self.format_timestamp(interaction.get("timestamp", ""))
            is_player_initiator = interaction.get("initiator_id") == player_id

            msg1 = interaction.get("initiator_message", "")
            msg2 = interaction.get("responder_message", "")

            if is_player_initiator:
                if msg1:
                    print(f"\n  [{ts}]")
                    print(f"  {player_name}: {msg1}")
                if msg2:
                    print(f"  {ai_name}: {msg2}")
            else:
                if msg1:
                    print(f"\n  [{ts}]")
                    print(f"  {ai_name}: {msg1}")
                if msg2:
                    print(f"  {player_name}: {msg2}")

        print(f"\n{'='*70}\n")

    def display_actions_only(self, slot_name: str = "autosave") -> None:
        data = self.load_session(slot_name)
        if not data:
            print(f"\n  No save file found for slot '{slot_name}'.")
            return

        story_state = data.get("flags", {}).get("story_state", {})
        choices = story_state.get("choices_made", {})
        impacts = story_state.get("impacts_accumulated", [])
        interactions = data.get("interaction_history", [])
        metrics = data.get("metrics", {})

        print(f"\n{'='*70}")
        print(f"  ACTIONS & DECISIONS LOG")
        print(f"{'='*70}")

        print(f"\n  Total Interactions: {len(interactions)}")
        print(f"  Positive Interactions: {int(metrics.get('positive_interactions', 0))}")
        print(f"  Negative Interactions: {int(metrics.get('negative_interactions', 0))}")
        print(f"  Conflict Count: {int(metrics.get('conflict_count', 0))}")

        print(f"\n  Story Choices Made:")
        if choices:
            for day, choice in choices.items():
                day_label = day.replace("_", " ").title()
                print(f"    [{day_label}] -> {choice}")
        else:
            print("    None yet.")

        print(f"\n  Behavioral Impacts Accumulated:")
        if impacts:
            for impact in impacts:
                print(f"    - {impact.replace('_', ' ').title()}")
        else:
            print("    None yet.")

        print(f"\n  Relationship Quality: {metrics.get('relationship_quality', 0):.2f}")
        print(f"  Communication Score:  {metrics.get('communication_score', 0):.2f}")

        print(f"\n{'='*70}\n")

    def display_ai_mood(self, slot_name: str = "autosave") -> None:
        data = self.load_session(slot_name)
        if not data:
            print(f"\n  No save file found for slot '{slot_name}'.")
            return

        ai = data.get("ai_parent", {})
        ai_name = ai.get("name", "AI Partner")
        ai_role = ai.get("role", "unknown").title()
        emotions = ai.get("emotional_state", {}).get("emotions", {})
        stress = ai.get("emotional_state", {}).get("stress_level", 0)
        baseline = ai.get("emotional_state", {}).get("baseline_mood", 0.5)
        volatility = ai.get("emotional_state", {}).get("volatility", 0.3)
        regulation = ai.get("emotional_state", {}).get("regulation_capacity", 0.6)

        print(f"\n{'='*70}")
        print(f"  AI PARTNER MOOD - {ai_name} ({ai_role})")
        print(f"{'='*70}")

        if not emotions:
            print("\n  No emotional data available.\n")
            return

        print(f"\n  Current Emotions:")
        print(f"  {'─'*60}")
        for emo, val in emotions.items():
            label = emo.title()
            bar = self._progress_bar(val)
            level = self._mood_label(val)
            print(f"    {label:<15} {bar} {val:.2f}  ({level})")

        print(f"\n  Overall Stats:")
        print(f"  {'─'*60}")
        print(f"    {'Stress Level':<15} {self._progress_bar(stress)} {stress:.2f}  ({self._mood_label(stress)})")
        print(f"    {'Baseline Mood':<15} {self._progress_bar(baseline)} {baseline:.2f}")
        print(f"    {'Volatility':<15} {self._progress_bar(volatility)} {volatility:.2f}  ({'Reactive' if volatility > 0.5 else 'Stable'})")
        print(f"    {'Self-Control':<15} {self._progress_bar(regulation)} {regulation:.2f}  ({'Strong' if regulation > 0.5 else 'Weak'})")

        dominant_emo = max(emotions.items(), key=lambda x: x[1]) if emotions else ("none", 0)
        print(f"\n  Dominant Emotion: {dominant_emo[0].title()} ({dominant_emo[1]:.2f})")

        interactions = data.get("interaction_history", [])
        if interactions:
            print(f"\n  Mood Changes Over Conversation:")
            print(f"  {'─'*60}")
            for i, interaction in enumerate(interactions, 1):
                emotional = interaction.get("emotional_impact", {})
                av = emotional.get("ai_valence", 0)
                indicator = "+" if av > 0 else ("-" if av < 0 else "=")
                msg_preview = interaction.get("initiator_message", "")[:35]
                if len(interaction.get("initiator_message", "")) > 35:
                    msg_preview += "..."
                print(f"    Turn {i}: [{indicator}] {av:+.4f}  \"{msg_preview}\"")

        print(f"\n{'='*70}\n")

    def _mood_label(self, value: float) -> str:
        if value >= 0.8:
            return "Very High"
        elif value >= 0.6:
            return "High"
        elif value >= 0.4:
            return "Moderate"
        elif value >= 0.2:
            return "Low"
        else:
            return "Very Low"

    def _progress_bar(self, value: float, max_val: float = 1.0, width: int = 20) -> str:
        ratio = min(1.0, max(0.0, value / max_val))
        filled = int(ratio * width)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}]"

    def show_log_menu(self, slot_name: str = "autosave") -> None:
        while True:
            print(f"\n{'='*70}")
            print(f"  GAME LOGS VIEWER")
            print(f"{'='*70}")
            print(f"\n  1. Player & AI Conversations")
            print(f"  2. Choices & Decisions")
            print(f"  3. AI Mood (stress, happiness, etc.)")
            print(f"  4. Everything (full log)")
            print(f"  5. Exit")

            choice = input("\n  Select (1-5): ").strip()

            if choice == "1":
                self.display_conversation_only(slot_name)
            elif choice == "2":
                self.display_actions_only(slot_name)
            elif choice == "3":
                self.display_ai_mood(slot_name)
            elif choice == "4":
                self.display_full_log(slot_name)
            elif choice == "5":
                break
            else:
                print("  Invalid choice. Enter 1-5.")

            if choice in ["1", "2", "3", "4"]:
                input("  Press Enter to continue...")
