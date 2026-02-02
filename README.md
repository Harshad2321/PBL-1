# Nurture - Parent Agent Simulation

A modular Python backend for an AI-based social learning simulation game focused on parent interactions and co-parenting dynamics.

## Overview

Nurture is a text-based simulation where players take on a parental role (Father or Mother) and interact with an AI-controlled partner to navigate parenting scenarios together. The AI partner has its own personality, emotional state, and memory, creating realistic and dynamic conversations.

## Features

- **Role Selection**: Choose to play as Father or Mother; AI automatically takes the opposite role
- **AI Personality System**: AI parent has configurable personality traits affecting responses
- **Emotional State Tracking**: Both agents maintain emotional states that evolve during interactions
- **Memory System**: AI remembers past interactions and uses them to inform responses
- **Rule-Based Reasoning**: Behavioral constraints and rules guide AI decision-making
- **LLM Integration**: Pluggable interface for various LLM backends (OpenAI, local models, or mock)
- **Save/Load**: Persist game state for continued sessions

## Project Structure

```
nurture/
├── __init__.py              # Package root
├── main.py                  # Main entry point & interactive mode
├── examples.py              # Usage examples
│
├── core/                    # Core data structures and systems
│   ├── __init__.py
│   ├── enums.py            # Type-safe enumerations
│   ├── data_structures.py  # EmotionalState, PersonalityProfile, etc.
│   ├── events.py           # Event bus for pub-sub messaging
│   └── interaction_manager.py  # Coordinates parent dialogue
│
├── agents/                  # Parent agent implementations
│   ├── __init__.py
│   ├── base_parent.py      # Abstract base class
│   ├── player_parent.py    # Human-controlled parent
│   └── ai_parent.py        # AI-controlled parent
│
├── memory/                  # Memory and state management
│   ├── __init__.py
│   ├── memory_store.py     # Agent memory storage
│   └── state_manager.py    # Game session persistence
│
├── rules/                   # Rule-based reasoning
│   ├── __init__.py
│   ├── rule_engine.py      # Rule evaluation engine
│   ├── emotional_rules.py  # Emotional state rules
│   └── behavioral_constraints.py  # Behavioral limits
│
├── config/                  # Configuration files
│   └── __init__.py
│
└── utils/                   # Utility functions
    ├── __init__.py
    ├── helpers.py           # General helpers
    ├── logger.py            # Logging utility
    └── llm_interface.py     # LLM abstraction layer
```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd "PBL CODE"
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   
   Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Interactive Mode

Run the main script to start the interactive console game:

```bash
python -m nurture.main
```

This will:
1. Prompt you to select a role (Father/Mother)
2. Set up a default scenario
3. Start the conversation loop

#### Console Commands

During gameplay, use these commands:
- `/choices` - Show available response choices
- `/select <id>` - Select a predefined choice
- `/status` - View relationship metrics
- `/save` - Save the game
- `/quit` - Exit (with option to save)

### Programmatic Usage

```python
from nurture.main import NurtureGame
from nurture.core.enums import ParentRole

# Create game instance
game = NurtureGame()

# Select role
game.select_role(ParentRole.FATHER)

# Optionally configure LLM (default is mock)
game.configure_llm(provider="openai", api_key="sk-...")

# Set up a scenario
game.set_scenario(
    title="Bedtime Discussion",
    description="Discussing your child's bedtime routine",
    topic="sleep"
)

# Send messages and get responses
response = game.send_message("I think 8pm is a good bedtime for our child.")
print(response)

# Check relationship status
status = game.get_relationship_status()
```

### Running Examples

To see various features in action:

```bash
python -m nurture.examples
```

This runs examples demonstrating:
- Basic conversation
- Personality differences
- Memory system
- Emotional states
- Rule engine
- Event system
- State management

## LLM Configuration

The AI parent can use different LLM backends:

### Groq (FREE & Ultra-Fast - Recommended! 🚀)
```python
# Get your FREE API key at: https://console.groq.com
game.configure_llm(
    provider="groq",
    api_key="gsk_your_key_here",
    model_name="llama-3.3-70b-versatile"
)

# Or set environment variable GROQ_API_KEY and just:
game.configure_llm(provider="groq")
```

**Groq Free Tier:** 30 requests/min, 14,400 requests/day

### Mock (Testing - No API needed)
```python
game.configure_llm(provider="mock")
```

### OpenAI (Paid)
```python
game.configure_llm(
    provider="openai",
    api_key="sk-your-key",
    model_name="gpt-4"
)
```

### Local (Ollama - Free, requires setup)
```python
game.configure_llm(
    provider="ollama",
    api_base="http://localhost:11434",
    model_name="llama2"
)
```

## Memory System

Two memory implementations available:

### FastMemoryStore (Recommended)
Optimized with O(1) lookups using hash indexes:
```python
from nurture.memory import FastMemoryStore, FastMemory

store = FastMemoryStore(agent_id="parent_1")
store.create(
    content="Agreed on bedtime rules",
    tags={"parenting", "agreement"},
    emotional_valence=0.7,
    importance=0.8
)

# O(1) tag lookup
memories = store.get_by_tag("parenting")
```

### MemoryStore (Original)
Full-featured with pattern analysis:
```python
from nurture.memory import MemoryStore, Memory
```

## Architecture

### Core Components

1. **InteractionManager**: Central coordinator for parent dialogue
   - Manages turn-based conversation flow
   - Applies rules and constraints
   - Records interaction history

2. **AIParent**: AI-controlled partner with:
   - Personality-driven behavior
   - Strategy selection (supportive, assertive, compromising, etc.)
   - Memory retrieval for context-aware responses
   - LLM integration for natural language

3. **RuleEngine**: Priority-based rule evaluation
   - Evaluates conditions against context
   - Returns action recommendations
   - Supports custom rule definitions

4. **MemoryStore**: Persistent memory for agents
   - Tag-based retrieval
   - Emotional valence filtering
   - Importance scoring

### Event System

The game uses a pub-sub event bus for loose coupling:

```python
from nurture.core.events import get_event_bus, EventType, Event

bus = get_event_bus()
bus.subscribe(EventType.DIALOGUE, my_handler)
bus.publish(Event(EventType.DIALOGUE, data={"message": "Hello"}))
```

## Extending the System

### Adding Custom Rules

```python
from nurture.rules.rule_engine import Rule

my_rule = Rule(
    rule_id="custom_rule",
    name="My Custom Rule",
    condition=lambda ctx: ctx.get("some_value", 0) > threshold,
    action=lambda ctx: {"recommendation": "do_something"},
    priority=80
)
rule_engine.add_rule(my_rule)
```

### Creating Custom Personalities

```python
from nurture.core.data_structures import PersonalityProfile
from nurture.core.enums import PersonalityTrait

personality = PersonalityProfile(
    traits={
        PersonalityTrait.WARMTH: 0.9,
        PersonalityTrait.ASSERTIVENESS: 0.4,
        PersonalityTrait.PATIENCE: 0.8,
        PersonalityTrait.FLEXIBILITY: 0.7,
    }
)
```

## Future Development

This Phase 1 implementation focuses on the Parent Agent system. Future phases will include:

- **Child Agent**: AI-controlled child with development stages
- **Simulation Engine**: Long-term simulation and outcome tracking
- **Voice Integration**: Text-to-speech and speech-to-text
- **Web Interface**: Browser-based UI
- **Multiplayer**: Multiple human players

## License

This project is for educational purposes.

## Contributing

This is a PBL (Project-Based Learning) project. Contributions should align with the project requirements.
#   P B L  
 