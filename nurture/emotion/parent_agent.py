from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import json
from datetime import datetime
from pathlib import Path

from nurture.emotion.emotion_state import EmotionState, EmotionPresets
from nurture.emotion.perception import Perception, PerceptionResult
from nurture.emotion.reaction_policy import ReactionPolicy, ReactionDecision, ReactionMode
from nurture.emotion.prompt_builder import PromptBuilder, BuiltPrompt

@dataclass
class ConversationTurn:
    timestamp: str
    user_input: str
    perception: Dict[str, Any]
    emotion_before: Dict[str, float]
    reaction: Dict[str, Any]
    agent_response: str
    emotion_after: Dict[str, float]

@dataclass
class Memory:
    successful_patterns: List[Dict[str, Any]] = field(default_factory=list)

    failed_patterns: List[Dict[str, Any]] = field(default_factory=list)

    open_conflicts: List[str] = field(default_factory=list)

    pending_apologies: List[str] = field(default_factory=list)

    partner_promises: List[str] = field(default_factory=list)

    trust_history: List[Dict[str, Any]] = field(default_factory=list)

    def add_success(self, context: str, response_mode: str, outcome: str):
        self.successful_patterns.append({
            'context': context,
            'mode': response_mode,
            'outcome': outcome,
            'timestamp': datetime.now().isoformat(),
        })

    def add_failure(self, context: str, response_mode: str, what_went_wrong: str):
        self.failed_patterns.append({
            'context': context,
            'mode': response_mode,
            'issue': what_went_wrong,
            'timestamp': datetime.now().isoformat(),
        })

    def add_conflict(self, conflict: str):
        if conflict not in self.open_conflicts:
            self.open_conflicts.append(conflict)

    def resolve_conflict(self, conflict: str):
        if conflict in self.open_conflicts:
            self.open_conflicts.remove(conflict)

    def add_apology(self, apology: str):
        self.pending_apologies.append(apology)

    def accept_apology(self, apology: str):
        if apology in self.pending_apologies:
            self.pending_apologies.remove(apology)

    def add_promise(self, promise: str):
        self.partner_promises.append(promise)

    def record_promise_outcome(self, promise: str, kept: bool):
        self.trust_history.append({
            'promise': promise,
            'kept': kept,
            'timestamp': datetime.now().isoformat(),
        })
        if promise in self.partner_promises:
            self.partner_promises.remove(promise)

    def get_trust_score(self) -> float:
        if not self.trust_history:
            return 0.5

        kept = sum(1 for h in self.trust_history if h['kept'])
        total = len(self.trust_history)
        return kept / total if total > 0 else 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            'successful_patterns': self.successful_patterns,
            'failed_patterns': self.failed_patterns,
            'open_conflicts': self.open_conflicts,
            'pending_apologies': self.pending_apologies,
            'partner_promises': self.partner_promises,
            'trust_history': self.trust_history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        return cls(
            successful_patterns=data.get('successful_patterns', []),
            failed_patterns=data.get('failed_patterns', []),
            open_conflicts=data.get('open_conflicts', []),
            pending_apologies=data.get('pending_apologies', []),
            partner_promises=data.get('partner_promises', []),
            trust_history=data.get('trust_history', []),
        )

class ParentAgent:

    def __init__(
        self,
        llm_interface=None,
        initial_emotion: Optional[EmotionState] = None,
        name: str = "Sarah",
    ):
        self.name = name
        self.llm = llm_interface

        self.emotion_state = initial_emotion or EmotionPresets.stressed_new_parent()
        self.perception = Perception()
        self.reaction_policy = ReactionPolicy()
        self.prompt_builder = PromptBuilder()
        self.memory = Memory()

        self.conversation_history: List[Dict[str, str]] = []
        self.turn_history: List[ConversationTurn] = []
        self.current_scenario: Optional[str] = None

        self.emotion_decay_rate = 0.1

    def set_scenario(self, scenario: str):
        self.current_scenario = scenario

    def set_llm(self, llm_interface):
        self.llm = llm_interface

    def process_input(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        emotion_before = self._emotion_snapshot()

        perception_result = self.perception.analyze(user_input)

        reaction = self.reaction_policy.decide(self.emotion_state, perception_result)

        self.emotion_state.update(reaction.emotion_deltas)

        prompt = self.prompt_builder.build(
            emotion_state=self.emotion_state,
            reaction=reaction,
            perception=perception_result,
            scenario_context=self.current_scenario,
            conversation_history=self.conversation_history,
        )

        if self.llm:
            response = self._generate_llm_response(prompt, user_input)
        else:
            response = self._generate_fallback_response(reaction)

        self.emotion_state.decay_toward_baseline()

        self._update_history(user_input, response)
        self._update_memory(perception_result, reaction)

        emotion_after = self._emotion_snapshot()

        turn = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            perception={
                'sentiment': perception_result.sentiment.value,
                'intent': perception_result.intent.value,
                'triggers': [t.value for t in perception_result.triggers],
                'severity': perception_result.severity,
            },
            emotion_before=emotion_before,
            reaction={
                'mode': reaction.mode.value,
                'intensity': reaction.intensity,
                'allowed': reaction.allowed_by_gate,
                'reasoning': reaction.reasoning,
            },
            agent_response=response,
            emotion_after=emotion_after,
        )
        self.turn_history.append(turn)

        debug_info = {
            'perception': turn.perception,
            'emotion_before': emotion_before,
            'reaction': turn.reaction,
            'emotion_after': emotion_after,
            'prompt_mode': reaction.mode.value,
        }

        return response, debug_info

    def _generate_llm_response(self, prompt: BuiltPrompt, user_input: str) -> str:
        try:
            messages = [
                {"role": "system", "content": prompt.system_prompt},
            ]

            for msg in self.conversation_history[-4:]:
                messages.append(msg)

            messages.append({"role": "user", "content": user_input})


            if hasattr(self.llm, 'generate_with_system'):
                response = self.llm.generate_with_system(
                    prompt.system_prompt,
                    user_input
                )
            elif hasattr(self.llm, 'generate'):
                combined_prompt = f"{prompt.system_prompt}\n\nPartner says: {user_input}\n\n{self.name}:"
                response = self.llm.generate(combined_prompt)
            else:
                response = self._generate_fallback_response(
                    ReactionDecision(
                        mode=ReactionMode.COLD,
                        intensity=0.5,
                        allowed_by_gate=True,
                        emotion_deltas={},
                        reasoning="LLM unavailable"
                    )
                )

            return self._clean_response(response)

        except Exception as e:
            print(f"LLM error: {e}")
            return self._generate_fallback_response(
                ReactionDecision(
                    mode=ReactionMode.COLD,
                    intensity=0.5,
                    allowed_by_gate=True,
                    emotion_deltas={},
                    reasoning=f"LLM error: {e}"
                )
            )

    def _generate_fallback_response(self, reaction: ReactionDecision) -> str:
        import random

        responses = {
            ReactionMode.SUPPORTIVE: [
                "Okay. Thanks for saying that.",
                "I appreciate you trying.",
                "*small nod*",
            ],
            ReactionMode.DEFENSIVE: [
                "I've been doing my best.",
                "That's not fair.",
                "What do you expect from me?",
            ],
            ReactionMode.CONFRONTATIONAL: [
                "Are you serious?",
                "No. I'm done.",
                "That's rich coming from you.",
            ],
            ReactionMode.COLD: [
                "Fine.",
                "Okay.",
                "Whatever.",
            ],
            ReactionMode.WITHDRAWN: [
                "*silence*",
                "I can't do this.",
                "*walks away*",
            ],
            ReactionMode.COOPERATIVE: [
                "Okay, let's figure this out.",
                "What do you suggest?",
                "I'm willing to try.",
            ],
            ReactionMode.SARCASTIC: [
                "Oh, wonderful.",
                "Sure, that makes sense.",
                "Right. Of course.",
            ],
            ReactionMode.VULNERABLE: [
                "I'm just... so tired.",
                "This is really hard.",
                "I need you to see me.",
            ],
            ReactionMode.DISMISSIVE: [
                "Uh huh.",
                "Sure.",
                "*shrug*",
            ],
            ReactionMode.HURT: [
                "...okay.",
                "That hurt.",
                "*quiet*",
            ],
        }

        options = responses.get(reaction.mode, responses[ReactionMode.COLD])
        return random.choice(options)

    def _clean_response(self, response: str) -> str:
        response = response.strip()

        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]

        prefixes = [f"{self.name}:", f"{self.name} says:", "Sarah:"]
        for prefix in prefixes:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()

        if len(response) > 200:
            for punct in ['. ', '! ', '? ']:
                last_break = response[:200].rfind(punct)
                if last_break > 50:
                    response = response[:last_break+1]
                    break
            else:
                response = response[:200] + "..."

        return response

    def _update_history(self, user_input: str, response: str):
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": response})

        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def _update_memory(self, perception: PerceptionResult, reaction: ReactionDecision):
        from nurture.emotion.perception import Intent, TriggerType

        if perception.intent == Intent.APOLOGIZE:
            self.memory.add_apology(perception.raw_input)

        if perception.sentiment.value in ['hostile', 'negative']:
            if any(t in perception.triggers for t in [TriggerType.BLAME, TriggerType.INSULT]):
                self.memory.add_conflict(f"Conflict: {perception.raw_input[:50]}...")

    def _emotion_snapshot(self) -> Dict[str, float]:
        return {
            'anger': self.emotion_state.anger,
            'stress': self.emotion_state.stress,
            'fatigue': self.emotion_state.fatigue,
            'trust': self.emotion_state.trust,
            'empathy': self.emotion_state.empathy,
            'hurt': self.emotion_state.hurt,
            'love': self.emotion_state.love,
        }

    def get_emotional_summary(self) -> str:
        return self.emotion_state.describe()

    def save_state(self, path: str):
        state = {
            'emotion_state': self._emotion_snapshot(),
            'memory': self.memory.to_dict(),
            'conversation_history': self.conversation_history,
            'current_scenario': self.current_scenario,
        }

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)

    def load_state(self, path: str):
        with open(path, 'r') as f:
            state = json.load(f)

        if 'emotion_state' in state:
            es = state['emotion_state']
            self.emotion_state = EmotionState(
                anger=es.get('anger', 0.1),
                stress=es.get('stress', 0.3),
                fatigue=es.get('fatigue', 0.5),
                trust=es.get('trust', 0.5),
                empathy=es.get('empathy', 0.6),
                hurt=es.get('hurt', 0.1),
                love=es.get('love', 0.6),
            )

        if 'memory' in state:
            self.memory = Memory.from_dict(state['memory'])

        if 'conversation_history' in state:
            self.conversation_history = state['conversation_history']

        if 'current_scenario' in state:
            self.current_scenario = state['current_scenario']

    def reset_conversation(self):
        self.conversation_history = []

    def reset_emotions(self, preset: str = 'stressed_new_parent'):
        presets = {
            'calm': EmotionPresets.calm,
            'stressed_new_parent': EmotionPresets.stressed_new_parent,
            'betrayed': EmotionPresets.betrayed,
            'exhausted': EmotionPresets.exhausted,
            'loving': EmotionPresets.loving,
        }

        if preset in presets:
            self.emotion_state = presets[preset]()
        else:
            self.emotion_state = EmotionPresets.stressed_new_parent()

    def apply_scenario_emotion(self, scenario_type: str):
        effects = {
            'feeding_time_chaos': {'stress': 0.2, 'fatigue': 0.1},
            'sleepless_night': {'fatigue': 0.3, 'stress': 0.2, 'empathy': -0.1},
            'partner_absent': {'anger': 0.2, 'hurt': 0.2, 'trust': -0.1},
            'baby_sick': {'stress': 0.3, 'fatigue': 0.2},
            'good_moment': {'love': 0.2, 'stress': -0.1},
            'argument': {'anger': 0.3, 'hurt': 0.2, 'trust': -0.1},
        }

        if scenario_type in effects:
            self.emotion_state.update(effects[scenario_type])

def create_parent_agent(
    llm_interface=None,
    preset: str = 'stressed_new_parent'
) -> ParentAgent:
    presets = {
        'calm': EmotionPresets.calm,
        'stressed_new_parent': EmotionPresets.stressed_new_parent,
        'betrayed': EmotionPresets.betrayed,
        'exhausted': EmotionPresets.exhausted,
        'loving': EmotionPresets.loving,
    }

    initial_emotion = presets.get(preset, EmotionPresets.stressed_new_parent)()

    return ParentAgent(
        llm_interface=llm_interface,
        initial_emotion=initial_emotion,
    )
