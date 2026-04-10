# Nurture - Complete Project Documentation

> A social learning simulation game exploring the joys and challenges of co-parenting through realistic conversations and meaningful choices.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Why This Project Exists](#why-this-project-exists)
3. [Project Architecture](#project-architecture)
4. [How It Works](#how-it-works)
5. [Getting Started / How to Use](#getting-started--how-to-use)
6. [Current Implementation Status](#current-implementation-status)
7. [Key Systems in Detail](#key-systems-in-detail)
8. [Technical Highlights](#technical-highlights)
9. [Game Flow Example](#game-flow-example)
10. [Testing & Validation](#testing--validation)
11. [Future Development](#future-development)

---

## Project Overview

**Nurture** is a text-based parenting simulation game where players step into the role of a parent (Mom or Dad) navigating the beautiful chaos of raising a child while co-parenting with an AI partner.

### Key Characteristics

- **Genre**: Interactive text-based simulation / narrative game
- **Duration**: Phase 1 (Act 1) = 12 days of gameplay
- **Target Audience**: People interested in parenting education, family dynamics, AI interactions
- **Technical Foundation**: Python-based with modular agent architecture
- **State**: Phase 1 Complete (ACT 1 fully implemented and playable)

### What Makes Nurture Different

Unlike traditional parenting advice games, Nurture:

1. **Simulates Real Relationships**: Your AI partner has distinct personality traits, emotional states, and learning capabilities. They're not just a decision tree—they genuinely adapt to how you interact.

2. **Learning Through Experience**: Every choice you make cascades through hidden systems that influence your AI partner's behavior. You see the impacts, but the underlying mechanics remain opaque (just like real relationships).

3. **Explores Co-Parenting Complexity**: Most parenting education focuses on individual parents. Nurture specifically explores partnership dynamics—how two different people who care about the same child navigate disagreement, compromise, and shared responsibility.

4. **Psychological Depth**: Systems track relationship dynamics (trust, resentment, communication openness, power balance), emotional states, and personality evolution.

---

## Why This Project Exists

### Educational Purpose (Project-Based Learning)

Nurture developed as a **project-based learning (PBL)** initiative at the intersection of several computer science and psychology concepts:

- **AI Agent Design**: Creating believable agents with personality and learning
- **Emotional Modeling**: Representing human emotions in computational systems
- **Interactive Storytelling**: Blending narrative with player agency
- **System Design**: Building scalable multi-module architecture
- **Natural Language Processing**: Integrating LLMs intelligently

### Real-World Context

Parenting is hard. Co-parenting is harder. Contemporary society offers extensive resources about child development but relatively little about **partnership dynamics under parenting stress**.

Nurture addresses this gap by creating a safe space to:
- Explore different approaches to common parenting challenges
- See how your decisions play out over time
- Understand your partner's perspective
- Learn patterns about your own parenting style
- Develop communication strategies

### Learning Outcomes

By engaging with Nurture, players develop:

- **Perspective-taking**: Understanding both parental viewpoints
- **Decision awareness**: Recognizing hidden impacts of choices
- **Pattern recognition**: Seeing their own behavioral patterns
- **Communication skills**: Learning through dialogue with different personality types
- **Emotional intelligence**: Understanding relationship dynamics and emotional responses

---

## Project Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│              (Console-based, narrative-driven)                │
├─────────────────────────────────────────────────────────────┤
│                         MAIN.PY                              │
│         (Game orchestration and turn management)             │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │            CORE SIMULATION LAYER                      │   │
│  │                                                        │   │
│  │  ┌─────────────────────────────────────────────┐     │   │
│  │  │    Story Engine                             │     │   │
│  │  │  - Scenario presentation                    │     │   │
│  │  │  - Choice processing                        │     │   │
│  │  │  - Progress tracking                        │     │   │
│  │  └─────────────────────────────────────────────┘     │   │
│  │                                                        │   │
│  │  ┌──────────────┐        ┌──────────────┐             │   │
│  │  │ Player Parent│◄──────►│ AI Parent    │             │   │
│  │  │ (Human State)│        │ (AI Logic)   │             │   │
│  │  └──────────────┘        └──────────────┘             │   │
│  │         ▲                        ▲                     │   │
│  │         │                        │                     │   │
│  │  ┌──────────────────────────────────────┐             │   │
│  │  │    Interaction Manager                │             │   │
│  │  │  - Dialogue coordination              │             │   │
│  │  │  - Context management                │             │   │
│  │  │  - Response orchestration             │             │   │
│  │  └──────────────────────────────────────┘             │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │        INTELLIGENT SYSTEMS LAYER                      │   │
│  │                                                        │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │   │
│  │  │Learning      │  │Rule          │  │Personality/ │ │   │
│  │  │System        │  │Engine        │  │Emotional    │ │   │
│  │  │(Adaptation)  │  │(Decision)    │  │Systems      │ │   │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │   │
│  │         ▲                  ▲                  ▲         │   │
│  │         └──────────────────┼──────────────────┘         │   │
│  │                            │                            │   │
│  │                   ┌─────────────────┐                   │   │
│  │                   │  Event Bus      │                   │   │
│  │                   │ (Pub/Sub)       │                   │   │
│  │                   └─────────────────┘                   │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │          PERSISTENCE & MEMORY LAYER                   │   │
│  │                                                        │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │   │
│  │  │Memory Store  │  │State Manager │  │Fast Memory  │ │   │
│  │  │(Long-term)   │  │(Session)     │  │(O(1) Cache) │ │   │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │           EXTERNAL INTEGRATION LAYER                  │   │
│  │                                                        │   │
│  │  ┌──────────────────────────────────────┐             │   │
│  │  │    LLM Interface                      │             │   │
│  │  │  ├─ OpenAI (GPT-4, GPT-3.5)           │             │   │
│  │  │  ├─ Ollama (Local & Offline)          │             │   │
│  │  │  └─ Mock (Testing & Development)      │             │   │
│  │  └──────────────────────────────────────┘             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Module Organization

```
nurture/
├── main.py                           # Game entry point & orchestration
│
├── core/                             # Fundamental DATA & ARCHITECTURE
│   ├── enums.py                     # ParentRole, PersonalityTrait, EmotionType, etc.
│   ├── data_structures.py           # RelationshipState, PersonalityProfile, etc.
│   ├── events.py                    # EventBus (pub-sub pattern)
│   ├── interaction_manager.py       # Dialogue coordination
│   └── learning_system.py           # Adaptive personality engine
│
├── agents/                           # PARENT AGENTS
│   ├── base_parent.py               # Abstract base class
│   ├── player_parent.py             # Human player representation
│   └── ai_parent.py                 # AI agent with personality & learning
│
├── story/                            # NARRATIVE ENGINE
│   ├── story_engine.py              # Acts/days progression
│   ├── story_data.py                # 12 scenarios × 3 choices per Act
│   └── __init__.py
│
├── learning/                         # PATTERN RECOGNITION & ADAPTATION
│   ├── learning_system.py           # Sentiment, topic, decision tracking
│   └── __init__.py
│
├── memory/                           # PERSISTENCE & RETRIEVAL
│   ├── memory_store.py              # Memory objects (episodic & semantic)
│   ├── fast_memory.py               # O(1) lookups with LRU cache
│   ├── state_manager.py             # Session management & save/load
│   └── __init__.py
│
├── personality/                      # EMOTIONAL & BEHAVIORAL SYSTEMS
│   ├── emotional_memory.py          # Emotional association tracking
│   ├── pattern_tracker.py           # Behavioral pattern detection
│   ├── trust_dynamics.py            # Trust score management
│   └── __init__.py
│
├── rules/                            # DECISION-MAKING FRAMEWORK
│   ├── rule_engine.py               # Priority-based evaluation
│   ├── emotional_rules.py           # Emotion-driven behaviors
│   ├── behavioral_constraints.py    # Character consistency rules
│   └── __init__.py
│
├── utils/                            # UTILITIES & INTEGRATIONS
│   ├── llm_interface.py             # LLM provider abstraction
│   ├── logger.py                    # Logging system
│   └── helpers.py                   # Common utilities
│
└── simulation/                       # GAME ENGINE (newer architecture)
    ├── game_engine.py               # Main simulation loop
    ├── entities.py                  # Parent, AI, Child, Relationship objects
    ├── decision_engine.py           # Context-aware decision making
    ├── event_catalog.py             # All scenarios & events
    ├── event_models.py              # Event and choice data structures
    ├── state_models.py              # State enums and models
    ├── state_update_system.py       # State transition logic
    ├── memory_tags_store.py         # Tagged memory system
    └── __init__.py
```

---

## How It Works

### Game Loop (High Level)

```
1. START
   └─ Load or create new game
      └─ Establish player role (Mom or Dad)
         └─ Create opposing AI parent

2. DAY LOOP (12 times per Act)
   │
   ├─ Present Scenario
   │  └─ Display situation (e.g., "Baby won't stop crying at 2 AM")
   │
   ├─ Get Player Choice
   │  └─ Player selects 1, 2, or 3 from meaningful options
   │     └─ System records choice and associated impacts
   │
   ├─ Process Through Learning
   │  └─ Learning system:
   │     ├─ Analyzes sentiment of choice
   │     ├─ Identifies decision style (collaborative vs assertive)
   │     ├─ Detects patterns
   │     └─ Adjusts AI personality traits
   │
   ├─ Optional: Conversation Phase
   │  └─ Player can have free-form dialogue with AI
   │     └─ AI response is:
   │        ├─ Contextualized by scenario
   │        ├─ Aligned with learned patterns
   │        ├─ Emotionally consistent
   │        └─ Generated via LLM (or mock for testing)
   │
   └─ PROG RESSION
      └─ Day++
         └─ If day > 12: Act Complete, transition to Act 2

3. END (After Act Complete or Manual /quit)
   └─ Save game state for later resumption
```

### Key Interaction Flow

#### Scenario Presentation ➜ Choice ➜ Impact Recording

```
┌──────────────────────────────────┐
│   STORY ENGINE PRESENTS          │
│   "Baby crying at 2 AM"          │
│   "You're exhausted, so is they  │  (act, day, time)
│   partner. What do you do?"      │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│   PLAYER SEES 3 CHOICES:         │
│   1. Get up immediately          │
│   2. Try to comfort in bed       │
│   3. Wake partner                │
└──────────────────────────────────┘
           │
           ▼ (Player selects: 1)
┌──────────────────────────────────┐
│   CHOICE RECORDED & PROCESSED    │
│   ├─ Choice ID: choice_1_day1   │
│   └─ Hidden impacts:             │
│      ├─ responsibility_high     │  (recorded in story)
│      ├─ presence_high           │  (accumulated over game)
│      └─ attachment_security_pos │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│   LEARNING SYSTEM ANALYZES       │
│   "This player prioritizes       │
│    presence and responsibility   │
│    even at personal cost"        │
│                                  │
│   → Boosts AI warmth trait      │
│   → Adjusts AI assertiveness    │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│   AI BECOMES SLIGHTLY DIFFERENT  │
│   Next interaction will show     │
│   increased sensitivity to       │
│   player's commitment patterns   │
└──────────────────────────────────┘
```

### How AI Parent Generates Responses

```
User Message: "I feel guilty whenever I rest"

         ↓

┌──────────────────────────────────────┐
│  ANALYSIS PHASE                      │
│  ├─ Sentiment extraction            │ → NEGATIVE (guilt)
│  ├─ Topic identification             │ → REST/GUILT/WORK-BALANCE
│  ├─ Context retrieval                │ → Previous messages about guilt
│  └─ Relationship state eval          │ → Trust: 70, Warmth: 75, Resentment: 15
└──────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│  RULE EVALUATION PHASE               │
│  ├─ Match relevant behavioral rules  │ → "Guilt-driven behaviors"
│  ├─ Check emotional constraints       │ → AI should be sympathetic
│  ├─ Verify consistency with          │ → Match AI's learned warmth
│  │   personality                      │
│  └─ Determine response strategy       │ → SUPPORTIVE
└──────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│  PROMPT CONSTRUCTION PHASE           │
│  ├─ AI personality context           │
│  ├─ Relationship status context      │
│  ├─ Recent interaction history       │
│  ├─ Learned pattern context          │
│  └─ Scenario context                 │
└──────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│  LLM GENERATION PHASE                │
│  │                                   │
│  └─ Query LLM with context:          │
│     "You are Sarah, a warm mother    │
│      who has learned your partner    │
│      struggles with guilt about      │
│      rest. Given the context below,  │
│      respond empathetically..."      │
└──────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│  RESPONSE: "I see you pushing        │
│  yourself so hard. But you can't     │
│  pour from an empty cup. I need you  │
│  healthy and present, not burnt out. │
│  Let's find ways you can rest guilt- │
│  free. We're a team in this."        │
└──────────────────────────────────────┘
```

### Learning System - How AI Adapts Over Time

The Learning System continuously observes and records patterns:

```
OBSERVATION CYCLE (After each message):

1. SENTIMENT ANALYSIS
   └─ Extract emotional tone (-1.0 to +1.0)
      Example: "I think you're being unfair" → -0.4 (slightly negative)

2. TOPIC EXTRACTION
   └─ Identify what user cares about
      Example: "work", "sleep", "support", "fairness"

3. PATTERN DETECTION
   └─ Match against known patterns:
      ├─ Decision styles:
      │  ├─ Collaborative (works with partner)
      │  ├─ Assertive (takes charge)
      │  ├─ Avoidant (steps back)
      │  └─ Compromising (finds middle ground)
      │
      └─ Emotional drivers:
         ├─ Guilt (motivated by feeling bad)
         ├─ Pride (motivated by autonomy)
         ├─ Fear (motivated by things going wrong)
         └─ Love (motivated by connection)

4. CONFIDENCE ASSESSMENT
   └─ How confident is the system in this pattern?
      ├─ First observation: confidence = 0.1
      ├─ Repeated observations: confidence increases
      └─ Exponential decay if not reinforced

5. PERSONALITY ADJUSTMENT
   └─ Modify AI's trait scores:
      Example: "This user is collaborative and guilt-driven"
      ├─ AI Warmth += 0.05
      ├─ AI Assertiveness -= 0.03
      └─ AI Flexibility += 0.04

RESULT: After 24 turns (12 days × 2 turns), AI has absorbed:
        ├─ Emotional patterns
        ├─ Value priorities
        ├─ Communication preferences
        └─ Vulnerability & strengths

Next Act, AI starts with these learned adjustments.
```

---

## Getting Started / How to Use

### Prerequisites

- Python 3.9 or newer
- pip (comes with Python)
- Optional: OpenAI API key (for GPT responses) or Ollama (for local models)

### Installation

```bash
# Clone repository
git clone https://github.com/Harshad2321/PBL-1.git
cd PBL-1

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Playing the Game

```bash
# Start the game
python -m nurture.main
```

You'll be prompted to:
1. Choose your role: **Mother** or **Father**
2. Choose AI partner's name (default suggestions provided)
3. Choose your name (default suggestions provided)

Then the story begins!

### In-Game Commands

During gameplay, type any of these commands:

| Command | Effect |
|---------|--------|
| `/status` | View relationship metrics and learning status |
| `/save` | Manually save your progress |
| `/quit` | Exit game (you'll be asked if you want to save) |
| Any text | Engage in free-form conversation with your partner |

### Example Gameplay Session

```
┌─────────────────────────────────────────────────┐
│  NURTURE - PARENT AGENT SIMULATION              │
│  Act 1: FOUNDATION (Days 1-12)                  │
│  Act 1, Day 1: "The First Night"               │
└─────────────────────────────────────────────────┘

Your newborn won't stop crying at 2 AM. 
You're both exhausted and running on fumes.

What do you do?

1. Get up immediately
   (Your instinct: respond quickly, be present)

2. Try to comfort from bed first
   (Alternative: check if they actually need something)

3. Wake your partner to share the load
   (Split responsibility: neither of you handles this alone)

Your choice (1-2-3): 1

Hidden Impact: 
  → Responsibility: HIGH
  → Presence: HIGH  
  → Self-care: LOW
  → Partnership: SHARED but unequal

── Optional Conversation ──

You: I hate feeling helpless when they cry

AI Partner: I know. Last night I watched you
get up five times. You're running yourself into
the ground, and I don't know how to help without
feeling like I'm not doing enough either.

(Continue conversation or proceed to Day 2)
```

### Configuration (Optional)

To use advanced LLM providers, create a `.env` file:

```bash
# .env file in project root

# OpenAI Configuration (if you have an API key)
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4

# Or use Ollama (local & free)
# Download from https://ollama.ai
# Run: ollama pull llama2
# Then configure:
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Using in Your Code

```python
# Import the game
from nurture.main import NurtureGame
from nurture.core.enums import ParentRole

# Create a new game
game = NurtureGame()

# Configure LLM (optional)
game.configure_llm(provider="mock")  # or "openai", "ollama"

# Select role
game.select_role(ParentRole.FATHER)

# Get current scenario
scenario = game.get_scenario_presentation()
print(f"Day {scenario['day']}: {scenario['title']}")

# Process player choice
game.process_choice("choice_1_day1")

# Have a conversation
response = game.send_message("I think we need to be more consistent")
print(response)

# Check relationship status
status = game.get_relationship_status()
print(f"Trust: {status['trust']}, Warmth: {status['emotional_closeness']}")

# Save game
game.save_game()
```

---

## Current Implementation Status

### ✅ Completed & Fully Tested

#### Core Architecture & Infrastructure
- ✅ Modular project structure (10 main modules)
- ✅ Comprehensive enum system (ParentRole, PersonalityTrait, EmotionType, etc.)
- ✅ Rich data structures (RelationshipState, EmotionalState, PersonalityProfile)
- ✅ Event bus (pub-sub pattern for loose coupling)
- ✅ State machines for role selection and game progression

#### Agent Systems
- ✅ **PlayerParent**: Tracks human player state, choices, and emotional trajectory
- ✅ **AIParent**: Full implementation with:
  - Personality trait system (warmth, strictness, patience, flexibility)
  - Dynamic emotional state (stress, happiness, empathy, frustration)
  - Memory integration for context awareness
  - Rule-based response generation
  - Adaptive behavior based on player patterns

#### Memory & Persistence
- ✅ **MemoryStore**: Episodic and semantic memory management
- ✅ **FastMemoryStore**: O(1) performance lookups with LRU cache
- ✅ **StateManager**: Game state serialization/deserialization
- ✅ **Save/Load System**: Full game progress persistence with timestamps

#### Story & Narrative
- ✅ **Story Engine**: Full Act 1 with 12-day narrative arc
- ✅ **12 Scenarios** × **3 Choices** per scenario = **36 unique branches**
- ✅ **Story Data**: Complete narrative with context for all scenarios
- ✅ **Impact Tracking**: Hidden psychological impacts of each choice
- ✅ **Progress Tracking**: Day-by-day advancement through Act 1

#### Learning & Adaptation
- ✅ **Learning System**: Pattern recognition from player behavior
- ✅ **Sentiment Analysis**: Emotional tone extraction
- ✅ **Topic Detection**: Identifying what player cares about
- ✅ **Decision Style Profiling**: Collaborative vs. assertive patterns
- ✅ **Confidence Scoring**: Exponential decay for pattern strength
- ✅ **Personality Adjustment**: Dynamic AI trait modification

#### Decision-Making Systems
- ✅ **Rule Engine**: Priority-based behavioral rules
- ✅ **Emotional Rules**: Emotion-driven response generation
- ✅ **Behavioral Constraints**: Character consistency enforcement
- ✅ **Interaction Manager**: Scenario presentation and choice processing

#### External Integration
- ✅ **LLM Interface**: Multiple provider support
  - ✅ OpenAI (GPT-4, GPT-3.5-turbo)
  - ✅ Ollama (local & offline)
  - ✅ Mock (for testing, no API needed)

#### Testing & Validation
- ✅ Property-based tests (hypothesis framework)
- ✅ Unit tests for:
  - Data structures
  - Emotional memory system
  - Pattern tracking
  - Trust dynamics
- ✅ Integration tests for full game loops
- ✅ Demo scripts showing all major systems

#### Documentation
- ✅ Complete README with features & getting started
- ✅ PROJECT_SUMMARY with architecture overview
- ✅ Extensive code documentation and docstrings
- ✅ Example gameplay flows
- ✅ Configuration guides

### ⏳ Planned / Not Yet Implemented

#### Future Acts (Narrative Content)
- ☐ **Act 2 - MIRROR** (Age 4-7): Child becomes reflective, testing boundaries
- ☐ **Act 3 - FRACTURE** (Age 8-12): Identity questions, school pressures, first independence
- ☐ **Act 4 - RECKONING** (Age 13-18): Adolescence, autonomy, philosophical disagreement

#### Advanced Mechanics
- ☐ **Dynamic Story Branching**: Multiple paths per day based on previous choices
- ☐ **Long-term Consequences**: Choices have cascading effects over multiple acts
- ☐ **Relationship Degradation**: Trust can be permanently damaged
- ☐ **Parenting Grades**: System that scores parenting decisions
- ☐ **Explicit Pattern Feedback**: AI intentionally references learned patterns

#### User Experience
- ☐ **Web Interface**: Browser-based UI instead of console
- ☐ **Voice Features**: Hear the AI partner speak (text-to-speech)
- ☐ **Voice Input**: Speak your responses (speech-to-text)
- ☐ **Visual Elements**: Character avatars, relationship graphs
- ☐ **Story Visualization**: Timeline of choices and impacts

#### Multiplayer & Variants
- ☐ **Multiplayer Mode**: Two human players co-parenting together
- ☐ **Solo Parent Mode**: Raise child without partner
- ☐ **Different Cultures/Contexts**: Customize cultural background
- ☐ **Difficulty Modes**: "practice", "realistic", "challenging"

---

## Key Systems in Detail

### 1. Story Engine

**Location**: `nurture/story/story_engine.py`

The Story Engine manages narrative progression and presents scenarios to the player.

#### Key Components:

- **StoryProgress**: Tracks current act, day, and choices
- **DayScenario**: Single scenario with title, description, 3 choices
- **ActData**: Complete act with 12 days of scenarios
- **Story Chain**: Acts are linked; completing Act 1 leads to Act 2 (eventually)

#### What It Does:

```python
# Get current scenario
scenario = story_engine.get_current_scenario()
# Returns: DayScenario object with title, description, choices

# Process player choice
impact = story_engine.process_choice("choice_1")
# Returns dictionary with:
# - impact_summary (what player will see)
# - hidden_impacts (psychological tags for learning system)
# - impact_explanation (brief explanation of impact)

# Progress to next day
story_engine.advance_to_next_day()
# Updates internal state; automatically transitions acts if needed
```

#### Story Data Structure:

Each scenario contains:

```python
@dataclass
class DayScenario:
    day: int
    title: str                           # e.g., "The First Night"
    description: str                     # Setup (1-2 sentences)
    scenario_text: str                   # Full context
    gameplay_time: str                   # e.g., "2:00 AM", "Saturday Evening"
    hidden_impact_intro: str             # Explanation of impact system
    
    choices: List[Choice]                # 3 choices per scenario
    
    # Choice contains:
    # - choice_id (e.g., "choice_1_day1")
    # - text (displayed to player)
    # - impact_summary (shown after choice)
    # - hidden_impacts (psychological tags)
```

#### Impact Tags (Psychology-Based):

Examples of hidden impacts that affect AI learning:

- **Responsibility**: HIGH, MODERATE, LOW
- **Presence**: Physical and emotional availability
- **Self-care**: How much player prioritizes their own needs
- **Partnership**: How equitable the responsibility division
- **Emotional_Safety**: Does choice create secure environment
- **Boundaries**: Does choice respect personal limits
- **Growth_Mindset**: Does choice support learning and change

### 2. Learning System

**Location**: `nurture/learning/learning_system.py`

The Learning System enables the AI to evolve based on player behavior.

#### Key Components:

- **UserPattern**: Represents a learned pattern about the player
- **LearningSystem**: Main class that tracks patterns and behaviors
- **Pattern Types**: sentiment, topic, decision, preference

#### How It Works:

```
Every time player sends a message:

1. Sentiment Analysis
   └─ Extract emotion: -1.0 (negative) ↔ +1.0 (positive)
      Example: "I'm frustrated" → -0.3
      
2. Topic Extraction
   └─ Identify domains: education, health, discipline, emotion, etc.
   
3. Decision Style Assessment
   └─ Match to templates:
      ├─ collaborative (0.0 = "avoidant", 1.0 = "cooperative")
      ├─ assertive (0.0 = "passive", 1.0 = "dominant")
      ├─ emotional (0.0 = "logical", 1.0 = "feelings-driven")
      └─ modern (0.0 = "traditional", 1.0 = "progressive")

4. Pattern Confidence
   └─ First observation: confidence = 0.1
   └─ Each reinforcement: confidence += 0.1
   └─ Over time: stabilizes to 0.8-1.0
   └─ Decay rate: exponential (0.99 ^ hours)

5. Personality Adjustment
   └─ Calculate delta for each AI trait:
      Example:
      ├─ If player collaborative + supportive:
      │  ├─ AI's warmth += 0.05
      │  └─ AI's assertiveness -= 0.02
      └─ Applied gradually over multiple interactions
```

#### Pattern Confidence Decay:

```python
# Pattern gets less confident over time
confidence_at_time_t = initial_confidence * (0.99 ^ hours_elapsed)

Example:
- Pattern formed 1 hour ago: 0.8 * 0.99^1  = 0.792
- Pattern formed 10 hours ago: 0.8 * 0.99^10 = 0.725
- Pattern formed 100 hours ago: 0.8 * 0.99^100 = 0.379

This models "forgetting" unless the pattern is reinforced.
```

### 3. AI Parent Agent

**Location**: `nurture/agents/ai_parent.py`

The AI Parent is the core agent that responds to the player.

#### Key Characteristics:

- **Personality**: Defined by 5 traits (warmth, strictness, patience, flexibility, assertiveness)
- **Emotional State**: Stress, happiness, empathy, frustration (updated each turn)
- **Memory**: Stores past interactions as tagged memories
- **Learning**: Adapts personality based on player patterns
- **Rule-Based**: Follows behavioral rules while maintaining consistency

#### Core Methods:

```python
# Process incoming message
ai_parent.process_input(
    message="I think you're being too harsh",
    context=DialogueContext(...)
)

# Generate response
response = ai_parent.generate_response(context)
# Returns: str with natural language response

# Get emotional state
state = ai_parent.get_emotional_state()
# Returns: EmotionalState with current stress, happiness, etc.

# Update personality (from learning)
ai_parent.adapt_personality(
    trait=PersonalityTrait.WARMTH,
    delta=0.05  # Increase warmth by 5 percentage points
)
```

#### Personality Traits (0.0 to 1.0 scale):

| Trait | Description | Impact |
|-------|-------------|--------|
| **Warmth** | Affectionate vs. cold | How accepting and validating responses are |
| **Strictness** | Permissive vs. strict | How firm on rules and expectations |
| **Patience** | Quick-tempered vs. calm | How easily frustrated; willingness to discuss |
| **Flexibility** | Rigid vs. adaptable | Open to changing mind; compromise |
| **Assertiveness** | Passive vs. dominant | Who drives conversations and decisions |

### 4. Interaction Manager

**Location**: `nurture/core/interaction_manager.py`

Coordinates all interactions between player, AI, and story systems.

#### Responsibilities:

- **Scenario Presentation**: Format and display scenarios
- **Choice Processing**: Parse and validate player choices
- **Context Management**: Maintain dialogue context
- **Response Orchestration**: Coordinate AI response generation
- **Relationship Updates**: Adjust relationship state based on interactions

#### Key Flow:

```python
# Initialize
manager = InteractionManager(player_state, ai_state)

# Present scenario
manager.present_scenario(scenario)

# Process choice
choice_result = manager.process_scenario_choice(choice_id)

# Conduct conversation
response = manager.process_message(
    player_message="I need more support",
    dialogue_context=context
)
```

### 5. Memory Systems

**Location**: `nurture/memory/`

Multiple memory systems provide different storage and retrieval patterns.

#### MemoryStore (Long-term)

```python
# Store a memory
memory = Memory(
    memory_type=MemoryType.INTERACTION,
    content="Player said they feel guilty about rest",
    emotional_valence=-0.3,  # slightly negative
    tags=["guilt", "self-care", "stress"]
)
store.store_memory(memory)

# Retrieve by tag
guilt_memories = store.get_memories_by_tag("guilt")

# Retrieve by type
interaction_memories = store.get_memories_by_type(MemoryType.INTERACTION)
```

#### FastMemoryStore (Cache)

```python
# O(1) lookups with LRU cache
cache = FastMemoryStore(max_size=1000)

# Store and retrieve
cache.put("player_guilt_pattern", {"confidence": 0.8})
pattern = cache.get("player_guilt_pattern")  # Instant retrieval

# Supports tag-based queries with caching
recent_guilt = cache.get_by_tag("guilt", limit=5)
```

#### StateManager (Session)

```python
# Save game state
state_manager.save_state(
    player_state=player,
    ai_state=ai,
    relationship_state=relationship,
    story_progress=story
)

# Load saved game
loaded_game = state_manager.load_state(save_id="game_001")
```

### 6. Rule Engine

**Location**: `nurture/rules/rule_engine.py`

Priority-based decision-making system for AI behavior.

#### How Rules Work:

```python
# Define a rule
rule = Rule(
    rule_id="bedtime_consistency",
    name="Bedtime Routine Importance",
    condition=lambda ctx: ctx[' topic'] == "sleep" and 
                          ctx['relationship']['stress'] > 70,
    action=lambda ctx: {"strategy": "emphasize_routine"},
    priority=80  # Higher = evaluated first
)

# Evaluate all rules
engine.evaluate(context)
# Returns: List of matched rules sorted by priority

# Apply highest priority rule
recommendation = engine.get_recommendation(context)
```

#### Rule Priority System:

- **Priority 100+**: Critical rules (relationship safety, boundaries)
- **Priority 80-99**: Important rules (consistency, fairness)
- **Priority 60-79**: Standard rules (communication patterns)
- **Priority < 60**: Low-priority rules (nice-to-have consistency)

---

## Technical Highlights

### Design Patterns Used

#### 1. **Event-Driven Architecture (Pub-Sub)**

```python
# System publishes events
event_bus.publish(Event(
    type=EventType.PERSONALITY_UPDATED,
    data={"trait": "warmth", "delta": 0.05}
))

# Subscribers listen automatically
@event_bus.subscribe(EventType.PERSONALITY_UPDATED)
def on_personality_update(event):
    print(f"AI personality updated: {event.data}")
```

**Benefits**: Loose coupling between systems, extensibility, clean separation of concerns

#### 2. **Strategy Pattern (Response Generation)**

```python
# Different strategies for response
strategies = {
    "supportive": warmth_based_response,
    "assertive": directive_response,
    "compromising": balanced_response,
    "avoidant": minimal_response
}

# Select based on context
strategy = strategies[ai_personality.preferred_strategy]
response = strategy(context)
```

**Benefits**: Easy to add new strategies, behavior is pluggable

#### 3. **Factory Pattern (LLM Provider)**

```python
# Create appropriate LLM backend
llm = create_llm_generator(
    provider="openai",  # or "ollama", "mock"
    api_key="...",
    model="gpt-4"
)

# Use same interface regardless of backend
response = llm.generate(prompt)
```

**Benefits**: Switching providers requires only configuration change

#### 4. **State Pattern (Parent States)**

```python
# Different states with distinct behaviors
class ParentState:
    def __init__(self, role: ParentRole):
        self.emotional_state: EmotionalState = EmotionalState()
        self.personality: PersonalityProfile = PersonalityProfile()
        self.memory_store: MemoryStore = MemoryStore()
```

**Benefits**: Clear encapsulation, easy to extend with new state types

### Performance Optimizations

#### 1. FastMemoryStore with LRU Cache

```python
# O(1) retrieval instead of O(n)
# Old approach: iterate through all memories
memories = [m for m in all_memories if tag in m.tags]  # O(n)

# New approach: hashmap + cache
memories = fast_cache.get(tag)  # O(1)

# LRU eviction: keep hot memories in cache
# Older, less-accessed memories get pushed out
```

#### 2. Lazy Loading of Personalities

```python
# Load only when needed
class PersonalityProfile:
    @property
    def traits(self):
        if self._traits is None:
            self._traits = load_from_storage()  # Only once
        return self._traits
```

#### 3. Rule Caching

```python
# Cache evaluation results
last_context = None
cached_matches = None

def evaluate(context):
    if context == last_context:
        return cached_matches  # Instant return
    
    # Otherwise: recalculate
    matches = [r for r in rules if r.condition(context)]
    cached_matches = matches
    last_context = context
    return matches
```

### Type Safety

Throughout the codebase, use Python type hints for IDE support and runtime validation:

```python
from typing import List, Dict, Optional, Callable, Tuple

def process_choices(
    choice_id: str,
    context: DialogueContext,
    callbacks: Optional[List[Callable]] = None
) -> Dict[str, Any]:
    """Process player choice and return results."""
    ...
```

---

## Game Flow Example

### Complete 3-Day Playthough

#### **Day 1: "The First Night"**

```
┌─────────────────────────────────────────────────┐
│ Act 1, Day 1 | THE FIRST NIGHT                  │
│ Time: 2:00 AM                                    │
└─────────────────────────────────────────────────┘

Your newborn won't stop crying at 2 AM.
Both of you are exhausted and running on fumes.

═══════════════════════════════════════════════════

What do you do?

1. GET UP IMMEDIATELY
   You're not sure what the baby needs, but you can't
   ignore the crying. You swing out of bed, even though
   you're desperate for sleep.

2. TRY TO COMFORT FROM BED FIRST
   Your partner has been up more. You whisper to the baby,
   try to console them while staying in bed. If this
   doesn't work, you'll get up.

3. WAKE YOUR PARTNER TO SHARE THE LOAD
   You both knew this was coming. This moment. You nudge
   your partner awake. Whatever happens next, neither of
   you handles it alone.

───────────────────────────────────────────────────
Your choice (1-2-3): 1

───────────────────────────────────────────────────
HIDDEN IMPACT

 Responsibility: HIGH
 → You're owning this moment fully.
   The baby learns: "Parent responds when I cry."
   Your partner notes: "You didn't hesitate."

 Presence: HIGH
 → You're physically and emotionally available.
   Cost: Your rest and resentment (slight).

 Partnership: UNEQUAL (THIS TIME)
 → You handled it solo. That's unsustainable,
   but right now—it works.

────────────────────────────────────────────────────
[Do you want to have a conversation with your partner?
 Or proceed to Day 2? (type message or /next)]
```

**Player's internal experience**: 
- Felt responsible, protective
- Tiring but meaningful
- Wondered if partner would do the same

**AI learns**: 
- Sentiment: +0.2 (slight positive—feeling of purpose)
- Topic: sleep, responsibility, partnership
- Decision style: collaborative + assertive (steps in, but with partner)
- Confidence: first observation

**AI personality changes** (minimal first time):
- Warmth += 0.02
- Assertiveness += 0.01

#### **Optional Conversation (Day 1)**

```
You: "That was exhausting. Are you okay?"

Sara (AI): "I watched you get up three times last hour.
You didn't even ask for help. I felt... helpless."

You: "I didn't want to wake you. You looked so tired."

Sara: "I know. But we agreed we're in this together.
Please wake me next time. I need to be part of this
—not just sleeping while you carry it all."

You: [feeling validated and guilty simultaneously]
```

**Learning Impact**:
- Topic: partnership, communication
- Sentiment: -0.1 (conflict-adjacent but processing)
- Pattern: player avoids burdening others
- AI increases warmth (empathetic) BUT emphasizes partnership
- Learned adjustment: AI becomes more assertive about "we"

#### **Day 2: "Relatives Arrive"**

```
┌─────────────────────────────────────────────────┐
│ Act 1, Day 2 | RELATIVES ARRIVE                 │
│ Time: Saturday Evening                           │
└─────────────────────────────────────────────────┘

Your mother-in-law called this morning saying she'd
"stop by with some casseroles." She's here. So is
your partner's brother.

The advice started before they set their bags down:
- "You're carrying the baby too much—it'll spoil them"
- "That diaper brand? I'd never use that"
- "Sleep training at this age? Seems harsh"

Your partner looks uncomfortable. You can feel
the tension rising.

═══════════════════════════════════════════════════

What do you do?

1. BACK YOUR PARTNER PUBLICLY
   You take their hand, look your mother-in-law in the
   eye, and say: "We appreciate the advice, but we've
   got this our way. That's how we need to parent."
   It's uncomfortable. But you're united.

2. STAY NEUTRAL
   You change the subject, smile, accept the advice
   politely without committing to any of it. Maybe it'll
   blow over. Your partner can decide what to do with
   the suggestions.

3. ACKNOWLEDGE THE ADVICE THOUGHTFULLY
   "That's interesting. We're trying a few different approaches.
   We'll see what works for our family." You validate without
   giving ground. Measured. Respectful.

────────────────────────────────────────────────────
Your choice (1-2-3): 2

────────────────────────────────────────────────────
HIDDEN IMPACT

 Avoidance: MODERATE
 → You're sidestepping the tension.
   Short-term: Uncomfortable conversation avoided.
   Long-term: Boundary was never set.

 Partnership: TENSION
 → Your partner's looking at you with disappointment.
   They needed to see you fight for "us."
   They'll remember this hesitation next time
   they're criticized—especially about YOUR role.

 Confidence: SLIGHT EROSION
   → Not catastrophic. But a fault line appeared.

────────────────────────────────────────────────────
After the visit, your partner is quiet.
Do you talk about it? (/message) Or move on? (/next)
```

**Learning Impact**:
- Sentiment: -0.35 (negative—conflict avoidance)
- Topic: boundaries, partnership, family dynamics
- Decision style: avoidant (not collaborative, not assertive)
- Pattern reinforced: "Player chooses harmony over confrontation"
- Confidence: +0.2 (now at 0.25 overall)

**AI personality shift** (more noticeable now):
- Warmth -= 0.03 (disappointment with avoidance)
- Assertiveness += 0.05 (learning partner is passive, needs to drive)
- Flexibility -= 0.02 (less patient with indirect communication)

#### **Day 2 Conversation**

```
You: "I know you were frustrated at your mom's visit."

Sara: "I wasn't frustrated with you. I was disappointed.
That comment about 'spoiling the baby' was out of line.
And I needed you to say something—anything—to show we're
on the same team."

You: "I didn't want to create drama."

Sara: "This isn't drama. It's our parenting. Our family
boundaries. I can't protect both our kid and our relationship
alone. I need you with me on this."

You: "I understand. I'll do better next time."

Sara: "I believe you. But I'm worried it'll happen again
because standing up is harder than staying quiet. And I
can't carry both of us through every difficult moment."
```

**Learning Impact**:
- Sentiment: -0.1 (difficult but honest)
- Topic: partnership, boundaries, responsibility
- Pattern: **CRITICAL INSIGHT** — "Player values harmony over honesty"
- Confidence: 0.35 (stronger pattern now)

**AI adaptation**:
- Reduces warmth further: -0.04 (conditional, not automatic)
- Increases assertiveness significantly: +0.08 (will push harder)
- **Key shift**: AI stops being purely supportive; becomes more critical

#### **Day 3: "Fighting About Money"**

```
┌─────────────────────────────────────────────────┐
│ Act 1, Day 3 | FIGHTING ABOUT MONEY             │
│ Time: Afternoon                                  │
└─────────────────────────────────────────────────┘

Bills are piling up. Childcare is more expensive than
expected. Your partner just mentioned that one of you
might need to go part-time—and implied it should be
you since you have the more flexible job.

"We can't afford full-time daycare AND mortgage payments
AND healthcare," they said.

═══════════════════════════════════════════════════

What do you do?

1. AGREE WITHOUT DISCUSSION
   You nod. You knew this was coming. Work is work,
   but family is family. Your career can take a hit.
   "Okay. I'll talk to my boss on Monday."

2. PUSH BACK
   "Hold on. Why does it have to be me? You could
   go part-time. Let's actually talk about what's
   sustainable for both of us."

3. SUGGEST A COMPROMISE
   "Let's sit down with the budget. Maybe it's not
   either/or. Maybe we can optimize childcare, trim
   somewhere else, and BOTH work adjusting schedules."

────────────────────────────────────────────────────
Your choice (1-2-3): 2

────────────────────────────────────────────────────
HIDDEN IMPACT

 Assertiveness: HIGH
 → You're protecting your career and your equality.
   Relationship: CONFRONTATIONAL (now)
   But: Standing up for yourself is psychologically
   healthy. Long-term: Respect may increase.

 Partnership: TENSION BUT HONEST
 → You refused to sacrifice silently.
   Your partner can't point to your decision without
   acknowledging you pushed back.

 Self-Care: HIGH
 → You're not automatically martyring yourself.
```

**Learning Impact** (CRITICAL SHIFT):
- Sentiment: -0.45 (conflict, but directness)
- Topic: partnership, fairness, career, family
- **PATTERN BREAKING**: "Player is NOT always avoidant!"
- Confidence: Pattern shifts from -0.35 to +0.15

**AI's Crisis** (Personality Recalibration):
- AI's model was: "Player avoids confrontation"
- Evidence now: "Player will confront when stakes are personal"
- **Emotional state**: Surprise, re-evaluation
- AI **resets warmth**: +0.08 (respect for honesty)
- AI **returns assertiveness**: -0.03 (doesn't need to drive as hard)

**AI's New Understanding**:
- "Player isn't conflict-avoidant; player is other-focused"
- "When it affects player directly, they'll fight"
- "When it affects relationship/partner, they hide"
- "Key to influence: frame issues as affecting PLAYER"

---

## Testing & Validation

### Test Suite Overview

Location: `tests/`

```
├── conftest.py                           # Pytest fixtures
├── test_data_structures_properties.py    # Property tests for core structures
├── test_emotional_memory_unit.py         # Unit tests for emotional memory
├── test_emotional_memory_properties.py   # Property tests for emotional memory
├── test_pattern_tracker_unit.py          # Unit tests for pattern tracking
├── test_pattern_tracker_properties.py    # Property tests for patterns
├── test_trust_dynamics_unit.py           # Unit tests for trust system
└── test_trust_dynamics_properties.py     # Property tests for trust
```

### Test Categories

#### 1. **Property-Based Testing** (using Hypothesis)

```python
# Test that properties hold across random inputs
from hypothesis import given, strategies as st

@given(st.floats(min_value=0, max_value=100))
def test_relationship_state_clamping(value):
    """Trust should always be in [0, 100] range."""
    state = RelationshipState(trust=value)
    state.clamp()
    assert 0 <= state.trust <= 100
```

**Benefit**: Catches edge cases humans wouldn't think of

#### 2. **Unit Testing**

```python
def test_emotional_memory_decay():
    """Test that emotional memory confidence decays over time."""
    memory = EmotionalMemory(content="...", confidence=0.8)
    
    # Simulate 10 hours passing
    memory.decay(hours=10)
    
    # Should be significantly less confident
    assert 0.5 < memory.confidence < 0.8
```

**Benefit**: Isolated component testing

#### 3. **Integration Testing**

```python
def test_full_gameplay_loop():
    """Test complete game flow: setup → scenario → choice → learning."""
    game = NurtureGame()
    game.select_role(ParentRole.MOTHER)
    
    scenario = game.get_scenario_presentation()
    assert scenario['day'] == 1
    
    game.process_choice("choice_1_day1")
    relationship = game.get_relationship_status()
    
    assert 'trust' in relationship
    assert 0 <= relationship['trust'] <= 100
```

**Benefit**: Catch system-level issues

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_emotional_memory_unit.py -v

# Run with coverage report
pytest tests/ --cov=nurture --cov-report=html

# Run tests matching pattern
pytest tests/ -k "emotional" -v
```

### What's Been Validated

✅ **Core Data Structures**
- RelationshipState clamping (values stay in ranges)
- EmotionalState consistency
- PersonalityProfile sanity (traits in [0, 1])

✅ **Learning System**
- Pattern confidence increases with reinforcement
- Sentiment analysis extracts emotions correctly
- Decision style detection matches expected patterns
- Personality adjustments are monotonic (in right direction)

✅ **AI Agent**
- Response generation produces valid output
- Emotional state updates appropriately
- Memory retrieval returns relevant memories
- Personality changes persist across interactions

✅ **Game Flow**
- Scenario presentation works end-to-end
- Choice processing flows correctly
- Save/load preserves game state
- Progress tracking advances properly

---

## Future Development

### Phase 2: Expanded Narrative (Acts 2-4)

#### **Act 2: MIRROR** (Age 4-7)

*The child becomes reflective, testing boundaries, learning social rules*

**Themes**:
- Identity formation ("Who am I without my parents?")
- Boundary testing ("What happens if I disobey?")
- Social learning ("How do I make friends?")
- Emotional regulation ("Why am I so angry/sad?")

**Challenges to navigate**:
- School conflicts & teacher relationships
- Sibling dynamics (if applicable)
- Gender/identity questions
- Aggression and emotional dysregulation
- Separation anxiety

#### **Act 3: FRACTURE** (Age 8-12)

*Growing independence creates philosophical divergence between parents*

**Themes**:
- Autonomy vs. security
- Values transmission
- Academic pressure
- Peer influence vs. family values
- Early identity crisis

**New systems needed**:
- Child's own personality & goals
- School as external system influencing values
- Friend group dynamics affecting behavior
- diverging parental values becoming apparent

#### **Act 4: RECKONING** (Age 13-18)

*Fundamentally different people learning to coexist as adolescent becomes adult*

**Themes**:
- Identity solidification
- Values competition (family vs. peer culture)
- Autonomy assertion
- Trust erosion / renegotiation
- Philosophical disagreement about who child should become

**Long-term tracking**:
- How parental choices in Acts 1-3 influence teen outcomes
- Relationship repair (can trust be rebuilt?)
- Role transformation (from parent to... guide? consultant?)

### Phase 3: Interactive & Immersive Features

#### **Voice Support**
- Text-to-speech for AI responses
- Speech-to-text for player input
- Emotional prosody in AI voice

#### **Web Interface**
- Browser-based UI
- Relationship graphs and dashboards
- Timeline visualization
- Achievement system

#### **Multiplayer Mode**
- Two human players co-parenting
- Async play (send messages to each other's game)
- Shared child entity
- Relationship updates from both directions

### Phase 4: Advanced AI Features

#### **Child Agent**
- AI-controlled child with own personality & goals
- Responds to parental choices
- Develops trust/distrust based on consistency
- Expresses preferences and values

#### **Long-term Simulation Engine**
- Cumulative effect of choices (choice in Day 1 affects outcome in Day 50)
- Flashback mechanics (seeing consequences of old decisions)
- Butterfly effect: small choices, big consequences

#### **Parenting Grades**
- Computed at end of each Act
- Measures: emotional safety, autonomy support, consistency, etc.
- Not "right" or "wrong," but trade-offs revealed
- Feedback: "You excelled at X, but Y suffered"

#### **Explicit Pattern Feedback**
- AI explicitly mentions learned patterns
- "I've noticed you avoid conflict when it affects me"
- "You always prioritize the baby's immediate needs"
- Creates metacognitive awareness

---

## Conclusion

**Nurture** represents a complete Phase 1 of an ambitious project exploring AI agents, emotional modeling, and interactive storytelling within the context of parenting and co-parenting relationships.

### What's Accomplished

- ✅ Full game engine with 12-day narrative Act
- ✅ Believable AI agent with personality and learning
- ✅ Comprehensive story with 36 unique choice branches
- ✅ Learning system that adapts AI to player patterns
- ✅ Memory and persistence systems
- ✅ Tested, documented, playable codebase
- ✅ Multiple LLM backend options

### What's Next

- 📝 Acts 2-4 narrative content
- 🧠 Child AI agent
- 🎮 Web interface and voice support
- 👥 Multiplayer co-parenting mode
- 📊 Long-term impact tracking

### The Vision

Nurture aims to become a **space for reflection on partnership and parenting**—one where people can:

- Explore different approaches consequence-free
- See patterns in their own thinking
- Understand their partner's perspective
- Learn through iterative dialogue
- Recognize the complexity of good parenting

It's a game, but it's also a tool for growth.

---

**Created by**: Harsh and the PBL-1 Project Team  
**License**: Educational Use  
**Last Updated**: March 2026

For more information, see:
- [README.md](README.md) - Quick start guide
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Technical overview
- Run `python -m nurture.main` to play!
