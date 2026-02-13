# NURTURE - Project Summary
## AI-Powered Parent Agent Simulation

---

## 1. Project Overview

**Nurture** is a text-based parenting simulation game that uses **Artificial Intelligence** to create realistic co-parenting conversations. Players experience parenting dilemmas and interact with an AI partner that learns and adapts to their choices.

### Core Concept
- Player chooses to be either **Father** or **Mother**
- AI automatically plays the other parent
- Navigate 12 days of parenting scenarios (Act 1: Baby age 0-3)
- AI partner remembers conversations and adapts personality over time

---

## 2. Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.9+** | Primary programming language |
| **Ollama** | Local LLM (Large Language Model) server |
| **Mistral 7B** | AI model for generating natural responses |
| **JSON** | Game state persistence (save/load) |
| **Dataclasses** | Clean data structure design |
| **pytest** | Unit testing framework |
| **hypothesis** | Property-based testing |

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MAIN GAME LOOP                             │
│                      (main.py)                                  │
│  • Role selection (Father/Mother)                               │
│  • Command handling (/save, /status, /quit)                     │
│  • Game flow coordination                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  STORY ENGINE   │ │ LEARNING SYSTEM │ │   AI PARENT     │
│                 │ │                 │ │                 │
│ • 12 scenarios  │ │ • Pattern track │ │ • Personality   │
│ • Choices (3)   │ │ • Decision hist │ │ • Emotions      │
│ • Hidden impact │ │ • Adaptation    │ │ • LLM responses │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OLLAMA (Local LLM)                         │
│              mistral:7b-instruct-v0.3-q4_K_M                    │
│  • Processes conversation context                               │
│  • Generates natural language responses                         │
│  • Runs locally (no internet required for AI)                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Module Breakdown

### 4.1 Core Modules (`/nurture/core/`)

| File | Description |
|------|-------------|
| `data_structures.py` | Defines ParentState, EmotionalState, PersonalityProfile |
| `enums.py` | All game constants (EmotionType, ParentRole, etc.) |
| `events.py` | Event bus for inter-module communication |
| `interaction_manager.py` | Coordinates parent interactions |

### 4.2 Agent System (`/nurture/agents/`)

| File | Description |
|------|-------------|
| `base_parent.py` | Abstract base class for all parent agents |
| `player_parent.py` | Handles player input and state |
| `ai_parent.py` | **AI-controlled parent with LLM integration** |

### 4.3 Story System (`/nurture/story/`)

| File | Description |
|------|-------------|
| `story_engine.py` | Manages narrative progression |
| `story_data.py` | 12 days of scenarios with choices and impacts |

### 4.4 Learning System (`/nurture/learning/`)

| File | Description |
|------|-------------|
| `learning_system.py` | **Tracks user patterns and adapts AI** |

**What the AI Learns:**
- Decision patterns (collaborative vs assertive)
- Emotional tendencies
- Topic preferences
- Response styles

### 4.5 Personality System (`/nurture/personality/`)

| File | Description |
|------|-------------|
| `trust_dynamics.py` | Trust builds slowly, erodes quickly (2:1 ratio) |
| `emotional_memory.py` | Long-term emotional event storage |
| `pattern_tracker.py` | Identifies behavioral patterns |

### 4.6 Memory System (`/nurture/memory/`)

| File | Description |
|------|-------------|
| `memory_store.py` | Stores conversation memories |
| `state_manager.py` | **Save/Load game functionality** |
| `fast_memory.py` | Short-term memory for current session |

### 4.7 Rules Engine (`/nurture/rules/`)

| File | Description |
|------|-------------|
| `rule_engine.py` | Applies behavioral rules |
| `emotional_rules.py` | Emotion-based response rules |
| `behavioral_constraints.py` | Personality-based constraints |

### 4.8 LLM Interface (`/nurture/utils/`)

| File | Description |
|------|-------------|
| `llm_interface.py` | **Connects to Ollama for AI responses** |

**Supported LLM Providers:**
1. **Ollama (Local)** - Currently used
2. Groq (Cloud, Free tier)
3. OpenAI (Cloud, Paid)
4. Mock (Testing)

---

## 5. Workflow: How the Game Works

### Step 1: Game Initialization
```
python -m nurture.main
```
- Load saved game OR start new
- Select role (Father/Mother)
- Initialize AI parent with opposite role
- Connect to Ollama LLM

### Step 2: Story Presentation
```
ACT 1 — FOUNDATION (Age 0–3) - Day 1/12
────────────────────────────────────────
First Night Home

Baby crying nonstop at 2 AM. Both parents exhausted.
────────────────────────────────────────
What do you do?
  1. Get up immediately and handle the baby
  2. Wait and hope the other parent gets up
  3. Wake the other parent and insist they do it
```

### Step 3: Player Choice Processing
```python
# Player selects option 1
choice = "immediate"

# Story engine processes choice
impacts = [
    "responsibility_high",      # Hidden tag
    "presence_high",            # Hidden tag  
    "attachment_security_positive"
]

# Learning system records pattern
learning_system.record_story_decision("first_night", choice, impacts)
```

### Step 4: AI Conversation
```
Would you like to have a conversation with your partner? (y/n): y

You: "I'm so tired but I want to be there for the baby"

[AI processes message through Ollama]
[Considers: scenario context, choice made, emotional state, past patterns]

Mother: "I saw you get up right away. That means a lot to me.
         We're in this together, even when we're exhausted."
```

### Step 5: AI Response Generation

```python
# Context sent to Ollama:
prompt = """
You are Sarah, a new mother. Your husband just chose to get up 
immediately when the baby cried at 2 AM. He says: "I'm so tired 
but I want to be there for the baby"

Sarah responds (short, real, no therapy talk):
"""

# Ollama generates response using Mistral 7B model
response = ollama.generate(model="mistral:7b-instruct", prompt=prompt)
```

---

## 6. AI/ML Components

### 6.1 Large Language Model (LLM)

**Model Used:** `mistral:7b-instruct-v0.3-q4_K_M`
- 7 Billion parameters
- Quantized to 4-bit (4.4 GB)
- Runs locally via Ollama
- No API costs

**How it works:**
1. User types message
2. System builds context (scenario, choice, history)
3. Prompt sent to Ollama API (localhost:11434)
4. Model generates natural language response
5. Response displayed to player

### 6.2 Learning System

The AI **learns from player behavior** across sessions:

```python
class LearningSystem:
    decision_style = {
        "collaborative": 0.5,   # Works with partner
        "assertive": 0.5,       # Takes charge
        "compromising": 0.5,    # Finds middle ground
        "empathetic": 0.5,      # Focuses on emotions
        "practical": 0.5,       # Focus on solutions
    }
```

**Learning happens when:**
- Player makes story choices → Updates decision patterns
- Player types messages → Analyzes sentiment
- Player discusses topics → Tracks preferences

### 6.3 Trust Dynamics Engine

**Mathematical Model:**
```
Trust increase: +2.0 per positive action
Trust decrease: -4.0 per negative action (2x faster!)

Withdrawal triggers:
- Trust < 50%: Mild withdrawal
- Trust < 30%: Critical withdrawal

Resentment accumulates from repeated negative patterns
```

### 6.4 Emotional State System

Each parent has dynamic emotions:
```python
emotions = {
    "calm": 0.6,
    "joy": 0.4,
    "trust": 0.5,
    "stress": 0.2,
    "anxiety": 0.1,
    "frustration": 0.1,
    "anger": 0.0,
    "sadness": 0.1,
}
```

Emotions affect:
- AI response tone
- Available dialogue options
- Relationship dynamics

---

## 7. Data Flow Diagram

```
┌──────────┐     ┌──────────────┐     ┌─────────────┐
│  Player  │────▶│ Story Engine │────▶│   Choice    │
│  Input   │     │  (Scenario)  │     │  Selection  │
└──────────┘     └──────────────┘     └─────────────┘
                                            │
                                            ▼
┌──────────────────────────────────────────────────────┐
│              LEARNING SYSTEM                         │
│  • Records choice                                    │
│  • Updates decision patterns                         │
│  • Adjusts adaptation level                          │
└──────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌──────────────────────────────────────────────────────┐
│              CONVERSATION MODE                       │
│  Player types: "I'm feeling overwhelmed"             │
└──────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌──────────────────────────────────────────────────────┐
│              CONTEXT BUILDER                         │
│  • Current scenario: "first_night"                   │
│  • Player's choice: "immediate"                      │
│  • Emotional state: tired but committed              │
│  • Past patterns: collaborative style                │
└──────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌──────────────────────────────────────────────────────┐
│              OLLAMA LLM                              │
│  Model: mistral:7b-instruct                          │
│  Input: Contextual prompt + player message           │
│  Output: Natural language AI response                │
└──────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌──────────────────────────────────────────────────────┐
│              AI RESPONSE                             │
│  "I saw you get up right away. That means a lot."   │
└──────────────────────────────────────────────────────┘
```

---

## 8. Key Features

| Feature | Implementation |
|---------|---------------|
| **Role Selection** | Player chooses Father/Mother, AI takes other |
| **12 Parenting Scenarios** | Each with 3 choices and hidden impacts |
| **Natural Conversations** | Powered by local Mistral 7B LLM |
| **Adaptive AI** | Learns from player decisions over time |
| **Emotional Modeling** | 8 emotion types affect behavior |
| **Trust System** | Asymmetric trust (builds slow, erodes fast) |
| **Save/Load** | JSON-based game state persistence |
| **Pattern Recognition** | Tracks player behavior patterns |

---

## 9. File Structure

```
PBL-1/
├── nurture/
│   ├── main.py              # Entry point
│   ├── agents/              # Parent agent classes
│   ├── core/                # Data structures & enums
│   ├── emotion/             # Emotion processing
│   ├── learning/            # AI learning system
│   ├── memory/              # Memory & state management
│   ├── personality/         # Trust & personality tracking
│   ├── rules/               # Behavioral rules engine
│   ├── story/               # Scenarios & narrative
│   └── utils/               # LLM interface & helpers
├── saves/                   # Save files (JSON)
├── tests/                   # Unit & property tests
├── requirements.txt         # Dependencies
├── README.md                # Project documentation
└── QUICKSTART.md           # Quick start guide
```

---

## 10. How to Run

### Prerequisites
1. Python 3.9+
2. Ollama installed (`winget install Ollama.Ollama`)
3. Mistral model (`ollama pull mistral:7b-instruct-v0.3-q4_K_M`)

### Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Start Ollama (runs in background automatically)
ollama serve

# Run the game
python -m nurture.main
```

---

## 11. Future Plans (Acts 2-4)

| Act | Age Range | Days | Focus |
|-----|-----------|------|-------|
| Act 1 | 0-3 years | 12 | Foundation (IMPLEMENTED) |
| Act 2 | 4-7 years | 16 | Mirror - Child mirrors parent behavior |
| Act 3 | 8-12 years | 20 | Fracture - Independence begins |
| Act 4 | 13-18 years | 25 | Reckoning - Teenage consequences |

---

## 12. Learning Outcomes

This project demonstrates:

1. **AI/ML Integration** - Using LLMs for natural language generation
2. **Software Architecture** - Modular design with clear separation of concerns
3. **State Management** - Complex state tracking and persistence
4. **Behavioral Modeling** - Trust dynamics, emotional states, pattern recognition
5. **Game Design** - Narrative structure, meaningful choices, consequence systems
6. **Python Best Practices** - Dataclasses, type hints, documentation

---

## 13. Team Contributors

- Harshad (Project Lead & AI Integration)
- [Add team members here]

---

## 14. Summary

**Nurture** is an AI-powered parenting simulation that combines:
- **Story-driven gameplay** with meaningful choices
- **Local LLM integration** (Mistral 7B via Ollama)
- **Adaptive AI** that learns from player behavior
- **Psychological modeling** (trust, emotions, patterns)
- **Clean Python architecture** with comprehensive testing

The project showcases how modern AI can create engaging, emotionally intelligent interactive experiences while running entirely on local hardware.

---

*Project developed as part of Project-Based Learning (PBL) initiative.*
