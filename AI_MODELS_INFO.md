# AI Models Information

This document explains which AI models are used in the Nurture game and in development.

## Models Used in Nurture Game

### AI Parent
The AI parent (your co-parenting partner) can use different models depending on your configuration:

- **Default**: Mock LLM (template-based responses, no API key needed)
- **Ollama**: Local models like Llama, Mistral, Neural-Chat (free, offline)
- **OpenAI**: GPT models (requires API key)
- **Groq**: Fast LLM via LPU (free API key from https://console.groq.com)

To check which model is currently active, type `/status` in the game.

### Child AI (Lily)
The child AI uses the same backend as the AI parent by default:
- In the game, it mirrors the parent AI configuration
- The JavaScript implementation (`child_ai_system.js`) is configured to use **Claude Sonnet 4.6** when the Anthropic API is available

To check which model is active for the child AI, type `/status` in the game.

## Claude Models in Development

### Claude Code Assistant
When you're working with this repository using Claude Code (the AI assistant helping you develop this project), you're talking to:

**Claude Sonnet 4.5**
- Model ID: `claude-sonnet-4-5-20250929`
- This is the AI assistant that helps you write code, fix bugs, and implement features

### Claude in Child AI System
The child AI JavaScript system (`nurture/child_ai_system.js`) is configured to use:

**Claude Sonnet 4.6**
- Model ID: `claude-sonnet-4-6` (line 31 of child_ai_system.js)
- This provides age-appropriate child behavior simulation

## How to Configure Models

### In the Game
The game will automatically detect and use the best available model:
1. First tries Ollama (local, free)
2. Falls back to Mock LLM (template responses)

To use a specific provider:
```python
from nurture.main import NurtureGame

game = NurtureGame()
game.select_role(ParentRole.FATHER)

# Use OpenAI
game.configure_llm(
    provider="openai",
    api_key="your-key-here",
    model_name="gpt-4"
)

# Or use Groq (fast and free)
game.configure_llm(
    provider="groq",
    api_key="your-groq-key",
    model_name="llama-3.3-70b-versatile"
)
```

### For Child AI with Anthropic Claude
To enable Claude Sonnet 4.6 for the child AI, set the environment variable:
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

Then the JavaScript child AI system will use Claude Sonnet 4.6 for realistic child behavior.

## Which Model Am I Talking To Right Now?

### If you're playing the game:
Type `/status` in the game to see which models are active for the AI parent and child.

### If you're developing with Claude Code:
You're talking to **Claude Sonnet 4.5** (the AI assistant helping you code).

### If you're testing the child AI directly:
The child AI uses **Claude Sonnet 4.6** when you have an Anthropic API key configured.
