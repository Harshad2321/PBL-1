"""
Nurture - Main Entry Point
===========================

Main entry point for the Nurture parent agent simulation.
Provides role selection, scenario management, and the main interaction loop.
"""

import os
import sys
from typing import Optional, Dict, Any
from pathlib import Path

# Core imports
from nurture.core.enums import ParentRole
from nurture.core.data_structures import PersonalityProfile
from nurture.core.events import get_event_bus
from nurture.core.interaction_manager import InteractionManager, ScenarioContext

# Agent imports
from nurture.agents.player_parent import PlayerParent
from nurture.agents.ai_parent import AIParent

# Memory imports
from nurture.memory.state_manager import StateManager

# Learning imports
from nurture.learning.learning_system import LearningSystem

# Story imports
from nurture.story.story_engine import StoryEngine

# Rules imports
from nurture.rules.rule_engine import RuleEngine, create_default_rules
from nurture.rules.emotional_rules import EmotionalRules
from nurture.rules.behavioral_constraints import BehavioralConstraints

# Utils imports
from nurture.utils.llm_interface import create_llm_generator, LLMConfig


def load_env_file():
    """Load environment variables from .env file if it exists."""
    # Look for .env in the project root
    env_paths = [
        Path(__file__).parent.parent / ".env",  # nurture/../.env
        Path.cwd() / ".env",  # current directory
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


# Load .env file on module import
load_env_file()


class NurtureGame:
    """
    Main game class for Nurture simulation.
    
    Manages game setup, role selection, and the main interaction loop.
    Features adaptive AI that learns from user inputs.
    """
    
    def __init__(self, save_directory: str = "./saves"):
        """
        Initialize the Nurture game.
        
        Args:
            save_directory: Directory for save files
        """
        self.save_directory = save_directory
        self.event_bus = get_event_bus()
        
        # Core components (initialized on game start)
        self.player_parent: Optional[PlayerParent] = None
        self.ai_parent: Optional[AIParent] = None
        self.interaction_manager: Optional[InteractionManager] = None
        self.state_manager: Optional[StateManager] = None
        
        # Learning system - tracks user behavior and AI adaptation
        self.learning_system: Optional[LearningSystem] = None
        
        # Story engine - manages narrative progression
        self.story_engine: Optional[StoryEngine] = None
        
        # Game state
        self._is_running = False
        self._player_role: Optional[ParentRole] = None
        self._current_day_active = False  # True while day scenario is active
        
        # Context for AI conversations
        self._last_scenario_key = None
        self._last_choice_key = None
        self._accumulated_impacts = []
        
        # Ensure save directory exists
        os.makedirs(save_directory, exist_ok=True)
    
    def select_role(self, role: ParentRole) -> None:
        """
        Select the player's parental role.
        
        Args:
            role: FATHER or MOTHER
        """
        self._player_role = role
        ai_role = role.get_opposite()
        
        print(f"\n=== Role Selected ===")
        print(f"You: {role.value.title()}")
        print(f"AI Partner: {ai_role.value.title()}")
        
        # Initialize agents
        self._initialize_agents(role, ai_role)
    
    def _initialize_agents(self, player_role: ParentRole, ai_role: ParentRole) -> None:
        """Initialize player and AI parent agents."""
        
        # Create player parent state using factory method
        from nurture.core.data_structures import ParentState, PersonalityProfile
        from nurture.memory.memory_store import MemoryStore
        
        player_state = ParentState.create_player(
            role=player_role,
            name=player_role.get_display_name()
        )
        
        self.player_parent = PlayerParent(
            state=player_state,
            memory_store=MemoryStore("player")
        )
        
        # Create AI parent state using factory method
        ai_state = ParentState.create_ai(
            role=ai_role,
            name=ai_role.get_display_name(),
            personality=PersonalityProfile.create_balanced()
        )
        
        self.ai_parent = AIParent(
            state=ai_state,
            memory_store=MemoryStore("ai_partner")
        )
        
        # Set up LLM with Ollama (local) -> Mock fallback
        import os
        
        llm_generator = None
        
        # Try Ollama (local LLM)
        print("[*] Checking Ollama (local AI)...")
        try:
            import urllib.request
            req = urllib.request.Request('http://localhost:11434/api/tags')
            response = urllib.request.urlopen(req, timeout=3)
            
            # Try to find a good model
            import json
            models_data = json.loads(response.read().decode())
            available_models = [m['name'].split(':')[0] for m in models_data.get('models', [])]
            
            # Prefer conversational models
            preferred_models = ['neural-chat', 'mistral', 'llama2', 'dolphin-mixtral']
            selected_model = None
            
            for pref in preferred_models:
                for model in available_models:
                    if pref in model.lower():
                        selected_model = pref
                        break
                if selected_model:
                    break
            
            # Use first available model if no preference found
            if not selected_model and available_models:
                selected_model = available_models[0]
            
            if selected_model:
                print(f"[OK] Ollama detected! Using '{selected_model}' model for context-aware AI.")
                print("    Responses will understand scenario and conversation context.")
                llm_generator = create_llm_generator(
                    provider="ollama",
                    model_name=selected_model
                )
            else:
                print("[!] Ollama found but no models pulled.")
                print("    Pull a model with: ollama pull neural-chat")
        except Exception as e:
            print(f"[!] Ollama not available: {e}")
            print("    Install Ollama from https://ollama.ai and run: ollama pull neural-chat")
        
        # Fall back to Mock if Ollama not available
        if llm_generator is None:
            print("[*] Using Mock LLM (template responses)")
            print("    For real AI responses, install Ollama: https://ollama.ai")
            llm_generator = create_llm_generator(provider="mock")
        
        self.ai_parent.set_llm_generator(llm_generator)
        
        # Initialize rule engine
        rule_engine = RuleEngine()
        
        # Add default rules
        for rule in create_default_rules():
            rule_engine.add_rule(rule)
        for rule in EmotionalRules.get_all_rules():
            rule_engine.add_rule(rule)
        
        # Initialize constraints
        constraints = BehavioralConstraints()
        constraints.add_default_constraints()
        
        # Initialize state manager
        self.state_manager = StateManager(save_directory=self.save_directory)
        self.state_manager.initialize_session(
            player_role=player_role,
            player_name=player_role.get_display_name(),
            ai_name=ai_role.get_display_name()
        )
        
        # Initialize learning system - tracks user behavior and AI adaptation
        self.learning_system = LearningSystem(user_id="player")
        
        # Initialize interaction manager
        self.interaction_manager = InteractionManager(
            player_parent=self.player_parent,
            ai_parent=self.ai_parent,
            state_manager=self.state_manager,
            rule_engine=rule_engine,
            constraints=constraints
        )
        
        print("\n[OK] Game initialized successfully!")
        print(f"[OK] Learning System active - AI will adapt to your playstyle")
        
        # Initialize story engine
        self._initialize_story()
    
    def _initialize_story(self) -> None:
        """Initialize the story engine with Act 1."""
        self.story_engine = StoryEngine()
        print("[OK] Story Engine initialized - Your parenting journey begins...")
    
    def configure_llm(
        self,
        provider: str = "mock",
        api_key: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
        **kwargs
    ) -> None:
        """
        Configure the LLM for AI responses.
        
        Args:
            provider: LLM provider (openai, local, mock)
            api_key: API key if needed
            model_name: Model to use
            **kwargs: Additional configuration
        """
        if not self.ai_parent:
            print("Error: Start game first before configuring LLM")
            return
        
        llm_generator = create_llm_generator(
            provider=provider,
            api_key=api_key,
            model_name=model_name,
            **kwargs
        )
        self.ai_parent.set_llm_generator(llm_generator)
        print(f"[OK] LLM configured: {provider} / {model_name}")
    
    def set_scenario(
        self,
        title: str,
        description: str,
        topic: str = "",
        **kwargs
    ) -> None:
        """
        Set the current interaction scenario.
        
        Args:
            title: Scenario title
            description: Scenario description
            topic: Main topic of discussion
        """
        if not self.interaction_manager:
            print("Error: Start game first")
            return
        
        scenario = ScenarioContext(
            scenario_id=f"scenario_{hash(title) % 10000:04d}",
            scenario_name=title,
            description=description,
            **kwargs
        )
        
        self.interaction_manager.start_scenario(scenario)
        print(f"\n=== Scenario: {title} ===")
        print(f"{description}\n")
    
    def send_message(self, message: str) -> str:
        """
        Send a message from the player to their partner.
        Uses context from the last scenario and accumulated learning.
        
        Args:
            message: Player's message text
            
        Returns:
            AI partner's response
        """
        if not self.interaction_manager:
            return "Error: Game not started"
        
        # Learn from this user input
        if self.learning_system:
            self.learning_system.learn_from_input(message)
        
        # Build context for the AI
        context = {
            "scenario_key": self._last_scenario_key,
            "choice_key": self._last_choice_key,
            "player_patterns": {},
        }
        
        # Get accumulated patterns from story engine
        if self.story_engine:
            context["player_patterns"] = self.story_engine.get_learning_tags_for_ai()
        
        # Pass context to interaction manager for AI response
        ai_response = self.interaction_manager.process_player_message(message, context=context)
        
        # Record learning outcome
        if self.learning_system:
            self.learning_system.learn_from_outcome(ai_response, user_satisfaction=0.5)
        
        return ai_response
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get AI's learning progress."""
        if not self.learning_system:
            return {}
        
        return {
            "adaptation_level": f"{self.learning_system.adaptation_level * 100:.1f}%",
            "interactions": self.learning_system.total_interactions,
            "dominant_style": self.learning_system.get_dominant_style(),
            "topics_learned": list(self.learning_system.topics_discussed),
        }
    
    def get_relationship_status(self) -> dict:
        """Get current relationship metrics."""
        if not self.interaction_manager:
            return {}
        
        return self.interaction_manager.get_relationship_status()
    
    def get_current_scenario(self) -> Dict[str, Any]:
        """Get the current day's scenario from the story."""
        if not self.story_engine:
            return {}
        
        return self.story_engine.get_scenario_presentation()
    
    def present_scenario(self) -> None:
        """Display the current scenario to the player."""
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
        
        # Display choices
        for i, choice in enumerate(scenario['choices'], 1):
            print(f"  {i}. {choice['text']}")
        
        self._current_day_active = True
    
    def respond_to_scenario(self, choice_number: int) -> bool:
        """
        Process player's choice in the scenario.
        
        Args:
            choice_number: The choice number (1-based)
            
        Returns:
            True if choice was processed, False if invalid
        """
        if not self.story_engine or not self._current_day_active:
            return False
        
        scenario = self.story_engine.get_current_scenario()
        
        # Convert 1-based to 0-based index
        choice_idx = choice_number - 1
        
        if choice_idx < 0 or choice_idx >= len(scenario.choices):
            print(f"Invalid choice. Please select 1-{len(scenario.choices)}")
            return False
        
        choice = scenario.choices[choice_idx]
        
        # Store context for AI conversations
        # Map day titles to scenario keys
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
        
        # Map choice_id to simple keys
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
        
        # Process the choice through the story engine
        result = self.story_engine.process_choice(choice.choice_id)
        
        if not result.get("success"):
            print(f"Error processing choice: {result.get('error')}")
            return False
        
        # Feed choice data into learning system
        if self.learning_system:
            choice_text = result.get("choice_text", "")
            impact_desc = result.get("impact_description", "")
            self.learning_system.learn_from_input(choice_text)
            self.learning_system.learn_from_outcome(impact_desc, user_satisfaction=0.7)
            
            # Also add story impacts directly to learning
            for impact_tag in result.get("hidden_impacts", []):
                # Map story impacts to learning patterns
                self.learning_system.topics_discussed.add(impact_tag.split("_")[0])
        
        # Display the choice briefly
        print(f"\nYou chose: {result.get('choice_text')}\n")
        
        # Check if act is complete - show full results only then
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
        """Get current story progress."""
        if not self.story_engine:
            return {}
        
        return self.story_engine.get_status()
    
    def save_game(self, filename: str = None) -> str:
        """
        Save the current game state.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to save file
        """
        if not self.state_manager:
            return "Error: Game not started"
        
        return self.state_manager.save_game(filename)
    
    def load_game(self, filepath: str) -> bool:
        """
        Load a saved game.
        
        Args:
            filepath: Path to save file
            
        Returns:
            Success status
        """
        if not self.state_manager:
            self.state_manager = StateManager(save_directory=self.save_directory)
        
        if self.state_manager.load_session(filepath):
            # Restore agents from session
            session = self.state_manager.get_current_session()
            if session:
                # Determine roles from session
                player_role = ParentRole(session.player_role) if hasattr(session, 'player_role') else ParentRole.FATHER
                ai_role = player_role.get_opposite()
                
                self._player_role = player_role
                self._initialize_agents(player_role, ai_role)
                
                print(f"[OK] Game loaded successfully!")
                return True
        
        return False
    
    def run_interactive(self) -> None:
        """
        Run the game in interactive console mode with narrative progression.
        """
        print("\n" + "="*70)
        print("  NURTURE - A Parent Agent Simulation")
        print("  Watch your parenting journey unfold as your AI partner learns from you")
        print("="*70)
        
        # Role selection
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
        
        # Main game loop
        self._is_running = True
        
        while self._is_running:
            # Present the current scenario
            if not self._current_day_active:
                self.present_scenario()
            
            # Get player input
            try:
                user_input = input("\nYour choice (1-3 or /command): ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    self._handle_command(user_input[1:])
                    continue
                
                # Try to process as scenario choice
                try:
                    choice_num = int(user_input)
                    if self.respond_to_scenario(choice_num):
                        # Check if act completed - end the game for now
                        if self.story_engine and self.story_engine.can_progress_to_next_act():
                            print("\nThank you for playing Nurture!")
                            print("Your parenting story has been saved.\n")
                            self._is_running = False
                            break
                        
                        # After scenario choice is processed, ask about conversation
                        print("Would you like to have a conversation with your partner? (y/n): ", end="")
                        conv_input = input().strip().lower()
                        if conv_input == "y":
                            # Reset AI conversation history for fresh start
                            if self.ai_parent:
                                self.ai_parent.reset_conversation()
                            
                            ai_role = self._player_role.get_opposite() if self._player_role else "Partner"
                            print(f"\n--- Conversation with {ai_role.value.title()} ---")
                            print("(Type your messages. Enter /done or /skip to end conversation)\n")
                            
                            # Multi-turn conversation loop
                            while True:
                                message = input("You: ").strip()
                                
                                # Check for exit commands
                                if not message or message.lower() in ["/done", "/skip", "/end", "/quit"]:
                                    print("\n--- End of conversation ---\n")
                                    break
                                
                                # Handle other commands during conversation
                                if message.startswith("/"):
                                    if message.lower() == "/status":
                                        self._handle_command("status")
                                    else:
                                        print("(Use /done to end conversation, or just type your message)")
                                    continue
                                
                                # Get AI response
                                response = self.send_message(message)
                                print(f"\n{ai_role.value.title()}: {response}\n")
                except (ValueError, IndexError):
                    print("Invalid input. Enter 1-3 for choices or /command")
                
            except KeyboardInterrupt:
                print("\n\nGame interrupted.")
                self._is_running = False
            except EOFError:
                print("\n\nEnd of input.")
                self._is_running = False
        
        print("\nThank you for playing Nurture!")
        print("Your parenting story has been saved.\n")
    
    def _handle_command(self, command: str) -> None:
        """Handle console commands."""
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
            print(f"[OK] Game saved to: {filepath}")
        
        elif cmd == "quit" or cmd == "exit":
            confirm = input("Save before quitting? (y/n): ").strip().lower()
            if confirm == "y":
                self.save_game()
            self._is_running = False
        
        else:
            print(f"Unknown command: /{cmd}")
            print("Available commands: /status, /save, /quit")


def main():
    """Main entry point."""
    game = NurtureGame()
    game.run_interactive()


if __name__ == "__main__":
    main()
