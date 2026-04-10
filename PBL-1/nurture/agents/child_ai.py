"""
nurture/agents/child_ai.py

AI-driven child character. Mirrors the structure of AIParent:
  - Has internal state (ChildInternalState)
  - Accepts an llm_generator callable via set_llm_generator()
  - process_parent_action() is the equivalent of AIParent.process_input()
  - _generate_output() is the equivalent of AIParent.generate_response()

Age is tied to story day via advance_age(act, day) which is called automatically
when act and day are passed to process_parent_action().

Act 1 — 12 days, ages 0-3  (3 months per day)
Act 2 — 14 days, ages 4-7  (~2.57 months per day)
"""

import json
import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


# ─── ACT → AGE MAP ────────────────────────────────────────────────────────────
#
#  Act 1 day-by-day:                   Act 2 day-by-day:
#  Day  1 → 0y 0m  (newborn)           Day  1 → 4y 0m  (school entry)
#  Day  2 → 0y 3m                      Day  2 → 4y 2m
#  Day  3 → 0y 6m                      Day  3 → 4y 5m
#  Day  4 → 0y 9m                      Day  4 → 4y 7m
#  Day  5 → 1y 0m  (first words)       Day  5 → 4y 10m
#  Day  6 → 1y 3m                      Day  6 → 5y 0m  (cause & effect)
#  Day  7 → 1y 6m                      Day  7 → 5y 3m
#  Day  8 → 1y 9m                      Day  8 → 5y 5m
#  Day  9 → 2y 0m  (2-word sentences)  Day  9 → 5y 8m
#  Day 10 → 2y 3m                      Day 10 → 5y 10m
#  Day 11 → 2y 6m  (10-word cap)       Day 11 → 6y 1m  (fairness / grudges)
#  Day 12 → 2y 9m  (end of act 1)      Day 12 → 6y 3m
#                                       Day 13 → 6y 6m
#                                       Day 14 → 6y 9m  (end of act 2)

_ACT_AGE_CONFIG: Dict[int, Dict] = {
    1: {"start_months": 0,  "days": 12, "end_months": 36},
    2: {"start_months": 48, "days": 14, "end_months": 84},
}

_MAX_DELTA        = 15    # max any variable may shift in one event
_MAX_SESSION_EVENTS = 10  # rolling window of remembered events

# AI-voice patterns that must never appear in child dialogue
_BANNED_AI_PATTERNS = [
    r"\bi feel like\b",
    r"\bi'?m experiencing\b",
    r"\bi understand that\b",
    r"\bcan we talk about\b",
    r"\bwould you mind\b",
    r"\bi know you'?re busy but\b",
    r"\bfrom (my|a) perspective\b",
    r"\bemotionally (unsafe|unavailable|overwhelmed)\b",
    r"\bi('?m| am) feeling\b",
]


def calculate_age_for_day(act: int, day: int) -> Dict[str, int]:
    """
    Return {"age_years": int, "age_months": int} for a given act and story day.
    Clamps day to valid range; raises ValueError for unknown acts.
    """
    config = _ACT_AGE_CONFIG.get(act)
    if not config:
        raise ValueError(f"Unknown act: {act}. Supported: 1, 2.")
    clamped        = max(1, min(day, config["days"]))
    total_months   = config["end_months"] - config["start_months"]
    elapsed        = round((clamped - 1) * (total_months / config["days"]))
    age_total      = config["start_months"] + elapsed
    return {"age_years": age_total // 12, "age_months": age_total % 12}


# ─── BEHAVIOR MODES ───────────────────────────────────────────────────────────

class BehaviorMode:
    CONFIDENT_EXPRESSIVE = "CONFIDENT_EXPRESSIVE"
    ANXIOUS_CLINGY       = "ANXIOUS_CLINGY"
    WITHDRAWN_QUIET      = "WITHDRAWN_QUIET"
    DEFIANT_REBELLIOUS   = "DEFIANT_REBELLIOUS"


# ─── DATA CLASSES ─────────────────────────────────────────────────────────────

@dataclass
class ChildInternalState:
    """
    Complete internal state for the child AI.
    Uses 0-100 scale (spec scale) rather than the simulation stack's 0-1 scale.
    """
    # Age (set automatically by advance_age)
    age_years:  int = 0
    age_months: int = 0

    # Core emotional variables (0-100)
    attachment_security:      float = 60.0
    emotional_safety:         float = 60.0
    self_worth:               float = 60.0
    conflict_internalization: float = 10.0
    attention_need:           float = 40.0
    emotional_expression:     float = 55.0

    # Relationship context (0-100)
    parent_conflict_intensity: float = 20.0
    trust_between_parents:     float = 70.0
    household_stress:          float = 25.0

    # Runtime
    active_behavior_mode: str       = BehaviorMode.CONFIDENT_EXPRESSIVE
    session_events_today: List[str] = field(default_factory=list)

    # Locked at act boundaries (None until locked)
    attachment_style: Optional[str] = None
    archetype:        Optional[str] = None

    _CHILD_FIELDS = [
        "attachment_security", "emotional_safety", "self_worth",
        "conflict_internalization", "attention_need", "emotional_expression",
    ]
    _CONTEXT_FIELDS = [
        "parent_conflict_intensity", "trust_between_parents", "household_stress",
    ]

    def clamp_all(self):
        for f in self._CHILD_FIELDS + self._CONTEXT_FIELDS:
            setattr(self, f, max(0.0, min(100.0, getattr(self, f))))

    def to_dict(self) -> dict:
        return {
            "age_years":  self.age_years,
            "age_months": self.age_months,
            "child_state": {f: getattr(self, f) for f in self._CHILD_FIELDS},
            "relationship_context": {f: getattr(self, f) for f in self._CONTEXT_FIELDS},
            "active_behavior_mode": self.active_behavior_mode,
            "session_events_today": self.session_events_today[-_MAX_SESSION_EVENTS:],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChildInternalState":
        s = cls()
        s.age_years  = data.get("age_years",  0)
        s.age_months = data.get("age_months", 0)
        cs = data.get("child_state", {})
        for f in cls._CHILD_FIELDS:
            setattr(s, f, float(cs.get(f, getattr(s, f))))
        rc = data.get("relationship_context", {})
        for f in cls._CONTEXT_FIELDS:
            setattr(s, f, float(rc.get(f, getattr(s, f))))
        s.active_behavior_mode = data.get("active_behavior_mode", BehaviorMode.CONFIDENT_EXPRESSIVE)
        s.session_events_today = data.get("session_events_today", [])
        s.attachment_style     = data.get("attachment_style")
        s.archetype            = data.get("archetype")
        return s


@dataclass
class ChildOutput:
    physical_behavior:    str = ""
    verbal_output:        str = ""
    emotional_subtext:    str = ""
    attention_directed_at: str = "SELF"
    escalation_signal:    str = "NONE"
    player_opportunity:   str = ""

    def to_dict(self) -> dict:
        return {
            "physical_behavior":    self.physical_behavior,
            "verbal_output":        self.verbal_output,
            "emotional_subtext":    self.emotional_subtext,
            "attention_directed_at": self.attention_directed_at,
            "escalation_signal":    self.escalation_signal,
            "player_opportunity":   self.player_opportunity,
        }


@dataclass
class ChildTurnResult:
    behavior_mode:   str         = ""
    regression_flags: Dict       = field(default_factory=dict)
    state_narrative: str         = ""
    child_output:    ChildOutput = field(default_factory=ChildOutput)

    def to_dict(self) -> dict:
        return {
            "behavior_mode":   self.behavior_mode,
            "regression_flags": self.regression_flags,
            "state_narrative": self.state_narrative,
            "child_output":    self.child_output.to_dict(),
        }


# ─── CHILD AI ─────────────────────────────────────────────────────────────────

class ChildAI:
    """
    AI-controlled child character.

    Usage — mirrors AIParent exactly:

        child = ChildAI(name="Lily")
        child.set_llm_generator(create_child_llm_generator("groq", api_key=...))

        # Each game turn:
        result = child.process_parent_action(
            event_description="Parents had a loud argument.",
            scene_context={
                "location":      "Living room",
                "present":       ["CHILD_ALONE"],
                "trigger_event": "Front door slammed",
                "time_of_day":   "EVENING",
                "recent_events": ["parents argued at dinner"],
            },
            act=2, day=5,   # age auto-calculated: 4y 10m
        )
        print(result.child_output.verbal_output)
        print(result.child_output.physical_behavior)
    """

    def __init__(self, name: str, llm_generator: Optional[Callable] = None):
        self.name              = name
        self.state             = ChildInternalState()
        self._llm_generator    = llm_generator
        self._sustained_high_stress_days = 0

    # ─── PUBLIC API ───────────────────────────────────────────────────────────

    def set_llm_generator(self, generator: Callable):
        """Set or replace the LLM generator. Same pattern as AIParent."""
        self._llm_generator = generator

    def advance_age(self, act: int, day: int):
        """
        Advance the child's age to the correct point in the story.
        Called automatically when act + day are passed to process_parent_action().
        """
        age = calculate_age_for_day(act, day)
        self.state.age_years  = age["age_years"]
        self.state.age_months = age["age_months"]

    def process_parent_action(
        self,
        event_description: str,
        scene_context: dict,
        act:  Optional[int] = None,
        day:  Optional[int] = None,
        sustained_high_stress_days: Optional[int] = None,
    ) -> ChildTurnResult:
        """
        Main entry point — equivalent of AIParent.process_input() + generate_response().

        1. Auto-advances age if act + day are provided
        2. Calls LLM to update internal state (PROMPT 2)
        3. Enforces: delta cap, behavior mode, regression flags
        4. Calls LLM to generate child output (PROMPT 3)
        5. Enforces: age-lock word caps, banned AI patterns
        6. Returns ChildTurnResult
        """
        # Age progression
        if act is not None and day is not None:
            self.advance_age(act, day)

        # Regression day counter (caller manages this)
        if sustained_high_stress_days is not None:
            self._sustained_high_stress_days = sustained_high_stress_days

        # Step 1 — update internal state
        state_result = self._update_state(event_description)

        # Step 2 — generate behavioral / verbal output
        child_output = self._generate_output(scene_context, state_result)

        return ChildTurnResult(
            behavior_mode    = self.state.active_behavior_mode,
            regression_flags = self._get_regression_flags(),
            state_narrative  = state_result.get("state_narrative", ""),
            child_output     = child_output,
        )

    # ─── STATE UPDATE — PROMPT 2 ──────────────────────────────────────────────

    def _update_state(self, event_description: str) -> dict:
        """Call LLM with PROMPT 2, then apply code-level enforcement."""
        system_prompt = self._build_system_prompt()
        user_prompt   = self._build_state_update_prompt(event_description)

        raw = self._call_llm(user_prompt, system_prompt, "child_state_update")
        parsed = self._extract_json(raw)

        if parsed:
            self._apply_state_update(parsed, event_description)
            return parsed

        # Fallback: keep current state unchanged
        self._append_session_event(event_description)
        return {
            "state_narrative":       "State update failed; child state preserved.",
            "suggested_child_trigger": "child waits quietly",
        }

    def _build_state_update_prompt(self, event_description: str) -> str:
        s = self.state
        return f"""TASK: You are the Child AI state engine. Process the following game event and update the child's internal emotional state variables.

CURRENT STATE:
{json.dumps(s.to_dict(), indent=2)}

EVENT THAT JUST HAPPENED:
{event_description}

---

REASONING INSTRUCTIONS (silently — do not include reasoning in output):

STEP 1 — CLASSIFY THE EVENT TYPE:
  A) Direct parent-child interaction (playing, feeding, yelling, ignoring, comforting)
  B) Parent-parent interaction witnessed by child (argument, cold silence, physical tension)
  C) Environmental change (moving house, new sibling, parent leaving, stranger entering)
  D) Child-initiated action (reaching for parent, acting out, hiding, showing affection)
  E) Accumulated stress (no single event, sustained low-grade neglect/tension)

STEP 2 — CALCULATE VARIABLE DELTAS:
  DIRECT WARM INTERACTION (plays, cuddles, responds to cry within 2 min):
  → attachment_security: +3 to +8  |  emotional_safety: +2 to +6
  → attention_need: -5 to -15      |  self_worth: +1 to +4

  DIRECT COLD/HARSH INTERACTION (yelling, shaming, ignoring distress):
  → attachment_security: -5 to -12 |  emotional_safety: -4 to -10
  → self_worth: -3 to -8           |  conflict_internalization: +2 to +6
  → attention_need: +5 to +10 (need rises when rejected)

  WITNESSED PARENT CONFLICT (argument child can see or hear):
  → emotional_safety: -(conflict_intensity × 0.12 to 0.18)
  → conflict_internalization: +(conflict_intensity × 0.08 to 0.12)
  → attachment_security: -(conflict_intensity × 0.05)
  → If conflict_intensity > 70: attention_need +10, emotional_expression -8

  CONSISTENT DAILY WARMTH: all vars drift toward 60-70 by +1 to +3
  CONSISTENT DAILY NEGLECT: all vars drift toward 20-30 by -1 to -4

  ACCUMULATION RULE: no single event moves any variable more than 15 points.

STEP 3 — DETERMINE BEHAVIOR MODE (priority: WITHDRAWN > DEFIANT > ANXIOUS > CONFIDENT):
  CONFIDENT_EXPRESSIVE: attachment_security > 65 AND emotional_safety > 60 AND self_worth > 55
  ANXIOUS_CLINGY:       attachment_security < 45 OR (attention_need > 70 AND emotional_safety < 50)
  WITHDRAWN_QUIET:      emotional_safety < 35 OR (conflict_internalization > 65 AND emotional_expression < 40)
  DEFIANT_REBELLIOUS:   attention_need > 75 AND emotional_safety < 55 AND child age > 18 months

STEP 4 — DETECT REGRESSION TRIGGERS:
  conflict_internalization > 70      → regression_risk: true
  household_stress > 75 for 3+ days → regression_active: true
  parent_conflict_intensity > 80     → acute_stress_response: true

---

OUTPUT FORMAT — return ONLY this JSON, no explanation, no markdown fences:

{{
  "updated_state": {{
    "age_years": {s.age_years},
    "age_months": {s.age_months},
    "child_state": {{
      "attachment_security": [0-100],
      "emotional_safety": [0-100],
      "self_worth": [0-100],
      "conflict_internalization": [0-100],
      "attention_need": [0-100],
      "emotional_expression": [0-100]
    }},
    "relationship_context": {{
      "parent_conflict_intensity": [0-100],
      "trust_between_parents": [0-100],
      "household_stress": [0-100]
    }}
  }},
  "active_behavior_mode": "[CONFIDENT_EXPRESSIVE|ANXIOUS_CLINGY|WITHDRAWN_QUIET|DEFIANT_REBELLIOUS]",
  "regression_flags": {{
    "regression_risk": [true|false],
    "regression_active": [true|false],
    "acute_stress_response": [true|false]
  }},
  "state_narrative": "[ONE sentence, max 20 words]",
  "suggested_child_trigger": "[one short phrase — what the child is about to do]"
}}"""

    def _apply_state_update(self, parsed: dict, event_description: str):
        """Apply parsed LLM response with code-level enforcement."""
        updated = parsed.get("updated_state", {})

        # Cap deltas on child_state fields
        cs = updated.get("child_state", {})
        for f in ChildInternalState._CHILD_FIELDS:
            if f in cs:
                original = getattr(self.state, f)
                new_val  = float(cs[f])
                delta    = new_val - original
                if abs(delta) > _MAX_DELTA:
                    new_val = original + (_MAX_DELTA if delta > 0 else -_MAX_DELTA)
                setattr(self.state, f, max(0.0, min(100.0, new_val)))

        # Clamp relationship_context (no delta cap needed — parent AI owns these)
        rc = updated.get("relationship_context", {})
        for f in ChildInternalState._CONTEXT_FIELDS:
            if f in rc:
                setattr(self.state, f, max(0.0, min(100.0, float(rc[f]))))

        # Age MUST NOT change — LLM cannot alter it
        # (already baked into the prompt, but enforce in code too)

        # Code-derive behavior mode — overrides whatever LLM returned
        self.state.active_behavior_mode = self._calculate_behavior_mode()

        # Append event to session window
        self._append_session_event(event_description)

    # ─── DIALOGUE GENERATION — PROMPT 3 ──────────────────────────────────────

    def _generate_output(self, scene_context: dict, state_result: dict) -> ChildOutput:
        """Call LLM with PROMPT 3, then enforce age locks."""
        regression_flags = self._get_regression_flags()

        # Regression drops effective age by 1 year
        effective_age_years = self.state.age_years
        if regression_flags.get("regression_active"):
            effective_age_years = max(0, self.state.age_years - 1)

        system_prompt  = self._build_system_prompt(effective_age_years)
        dialogue_prompt = self._build_dialogue_prompt(
            scene_context, state_result, regression_flags, effective_age_years
        )

        raw    = self._call_llm(dialogue_prompt, system_prompt, "child_dialogue")
        parsed = self._extract_json(raw)

        # Build ChildOutput from parsed JSON
        if parsed and "child_output" in parsed:
            raw_out = parsed["child_output"]
            output  = ChildOutput(
                physical_behavior    = raw_out.get("physical_behavior", ""),
                verbal_output        = raw_out.get("verbal_output", ""),
                emotional_subtext    = raw_out.get("emotional_subtext", ""),
                attention_directed_at = raw_out.get("attention_directed_at", "SELF"),
                escalation_signal    = raw_out.get("escalation_signal", "NONE"),
                player_opportunity   = raw_out.get("player_opportunity", ""),
            )
        else:
            # Fallback output
            output = ChildOutput(
                physical_behavior    = "[cries softly]" if effective_age_years < 2 else "[goes still and quiet]",
                verbal_output        = "",
                emotional_subtext    = "Dialogue generation failed; child is unresponsive.",
                attention_directed_at = "SELF",
                escalation_signal    = "NONE",
                player_opportunity   = "Approach the child gently and sit nearby.",
            )

        # Code-enforce age locks on the output
        output = self._enforce_age_locks(output, effective_age_years)

        # Guarantee physical_behavior is always present
        if not output.physical_behavior.strip():
            output.physical_behavior = "[cries softly]" if effective_age_years < 2 else "[goes still and quiet]"

        # Validate enum fields
        if output.escalation_signal not in {"NONE", "LOW", "MEDIUM", "HIGH"}:
            output.escalation_signal = "NONE"
        if output.attention_directed_at not in {"PLAYER_PARENT", "AI_PARENT", "BOTH", "SELF", "ENVIRONMENT"}:
            output.attention_directed_at = "SELF"

        return output

    def _build_dialogue_prompt(
        self,
        scene_context:     dict,
        state_result:      dict,
        regression_flags:  dict,
        effective_age_years: int,
    ) -> str:
        regression_note = (
            f"\nREGRESSION ACTIVE: Child speaks and behaves like a {effective_age_years}-year-old, not {self.state.age_years}."
            if regression_flags.get("regression_active") else ""
        )
        return f"""TASK: Generate the child's behavioral response for this scene.

CHILD STATE (post-update):
{json.dumps(self.state.to_dict(), indent=2)}

ACTIVE BEHAVIOR MODE: {self.state.active_behavior_mode}
REGRESSION FLAGS: {json.dumps(regression_flags)}{regression_note}

SCENE CONTEXT:
- Location:             {scene_context.get("location", "unknown")}
- Who is present:       {", ".join(scene_context.get("present", []))}
- What just happened:   {scene_context.get("trigger_event", "")}
- Child trigger:        {state_result.get("suggested_child_trigger", "")}
- Time of day:          {scene_context.get("time_of_day", "unknown")}
- Recent session events: {"; ".join(scene_context.get("recent_events", [])) or "none"}

---

GENERATION RULES:

RULE 1 — AGE LOCKS YOUR VOCABULARY. Effective age: {effective_age_years}y {self.state.age_months}m.
  Under 12 months: No verbal output. Physical only.
  12-23 months: Max 4 words. "No." "Mine." "Mama go?"
  24-35 months: Max 6 words. "Dat"/"dis"/"goed" — mispronounce R, L, TH.
  36-47 months: Max 10 words. Wrong logic, magical thinking, "Because" misused.
  48-59 months: Max 15 words. Negotiates, why-questions, lies to protect feelings.
  60-71 months: Max 22 words. Cause-effect, shame, comparisons. "Jake's dad doesn't yell."
  72-83 months: Max 22 words. Fairness, grudges. "You said you wouldn't fight. You lied."

RULE 2 — STATE DETERMINES TONE. emotional_safety < 30 makes even safe events feel threatening.

RULE 3 — NO AI DIALOGUE PATTERNS. BANNED:
  "I feel like..." / "I'm experiencing..." / "I understand that..." /
  "Can we talk about..." / "Would you mind..." / Balanced perspectives.

RULE 4 — USE THE BEHAVIOR MODE.
  CONFIDENT_EXPRESSIVE: "Watch me! Did you see?! Do it again?"
  ANXIOUS_CLINGY:       "Where are you going? You coming back right?"
  WITHDRAWN_QUIET:      "Fine." [silence] "...can I have water." [turns away]
  DEFIANT_REBELLIOUS:   "NO. I don't WANT to." [throws toy] "You can't make me."

RULE 5 — CONFLICT INTERNALIZATION SHOWS.
  > 55: "Was it because I was bad?" / "If I clean my room will they stop?"
  > 75: "It's okay." [said in a way that is utterly not okay]

RULE 6 — PHYSICAL BEHAVIOR IS AS IMPORTANT AS WORDS. Format in [brackets].
  Ages 0-3: output is MOSTLY physical. [cries until face goes red] [crawls to corner]

RULE 7 — SILENCE IS VALID. High stress + low emotional_expression = only physical, zero words.

RULE 8 — HARSH IS SOMETIMES CORRECT.
  DEFIANT + high attention_need + low trust_between_parents:
  "I hate you. I wish you weren't my dad." — developmentally real. Do not soften it.

---

OUTPUT FORMAT — return ONLY this JSON, no explanation, no markdown fences:

{{
  "child_output": {{
    "physical_behavior": "[What the child does — always include, never empty]",
    "verbal_output": "[Exact words in child's voice. Empty string if silent.]",
    "emotional_subtext": "[What child actually feels — game engine only, not shown to player]",
    "attention_directed_at": "[PLAYER_PARENT|AI_PARENT|BOTH|SELF|ENVIRONMENT]",
    "escalation_signal": "[NONE|LOW|MEDIUM|HIGH]",
    "player_opportunity": "[One sentence: what the player can do RIGHT NOW]"
  }}
}}"""

    # ─── SYSTEM PROMPT — PROMPT 1 ─────────────────────────────────────────────

    def _build_system_prompt(self, effective_age_years: Optional[int] = None) -> str:
        age_years  = effective_age_years if effective_age_years is not None else self.state.age_years
        age_months = self.state.age_months
        return f"""You are the internal simulation engine for a child character in a life simulation game.

The child's name is {self.name}. The current age is {age_years} years and {age_months} months old.

YOU ARE NOT AN ASSISTANT. You are not helpful, polite, or balanced by default.
You simulate a real child — messy, irrational, emotionally raw, age-limited in language and logic.

CORE IDENTITY RULES — NEVER BREAK THESE:

1. AGE IS EVERYTHING. The child thinks, speaks, and reasons ONLY at the level of their current age.
   - Age 0-1:  No words. Output is physical: crying, reaching, pulling away, laughing.
   - Age 1-2:  1-4 word fragments. "No." "Mine." "Mama go?" "No want."
   - Age 2-3:  Short sentences, present tense only, mispronunciations, tantrums, no logic.
   - Age 3-4:  "Why?" everything. Magical thinking. Egocentric. Dramatic.
   - Age 4-5:  Longer sentences, wrong grammar. Negotiates. Tests rules constantly.
   - Age 5-6:  Understands cause/effect. Feels shame. Compares self to others. Lies.
   - Age 6-7:  Understands fairness. Holds grudges. Wants to understand adult arguments.

2. NO AI SOFTNESS. Do NOT generate diplomatic output unless self_worth AND
   emotional_expression are BOTH above 75.

3. INTERNAL STATE DRIVES EVERYTHING. Variables are on 0-100 scale.
   State overrides the surface pleasantness of any scene.

4. CONFLICT EFFECTS ARE BRUTAL. When parent_conflict_intensity > 60, the child knows.
   High conflict → regression, acting out, peacemaking, or internalizing blame.

5. AUTHENTICITY OVER COMFORT. If the child is scared, angry, or shutting down — show it.
   Do not soften. Do not add hope. A child in a high-stress household is not okay."""

    # ─── CODE-LEVEL ENFORCEMENT ───────────────────────────────────────────────

    def _calculate_behavior_mode(self) -> str:
        """
        Code-derived behavior mode — always overrides the LLM's answer.
        Priority: WITHDRAWN > DEFIANT > ANXIOUS > CONFIDENT
        """
        s           = self.state
        total_months = s.age_years * 12 + s.age_months

        if s.emotional_safety < 35 or (s.conflict_internalization > 65 and s.emotional_expression < 40):
            return BehaviorMode.WITHDRAWN_QUIET

        if s.attention_need > 75 and s.emotional_safety < 55 and total_months > 18:
            return BehaviorMode.DEFIANT_REBELLIOUS

        if s.attachment_security < 45 or (s.attention_need > 70 and s.emotional_safety < 50):
            return BehaviorMode.ANXIOUS_CLINGY

        if s.attachment_security > 65 and s.emotional_safety > 60 and s.self_worth > 55:
            return BehaviorMode.CONFIDENT_EXPRESSIVE

        return BehaviorMode.ANXIOUS_CLINGY  # safe mid-range default

    def _get_regression_flags(self) -> dict:
        """Code-derived regression flags — always overrides the LLM's answer."""
        s = self.state
        return {
            "regression_risk":       s.conflict_internalization > 70,
            "regression_active":     s.household_stress > 75 and self._sustained_high_stress_days >= 3,
            "acute_stress_response": s.parent_conflict_intensity > 80,
        }

    def _enforce_age_locks(self, output: ChildOutput, effective_age_years: int) -> ChildOutput:
        """
        Enforce vocabulary and word-count limits by effective age.
        Strip banned AI-voice patterns.
        Same rules as the spec — enforced in code, not just in the prompt.
        """
        total_months = effective_age_years * 12 + self.state.age_months
        verbal = (output.verbal_output or "").strip()

        # Strip banned AI patterns first
        for pattern in _BANNED_AI_PATTERNS:
            if re.search(pattern, verbal, re.IGNORECASE):
                verbal = ""
                break

        # Apply word-count cap by age
        if total_months < 12:
            verbal = ""
            if not output.physical_behavior.strip():
                output.physical_behavior = "[cries or reacts physically]"
        elif total_months < 24:
            verbal = self._cap_words(verbal, 4)
        elif total_months < 36:
            verbal = self._cap_words(verbal, 6)
        elif total_months < 48:
            verbal = self._cap_words(verbal, 10)
        elif total_months < 60:
            verbal = self._cap_words(verbal, 15)
        elif total_months < 84:
            verbal = self._cap_words(verbal, 22)
        else:
            verbal = self._cap_words(verbal, 35)

        output.verbal_output = verbal
        return output

    @staticmethod
    def _cap_words(text: str, max_words: int) -> str:
        if not text:
            return text
        words = text.split()
        if len(words) <= max_words:
            return text
        truncated = " ".join(words[:max_words])
        truncated = re.sub(r"[,;:]$", "", truncated)
        if not truncated.endswith((".", "!", "?")):
            truncated += "."
        return truncated

    # ─── LLM CALL ─────────────────────────────────────────────────────────────

    def _call_llm(self, prompt: str, system_prompt: str, call_type: str) -> str:
        """
        Call the LLM generator. Passes system_prompt through context dict
        so child LLM backends can use the dynamic, age-aware system prompt.
        """
        if not self._llm_generator:
            return ""
        try:
            return self._llm_generator(
                prompt,
                {"system_prompt": system_prompt, "type": call_type},
            )
        except Exception as e:
            print(f"[ChildAI] LLM error ({call_type}): {e}")
            return ""

    # ─── JSON EXTRACTION ──────────────────────────────────────────────────────

    @staticmethod
    def _extract_json(raw_text: str) -> Optional[dict]:
        """Three-strategy JSON extraction — same as JS implementation."""
        if not raw_text:
            return None

        # Strategy 1: strip markdown fences, try whole string
        clean = re.sub(r"```json\s*", "", raw_text, flags=re.IGNORECASE)
        clean = re.sub(r"```\s*", "", clean).strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            pass

        # Strategy 2: find outermost { ... }
        start = clean.find("{")
        end   = clean.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(clean[start:end + 1])
            except json.JSONDecodeError:
                pass

        # Strategy 3: scan for any parseable object
        for i, ch in enumerate(clean):
            if ch == "{":
                for j in range(len(clean), i, -1):
                    if clean[j - 1] == "}":
                        try:
                            return json.loads(clean[i:j])
                        except json.JSONDecodeError:
                            pass
        return None

    # ─── SESSION HELPERS ──────────────────────────────────────────────────────

    def _append_session_event(self, event_description: str):
        self.state.session_events_today.append(event_description)
        self.state.session_events_today = \
            self.state.session_events_today[-_MAX_SESSION_EVENTS:]

    # ─── ACT-END LOCKING ──────────────────────────────────────────────────────

    def lock_attachment_style(self):
        """
        Called at end of Act 1. Locks the child's attachment style permanently.
        Mirrors ChildState.lock_attachment_style() in simulation/state_models.py
        but uses the 0-100 scale of ChildInternalState.
        """
        if self.state.attachment_style is not None:
            return  # already locked
        s   = self.state
        sec = s.attachment_security / 100
        safe = s.emotional_safety / 100
        conf = s.conflict_internalization / 100

        if sec >= 0.70 and safe >= 0.65:
            self.state.attachment_style = "SECURE"
        elif sec < 0.45 and conf > 0.60:
            self.state.attachment_style = "DISORGANIZED"
        elif sec < 0.50:
            self.state.attachment_style = "AVOIDANT"
        else:
            self.state.attachment_style = "ANXIOUS"

    def lock_archetype(self):
        """
        Called at end of Act 2. Locks the child's personality archetype permanently.
        Derived from the 6 core state variables.
        """
        if self.state.archetype is not None:
            return  # already locked
        s    = self.state
        conf = s.conflict_internalization / 100
        expr = s.emotional_expression / 100
        attn = s.attention_need / 100
        wrth = s.self_worth / 100
        sec  = s.attachment_security / 100

        if conf > 0.65 and expr < 0.40:
            self.state.archetype = "WITHDRAWN"
        elif attn > 0.70 and wrth < 0.50:
            self.state.archetype = "DEFIANT"
        elif conf > 0.50 and sec < 0.50:
            self.state.archetype = "ANXIOUS"
        else:
            self.state.archetype = "BALANCED"

    # ─── PERSISTENCE ──────────────────────────────────────────────────────────

    def get_state_summary(self) -> dict:
        """Summary for /status display. Mirrors AIParent.get_state_summary()."""
        s = self.state
        return {
            "name":                    self.name,
            "age":                     f"{s.age_years}y {s.age_months}m",
            "behavior_mode":           s.active_behavior_mode,
            "attachment_security":     s.attachment_security,
            "emotional_safety":        s.emotional_safety,
            "self_worth":              s.self_worth,
            "conflict_internalization": s.conflict_internalization,
            "attention_need":          s.attention_need,
            "emotional_expression":    s.emotional_expression,
            "regression_flags":        self._get_regression_flags(),
            "attachment_style":        s.attachment_style or "unlocked",
            "archetype":               s.archetype or "unlocked",
        }

    def to_dict(self) -> dict:
        return {
            "name":                    self.name,
            "state":                   self.state.to_dict(),
            "sustained_high_stress_days": self._sustained_high_stress_days,
            "attachment_style":        self.state.attachment_style,
            "archetype":               self.state.archetype,
        }

    @classmethod
    def from_dict(cls, data: dict, llm_generator: Optional[Callable] = None) -> "ChildAI":
        child = cls(name=data["name"], llm_generator=llm_generator)
        child.state = ChildInternalState.from_dict(data.get("state", {}))
        child._sustained_high_stress_days = data.get("sustained_high_stress_days", 0)
        child.state.attachment_style = data.get("attachment_style")
        child.state.archetype        = data.get("archetype")
        return child
