import os
import sys
from typing import Optional, Dict, Any
from pathlib import Path

from nurture.core.enums import ParentRole
from nurture.core.data_structures import ParentState, PersonalityProfile
from nurture.core.events import get_event_bus
from nurture.core.interaction_manager import InteractionManager

from nurture.agents.player_parent import PlayerParent
from nurture.agents.ai_parent import AIParent

from nurture.memory.state_manager import StateManager

from nurture.learning.learning_system import LearningSystem

from nurture.story.story_engine import StoryEngine

from nurture.rules.rule_engine import RuleEngine, create_default_rules
from nurture.rules.emotional_rules import EmotionalRules
from nurture.rules.behavioral_constraints import BehavioralConstraints

from nurture.utils.llm_interface import create_llm_generator
from nurture.utils.log_viewer import LogViewer

def load_env_file():
    env_paths = [
        Path(__file__).parent.parent / ".env",
        Path.cwd() / ".env",
    ]

    for env_path in env_paths:
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            return True
    return False

load_env_file()

class NurtureGame:

    AUTO_SAVE_NAME = "autosave"

    def __init__(self, save_directory: str = "./saves"):
        self.save_directory = save_directory
        self.event_bus = get_event_bus()

        self.player_parent: Optional[PlayerParent] = None
        self.ai_parent: Optional[AIParent] = None
        self.interaction_manager: Optional[InteractionManager] = None
        self.state_manager: Optional[StateManager] = None

        self.learning_system: Optional[LearningSystem] = None

        self.story_engine: Optional[StoryEngine] = None

        self._is_running = False
        self._player_role: Optional[ParentRole] = None
        self._current_day_active = False

        self._last_scenario_key = None
        self._last_choice_key = None
        self._accumulated_impacts = []

        os.makedirs(save_directory, exist_ok=True)

    def select_role(self, role: ParentRole) -> None:
        self._player_role = role
        ai_role = role.get_opposite()

        print(f"\n=== Role Selected ===")
        print(f"You: {role.value.title()}")
        print(f"AI Partner: {ai_role.value.title()}")

        self._initialize_agents(role, ai_role)

    def _initialize_agents(self, player_role: ParentRole, ai_role: ParentRole) -> None:
        from nurture.memory.memory_store import MemoryStore

        player_state = ParentState.create_player(
            role=player_role,
            name=player_role.get_display_name()
        )

        self.player_parent = PlayerParent(
            state=player_state,
            memory_store=MemoryStore("player")
        )

        ai_state = ParentState.create_ai(
            role=ai_role,
            name=ai_role.get_display_name(),
            personality=PersonalityProfile.create_balanced()
        )

        self.ai_parent = AIParent(
            state=ai_state,
            memory_store=MemoryStore("ai_partner")
        )

        llm_generator = None

        print("[*] Connecting to Ollama (mistral:7b-instruct)...")
        try:
            llm_generator = create_llm_generator(
                provider="ollama",
                model_name="mistral:7b-instruct-v0.3-q4_K_M",
                timeout=120
            )
            print("[OK] Ollama connected with mistral:7b-instruct model!")
            print("    Responses will be natural and context-aware.")
        except Exception as e:
            print(f"[!] Ollama not available: {e}")
            print("    Make sure Ollama is running: ollama serve")
            print("[*] Using Mock LLM (template responses)")
            llm_generator = create_llm_generator(provider="mock")

        self.ai_parent.set_llm_generator(llm_generator)

        self.ai_parent.reset_conversation()

        rule_engine = RuleEngine()

        for rule in create_default_rules():
            rule_engine.add_rule(rule)
        for rule in EmotionalRules.get_all_rules():
            rule_engine.add_rule(rule)

        constraints = BehavioralConstraints()
        constraints.add_default_constraints()

        self.state_manager = StateManager(save_directory=self.save_directory)
        self.state_manager.initialize_session(
            player_role=player_role,
            player_name=player_role.get_display_name(),
            ai_name=ai_role.get_display_name()
        )

        self.learning_system = LearningSystem(user_id="player")

        self.interaction_manager = InteractionManager(
            player_parent=self.player_parent,
            ai_parent=self.ai_parent,
            state_manager=self.state_manager,
            rule_engine=rule_engine,
            constraints=constraints
        )

        print("\n[OK] Game initialized successfully!")
        print(f"[OK] Learning System active - AI will adapt to your playstyle")

        self._initialize_story()

    def _initialize_story(self) -> None:
        self.story_engine = StoryEngine()
        print("[OK] Story Engine initialized - Your parenting journey begins...")

    def send_message(self, message: str) -> str:
        if not self.interaction_manager:
            return "Error: Game not started"

        if self.learning_system:
            self.learning_system.learn_from_input(message)

        context = {
            "scenario_key": self._last_scenario_key,
            "choice_key": self._last_choice_key,
            "player_patterns": {},
        }

        if self.story_engine:
            context["player_patterns"] = self.story_engine.get_learning_tags_for_ai()

        ai_response = self.interaction_manager.process_player_message(message, context=context)

        if self.learning_system:
            self.learning_system.learn_from_outcome(ai_response, user_satisfaction=0.5)

        return ai_response

    def get_learning_status(self) -> Dict[str, Any]:
        if not self.learning_system:
            return {}

        return {
            "adaptation_level": f"{self.learning_system.adaptation_level * 100:.1f}%",
            "interactions": self.learning_system.total_interactions,
            "dominant_style": self.learning_system.get_dominant_style(),
            "topics_learned": list(self.learning_system.topics_discussed),
        }

    def get_relationship_status(self) -> dict:
        if not self.interaction_manager:
            return {}

        return self.interaction_manager.get_relationship_status()

    def get_current_scenario(self) -> Dict[str, Any]:
        if not self.story_engine:
            return {}

        return self.story_engine.get_scenario_presentation()

    def present_scenario(self) -> None:
        if not self.story_engine:
            print("Error: Story engine not initialized")
            return

        scenario = self.get_current_scenario()

        print(f"\n{'='*70}")
        print(f"{scenario['act']} - Day {scenario['day']}/{scenario['total_days_in_act']}")
        print(f"{'='*70}")
        print(f"\n{scenario['title']}")
        print(f"\n{scenario['description']}\n")
        print(f"{'-'*70}")
        print(f"\n{scenario['scenario_text']}\n")
        print(f"{'-'*70}")
        print(f"\nWhat do you do?\n")

        for i, choice in enumerate(scenario['choices'], 1):
            print(f"  {i}. {choice['text']}")

        self._current_day_active = True

    def respond_to_scenario(self, choice_number: int) -> bool:
        if not self.story_engine or not self._current_day_active:
            return False

        scenario = self.story_engine.get_current_scenario()

        choice_idx = choice_number - 1

        if choice_idx < 0 or choice_idx >= len(scenario.choices):
            print(f"Invalid choice. Please select 1-{len(scenario.choices)}")
            return False

        choice = scenario.choices[choice_idx]

        title_to_key = {
            "First Night Home": "first_night",
            "Visitors": "visitors",
            "Money Talk": "money",
            "The First Fight": "fight",
            "Quiet Morning": "quiet_morning",
            "Back to Work": "back_to_work",
            "Missed Milestone": "missed_milestone",
            "Sick Night": "sick_night",
            "First Words": "first_words",
            "Unspoken Distance": "unspoken_distance",
            "Public Embarrassment": "public_embarrassment",
            "Third Birthday": "third_birthday",
        }

        choice_id = choice.choice_id
        if "immediate" in choice_id or "defend" in choice_id or "reduce" in choice_id:
            choice_key = "immediate" if "immediate" in choice_id else ("defend" if "defend" in choice_id else "reduce")
        elif "wait" in choice_id or "neutral" in choice_id or "work" in choice_id:
            choice_key = "wait" if "wait" in choice_id else ("neutral" if "neutral" in choice_id else "work")
        elif "wake" in choice_id or "agree" in choice_id or "avoid" in choice_id:
            choice_key = "wake" if "wake" in choice_id else ("agree" if "agree" in choice_id else "avoid")
        elif "calm" in choice_id or "engage" in choice_id or "reassure" in choice_id:
            choice_key = "calm" if "calm" in choice_id else ("engage" if "engage" in choice_id else "reassure")
        elif "continue" in choice_id or "mechanical" in choice_id or "dismiss" in choice_id:
            choice_key = "continue" if "continue" in choice_id else ("mechanical" if "mechanical" in choice_id else "dismiss")
        elif "leave" in choice_id or "distracted" in choice_id or "promise" in choice_id:
            choice_key = "leave" if "leave" in choice_id else ("distracted" if "distracted" in choice_id else "promise")
        elif "apologize" in choice_id or "cooperate" in choice_id or "celebrate" in choice_id:
            choice_key = "apologize" if "apologize" in choice_id else ("cooperate" if "cooperate" in choice_id else "celebrate")
        elif "excuse" in choice_id or "control" in choice_id or "compete" in choice_id:
            choice_key = "excuse" if "excuse" in choice_id else ("control" if "control" in choice_id else "compete")
        elif "blame" in choice_id or "shut" in choice_id or "casual" in choice_id:
            choice_key = "blame" if "blame" in choice_id else ("shutdown" if "shut" in choice_id else "casual")
        elif "honest" in choice_id or "support" in choice_id or "reconnect" in choice_id:
            choice_key = "honest" if "honest" in choice_id else ("support" if "support" in choice_id else "reconnect")
        elif "avoid" in choice_id or "correct" in choice_id or "minimize" in choice_id:
            choice_key = "avoid" if "avoid" in choice_id else ("correct" if "correct" in choice_id else "minimize")
        elif "pretend" in choice_id or "passive" in choice_id or "blame" in choice_id:
            choice_key = "pretend" if "pretend" in choice_id else ("passive" if "passive" in choice_id else "blame")
        else:
            choice_key = choice_id.split("_")[-1] if "_" in choice_id else choice_id

        self._last_scenario_key = title_to_key.get(scenario.title, scenario.title.lower().replace(" ", "_"))
        self._last_choice_key = choice_key

        result = self.story_engine.process_choice(choice.choice_id)

        if not result.get("success"):
            print(f"Error processing choice: {result.get('error')}")
            return False

        if self.learning_system:
            choice_text = result.get("choice_text", "")
            impact_desc = result.get("impact_description", "")
            self.learning_system.learn_from_input(choice_text)
            self.learning_system.learn_from_outcome(impact_desc, user_satisfaction=0.7)

            for impact_tag in result.get("hidden_impacts", []):
                self.learning_system.topics_discussed.add(impact_tag.split("_")[0])

        print(f"\nYou chose: {result.get('choice_text')}\n")

        if result.get("act_complete"):
            print(f"\n{'='*70}")
            print(f"END OF ACT 1 - FOUNDATION (Age 0-3)")
            print(f"{'='*70}\n")
            summary = result.get("act_summary", {})
            print(f"You completed {summary.get('days_completed')} days as a parent.\n")
            print("Your parenting patterns:")
            for pattern in summary.get('dominant_patterns', [])[:5]:
                print(f"  - {pattern.replace('_', ' ').title()}")
            print(f"\nThese choices have shaped your child's early development.")
            print("Ready for the next chapter? (coming soon: ACT 2 - MIRROR)\n")
        else:
            next_day = result.get("next_day_preview", "")
            print(f"The next day arrives...\n")

        self._current_day_active = False
        return True

    def get_story_status(self) -> Dict[str, Any]:
        if not self.story_engine:
            return {}

        return self.story_engine.get_status()

    def save_game(self, filename: str = None) -> str:
        if not self.state_manager:
            return "Error: Game not started"

        if filename is None:
            filename = self.AUTO_SAVE_NAME

        if self.story_engine and self.state_manager.session:
            status = self.story_engine.get_status()
            self.state_manager.session.current_day = status.get("current_day", 1)
            self.state_manager.session.current_act = status.get("current_act", 1)
            if self._player_role:
                self.state_manager.session.flags["player_role"] = self._player_role.value
            self.state_manager.session.flags["story_state"] = self.story_engine.get_save_state()

        return self.state_manager.save_game(filename)

    def load_game(self, filepath: str) -> bool:
        if not self.state_manager:
            self.state_manager = StateManager(save_directory=self.save_directory)

        if self.state_manager.load_session(filepath):
            session = self.state_manager.get_current_session()
            if session:
                player_role = ParentRole(session.player_role) if hasattr(session, 'player_role') else ParentRole.FATHER
                ai_role = player_role.get_opposite()

                self._player_role = player_role
                self._initialize_agents(player_role, ai_role)

                print(f"[OK] Game loaded successfully!")
                return True

        return False

    def _check_for_save(self) -> bool:
        save_path = Path(self.save_directory) / f"{self.AUTO_SAVE_NAME}.json"

        if not save_path.exists():
            return False

        try:
            import json
            with open(save_path, 'r') as f:
                data = json.load(f)

            last_saved = data.get("last_saved", "Unknown")
            current_day = data.get("current_day", 1)
            current_act = data.get("current_act", 1)

            print(f"\n{'='*70}")
            print("  SAVED GAME FOUND!")
            print(f"{'='*70}")
            print(f"\n  Last played: {last_saved[:19] if last_saved != 'Unknown' else 'Unknown'}")
            print(f"  Progress: Act {current_act}, Day {current_day}")
            print(f"\n  1. Continue from saved game")
            print(f"  2. Start a new game")

            while True:
                choice = input("\nYour choice (1 or 2): ").strip()
                if choice == "1":
                    return True
                elif choice == "2":
                    confirm = input("Are you sure? This will overwrite your save. (y/n): ").strip().lower()
                    if confirm == "y":
                        return False
                else:
                    print("Invalid choice. Please enter 1 or 2.")
        except Exception as e:
            print(f"[!] Could not read save file: {e}")
            return False

    def _load_saved_game(self) -> bool:
        try:
            self.state_manager = StateManager(save_directory=self.save_directory)

            session = self.state_manager.load_game(self.AUTO_SAVE_NAME)

            if session:
                role_value = session.flags.get("player_role", "father")
                self._player_role = ParentRole(role_value)
                ai_role = self._player_role.get_opposite()

                print(f"\n=== Continuing as {self._player_role.value.title()} ===")
                print(f"AI Partner: {ai_role.value.title()}")

                self._initialize_agents(self._player_role, ai_role)

                story_state = session.flags.get("story_state")
                if story_state and self.story_engine:
                    self.story_engine.load_save_state(story_state)
                    status = self.story_engine.get_status()
                    print(f"\n[OK] Restored progress: Act {status.get('current_act', 1)}, Day {status.get('day', 1)}")

                return True
        except Exception as e:
            print(f"[!] Error loading save: {e}")
            print("[*] Starting new game instead...")

        return False

    def run_interactive(self) -> None:
        print("\n" + "="*70)
        print("  NURTURE - A Parent Agent Simulation")
        print("  Watch your parenting journey unfold as your AI partner learns from you")
        print("="*70)

        if self._check_for_save():
            if self._load_saved_game():
                self._is_running = True
            else:
                pass

        if not self._is_running:
            print("\nSelect your role:")
            print("  1. Father")
            print("  2. Mother")

            while True:
                choice = input("\nEnter choice (1 or 2): ").strip()
                if choice == "1":
                    self.select_role(ParentRole.FATHER)
                    break
                elif choice == "2":
                    self.select_role(ParentRole.MOTHER)
                    break
                else:
                    print("Invalid choice. Please enter 1 or 2.")

            self._is_running = True

        print("\nCommands: /status /logs /save /quit /help")

        while self._is_running:
            if not self._current_day_active:
                self.present_scenario()

            try:
                user_input = input("\nYour choice (1-3 or /command): ").strip()

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    self._handle_command(user_input[1:])
                    continue

                try:
                    choice_num = int(user_input)
                    if self.respond_to_scenario(choice_num):
                        if self.story_engine and self.story_engine.can_progress_to_next_act():
                            self.save_game()
                            print("\nThank you for playing Nurture!")
                            print("Your progress has been saved.\n")
                            self._is_running = False
                            break

                        print("Would you like to have a conversation with your partner? (y/n): ", end="")
                        conv_input = input().strip().lower()
                        if conv_input == "y":
                            if self.ai_parent:
                                self.ai_parent.reset_conversation()

                            ai_role = self._player_role.get_opposite() if self._player_role else "Partner"
                            print(f"\n--- Conversation with {ai_role.value.title()} ---")
                            print("(Type your messages. Enter /done or /skip to end conversation)\n")

                            while True:
                                message = input("You: ").strip()

                                if not message or message.lower() in ["/done", "/skip", "/end", "/quit"]:
                                    print("\n--- End of conversation ---\n")
                                    break

                                if message.startswith("/"):
                                    if message.lower() == "/status":
                                        self._handle_command("status")
                                    else:
                                        print("(Use /done to end conversation, or just type your message)")
                                    continue

                                response = self.send_message(message)
                                print(f"\n{ai_role.value.title()}: {response}\n")
                except (ValueError, IndexError):
                    print("Invalid input. Enter 1-3 for choices or /command")

            except KeyboardInterrupt:
                print("\n\nGame interrupted. Saving...")
                self.save_game()
                self._is_running = False
            except EOFError:
                print("\n\nEnd of input. Saving...")
                self.save_game()
                self._is_running = False

        if self.state_manager:
            self.save_game()

        print("\nThank you for playing Nurture!")
        print("Your progress has been saved. See you next time!\n")

    def _handle_command(self, command: str) -> None:
        parts = command.split()
        cmd = parts[0].lower() if parts else ""

        if cmd == "status":
            print("\n=== Story Progress ===")
            story_status = self.get_story_status()
            for key, value in story_status.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.1f}%")
                else:
                    print(f"  {key}: {value}")

            status = self.get_relationship_status()
            learning_status = self.get_learning_status()

            print("\n=== Learning Status ===")
            for key, value in learning_status.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")

            print("\n=== Relationship Status ===")
            for key, value in status.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")

        elif cmd == "save":
            filepath = self.save_game()
            print(f"[OK] Game saved!")

        elif cmd == "quit" or cmd == "exit":
            print("[*] Saving game...")
            self.save_game()
            print("[OK] Game saved!")
            self._is_running = False

        elif cmd == "logs":
            self.save_game()
            viewer = LogViewer(save_directory=self.save_directory)
            viewer.show_log_menu(self.AUTO_SAVE_NAME)

        elif cmd == "help":
            print("\nAvailable commands:")
            print("  /status - View story and relationship progress")
            print("  /logs   - View full game logs (conversations, actions, emotions)")
            print("  /save   - Save your game")
            print("  /quit   - Save and exit game")
            print("  /help   - Show this help")

        else:
            print(f"Unknown command: /{cmd}")
            print("Type /help for available commands.")

def main():
    game = NurtureGame()
    game.run_interactive()

if __name__ == "__main__":
    main()
