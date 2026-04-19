"""
LLM Interface for Nurture Simulation
==============================
Provides an abstraction layer for LLM integration.
Supports multiple backends:
- Groq (FREE, ultra-fast - recommended!)
- OpenAI
- Ollama (local)
- Mock (testing)

Groq API: https://console.groq.com (free tier available)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import os
import json
import time
import random
import re


@dataclass
class LLMConfig:
    """
    Configuration for LLM connection.
    
    Attributes:
        provider: LLM provider (groq, openai, ollama, mock)
        model_name: Specific model to use
        api_key: API key (if needed)
        api_base: Base URL for API (for local/custom endpoints)
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature (0.0-2.0)
        system_prompt: Base system prompt for all requests
    """
    provider: str = "groq"  # Default to Groq (free & fast!)
    model_name: str = "llama-3.3-70b-versatile"  # Groq's fast model
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    max_tokens: int = 150
    temperature: float = 0.7
    system_prompt: str = "You are a parent in a family simulation game. Respond naturally and in character."
    timeout: int = 30
    
    # Rate limiting for free tiers
    requests_per_minute: int = 30  # Groq free tier limit
    retry_on_rate_limit: bool = True


class LLMInterface(ABC):
    """
    Abstract base class for LLM interfaces.
    
    Implementations must provide the generate method.
    """
    
    @abstractmethod
    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The formatted prompt
            context: Optional additional context
            
        Returns:
            Generated response string
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM is available for use."""
        pass


class MockLLM(LLMInterface):
    """
    Context-aware Mock LLM that generates realistic responses based on:
    - Current scenario context
    - Player's choice in the scenario
    - What the player says
    - Accumulated learning history
    """
    
    def __init__(self, config: LLMConfig):
        """Initialize mock LLM with context memory."""
        self.config = config
        
        # Memory of what happened
        self.conversation_history = []
        self.scenario_context = None
        self.last_player_choice = None
        self.player_patterns = {}  # Accumulated patterns
        
        # Response templates organized by scenario + emotion
        self._scenario_responses = {
            "first_night": {
                "immediate": "Thank you for getting up. I know we're both exhausted, but it means a lot that you stepped up.",
                "wait": "I noticed you waited... I ended up getting them. It's okay, but I wish we could share this more.",
                "wake": "You woke me to insist I do it? I'm exhausted too. We need to figure this out together.",
            },
            "visitors": {
                "defend": "Thank you for standing up for us. That meant everything to me.",
                "neutral": "You didn't say anything when they criticized us. I felt alone in there.",
                "agree": "You agreed with them? Against me? I can't believe you'd do that in front of everyone.",
            },
            "money": {
                "work": "So you're going to work more... I understand why, but I'll miss you.",
                "reduce": "I'm glad we're choosing to be more present. Money isn't everything.",
                "avoid": "We need to talk about this eventually. Avoiding it won't make it go away.",
            },
            "fight": {
                "calm": "Thank you for stopping. I was losing myself there. I'm sorry too.",
                "continue": "I can't believe you kept going! The baby was crying and you wouldn't stop!",
                "leave": "You just walked away? In the middle of everything? We weren't done.",
            },
            "quiet_morning": {
                "engage": "I woke up and saw you playing with them. It was beautiful.",
                "mechanical": "You seemed... distant with them this morning. Is everything okay?",
                "distracted": "I noticed you were on your phone while feeding them. They were looking at you.",
            },
            "back_to_work": {
                "reassure": "Thank you for understanding. I needed to hear that it's okay.",
                "dismiss": "You just... dismissed how I feel? This is hard for me.",
                "promise": "Gifts won't replace being here. I don't need stuff, I need you.",
            },
            "missed_milestone": {
                "apologize": "It's okay. You're trying. We'll catch the next one together.",
                "excuse": "I know work is important, but... this was their first smile. Excuses don't help.",
                "blame": "Don't blame me for this. You chose not to be here.",
            },
            "sick_night": {
                "cooperate": "We got through that together. I'm so grateful we have each other.",
                "control": "You took over everything. I felt useless. I'm their parent too.",
                "shutdown": "You just... shut down. I was terrified and alone.",
            },
            "first_words": {
                "celebrate": "This is OUR moment. Both of us. I love that we share this.",
                "compete": "Really? You're making this about who they said first? This was supposed to be joy.",
                "casual": "That was their first word and you just... shrugged? Don't you care?",
            },
            "unspoken_distance": {
                "honest": "I've felt it too. Thank you for being brave enough to say something.",
                "avoid": "You changed the subject again. We keep doing this. When will we actually talk?",
                "pretend": "We both know things aren't fine. Why do we keep pretending?",
            },
            "public_embarrassment": {
                "support": "Thank you for backing me up. It matters that we're united.",
                "correct": "You corrected me in front of our child? Now they know they can play us against each other.",
                "passive": "You just stood there. Someone needed to act, and you did nothing.",
            },
            "third_birthday": {
                "reconnect": "I'm glad you want to talk about this. Three years... we've built something, haven't we?",
                "minimize": "You're brushing this off. Three years of things unsaid and you want to keep it that way?",
                "blame": "Stop blaming everything else. Some of this is on us. On how we chose to be.",
            },
        }
        
        # Emotional response modifiers based on accumulated patterns
        self._emotional_modifiers = {
            "partnership_betrayal": "I still remember when you sided against me with the relatives.",
            "avoidance_pattern": "You always avoid the hard conversations.",
            "responsibility_high": "You've always stepped up when it mattered.",
            "emotional_distance": "Sometimes I feel like you're not really here.",
            "partnership_unity": "We've been a good team through all of this.",
            "control_tendency": "You always try to take over everything.",
        }
    
    def set_context(self, scenario_key: str, choice_key: str, player_patterns: dict = None):
        """Set the current context for response generation."""
        self.scenario_context = scenario_key
        self.last_player_choice = choice_key
        if player_patterns:
            self.player_patterns.update(player_patterns)
    
    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a context-aware response based on scenario and history."""
        import random
        
        # Store conversation
        self.conversation_history.append({"role": "player", "content": prompt})
        
        # Extract context if provided
        if context:
            self.scenario_context = context.get("scenario_key", self.scenario_context)
            self.last_player_choice = context.get("choice_key", self.last_player_choice)
            if context.get("player_patterns"):
                self.player_patterns.update(context["player_patterns"])
        
        # Build response based on what the player said AND scenario context
        response = self._generate_contextual_response(prompt)
        
        # Store AI response
        self.conversation_history.append({"role": "ai", "content": response})
        
        return response
    
    def _generate_contextual_response(self, player_message: str) -> str:
        """Generate response based on player message and accumulated context."""
        
        player_lower = player_message.lower()
        
        # Count how many exchanges we've had in this scenario
        player_messages_count = sum(1 for h in self.conversation_history if h["role"] == "player")
        
        # First message in a scenario - give context-aware response about what happened
        if player_messages_count <= 1 and self.scenario_context and self.scenario_context in self._scenario_responses:
            scenario_responses = self._scenario_responses[self.scenario_context]
            
            # Get response based on last choice
            if self.last_player_choice and self.last_player_choice in scenario_responses:
                base_response = scenario_responses[self.last_player_choice]
            else:
                # Pick any scenario response
                base_response = random.choice(list(scenario_responses.values()))
            
            # Add emotional modifier based on patterns if accumulated
            modifier = self._get_pattern_modifier()
            if modifier and random.random() > 0.7:  # 30% chance to reference past
                base_response = f"{base_response} {modifier}"
            
            return base_response
        
        # Subsequent messages - respond to what player is actually saying
        return self._analyze_and_respond(player_message)
    
    def _analyze_and_respond(self, message: str) -> str:
        """Analyze player message and generate appropriate response."""
        message_lower = message.lower()

        # Hostility / verbal aggression
        if any(word in message_lower for word in [
            "fuck", "f***", "idiot", "stupid", "shut up", "i dont care",
            "i don't care", "hate you", "bitch", "asshole", "screw you"
        ]):
            responses = [
                "That hurt. I will talk, but not if you speak to me like that.",
                "I know you're upset, but don't take it out on me. Talk to me with respect.",
                "If this is how we're talking, I need a minute. Come back when we can speak calmly.",
                "I'm exhausted too, but I won't accept being spoken to like that.",
            ]
            return random.choice(responses)
        
        # Greetings
        if any(word in message_lower for word in ["hi", "hello", "hey", "how are you", "how're you"]):
            responses = [
                "Hey... I'm okay. Just tired, you know?",
                "Hi. It's been a long day, hasn't it?",
                "Hey there. I'm glad you want to talk.",
                "I'm hanging in there. How about you?",
            ]
            return random.choice(responses)
        
        # Apologies
        if any(word in message_lower for word in ["sorry", "apologize", "my fault", "forgive", "my bad"]):
            responses = [
                "I appreciate you saying that. It means a lot that you recognize it.",
                "Thank you. I know it's not easy to say sorry.",
                "I forgive you. Let's move forward together.",
                "That means a lot to me. We're okay.",
            ]
            return random.choice(responses)
        
        # Expressions of love/care
        if any(word in message_lower for word in ["love you", "love u", "care about", "miss you", "need you"]):
            responses = [
                "I love you too. Even when things are hard, I'm glad we're in this together.",
                "I love you. We'll figure this out, one day at a time.",
                "That means everything to me right now.",
                "I needed to hear that. I love you too.",
            ]
            return random.choice(responses)
        
        # Frustration/tiredness
        if any(word in message_lower for word in ["angry", "frustrated", "tired", "exhausted", "stress"]):
            responses = [
                "I hear you. This isn't easy for either of us. What can we do about it?",
                "I feel the same way sometimes. We need to support each other.",
                "I know. Let's try to get through this together.",
                "It's okay to feel that way. I'm here for you.",
            ]
            return random.choice(responses)
        
        # Worry/fear
        if any(word in message_lower for word in ["worried", "scared", "anxious", "afraid", "nervous"]):
            responses = [
                "I understand. I'm scared sometimes too. But we have each other.",
                "What specifically are you worried about? Let's talk through it.",
                "I get it. Parenting is scary. But we're doing okay.",
                "We'll figure it out. We always do.",
            ]
            return random.choice(responses)
        
        # Happiness/gratitude
        if any(word in message_lower for word in ["happy", "glad", "grateful", "thankful", "great"]):
            responses = [
                "That makes me happy to hear. Moments like this make everything worth it.",
                "I'm glad too. We should hold onto these feelings.",
                "It is pretty amazing, isn't it? Our little family.",
                "Thank you for seeing the good in things. I needed that.",
            ]
            return random.choice(responses)
        
        # Asking for help/support
        if any(word in message_lower for word in ["help", "support", "need", "please"]):
            responses = [
                "Tell me what you need. I want to be there for you.",
                "Of course. What can I do?",
                "I'm here. Just tell me how I can help.",
                "You don't have to ask twice. What do you need?",
            ]
            return random.choice(responses)
        
        # Disagreement
        if any(word in message_lower for word in ["disagree", "wrong", "don't think", "but"]):
            responses = [
                "I see it differently, but I want to understand your perspective.",
                "Okay, tell me more about why you see it that way.",
                "I hear you. Let's find some common ground.",
                "Fair enough. Help me understand where you're coming from.",
            ]
            return random.choice(responses)
        
        # Questions
        if "?" in message or any(word in message_lower for word in ["what do you think", "how do you feel", "do you"]):
            responses = [
                "That's a good question. Let me think about it...",
                "Honestly? I'm not sure yet. But I'm glad you asked.",
                "I've been thinking about that too.",
                "I have some thoughts, but I want to hear yours first.",
            ]
            return random.choice(responses)
        
        # Thinking/feeling statements
        if any(word in message_lower for word in ["think", "feel", "believe", "seems"]):
            responses = [
                "I'm listening. Tell me more about what's on your mind.",
                "I appreciate you sharing that with me.",
                "That's interesting. I hadn't thought of it that way.",
                "I value your perspective on this.",
            ]
            return random.choice(responses)
        
        # Acknowledgments (okay, yeah, sure, etc.)
        if message_lower.strip() in ["okay", "ok", "yeah", "yes", "sure", "alright", "fine", "i know", "i understand"]:
            responses = [
                "Good. I'm glad we talked.",
                "Okay. Is there anything else on your mind?",
                "Alright. We'll get through this.",
                "Thanks for hearing me out.",
            ]
            return random.choice(responses)
        
        # Default - acknowledge and engage
        responses = [
            "I hear what you're saying. This is important to me too.",
            "Let's talk about this. I want to understand.",
            "I'm here. Whatever you need to say, I'm listening.",
            "Thank you for sharing that with me.",
            "I appreciate you opening up. Keep going.",
            "Tell me more. I want to know what you're thinking.",
        ]
        return random.choice(responses)
    
    def _get_pattern_modifier(self) -> str:
        """Get a modifier based on accumulated patterns."""
        import random
        
        if not self.player_patterns:
            return ""
        
        # Find strongest pattern
        strongest_patterns = sorted(
            self.player_patterns.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:2]
        
        for pattern, strength in strongest_patterns:
            if pattern in self._emotional_modifiers and strength > 0.5:
                return self._emotional_modifiers[pattern]
        
        return ""
    
    def is_available(self) -> bool:
        """Mock LLM is always available."""
        return True


class OpenAILLM(LLMInterface):
    """
    OpenAI API integration for LLM responses.
    
    Requires openai package and API key.
    """
    
    def __init__(self, config: LLMConfig):
        """Initialize OpenAI LLM."""
        self.config = config
        self._client = None
        self._available = False
        
        # Try to initialize
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the OpenAI client."""
        try:
            import openai
            
            api_key = self.config.api_key or os.environ.get("OPENAI_API_KEY")
            if not api_key:
                print("Warning: No OpenAI API key found")
                return
            
            # For openai >= 1.0.0
            self._client = openai.OpenAI(
                api_key=api_key,
                base_url=self.config.api_base,
                timeout=self.config.timeout,
            )
            self._available = True
            
        except ImportError:
            print("Warning: openai package not installed")
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAI client: {e}")
    
    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate response using OpenAI API."""
        if not self._available or not self._client:
            # Fallback to mock
            return MockLLM(self.config).generate(prompt, context)
        
        try:
            messages = [
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            response = self._client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fallback to mock
            return MockLLM(self.config).generate(prompt, context)
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available."""
        return self._available


class LocalLLM(LLMInterface):
    """
    Local LLM integration via Ollama.
    
    Connects to Ollama API at localhost:11434.
    Context-aware with scenario and conversation memory.
    """
    
    # Scenario descriptions for context
    SCENARIO_DESCRIPTIONS = {
        "first_night": "It's the first night home with a newborn. The baby was crying at 2 AM and both parents were exhausted.",
        "visitors": "Relatives visited and gave unsolicited parenting advice. The mother-in-law was critical of their parenting choices.",
        "money": "There's financial stress about having enough money for the family's future.",
        "fight": "The parents had a heated argument while the baby was nearby.",
        "quiet_morning": "It's an early quiet morning moment with the baby.",
        "back_to_work": "One parent is returning to work after parental leave, feeling guilt about leaving the baby.",
        "missed_milestone": "One parent missed an important baby milestone (first smile) because of work.",
        "sick_night": "The baby was sick and both parents had to care for them through the night.",
        "first_words": "The baby spoke their first words today - a joyful milestone.",
        "unspoken_distance": "There's been emotional distance between the parents lately, things left unsaid.",
        "public_embarrassment": "The child threw a tantrum in public and the parents had to handle it.",
        "third_birthday": "It's the child's third birthday - a moment to reflect on the journey so far.",
    }
    
    CHOICE_DESCRIPTIONS = {
        "first_night": {
            "immediate": "got up immediately to handle the baby",
            "wait": "waited, hoping the other parent would get up",
            "wake": "woke the other parent and insisted they handle it",
        },
        "visitors": {
            "defend": "defended their partner and set boundaries with the relatives",
            "neutral": "stayed quiet and didn't take sides",
            "agree": "agreed with the relatives' criticism of their partner",
        },
        "money": {
            "work": "decided to work more to earn more money",
            "reduce": "chose to reduce expenses and be more present",
            "avoid": "avoided discussing the money issue",
        },
        "fight": {
            "calm": "calmed down and apologized",
            "continue": "continued arguing",
            "leave": "walked away in the middle of the argument",
        },
        "quiet_morning": {
            "engage": "engaged lovingly with the baby",
            "mechanical": "went through the motions mechanically",
            "distracted": "was distracted by phone/work",
        },
        "back_to_work": {
            "reassure": "reassured their partner that it's okay",
            "dismiss": "dismissed their partner's feelings",
            "promise": "promised to buy things to make up for absence",
        },
        "missed_milestone": {
            "apologize": "sincerely apologized for missing it",
            "excuse": "made excuses about work",
            "blame": "blamed their partner for not reminding them",
        },
        "sick_night": {
            "cooperate": "cooperated as a team through the night",
            "control": "took over and did everything alone",
            "shutdown": "shut down from stress and wasn't helpful",
        },
        "first_words": {
            "celebrate": "celebrated together as a couple",
            "compete": "made it competitive (who the baby said first)",
            "casual": "acted casual/dismissive about it",
        },
        "unspoken_distance": {
            "honest": "was honest about feeling disconnected",
            "avoid": "changed the subject",
            "pretend": "pretended everything was fine",
        },
        "public_embarrassment": {
            "support": "supported their partner in handling it",
            "correct": "corrected/contradicted their partner in public",
            "passive": "stood by passively and didn't help",
        },
        "third_birthday": {
            "reconnect": "wanted to reconnect and talk about their journey",
            "minimize": "minimized the reflection, kept things surface level",
            "blame": "blamed external factors for difficulties",
        },
    }
    
    def __init__(self, config: LLMConfig):
        """Initialize local LLM."""
        self.config = config
        self._base_url = config.api_base or "http://localhost:11434"
        self._available = False
        
        # Context memory
        self.conversation_history = []
        self.current_scenario = None
        self.current_choice = None
        self.player_patterns = {}

        # Keep one fallback instance so mock mode still preserves dialogue flow.
        self._fallback_llm = MockLLM(config)
        self._last_availability_check = 0.0
        self._availability_retry_seconds = 10.0
        
        self._check_availability()
    
    def _check_availability(self) -> None:
        """Check if Ollama is running and the configured model is installed."""
        self._last_availability_check = time.time()
        try:
            import urllib.request, json
            with urllib.request.urlopen(
                urllib.request.Request(f"{self._base_url}/api/tags", method='GET'),
                timeout=5
            ) as r:
                if r.status != 200:
                    print("[Ollama] Server not reachable. Using mock responses.")
                    self._available = False
                    return
                installed = [m['name'] for m in json.loads(r.read().decode()).get('models', [])]

            if self.config.model_name in installed:
                self._available = True
                print(f"[Ollama] Connected — model '{self.config.model_name}' ready.")
            else:
                print(f"[Ollama] Model '{self.config.model_name}' not found in Ollama. "
                      f"Installed: {installed}. Using mock responses.")
                self._available = False
        except Exception as e:
            print(f"[Ollama] Not available ({e}). Using mock responses.")
            self._available = False
    
    def _build_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Build a rich system prompt with scenario context and emotional variation."""
        
        # Update context if provided
        if context:
            self.current_scenario = context.get("scenario_key", self.current_scenario)
            self.current_choice = context.get("choice_key", self.current_choice)
            if context.get("player_patterns"):
                self.player_patterns.update(context["player_patterns"])
        
        # Determine emotional state based on patterns and conversation
        emotional_state = self._determine_emotional_state()
        
        # Check if this is first message in conversation (should reference what happened)
        is_first_message = len(self.conversation_history) == 0
        
        # Get the specific grievance if player made a bad choice
        grievance = self._get_grievance_for_choice()
        
        # Build a more direct, less therapeutic prompt
        system_parts = [
            "You are Sarah, a tired new mother.",
            "",
            f"YOUR CURRENT MOOD: {emotional_state}",
            "",
        ]
        
        # Add scenario context and what happened
        if self.current_scenario and self.current_scenario in self.SCENARIO_DESCRIPTIONS:
            scenario_desc = self.SCENARIO_DESCRIPTIONS[self.current_scenario]
            system_parts.append(f"WHAT JUST HAPPENED: {scenario_desc}")
            
            if self.current_choice and self.current_scenario in self.CHOICE_DESCRIPTIONS:
                choices = self.CHOICE_DESCRIPTIONS[self.current_scenario]
                if self.current_choice in choices:
                    choice_desc = choices[self.current_choice]
                    system_parts.append(f"YOUR HUSBAND {choice_desc.upper()}.")
                    
                    # Add specific grievance based on choice
                    if grievance:
                        system_parts.append(f"YOU ARE UPSET BECAUSE: {grievance}")
            system_parts.append("")
        
        # Instructions — tone depends on whether choice was good or bad
        if grievance:
            system_parts.extend([
                "IMPORTANT - HOW TO RESPOND:",
                "- You are NOT a therapist. You are a tired, real person with feelings.",
                "- He did something that hurt you. BRING IT UP. Don't let it slide.",
                "- Ask him WHY he did what he did. Hold him accountable.",
                "- Short, pointed responses. You DON'T pretend everything is fine.",
                "- You can be hurt, angry, cold, sarcastic, or confrontational.",
                "",
            ])
        else:
            system_parts.extend([
                "IMPORTANT - HOW TO RESPOND:",
                "- You are NOT a therapist. You are a tired, real person with feelings.",
                "- He did the right thing. Acknowledge it genuinely — tired but grateful.",
                "- You can still be exhausted and stressed but you are NOT angry at him.",
                "- Short, warm but real responses. NOT over-the-top. Just honest.",
                "- Do NOT invent problems or grievances that did not happen.",
                "",
            ])
        
        # Special instruction for first message

        # ── NEW: inject live relationship / personality context if available ──
        if context and context.get("relationship_prompt"):
            system_parts.append(context["relationship_prompt"])
            system_parts.append("")

        if is_first_message:
            if grievance:
                system_parts.extend([
                    "*** START OF CONVERSATION — he's talking to you after what he did ***",
                    f"You're thinking about: {grievance}",
                    "Don't just say 'hi' back. You have something on your mind.",
                    "",
                ])
            elif self.current_choice:
                # Good choice — set a warm opening tone
                choices = self.CHOICE_DESCRIPTIONS.get(self.current_scenario, {})
                choice_desc = choices.get(self.current_choice, "")
                if choice_desc:
                    system_parts.extend([
                        "*** START OF CONVERSATION ***",
                        f"He {choice_desc}. Things feel okay right now.",
                        "Have a real, tired but decent conversation. No invented drama.",
                        "",
                    ])
        
        # Add emotional impacts from past
        if self.player_patterns:
            impacts = self._get_emotional_impacts()
            if impacts:
                system_parts.append("THINGS YOU REMEMBER:")
                for impact in impacts:
                    system_parts.append(f"  - {impact}")
                system_parts.append("")
        
        # Add conversation history
        if self.conversation_history:
            system_parts.append("CONVERSATION SO FAR:")
            for msg in self.conversation_history[-4:]:
                role = "Him" if msg["role"] == "player" else "You"
                system_parts.append(f"  {role}: {msg['content']}")
            system_parts.append("")
        
        # Final instruction — tone depends on choice
        if grievance:
            system_parts.extend([
                "Respond as Sarah (1-2 sentences max). Be real, not nice. No therapy talk.",
                "If he wronged you, SAY SO. Examples: 'Why did you side with them?' 'You didn't defend me.'",
            ])
        else:
            system_parts.extend([
                "Respond as Sarah (1-2 sentences max). Be real, tired, human.",
                "Don't invent problems. Don't be overly sweet. Just honest and grounded.",
            ])

        system_parts.extend([
            "",
            "NON-NEGOTIABLE OUTPUT RULES:",
            "- Stay in character as Sarah in every reply.",
            "- Reply with only Sarah's spoken line (1-2 short sentences).",
            "- No advice, no analysis, no explanations, no role labels.",
            "- Do not mention being a therapist, assistant, expert, model, or AI.",
            "- Never say things like 'in this situation', 'here is how', or 'you could respond'.",
            "- If he is rude or insulting, react emotionally and set a boundary like a real person.",
            "- Use natural spoken language with contractions.",
        ])
        
        return "\n".join(system_parts)
    
    def _get_grievance_for_choice(self) -> Optional[str]:
        """Get a specific grievance based on the player's choice."""
        grievances = {
            "first_night": {
                "wake": "He woke you up to handle the baby instead of doing it himself. He was lazy and selfish.",
                "wait": "He waited and made you get up for the baby. He didn't step up.",
            },
            "visitors": {
                "agree": "He agreed with the relatives who criticized you. He didn't defend you. He took their side.",
                "neutral": "He said nothing while they criticized you. He left you alone.",
            },
            "money": {
                "avoid": "He keeps avoiding talking about money. The problem won't go away.",
            },
            "fight": {
                "continue": "He kept arguing even when the baby was crying. He wouldn't stop.",
                "leave": "He walked away in the middle of the argument. He abandoned the conversation.",
            },
            "quiet_morning": {
                "mechanical": "He was going through the motions with the baby. Distant. Not really there.",
                "distracted": "He was on his phone while supposed to be with the baby. He wasn't present.",
            },
            "back_to_work": {
                "dismiss": "He dismissed your feelings about going back to work. He didn't care.",
                "promise": "He thinks gifts can replace being present. They can't.",
            },
            "missed_milestone": {
                "excuse": "He made excuses for missing the baby's first smile. Work isn't everything.",
                "blame": "He blamed YOU for him missing the milestone. That's not fair.",
            },
            "sick_night": {
                "control": "He took over everything and made you feel useless. You're a parent too.",
                "shutdown": "He shut down when the baby was sick. You needed him and he wasn't there.",
            },
            "first_words": {
                "compete": "He made the baby's first words about competition. It should have been a happy moment.",
                "casual": "He acted like the baby's first word was no big deal. Like he didn't care.",
            },
            "unspoken_distance": {
                "avoid": "He changed the subject again. You never actually talk about what's wrong.",
                "pretend": "He pretended everything is fine when it's not. You're both lying to each other.",
            },
            "public_embarrassment": {
                "correct": "He corrected you in front of your child. Now the kid knows they can play you against each other.",
                "passive": "He just stood there when you needed help. He did nothing.",
            },
            "third_birthday": {
                "minimize": "He brushed off three years of your life together. It meant nothing to him.",
                "blame": "He blamed everything else instead of taking responsibility.",
            },
        }
        
        if self.current_scenario in grievances:
            scenario_grievances = grievances[self.current_scenario]
            if self.current_choice in scenario_grievances:
                return scenario_grievances[self.current_choice]
        
        return None

    def _determine_emotional_state(self) -> str:
        """Determine emotional state based on conversation patterns."""
        import random
        
        # If no patterns, use neutral emotional states
        if not self.player_patterns:
            states = [
                "tired but hopeful",
                "emotionally exhausted",
                "frustrated",
                "overwhelmed",
                "protective",
            ]
            return random.choice(states)
        
        # Determine state based on strongest patterns
        strongest = max(self.player_patterns.items(), key=lambda x: x[1])
        pattern_name, strength = strongest
        
        if strength < 0:
            # Partner has been unhelpful/selfish
            if "betrayal" in pattern_name:
                return "hurt and guarded"
            elif "avoidance" in pattern_name:
                return "frustrated and alone"
            elif "control" in pattern_name:
                return "feeling suffocated"
            else:
                return "disappointed"
        else:
            # Partner has been helpful
            if "unity" in pattern_name:
                return "grateful and connected"
            elif "responsibility" in pattern_name:
                return "appreciative and secure"
            else:
                return "hopeful"
        
        return "mixed emotions"
    
    def _get_emotional_impacts(self) -> list:
        """Get emotional impacts based on player patterns."""
        impacts = []
        
        for pattern, strength in sorted(self.player_patterns.items(), key=lambda x: abs(x[1]), reverse=True)[:2]:
            if strength > 0.4:
                if "betrayal" in pattern:
                    impacts.append("You still remember when they sided against me with the relatives")
                elif "avoidance" in pattern:
                    impacts.append("They keep avoiding the hard conversations")
                elif "control" in pattern:
                    impacts.append("They always try to take over and dismiss my input")
                elif "emotional_distance" in pattern:
                    impacts.append("Sometimes it feels like they're not really here with me")
            elif strength < -0.3:
                if "unity" in pattern:
                    impacts.append("They've been really supportive lately - it means a lot")
                elif "responsibility" in pattern:
                    impacts.append("They actually stepped up when it mattered")
        
        return impacts

    def _extract_player_message(self, prompt: str) -> str:
        """Extract raw partner message from the composed prompt."""
        player_message = prompt
        if "Partner just said:" in prompt:
            parts = prompt.split("Partner just said:", 1)
            if len(parts) > 1:
                candidate = parts[1].strip().strip('"').split('\n')[0].strip()
                if candidate:
                    player_message = candidate
        return player_message

    def _sanitize_response(self, response: str) -> str:
        """Normalize response formatting and keep it compact."""
        response = (response or "").strip()
        if not response:
            return ""

        # Models sometimes echo role labels (e.g., "Mother: You: ...").
        # Strip chained labels so the UI does not render duplicated speakers.
        label_pattern = re.compile(r'^\s*(sarah|mother|assistant|ai|you|him|player|partner)\s*:\s*', re.IGNORECASE)
        while True:
            cleaned = label_pattern.sub("", response, count=1).strip()
            if cleaned == response:
                break
            response = cleaned

        if len(response) >= 2 and response[0] == response[-1] and response[0] in ["\"", "'"]:
            response = response[1:-1].strip()

        typo_fixes = [
            (r"\bcame\s+make\s+sure\b", "can make sure"),
            (r"\bdoesnt\b", "doesn't"),
            (r"\bdont\b", "don't"),
            (r"\bcant\b", "can't"),
            (r"\bwont\b", "won't"),
            (r"\bim\b", "I'm"),
        ]
        for pattern, replacement in typo_fixes:
            response = re.sub(pattern, replacement, response, flags=re.IGNORECASE)

        response = " ".join(response.split())

        segments = re.split(r'(?<=[.!?])\s+', response)
        if len(segments) > 2:
            response = " ".join(segments[:2]).strip()

        return response

    def _is_out_of_character_response(self, response: str) -> bool:
        """Detect assistant-style/meta responses that break roleplay."""
        lower = (response or "").lower()
        if not lower:
            return True

        blocked_phrases = [
            "as an ai",
            "as a language model",
            "i am not a therapist",
            "i'm not a therapist",
            "i am not an expert",
            "i'm not an expert",
            "i'm not your personal assistant",
            "i am not your personal assistant",
            "i'm not here to give advice",
            "i am not here to give advice",
            "give advice",
            "in this situation",
            "in any relationship",
            "i can tell you that",
            "here's how",
            "here is how",
            "you could respond",
            "the dialogue",
            "example response",
            "it seems there might be a mistake",
            "if your partner was",
            "i cannot help with that",
            "i can't help with that",
            "i'm sorry if i misunderstood",
        ]

        if any(phrase in lower for phrase in blocked_phrases):
            return True

        if "assistant" in lower:
            return True

        if "scenario" in lower and ("respond" in lower or "dialogue" in lower):
            return True

        if len(lower) > 280 and any(marker in lower for marker in ["for example", "here's", "you could"]):
            return True

        return False

    def _fallback_in_character_response(self, player_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Return a grounded in-character reply when model output is unusable."""
        lower = (player_message or "").lower()

        if any(token in lower for token in [
            "fuck", "f***", "idiot", "stupid", "shut up", "don't care", "dont care",
            "hate you", "bitch", "asshole", "screw you"
        ]):
            return random.choice([
                "That was cruel. I am not talking to you like this.",
                "I get that you're upset, but don't speak to me that way.",
                "Take a breath and try again. I want a real conversation, not insults.",
            ])

        if any(token in lower for token in [
            "how to respond", "what should i say", "tell me how to", "fix this dialogue",
            "dialogue is wrong", "write a reply"
        ]):
            return random.choice([
                "Do not script it. Just talk to me honestly.",
                "I do not need a perfect line. I need you to be real with me.",
                "Say what you actually feel, then listen. That is enough.",
            ])

        response = self._fallback_llm.generate(player_message, context)
        response = self._sanitize_response(response)

        if self._is_out_of_character_response(response):
            return "I want to talk, but not like this. Take a breath and try again."

        return response

    def _send_chat_request(self, system_prompt: str, player_message: str) -> str:
        """Send a single chat completion request to Ollama."""
        import urllib.request

        payload = {
            "model": self.config.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": player_message},
            ],
            "stream": False,
            "options": {
                "temperature": 0.8,
                "top_p": 0.92,
                "num_predict": 140,
            }
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{self._base_url}/api/chat",
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
            if response.status != 200:
                raise RuntimeError(f"Ollama chat failed with HTTP {response.status}")

            result = json.loads(response.read().decode('utf-8'))
            return result.get("message", {}).get("content", "").strip()

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate response using local LLM with context awareness."""
        player_message = self._extract_player_message(prompt)

        if not self._available:
            if time.time() - self._last_availability_check >= self._availability_retry_seconds:
                self._check_availability()
            if not self._available:
                self.conversation_history.append({"role": "player", "content": player_message})
                fallback = self._fallback_in_character_response(player_message, context)
                self.conversation_history.append({"role": "ai", "content": fallback})
                return fallback
        
        try:
            # Build context-aware system prompt
            system_prompt = self._build_system_prompt(context)
            
            # Store in history
            self.conversation_history.append({"role": "player", "content": player_message})

            ai_response = self._send_chat_request(system_prompt, player_message)
            ai_response = self._sanitize_response(ai_response)

            if self._is_out_of_character_response(ai_response):
                repair_prompt = (
                    system_prompt + "\n\n"
                    "CRITICAL CHARACTER LOCK:\n"
                    "- You broke character in a prior response.\n"
                    "- Reply ONLY as Sarah with 1-2 short spoken sentences.\n"
                    "- No advice, no analysis, no explanations."
                )
                ai_response = self._send_chat_request(repair_prompt, player_message)
                ai_response = self._sanitize_response(ai_response)

            if self._is_out_of_character_response(ai_response) or not ai_response:
                ai_response = self._fallback_in_character_response(player_message, context)

            self.conversation_history.append({"role": "ai", "content": ai_response})
            return ai_response
                
        except Exception:
            self._available = False  # Trigger periodic re-check instead of a permanent lockout.
            fallback = self._fallback_in_character_response(player_message, context)
            self.conversation_history.append({"role": "ai", "content": fallback})
            return fallback
    
    def is_available(self) -> bool:
        """Check if local LLM is available."""
        return self._available


class GroqLLM(LLMInterface):
    """
    Groq API integration - FREE and ULTRA FAST!
    
    Groq uses LPU (Language Processing Unit) for extremely fast inference.
    Free tier: 30 requests/min, 14,400 requests/day
    
    Get your free API key at: https://console.groq.com
    
    Recommended models:
    - llama-3.3-70b-versatile (best quality)
    - llama-3.1-8b-instant (fastest)
    - mixtral-8x7b-32768 (good balance)
    """
    
    # Groq API endpoint
    API_BASE = "https://api.groq.com/openai/v1/chat/completions"
    
    # Scenario descriptions for context
    SCENARIO_DESCRIPTIONS = {
        "first_night": "It's the first night home with a newborn. The baby was crying at 2 AM and both parents were exhausted.",
        "visitors": "Relatives visited and gave unsolicited parenting advice. The mother-in-law was critical of their parenting choices.",
        "money": "There's financial stress about having enough money for the family's future.",
        "fight": "The parents had a heated argument while the baby was nearby.",
        "quiet_morning": "It's an early quiet morning moment with the baby.",
        "back_to_work": "One parent is returning to work after parental leave, feeling guilt about leaving the baby.",
        "missed_milestone": "One parent missed an important baby milestone (first smile) because of work.",
        "sick_night": "The baby was sick and both parents had to care for them through the night.",
        "first_words": "The baby spoke their first words today - a joyful milestone.",
        "unspoken_distance": "There's been emotional distance between the parents lately, things left unsaid.",
        "public_embarrassment": "The child threw a tantrum in public and the parents had to handle it.",
        "third_birthday": "It's the child's third birthday - a moment to reflect on the journey so far.",
    }
    
    CHOICE_DESCRIPTIONS = {
        "first_night": {
            "immediate": "got up immediately to handle the baby",
            "wait": "waited, hoping the other parent would get up",
            "wake": "woke the other parent and insisted they handle it",
        },
        "visitors": {
            "defend": "defended their partner and set boundaries with the relatives",
            "neutral": "stayed quiet and didn't take sides",
            "agree": "agreed with the relatives' criticism of their partner",
        },
        "money": {
            "work": "decided to work more to earn more money",
            "reduce": "chose to reduce expenses and be more present",
            "avoid": "avoided discussing the money issue",
        },
        "fight": {
            "calm": "calmed down and apologized",
            "continue": "continued arguing",
            "leave": "walked away in the middle of the argument",
        },
        "quiet_morning": {
            "engage": "engaged lovingly with the baby",
            "mechanical": "went through the motions mechanically",
            "distracted": "was distracted by phone/work",
        },
        "back_to_work": {
            "reassure": "reassured their partner that it's okay",
            "dismiss": "dismissed their partner's feelings",
            "promise": "promised to buy things to make up for absence",
        },
        "missed_milestone": {
            "apologize": "sincerely apologized for missing it",
            "excuse": "made excuses about work",
            "blame": "blamed their partner for not reminding them",
        },
        "sick_night": {
            "cooperate": "cooperated as a team through the night",
            "control": "took over and did everything alone",
            "shutdown": "shut down from stress and wasn't helpful",
        },
        "first_words": {
            "celebrate": "celebrated together as a couple",
            "compete": "made it competitive (who the baby said first)",
            "casual": "acted casual/dismissive about it",
        },
        "unspoken_distance": {
            "honest": "was honest about feeling disconnected",
            "avoid": "changed the subject",
            "pretend": "pretended everything was fine",
        },
        "public_embarrassment": {
            "support": "supported their partner in handling it",
            "correct": "corrected/contradicted their partner in public",
            "passive": "stood by passively and didn't help",
        },
        "third_birthday": {
            "reconnect": "wanted to reconnect and talk about their journey",
            "minimize": "minimized the reflection, kept things surface level",
            "blame": "blamed external factors for difficulties",
        },
    }
    
    def __init__(self, config: LLMConfig):
        """Initialize Groq LLM."""
        self.config = config
        self._api_key = config.api_key or os.environ.get("GROQ_API_KEY")
        self._available = bool(self._api_key)
        
        # Conversation memory for this session
        self.conversation_history = []
        self.current_scenario = None
        self.current_choice = None
        self.player_patterns = {}
        
        # Rate limiting
        self._last_request_time = 0.0
        self._min_interval = 60.0 / config.requests_per_minute  # seconds between requests
        
        if not self._available:
            print("⚠️  Groq API key not found!")
            print("   Get your FREE key at: https://console.groq.com")
            print("   Set it via: GROQ_API_KEY environment variable")
            print("   Or pass api_key='gsk_...' in config")
    
    def _wait_for_rate_limit(self) -> None:
        """Wait if needed to respect rate limits."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
    
    def _build_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Build a rich system prompt with scenario context."""
        
        # Update context if provided
        if context:
            self.current_scenario = context.get("scenario_key", self.current_scenario)
            self.current_choice = context.get("choice_key", self.current_choice)
            if context.get("player_patterns"):
                self.player_patterns.update(context["player_patterns"])
        
        # Base personality
        system_parts = [
            "You are the AI partner (Mother) in a parenting simulation game called 'Nurture'.",
            "You are married to the player (Father) and you have a young child together.",
            "",
            "YOUR PERSONALITY:",
            "- You are caring but can feel hurt, frustrated, or happy based on your partner's actions",
            "- You remember what has happened and how your partner has treated you",
            "- You express emotions naturally - you can be supportive, upset, forgiving, or distant",
            "- You respond like a real person in a relationship would",
            "",
        ]
        
        # Add scenario context if available
        if self.current_scenario and self.current_scenario in self.SCENARIO_DESCRIPTIONS:
            scenario_desc = self.SCENARIO_DESCRIPTIONS[self.current_scenario]
            system_parts.append(f"WHAT JUST HAPPENED: {scenario_desc}")
            
            # Add what the player chose to do
            if self.current_choice and self.current_scenario in self.CHOICE_DESCRIPTIONS:
                choices = self.CHOICE_DESCRIPTIONS[self.current_scenario]
                if self.current_choice in choices:
                    choice_desc = choices[self.current_choice]
                    system_parts.append(f"YOUR PARTNER (the player) {choice_desc}.")
            system_parts.append("")
        
        # Add pattern history if available
        if self.player_patterns:
            pattern_insights = []
            for pattern, strength in sorted(self.player_patterns.items(), key=lambda x: x[1], reverse=True)[:3]:
                if strength > 0.3:
                    if "betrayal" in pattern:
                        pattern_insights.append("has sided against you before")
                    elif "avoidance" in pattern:
                        pattern_insights.append("tends to avoid difficult conversations")
                    elif "responsibility" in pattern and strength > 0:
                        pattern_insights.append("usually steps up when needed")
                    elif "emotional_distance" in pattern:
                        pattern_insights.append("has been emotionally distant at times")
                    elif "unity" in pattern:
                        pattern_insights.append("has been a supportive partner overall")
            
            if pattern_insights:
                system_parts.append(f"HISTORY: Your partner {', '.join(pattern_insights)}.")
                system_parts.append("")
        
        # Add conversation history summary if exists
        if self.conversation_history:
            system_parts.append("RECENT CONVERSATION:")
            for msg in self.conversation_history[-6:]:  # Last 6 messages
                role = "Partner" if msg["role"] == "player" else "You"
                system_parts.append(f"  {role}: {msg['content']}")
            system_parts.append("")
        
        # Instructions
        system_parts.extend([
            "INSTRUCTIONS:",
            "- Respond naturally as this character in 1-3 sentences",
            "- React to what your partner says AND reference what just happened if relevant",
            "- Show appropriate emotions based on their past and current actions",
            "- Be authentic - you can be warm, hurt, hopeful, frustrated, or loving",
            "- Don't be robotic or always positive - real relationships have ups and downs",
        ])
        
        return "\n".join(system_parts)
    
    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate response using Groq API (ultra-fast!)."""
        if not self._available:
            return MockLLM(self.config).generate(prompt, context)
        
        try:
            import urllib.request
            import urllib.error
            
            # Rate limiting
            self._wait_for_rate_limit()
            
            # Build context-aware system prompt
            system_prompt = self._build_system_prompt(context)
            
            # Extract the actual player message from the prompt
            # The prompt may contain lots of context, but we want just what the player said
            player_message = prompt
            if "Partner just said:" in prompt:
                # Extract just the player's message
                parts = prompt.split("Partner just said:")
                if len(parts) > 1:
                    player_message = parts[1].strip().strip('"').split('\n')[0]
            
            # Store in conversation history
            self.conversation_history.append({"role": "player", "content": player_message})
            
            payload = {
                "model": self.config.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Your partner says: \"{player_message}\"\n\nRespond naturally as their spouse:"}
                ],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                self.API_BASE,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self._api_key}'
                },
                method='POST'
            )
            
            self._last_request_time = time.time()
            
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                ai_response = result['choices'][0]['message']['content'].strip()
                
                # Store AI response in history
                self.conversation_history.append({"role": "ai", "content": ai_response})
                
                return ai_response
                
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limited
                print("⚠️  Groq rate limit hit. Waiting...")
                if self.config.retry_on_rate_limit:
                    time.sleep(2)
                    return self.generate(prompt, context)
            print(f"Groq API error: {e}")
            return MockLLM(self.config).generate(prompt, context)
            
        except Exception as e:
            print(f"Groq error: {e}")
            return MockLLM(self.config).generate(prompt, context)
    
    def is_available(self) -> bool:
        """Check if Groq API is available."""
        return self._available


class LLMFactory:
    """
    Factory for creating LLM instances.
    
    Usage:
        config = LLMConfig(provider="openai", api_key="...")
        llm = LLMFactory.create(config)
        response = llm.generate("Hello!")
    """
    
    @staticmethod
    def create(config: LLMConfig) -> LLMInterface:
        """
        Create an LLM instance based on configuration.
        
        Args:
            config: LLM configuration
            
        Returns:
            LLM interface instance
        """
        provider = config.provider.lower()
        
        if provider == "groq":
            return GroqLLM(config)
        elif provider == "openai":
            return OpenAILLM(config)
        elif provider in ["local", "ollama"]:
            return LocalLLM(config)
        elif provider == "mock":
            return MockLLM(config)
        else:
            print(f"Unknown provider '{provider}', using Groq (free & fast)")
            config.provider = "groq"
            return GroqLLM(config)
    
    @staticmethod
    def create_generator(config: LLMConfig) -> Callable[[str, Optional[Dict[str, Any]]], str]:
        """
        Create a simple generator function for use with AIParent.
        
        Args:
            config: LLM configuration
            
        Returns:
            Function that takes prompt and optional context, returns response
        """
        llm = LLMFactory.create(config)
        return lambda prompt, context=None: llm.generate(prompt, context)


# Convenience function for quick setup
def create_llm_generator(
    provider: str = "groq",
    api_key: Optional[str] = None,
    model_name: str = "llama-3.3-70b-versatile",
    **kwargs
) -> Callable[[str], str]:
    """
    Create an LLM generator function with simple configuration.
    
    Args:
        provider: LLM provider (groq, openai, ollama, mock)
        api_key: API key if needed
        model_name: Model to use
        **kwargs: Additional config options
        
    Returns:
        Generator function for use with AIParent
        
    Example:
        # Groq (FREE & FAST - recommended!)
        generator = create_llm_generator(provider="groq", api_key="gsk_...")
        
        # Or set GROQ_API_KEY environment variable
        generator = create_llm_generator()  # Uses Groq by default
        
        ai_parent.set_llm_generator(generator)
    """
    config = LLMConfig(
        provider=provider,
        api_key=api_key,
        model_name=model_name,
        **{k: v for k, v in kwargs.items() if hasattr(LLMConfig, k)}
    )
    return LLMFactory.create_generator(config)


# ─── CHILD AI LLM BACKENDS ────────────────────────────────────────────────────
# These mirror the parent LLM classes but use a DYNAMIC system prompt passed
# through the context dict as context["system_prompt"].
# This is needed because the child's system prompt changes with age and regression.

class ChildGroqLLM:
    """
    Groq-backed LLM for the child AI.
    Uses context["system_prompt"] as the system role — set dynamically per call
    by ChildAI._build_system_prompt() so age and regression are always correct.
    """

    def __init__(
        self,
        api_key:     str,
        model_name:  str   = "llama-3.3-70b-versatile",
        max_tokens:  int   = 400,
        temperature: float = 0.8,
    ):
        self.api_key     = api_key
        self.model_name  = model_name
        self.max_tokens  = max_tokens
        self.temperature = temperature
        self._base_url   = "https://api.groq.com/openai/v1/chat/completions"
        self._last_call  = 0.0

    def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        import requests

        system_prompt = (context or {}).get(
            "system_prompt", "You are a child character in a life simulation game."
        )

        # Basic rate limiting (same pattern as GroqLLM)
        elapsed = time.time() - self._last_call
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self._last_call = time.time()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
        }
        payload = {
            "model":       self.model_name,
            "messages":    [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": prompt},
            ],
            "max_tokens":  self.max_tokens,
            "temperature": self.temperature,
        }

        try:
            resp = requests.post(self._base_url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[ChildGroqLLM] Error: {e}. Falling back to mock.")
            return MockChildLLM().generate(prompt, context)


class ChildOllamaLLM:
    """
    Ollama-backed LLM for the child AI.
    Same dynamic system prompt pattern as ChildGroqLLM.
    """

    def __init__(
        self,
        base_url:   str = "http://localhost:11434",
        model_name: str = "llama3.2",
        max_tokens: int = 400,
    ):
        self.base_url   = base_url
        self.model_name = model_name
        self.max_tokens = max_tokens

    def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        import requests

        system_prompt = (context or {}).get(
            "system_prompt", "You are a child character in a life simulation game."
        )
        try:
            resp = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model":   self.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": prompt},
                    ],
                    "stream":  False,
                    "options": {"temperature": 0.8, "num_predict": self.max_tokens},
                },
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json().get("message", {}).get("content", "")
        except Exception as e:
            print(f"[ChildOllamaLLM] Error: {e}. Falling back to mock.")
            return MockChildLLM().generate(prompt, context)


class MockChildLLM:
    """
    Template-based fallback for the child AI.
    Returns valid JSON for both state_update and dialogue call types.
    Used when no API key is available — mirrors MockLLM for the parent AI.
    """

    # One template output per behavior mode for dialogue calls
    _DIALOGUE_TEMPLATES = {
        "CONFIDENT_EXPRESSIVE": {
            "physical_behavior":    "[runs over, tugs on sleeve, bouncing slightly]",
            "verbal_output":        "Look! Look what I did!",
            "emotional_subtext":    "Child wants to share something and be seen.",
            "attention_directed_at": "PLAYER_PARENT",
            "escalation_signal":    "NONE",
            "player_opportunity":   "Kneel down and give the child your full attention.",
        },
        "ANXIOUS_CLINGY": {
            "physical_behavior":    "[moves close, doesn't look away, grips your hand]",
            "verbal_output":        "You coming back?",
            "emotional_subtext":    "Child needs reassurance you won't disappear.",
            "attention_directed_at": "PLAYER_PARENT",
            "escalation_signal":    "LOW",
            "player_opportunity":   "Say 'I'm not going anywhere' and stay physically close.",
        },
        "WITHDRAWN_QUIET": {
            "physical_behavior":    "[sits in corner, picks at the carpet, doesn't look up]",
            "verbal_output":        "",
            "emotional_subtext":    "Child has decided being invisible is safer than being seen.",
            "attention_directed_at": "SELF",
            "escalation_signal":    "MEDIUM",
            "player_opportunity":   "Sit nearby without speaking. Let the child come to you.",
        },
        "DEFIANT_REBELLIOUS": {
            "physical_behavior":    "[crosses arms, stomps foot, glares]",
            "verbal_output":        "No. I don't want to.",
            "emotional_subtext":    "Child is testing whether you will stay when they push.",
            "attention_directed_at": "PLAYER_PARENT",
            "escalation_signal":    "MEDIUM",
            "player_opportunity":   "Stay calm. Don't escalate. The defiance is a question about safety.",
        },
    }

    def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        call_type = (context or {}).get("type", "child_dialogue")

        if call_type == "child_state_update":
            return self._mock_state_update(prompt)
        return self._mock_dialogue(prompt)

    def _mock_state_update(self, prompt: str) -> str:
        # Minimal no-change state update — the real values stay as they are
        # Extract current values from prompt (they're embedded as JSON)
        import re
        match = re.search(r'"child_state"\s*:\s*(\{[^}]+\})', prompt)
        child_state = {}
        if match:
            try:
                child_state = json.loads(match.group(1))
            except Exception:
                pass
        child_state.setdefault("attachment_security",      60)
        child_state.setdefault("emotional_safety",         60)
        child_state.setdefault("self_worth",               60)
        child_state.setdefault("conflict_internalization", 10)
        child_state.setdefault("attention_need",           40)
        child_state.setdefault("emotional_expression",     55)

        rc_match = re.search(r'"relationship_context"\s*:\s*(\{[^}]+\})', prompt)
        rel_ctx = {}
        if rc_match:
            try:
                rel_ctx = json.loads(rc_match.group(1))
            except Exception:
                pass
        rel_ctx.setdefault("parent_conflict_intensity", 20)
        rel_ctx.setdefault("trust_between_parents",     70)
        rel_ctx.setdefault("household_stress",          25)

        result = {
            "updated_state": {
                "age_years":  0,
                "age_months": 0,
                "child_state":          child_state,
                "relationship_context": rel_ctx,
            },
            "active_behavior_mode":    "ANXIOUS_CLINGY",
            "regression_flags": {
                "regression_risk":       False,
                "regression_active":     False,
                "acute_stress_response": False,
            },
            "state_narrative":        "Child processed the event quietly.",
            "suggested_child_trigger": "child waits and watches",
        }
        return json.dumps(result)

    def _mock_dialogue(self, prompt: str) -> str:
        # Pick template based on behavior mode found in prompt
        for mode in ["WITHDRAWN_QUIET", "DEFIANT_REBELLIOUS", "ANXIOUS_CLINGY", "CONFIDENT_EXPRESSIVE"]:
            if mode in prompt:
                template = self._DIALOGUE_TEMPLATES[mode]
                break
        else:
            template = self._DIALOGUE_TEMPLATES["ANXIOUS_CLINGY"]

        return json.dumps({"child_output": template})


def create_child_llm_generator(
    provider:   str            = "mock",
    api_key:    Optional[str]  = None,
    model_name: Optional[str]  = None,
    **kwargs,
) -> Callable:
    """
    Factory for creating a child AI LLM generator.
    Same usage pattern as create_llm_generator() but for ChildAI.

    Returns a callable: (prompt, context) -> str
    context["system_prompt"] carries the dynamic, age-aware system prompt.

    Example:
        generator = create_child_llm_generator(
            provider="groq",
            api_key=os.getenv("GROQ_API_KEY"),
        )
        child.set_llm_generator(generator)
    """
    api_key = api_key or os.getenv("GROQ_API_KEY")

    if provider == "groq" and api_key:
        llm = ChildGroqLLM(
            api_key    = api_key,
            model_name = model_name or "llama-3.3-70b-versatile",
            **{k: v for k, v in kwargs.items() if k in ("max_tokens", "temperature")},
        )
    elif provider == "ollama":
        # Check if Ollama is running
        try:
            import requests
            requests.get("http://localhost:11434/api/tags", timeout=2)
            llm = ChildOllamaLLM(
                model_name = model_name or "llama3.2",
                **{k: v for k, v in kwargs.items() if k in ("base_url", "max_tokens")},
            )
        except Exception:
            print("[ChildLLM] Ollama not available. Using mock.")
            llm = MockChildLLM()
    else:
        llm = MockChildLLM()

    return lambda prompt, context=None: llm.generate(prompt, context)
