#!/usr/bin/env python3
"""
Simple script to answer: "Which Claude model am I talking to right now?"

Usage: python which_model.py
"""

def main():
    print("\n" + "="*70)
    print("  Which Claude Model Am I Talking To?")
    print("="*70)

    print("\n📝 It depends on the context:\n")

    print("1. If you're DEVELOPING with Claude Code (AI assistant):")
    print("   → You're talking to: Claude Sonnet 4.5")
    print("   → Model ID: claude-sonnet-4-5-20250929")
    print("   → This is the AI helping you write code and fix bugs\n")

    print("2. If you're PLAYING the Nurture game:")
    print("   → Check active models by typing: /status")
    print("   → Default: Mock LLM (template responses)")
    print("   → Available: Ollama (local), OpenAI, Groq, or Anthropic Claude\n")

    print("3. If you're TESTING the child AI JavaScript system:")
    print("   → Child AI uses: Claude Sonnet 4.6")
    print("   → Model ID: claude-sonnet-4-6")
    print("   → (requires ANTHROPIC_API_KEY environment variable)\n")

    print("="*70)
    print("\nFor more details, see: AI_MODELS_INFO.md")
    print("="*70 + "\n")

    # Try to show current game models if running
    try:
        from nurture.main import NurtureGame
        from nurture.core.enums import ParentRole

        print("\n🎮 Testing Nurture game models...\n")

        game = NurtureGame()
        game.select_role(ParentRole.FATHER)

        print("\n" + "="*70)
        print("  Current Nurture Game Models")
        print("="*70)

        if hasattr(game, '_active_parent_model'):
            print(f"\n  AI Parent: {game._active_parent_model}")
        if hasattr(game, '_active_child_model'):
            print(f"  Child AI:  {game._active_child_model}")

        print("\n" + "="*70 + "\n")

    except Exception as e:
        print(f"\n(Could not test game models: {e})\n")

if __name__ == "__main__":
    main()
