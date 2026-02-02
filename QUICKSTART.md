START PLAYING NURTURE
═════════════════════════════════════════════════════════════════════════

From the terminal in VS Code:

  python nurture/main.py

What happens:
  1. Choose your role (Father or Mother)
  2. Read today's scenario carefully
  3. Choose response (1, 2, or 3)
  4. AI learns from your choice
  5. Optionally talk with your partner
  6. Move to next day
  7. Play through 12 days of Act 1

═════════════════════════════════════════════════════════════════════════

KEY CONCEPT: The AI learns from EVERYTHING you do.

Example:
  • Day 1: You choose to "Get up immediately" when baby cries
    → AI learns you're responsive and present
  
  • Day 2: You choose to "Stay neutral" on visitor advice  
    → AI learns you're conflict-avoidant
  
  • Day 3: You choose to "Make extra money"
    → AI learns you prioritize financial security
  
  By Day 12, the AI understands your parenting philosophy
  and will reference these patterns in conversations.

═════════════════════════════════════════════════════════════════════════

DURING CONVERSATION MODE:

After choosing a scenario, you can talk to your partner:
  
  You: "I'm feeling overwhelmed"
  Father: [AI responds based on what you just chose]

The AI adapts to you. Don't just type random things - the game
records patterns across all your choices.

═════════════════════════════════════════════════════════════════════════

SAVE YOUR GAME:

Type /save at any time. Your progress, learning data, and 
relationship status are all saved.

Check progress: /status
Quit: /quit

═════════════════════════════════════════════════════════════════════════

WHAT HAPPENS BEHIND THE SCENES:

1. Story Engine: Manages 12-day narrative with choices
2. Learning System: Tracks your decision patterns
3. AI Parent: Adapts personality based on what you chose
4. Interaction Manager: Generates contextual responses
5. State Manager: Saves everything

Each choice has hidden impacts:

  Choice: "Get up immediately"
  Hidden Tags: [responsibility_high, presence_high, attachment_security_positive]
  Long-term: Affects how your child views reliability

═════════════════════════════════════════════════════════════════════════

EXPECTED GAMEPLAY TIME:

  • 1 Day scenario: 3-8 minutes
  • All 12 Days (Act 1): ~60 minutes  
  • Future: Acts 2-4 will add 9+ more hours

═════════════════════════════════════════════════════════════════════════

TESTING THE SYSTEM (Without Full Playthrough):

  python test_narrative_gameplay.py

This runs through 3 days automatically to show how everything works.

═════════════════════════════════════════════════════════════════════════

FUTURE ACTS (Coming Soon):

  ACT 1 - FOUNDATION (Age 0-3): 12 days - YOU ARE HERE
  ACT 2 - MIRROR (Age 4-7): 16 days - Child mirrors your behavior
  ACT 3 - FRACTURE (Age 8-12): 20 days - Independence begins  
  ACT 4 - RECKONING (Age 13-18): 25 days - Teenage years & consequences

═════════════════════════════════════════════════════════════════════════

Ready to start? Run:

  python nurture/main.py

═════════════════════════════════════════════════════════════════════════
