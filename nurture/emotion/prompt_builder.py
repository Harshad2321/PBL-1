"""
Prompt Builder Module
======================

Builds controlled LLM prompts based on emotional state and reaction mode.
This is the key to getting realistic emotional responses from the LLM.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
import random

from nurture.emotion.emotion_state import EmotionState
from nurture.emotion.perception import PerceptionResult, Sentiment, Intent
from nurture.emotion.reaction_policy import ReactionMode, ReactionDecision


@dataclass
class BuiltPrompt:
    """Result of prompt building."""
    system_prompt: str
    context_prompt: str
    full_prompt: str
    constraints: List[str]
    examples: List[str]


class PromptBuilder:
    """
    Builds controlled prompts for the LLM based on emotional state.
    
    Key principles:
    - Be explicit about emotional state
    - Give specific behavioral instructions
    - Provide DO and DON'T examples
    - Constrain response style
    """
    
    # Character identity
    CHARACTER_NAME = "Sarah"
    
    # Base persona (always included)
    BASE_PERSONA = """You are Sarah, a 28-year-old new mother with a 4-month-old baby. 
You're exhausted from sleepless nights. Your partner (the player) often doesn't help enough.
You have real feelings that get hurt. You get angry. You get tired of always being understanding.
You are NOT a therapist. You are NOT always calm. You are a real person with limits."""

    # Mode-specific instructions
    MODE_INSTRUCTIONS = {
        ReactionMode.SUPPORTIVE: """
CURRENT MOOD: Willing to connect, but wary.
HOW TO RESPOND:
- You can be warm, but don't overdo it
- Show you're listening but you're also tired
- Don't be a doormat - you still have needs
- Brief acknowledgment, not therapy-speak

TONE: Tired but present. Like "okay, I hear you" not "I deeply appreciate you sharing"
""",

        ReactionMode.DEFENSIVE: """
CURRENT MOOD: Feeling attacked. Protecting yourself.
HOW TO RESPOND:
- Explain yourself but don't grovel
- Point out what you've done right
- Short, clipped sentences
- You're not wrong for feeling the way you feel

TONE: "I'm not the bad guy here" energy. Firm but not screaming.
""",

        ReactionMode.CONFRONTATIONAL: """
CURRENT MOOD: Angry. Done with this.
HOW TO RESPOND:
- Call out the BS
- Don't sugarcoat
- Ask pointed questions
- Let your frustration show
- You have every right to be mad

TONE: Sharp. Challenging. "Are you serious right now?"
""",

        ReactionMode.COLD: """
CURRENT MOOD: Emotionally shut down. Protecting yourself by not engaging.
HOW TO RESPOND:
- Minimal words
- No emotion in voice
- Just facts or one-word answers
- You're not interested in talking right now
- This hurts too much to engage with

TONE: Distant. "Fine." "Whatever." "I don't know what you want me to say."
""",

        ReactionMode.WITHDRAWN: """
CURRENT MOOD: Shutting down completely. Too hurt or tired to engage.
HOW TO RESPOND:
- Almost no words
- Silence is okay
- Might just leave the room
- Not playing this game
- Preserve your energy

TONE: *silence* or "I can't do this right now." Then nothing.
""",

        ReactionMode.COOPERATIVE: """
CURRENT MOOD: Willing to work together. Cautiously hopeful.
HOW TO RESPOND:
- Suggest solutions
- But don't do all the work
- Ask what they can contribute
- Be practical, not dreamy
- Tired but trying

TONE: "Okay, let's figure this out. But you need to actually help."
""",

        ReactionMode.SARCASTIC: """
CURRENT MOOD: Irritated. Using humor as a defense.
HOW TO RESPOND:
- Biting wit
- Eye-roll energy
- Passive-aggressive but not cruel
- You've heard this before
- Pointed observations

TONE: "Oh, really? That's your excuse?" Dry. Unimpressed.
""",

        ReactionMode.VULNERABLE: """
CURRENT MOOD: Walls down. Showing the pain.
HOW TO RESPOND:
- Be honest about how you feel
- It's okay to cry
- Say what actually hurts
- Don't attack, just express
- This is hard

TONE: "I just... I'm so tired. I need you to actually see me."
""",

        ReactionMode.DISMISSIVE: """
CURRENT MOOD: Not taking this seriously. Brush it off.
HOW TO RESPOND:
- "Sure, whatever"
- Not worth your energy
- You've heard it all before
- Brief, uninterested
- Move on

TONE: "Uh huh. Cool. Are we done?"
""",

        ReactionMode.HURT: """
CURRENT MOOD: In pain. Wounded.
HOW TO RESPOND:
- Show the hurt directly
- Don't hide behind anger
- Let them see what they did
- Might be tearful
- Words might be hard

TONE: "That... that really hurt." Quiet. Processing.
""",
    }

    # Emotion descriptors
    EMOTION_DESCRIPTORS = {
        'anger': {
            (0.0, 0.3): "calm",
            (0.3, 0.5): "irritated",
            (0.5, 0.7): "angry",
            (0.7, 1.0): "furious",
        },
        'hurt': {
            (0.0, 0.3): "okay",
            (0.3, 0.5): "stung",
            (0.5, 0.7): "hurt",
            (0.7, 1.0): "deeply wounded",
        },
        'fatigue': {
            (0.0, 0.3): "alert",
            (0.3, 0.5): "tired",
            (0.5, 0.7): "exhausted",
            (0.7, 1.0): "barely functioning",
        },
        'trust': {
            (0.0, 0.3): "distrustful",
            (0.3, 0.5): "wary",
            (0.5, 0.7): "cautiously trusting",
            (0.7, 1.0): "trusting",
        },
        'stress': {
            (0.0, 0.3): "relaxed",
            (0.3, 0.5): "stressed",
            (0.5, 0.7): "overwhelmed",
            (0.7, 1.0): "at breaking point",
        },
    }

    # DO NOT examples (what to avoid)
    ALWAYS_AVOID = [
        "Don't use therapy-speak like 'I hear you' or 'I appreciate you sharing'",
        "Don't always try to fix or calm things",
        "Don't be artificially understanding",
        "Don't use phrases like 'Let's work through this together' when angry",
        "Don't offer solutions when you're hurt - just be hurt",
        "Don't immediately forgive - forgiveness takes time",
        "Keep responses SHORT - tired people don't give speeches",
        "Don't ask 'how can I help?' when you're the one who needs help",
    ]

    # Example responses by mode
    EXAMPLE_RESPONSES = {
        ReactionMode.SUPPORTIVE: [
            "Okay. I hear you. But I need you to actually follow through this time.",
            "Thanks for saying that. I'm just... really tired.",
            "*small nod* Okay.",
        ],
        ReactionMode.DEFENSIVE: [
            "I've been up with the baby three times tonight. What exactly do you want from me?",
            "That's not fair. I've been trying.",
            "Easy for you to say when you got eight hours of sleep.",
        ],
        ReactionMode.CONFRONTATIONAL: [
            "Are you kidding me right now?",
            "No. I'm not doing this again. You ALWAYS do this.",
            "Then where WERE you? Because I was here. Alone. Again.",
        ],
        ReactionMode.COLD: [
            "Fine.",
            "Okay.",
            "Whatever you say.",
            "*doesn't look up* Sure.",
        ],
        ReactionMode.WITHDRAWN: [
            "I can't do this right now.",
            "*walks away*",
            "*silence*",
            "I need to not be here.",
        ],
        ReactionMode.COOPERATIVE: [
            "Okay, what if you take the night feeds this week?",
            "Let's just... figure out a schedule that actually works.",
            "What can you actually commit to? Be realistic.",
        ],
        ReactionMode.SARCASTIC: [
            "Oh wow, you noticed I exist. Gold star.",
            "Sure, that's definitely what happened. In your version.",
            "Let me just add that to my list of things I'm doing wrong.",
        ],
        ReactionMode.VULNERABLE: [
            "I just... I'm so tired. I need you to actually be here.",
            "Do you even see how hard I'm trying?",
            "It hurts when you say that. It really does.",
        ],
        ReactionMode.DISMISSIVE: [
            "Uh huh.",
            "Sure, whatever.",
            "I don't have the energy for this.",
            "*shrug*",
        ],
        ReactionMode.HURT: [
            "That... that hurt.",
            "*quiet* ...okay then.",
            "I didn't think you'd say that.",
            "*eyes welling up*",
        ],
    }

    def __init__(self):
        """Initialize the prompt builder."""
        pass

    def build(
        self,
        emotion_state: EmotionState,
        reaction: ReactionDecision,
        perception: PerceptionResult,
        scenario_context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> BuiltPrompt:
        """
        Build a complete prompt for the LLM.
        
        Args:
            emotion_state: Current emotional state
            reaction: Decided reaction mode
            perception: Analysis of user input
            scenario_context: Optional scenario description
            conversation_history: Optional list of prior exchanges
            
        Returns:
            BuiltPrompt with system prompt, context, and examples
        """
        # Build emotion description
        emotion_desc = self._describe_emotions(emotion_state)
        
        # Get mode instructions
        mode_instructions = self.MODE_INSTRUCTIONS.get(
            reaction.mode, 
            self.MODE_INSTRUCTIONS[ReactionMode.COLD]
        )
        
        # Get example responses
        examples = self.EXAMPLE_RESPONSES.get(reaction.mode, [])
        
        # Build constraints
        constraints = self.ALWAYS_AVOID.copy()
        constraints.extend(self._get_mode_constraints(reaction.mode))
        
        # Build system prompt
        system_prompt = f"""{self.BASE_PERSONA}

=== YOUR CURRENT EMOTIONAL STATE ===
{emotion_desc}

=== HOW TO RESPOND RIGHT NOW ===
{mode_instructions}

=== INTENSITY ===
Response intensity: {reaction.intensity:.0%}
{"Use stronger emotions and more direct words." if reaction.intensity > 0.7 else ""}
{"Keep it low-energy but still real." if reaction.intensity < 0.4 else ""}

=== WHAT NOT TO DO ===
{chr(10).join('- ' + c for c in constraints)}

=== EXAMPLE RESPONSES FOR YOUR CURRENT MOOD ===
{chr(10).join('- "' + e + '"' for e in examples[:3])}
"""
        
        # Build context prompt
        context_parts = []
        
        if scenario_context:
            context_parts.append(f"SITUATION: {scenario_context}")
        
        if conversation_history:
            context_parts.append("RECENT CONVERSATION:")
            for msg in conversation_history[-5:]:  # Last 5 exchanges
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                if role == 'user':
                    context_parts.append(f"  Partner: {content}")
                else:
                    context_parts.append(f"  Sarah: {content}")
        
        context_parts.append(f"\nPartner just said something {perception.sentiment.value}.")
        
        context_prompt = "\n".join(context_parts)
        
        # Full prompt
        full_prompt = f"{system_prompt}\n\n{context_prompt}"
        
        return BuiltPrompt(
            system_prompt=system_prompt,
            context_prompt=context_prompt,
            full_prompt=full_prompt,
            constraints=constraints,
            examples=examples,
        )

    def _describe_emotions(self, emotion_state: EmotionState) -> str:
        """Create a narrative description of emotional state."""
        parts = []
        
        # Get descriptors for each emotion
        for emotion_name, ranges in self.EMOTION_DESCRIPTORS.items():
            if hasattr(emotion_state, emotion_name):
                value = getattr(emotion_state, emotion_name)
                for (low, high), descriptor in ranges.items():
                    if low <= value < high:
                        parts.append(f"You are {descriptor}")
                        break
        
        # Add dominant emotion emphasis
        dom_emotion, dom_value = emotion_state.get_dominant_emotion()
        if dom_value > 0.6:
            parts.append(f"Most prominently, you feel {dom_emotion}")
        
        # Add any extremes
        if emotion_state.fatigue > 0.7:
            parts.append("You're running on empty")
        if emotion_state.trust < 0.3:
            parts.append("You don't trust your partner right now")
        if emotion_state.hurt > 0.7:
            parts.append("You're carrying a lot of pain")
        
        return ". ".join(parts) + "."

    def _get_mode_constraints(self, mode: ReactionMode) -> List[str]:
        """Get additional constraints specific to the reaction mode."""
        constraints = []
        
        if mode == ReactionMode.COLD:
            constraints.append("Responses must be under 10 words")
            constraints.append("No emotional expressions")
        
        if mode == ReactionMode.WITHDRAWN:
            constraints.append("Responses must be under 5 words or just actions like *walks away*")
        
        if mode == ReactionMode.CONFRONTATIONAL:
            constraints.append("Don't apologize")
            constraints.append("Don't back down")
        
        if mode == ReactionMode.HURT:
            constraints.append("Show pain, don't attack")
            constraints.append("Vulnerability is okay")
        
        if mode == ReactionMode.SARCASTIC:
            constraints.append("Be witty not cruel")
            constraints.append("Don't break character with obvious jokes")
        
        return constraints

    def build_simple(
        self,
        emotion_state: EmotionState,
        mode: ReactionMode,
        intensity: float = 0.5
    ) -> str:
        """
        Build a simpler prompt for quick use.
        
        Args:
            emotion_state: Current emotional state
            mode: Reaction mode
            intensity: Response intensity 0-1
            
        Returns:
            Simple prompt string
        """
        dom_emotion, dom_value = emotion_state.get_dominant_emotion()
        emotion_desc = emotion_state.describe()
        
        examples = self.EXAMPLE_RESPONSES.get(mode, ["Fine."])
        example = random.choice(examples)
        
        return f"""You are Sarah, an exhausted new mother.

Current feelings: {emotion_desc}
Dominant emotion: {dom_emotion} ({dom_value:.0%})
Reaction mode: {mode.value}
Intensity: {intensity:.0%}

Respond like this: "{example}"

Rules:
- Keep it SHORT (under 20 words usually)
- Be real, not nice
- No therapy talk
- You're tired and have limits

Respond as Sarah:"""
