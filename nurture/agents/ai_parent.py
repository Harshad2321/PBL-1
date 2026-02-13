from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import random

from nurture.agents.base_parent import BaseParent
from nurture.core.data_structures import (
    ParentState, PersonalityProfile, DialogueContext, EmotionalState,
    EmotionalImpact
)
from nurture.core.enums import (
    ParentRole, EmotionType, PersonalityTrait, ResponseStrategy,
    ConflictStyle, InteractionType, MemoryType, ContextType, ContextCategory
)
from nurture.core.events import Event, EventType, get_event_bus
from nurture.core.learning_system import AdaptiveLearningEngine
from nurture.memory.memory_store import MemoryStore, Memory
from nurture.personality.emotional_memory import EmotionalMemorySystem

class AIParent(BaseParent):

    def __init__(
        self,
        state: ParentState,
        memory_store: Optional[MemoryStore] = None,
        llm_generator: Optional[Callable[[str], str]] = None
    ):
        super().__init__(state, memory_store)

        self._llm_generator = llm_generator
        self._current_strategy: ResponseStrategy = ResponseStrategy.SUPPORTIVE
        self._strategy_weights: Dict[ResponseStrategy, float] = {}
        self._last_player_message: str = ""
        self._response_queue: List[str] = []

        self._trust_in_partner: float = 0.7
        self._respect_for_partner: float = 0.7
        self._perceived_partner_stress: float = 0.0

        self._conflict_history: List[Dict[str, Any]] = []
        self._agreement_streak: int = 0
        self._disagreement_streak: int = 0

        self._learning_engine = AdaptiveLearningEngine(agent_id=state.id)

        self._emotional_memory = EmotionalMemorySystem(max_capacity=1000)

    @property
    def personality(self) -> PersonalityProfile:
        return self.state.personality

    @property
    def current_strategy(self) -> ResponseStrategy:
        return self._current_strategy

    @property
    def learning_engine(self) -> AdaptiveLearningEngine:
        return self._learning_engine

    def process_input(self, message: str, context: Optional[DialogueContext] = None) -> None:
        if not message or not message.strip():
            return

        message = message.strip()
        self._last_player_message = message

        self.log_input(message, {"strategy_before": self._current_strategy.value})

        self.increment_interaction_count()

        preferences = self._learning_engine.analyzer.extract_preferences(message)

        analysis = self._analyze_incoming_message(message, context)

        self._apply_message_impact(analysis)

        relevant_memories = self._retrieve_relevant_memories(message, context)

        self._select_strategy(analysis, relevant_memories, context)

        self.create_memory(
            content=f"Partner said: {message[:100]}...",
            memory_type=MemoryType.INTERACTION,
            emotional_valence=analysis.get("sentiment", 0.0),
            importance=analysis.get("importance", 0.5),
            tags=set(analysis.get("tags", ["conversation"])),
            associated_agent_id=context.player_state.get("id") if context and context.player_state else None,
        )

        self._store_emotional_memory(message, analysis, context)

        self._event_bus.publish(Event(
            event_type=EventType.AI_STRATEGY_SELECTED,
            source=self.id,
            data={
                "strategy": self._current_strategy.value,
                "message_sentiment": analysis.get("sentiment", 0.0),
            }
        ))

    def _analyze_incoming_message(
        self,
        message: str,
        context: Optional[DialogueContext] = None
    ) -> Dict[str, Any]:
        message_lower = message.lower()

        analysis = {
            "sentiment": 0.0,
            "intensity": 0.5,
            "is_question": "?" in message,
            "is_accusation": False,
            "is_supportive": False,
            "is_critical": False,
            "topics": [],
            "tags": ["conversation"],
            "importance": 0.5,
        }

        positive_words = {
            "love": 0.3, "appreciate": 0.2, "thank": 0.2, "agree": 0.15,
            "understand": 0.15, "support": 0.2, "together": 0.15, "help": 0.1,
            "sorry": 0.1, "right": 0.1, "good": 0.1
        }

        negative_words = {
            "hate": -0.4, "never": -0.2, "always": -0.15, "fault": -0.25,
            "blame": -0.3, "wrong": -0.15, "stupid": -0.3, "useless": -0.35,
            "can't": -0.1, "won't": -0.1, "annoyed": -0.2, "frustrated": -0.2
        }

        accusation_patterns = [
            "you always", "you never", "your fault", "because of you",
            "you don't", "you should", "you're wrong"
        ]

        support_patterns = [
            "i understand", "i'm sorry", "let me help", "we can",
            "together", "i appreciate", "thank you", "i love"
        ]

        for word, score in positive_words.items():
            if word in message_lower:
                analysis["sentiment"] += score

        for word, score in negative_words.items():
            if word in message_lower:
                analysis["sentiment"] += score

        analysis["sentiment"] = max(-1.0, min(1.0, analysis["sentiment"]))

        for pattern in accusation_patterns:
            if pattern in message_lower:
                analysis["is_accusation"] = True
                analysis["intensity"] += 0.2
                analysis["tags"].append("conflict")
                break

        for pattern in support_patterns:
            if pattern in message_lower:
                analysis["is_supportive"] = True
                analysis["tags"].append("positive")
                break

        if message.isupper():
            analysis["intensity"] += 0.3
        analysis["intensity"] += message.count("!") * 0.1
        analysis["intensity"] = min(1.0, analysis["intensity"])

        topic_keywords = {
            "money": ["money", "bills", "expenses", "work", "salary", "afford"],
            "child": ["baby", "child", "kid", "son", "daughter"],
            "relationship": ["us", "we", "together", "marriage", "relationship"],
            "household": ["chores", "cleaning", "cooking", "house", "home"],
            "health": ["tired", "sick", "sleep", "rest", "doctor"],
        }

        for topic, keywords in topic_keywords.items():
            if any(kw in message_lower for kw in keywords):
                analysis["topics"].append(topic)
                analysis["tags"].append(topic)

        if analysis["is_accusation"] or analysis["intensity"] > 0.7:
            analysis["importance"] = 0.8
        elif analysis["is_supportive"]:
            analysis["importance"] = 0.6

        return analysis

    def _apply_message_impact(self, analysis: Dict[str, Any]) -> None:
        sentiment = analysis.get("sentiment", 0.0)
        intensity = analysis.get("intensity", 0.5)

        neuroticism = self.personality.get_trait(PersonalityTrait.NEUROTICISM)
        agreeableness = self.personality.get_trait(PersonalityTrait.AGREEABLENESS)

        reaction_strength = intensity * (0.5 + neuroticism * 0.5)

        if analysis.get("is_accusation"):
            self.update_emotion(EmotionType.SADNESS, 0.1 * reaction_strength)
            if agreeableness < 0.5:
                self.update_emotion(EmotionType.ANGER, 0.15 * reaction_strength)
            else:
                self.update_emotion(EmotionType.GUILT, 0.1 * reaction_strength)
            self.add_stress(0.1 * reaction_strength)
            self._disagreement_streak += 1
            self._agreement_streak = 0

        elif analysis.get("is_supportive"):
            self.update_emotion(EmotionType.JOY, 0.1 * reaction_strength)
            self.update_emotion(EmotionType.TRUST, 0.05)
            self.update_emotion(EmotionType.LOVE, 0.03)
            self.reduce_stress(0.05)
            self._agreement_streak += 1
            self._disagreement_streak = 0

        elif sentiment < -0.3:
            self.update_emotion(EmotionType.SADNESS, 0.05 * reaction_strength)
            self.update_emotion(EmotionType.ANXIETY, 0.05 * reaction_strength)

        elif sentiment > 0.3:
            self.update_emotion(EmotionType.JOY, 0.05 * reaction_strength)
            self.update_emotion(EmotionType.CONTENTMENT, 0.03)

        if self._agreement_streak > 3:
            self._trust_in_partner = min(1.0, self._trust_in_partner + 0.02)
        if self._disagreement_streak > 3:
            self._trust_in_partner = max(0.0, self._trust_in_partner - 0.03)

    def _retrieve_relevant_memories(
        self,
        message: str,
        context: Optional[DialogueContext] = None
    ) -> List[Memory]:
        memories = []

        memories.extend(self.memory.get_recent(3))

        message_lower = message.lower()
        if "always" in message_lower or "never" in message_lower:
            memories.extend(self.memory.retrieve_by_tags({"conflict"}, 3))

        if context and context.current_topic:
            topic_memories = self.memory.retrieve_by_tags({context.current_topic}, 2)
            memories.extend(topic_memories)

        if self.emotional_state.stress_level > 0.6:
            negative_memories = self.memory.retrieve_by_emotion((-1.0, -0.3), 2)
            memories.extend(negative_memories)

        seen = set()
        unique = []
        for m in memories:
            if m.id not in seen:
                seen.add(m.id)
                unique.append(m)

        return unique[:5]

    def _select_strategy(
        self,
        analysis: Dict[str, Any],
        memories: List[Memory],
        context: Optional[DialogueContext] = None
    ) -> ResponseStrategy:
        weights = {strategy: 0.0 for strategy in ResponseStrategy}

        warmth = self.personality.get_trait(PersonalityTrait.WARMTH)
        strictness = self.personality.get_trait(PersonalityTrait.STRICTNESS)
        patience = self.personality.get_trait(PersonalityTrait.PATIENCE)
        agreeableness = self.personality.get_trait(PersonalityTrait.AGREEABLENESS)

        weights[ResponseStrategy.SUPPORTIVE] = warmth * 0.5 + agreeableness * 0.3
        weights[ResponseStrategy.EMPATHETIC] = warmth * 0.4 + patience * 0.2
        weights[ResponseStrategy.ASSERTIVE] = strictness * 0.4 + (1 - agreeableness) * 0.2
        weights[ResponseStrategy.COMPROMISING] = patience * 0.3 + agreeableness * 0.3
        weights[ResponseStrategy.PRACTICAL] = (1 - warmth) * 0.3 + strictness * 0.2
        weights[ResponseStrategy.CHALLENGING] = (1 - agreeableness) * 0.3 + strictness * 0.2
        weights[ResponseStrategy.AVOIDANT] = (1 - patience) * 0.2
        weights[ResponseStrategy.EMOTIONAL] = warmth * 0.3

        stress = self.emotional_state.stress_level
        anger = self.emotional_state.emotions.get(EmotionType.ANGER, 0)
        sadness = self.emotional_state.emotions.get(EmotionType.SADNESS, 0)
        trust = self.emotional_state.emotions.get(EmotionType.TRUST, 0.5)

        if stress > 0.7:
            weights[ResponseStrategy.AVOIDANT] += 0.3
            weights[ResponseStrategy.ASSERTIVE] += 0.2
            weights[ResponseStrategy.SUPPORTIVE] -= 0.2

        if anger > 0.5:
            weights[ResponseStrategy.CHALLENGING] += 0.3
            weights[ResponseStrategy.ASSERTIVE] += 0.2
            weights[ResponseStrategy.SUPPORTIVE] -= 0.3

        if sadness > 0.5:
            weights[ResponseStrategy.EMOTIONAL] += 0.3
            weights[ResponseStrategy.AVOIDANT] += 0.2

        if trust < 0.4:
            weights[ResponseStrategy.AVOIDANT] += 0.2
            weights[ResponseStrategy.ASSERTIVE] += 0.1

        if analysis.get("is_accusation"):
            if agreeableness > 0.6:
                weights[ResponseStrategy.EMPATHETIC] += 0.3
                weights[ResponseStrategy.COMPROMISING] += 0.2
            else:
                weights[ResponseStrategy.ASSERTIVE] += 0.3
                weights[ResponseStrategy.CHALLENGING] += 0.2

        if analysis.get("is_supportive"):
            weights[ResponseStrategy.SUPPORTIVE] += 0.4
            weights[ResponseStrategy.EMPATHETIC] += 0.2

        if analysis.get("is_question"):
            weights[ResponseStrategy.PRACTICAL] += 0.2

        conflict_pattern = self.memory.get_pattern_summary("conflict")
        if conflict_pattern["count"] > 5 and conflict_pattern["trend"] == "declining":
            weights[ResponseStrategy.COMPROMISING] += 0.3
            weights[ResponseStrategy.EMPATHETIC] += 0.2

        self._strategy_weights = weights

        sorted_strategies = sorted(weights.items(), key=lambda x: x[1], reverse=True)

        top_strategies = sorted_strategies[:3]
        total_weight = sum(w for _, w in top_strategies)
        if total_weight > 0:
            r = random.random() * total_weight
            cumulative = 0
            for strategy, weight in top_strategies:
                cumulative += weight
                if r <= cumulative:
                    self._current_strategy = strategy
                    break
            else:
                self._current_strategy = top_strategies[0][0]
        else:
            self._current_strategy = ResponseStrategy.SUPPORTIVE

        self.state.current_strategy = self._current_strategy

        return self._current_strategy

    def generate_response(self, dialogue_context: Optional[DialogueContext] = None, context: Optional[Dict[str, Any]] = None) -> str:
        scenario_context = context or {}
        if not scenario_context and dialogue_context and hasattr(dialogue_context, 'extra_context'):
            scenario_context = dialogue_context.extra_context or {}

        if self._llm_generator:
            prompt = self._build_llm_prompt(dialogue_context)
            response = self._llm_generator(prompt, scenario_context)
        else:
            response = self._generate_template_response(dialogue_context)

        self.log_output(response, {
            "strategy": self._current_strategy.value,
            "emotional_valence": self.emotional_state.get_valence(),
        })

        if dialogue_context:
            dialogue_context.add_exchange(self.name, response)

        self._apply_response_effects()

        self._event_bus.publish(Event(
            event_type=EventType.AI_RESPONSE_GENERATED,
            source=self.id,
            data={
                "response_length": len(response),
                "strategy": self._current_strategy.value,
            }
        ))

        return response

    def _build_llm_prompt(self, context: Optional[DialogueContext] = None) -> str:
        dom_emotion, dom_intensity = self.emotional_state.get_dominant_emotion()

        prompt_parts = [
            f"You are {self.name}, a {self.role.value}.",
            f"Feeling: {dom_emotion.value} (stress: {self.emotional_state.stress_level:.1f})",
            f"Strategy: {self._current_strategy.value}",
        ]

        recent_memories = self._emotional_memory.get_recent_memories(hours=24, limit=2)
        if recent_memories and len(recent_memories) > 0:
            avg_valence = sum(m.emotional_impact.valence for m in recent_memories) / len(recent_memories)
            if avg_valence < -0.3:
                prompt_parts.append("Recent interactions felt hurtful.")
            elif avg_valence > 0.3:
                prompt_parts.append("Recent interactions felt warm.")

        prompt_parts.append("")

        if context:
            prompt_parts.extend([
                f"Scenario: {context.scenario_name}",
                f"Partner: \"{context.player_message}\"",
            ])
        else:
            prompt_parts.append(f"Partner: \"{self._last_player_message}\"")

        prompt_parts.extend([
            "",
            "Respond naturally in 1-2 sentences:",
        ])

        return "\n".join(prompt_parts)

    def _generate_template_response(self, context: Optional[DialogueContext] = None) -> str:
        templates = {
            ResponseStrategy.SUPPORTIVE: [
                "I understand how you feel. We'll get through this together.",
                "You're right, and I appreciate you sharing that with me.",
                "I'm here for you. What do you need from me?",
                "That makes sense. Let's figure this out as a team.",
            ],
            ResponseStrategy.EMPATHETIC: [
                "I can see this is really affecting you. Tell me more about how you feel.",
                "That sounds really difficult. I'm sorry you're going through this.",
                "Your feelings are completely valid. I hear you.",
                "I understand why you'd feel that way.",
            ],
            ResponseStrategy.ASSERTIVE: [
                "I hear you, but I need you to understand my perspective too.",
                "I disagree, and here's why this matters to me.",
                "I've thought about this a lot, and I believe we need to...",
                "Let me be clear about where I stand on this.",
            ],
            ResponseStrategy.COMPROMISING: [
                "Maybe we can find a middle ground here.",
                "What if we tried it your way this time, and my way next time?",
                "I'm willing to meet you halfway on this.",
                "Let's see if we can both give a little.",
            ],
            ResponseStrategy.PRACTICAL: [
                "Let's focus on what we can actually do about this.",
                "Here's what I think we should do next.",
                "Okay, so practically speaking, we need to...",
                "Let's break this down into manageable steps.",
            ],
            ResponseStrategy.CHALLENGING: [
                "Are you sure that's really what happened?",
                "I think we need to look at this more carefully.",
                "I'm not convinced that's the best approach.",
                "Let's think about this differently.",
            ],
            ResponseStrategy.AVOIDANT: [
                "Maybe we should talk about this later when we've both calmed down.",
                "I don't think now is the right time for this discussion.",
                "Let's take a break and come back to this.",
                "I need some time to think about this.",
            ],
            ResponseStrategy.EMOTIONAL: [
                "This really hurts me to hear.",
                "I feel so overwhelmed right now.",
                "Do you know how much this affects me?",
                "I just feel like we keep having the same issues.",
            ],
        }

        strategy_templates = templates.get(self._current_strategy, templates[ResponseStrategy.SUPPORTIVE])

        response = random.choice(strategy_templates)

        return response

    def _apply_response_effects(self) -> None:
        if self._current_strategy in [ResponseStrategy.CHALLENGING, ResponseStrategy.ASSERTIVE]:
            self.add_stress(0.03)
        elif self._current_strategy in [ResponseStrategy.SUPPORTIVE, ResponseStrategy.EMPATHETIC]:
            self.reduce_stress(0.02)
            self.update_emotion(EmotionType.CONTENTMENT, 0.02)

        if self._current_strategy == ResponseStrategy.AVOIDANT:
            self.update_emotion(EmotionType.GUILT, 0.03)

    def _store_emotional_memory(
        self,
        message: str,
        analysis: Dict[str, Any],
        context: Optional[DialogueContext] = None
    ) -> None:
        dom_emotion, intensity = self.emotional_state.get_dominant_emotion()

        if analysis.get("is_accusation") or "conflict" in analysis.get("tags", []):
            category = ContextCategory.CONFLICT
        elif analysis.get("is_supportive") or "positive" in analysis.get("tags", []):
            category = ContextCategory.SUPPORT
        elif "child" in analysis.get("topics", []):
            category = ContextCategory.PARENTING
        else:
            category = ContextCategory.INTIMACY

        impact = EmotionalImpact(
            primary_emotion=dom_emotion,
            intensity=intensity,
            valence=analysis.get("sentiment", 0.0),
            context_category=category
        )

        self._emotional_memory.store_memory(
            interaction_id=f"interaction_{datetime.now().timestamp()}",
            emotional_impact=impact,
            context=ContextType.PRIVATE,
            associated_patterns=[],
            timestamp=datetime.now()
        )

    def set_llm_generator(self, generator: Callable[[str], str]) -> None:
        self._llm_generator = generator

    def reset_conversation(self) -> None:
        if self._llm_generator and hasattr(self._llm_generator, 'reset'):
            self._llm_generator.reset()
        elif self._llm_generator and hasattr(self._llm_generator, 'conversation_history'):
            self._llm_generator.conversation_history = []

    def get_relationship_summary(self) -> Dict[str, float]:
        memory_stats = self._emotional_memory.get_memory_stats()

        return {
            "trust_in_partner": self._trust_in_partner,
            "respect_for_partner": self._respect_for_partner,
            "perceived_partner_stress": self._perceived_partner_stress,
            "agreement_streak": self._agreement_streak,
            "disagreement_streak": self._disagreement_streak,
            "total_emotional_memories": memory_stats.get("total_memories", 0),
            "average_emotional_valence": memory_stats.get("average_valence", 0.0),
            "support_feeling": self._emotional_memory.get_average_valence(ContextCategory.SUPPORT, days=7),
            "conflict_feeling": self._emotional_memory.get_average_valence(ContextCategory.CONFLICT, days=7),
        }

    def adjust_personality_slightly(self, trait: PersonalityTrait, delta: float) -> None:
        self.personality.adjust_trait(trait, delta)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.to_dict(),
            "current_strategy": self._current_strategy.value,
            "trust_in_partner": self._trust_in_partner,
            "respect_for_partner": self._respect_for_partner,
            "agreement_streak": self._agreement_streak,
            "disagreement_streak": self._disagreement_streak,
            "emotional_memory": self._emotional_memory.to_dict(),
        }

    def learn_from_outcome(self, user_input: str, ai_response: str, outcome_quality: float = 0.5) -> None:
        self._learning_engine.learn_from_interaction(user_input, ai_response, outcome_quality)

        self._apply_learning_adjustments()

    def _apply_learning_adjustments(self) -> None:
        adjustments = self._learning_engine.get_personality_adjustments()

        for trait, adjustment in adjustments.items():
            current_value = self.personality.traits.get(trait, 0.5)
            new_value = max(0.0, min(1.0, current_value + adjustment))
            self.personality.traits[trait] = new_value

    def get_learning_summary(self) -> Dict[str, Any]:
        return self._learning_engine.get_learning_summary()

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        memory_store: Optional[MemoryStore] = None,
        llm_generator: Optional[Callable[[str], str]] = None
    ) -> 'AIParent':
        state = ParentState.from_dict(data["state"])
        ai = cls(state, memory_store, llm_generator)
        ai._current_strategy = ResponseStrategy(data.get("current_strategy", "supportive"))
        ai._trust_in_partner = data.get("trust_in_partner", 0.7)
        ai._respect_for_partner = data.get("respect_for_partner", 0.7)
        ai._agreement_streak = data.get("agreement_streak", 0)
        ai._disagreement_streak = data.get("disagreement_streak", 0)

        if "emotional_memory" in data:
            ai._emotional_memory = EmotionalMemorySystem.from_dict(data["emotional_memory"])

        return ai
