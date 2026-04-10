/**
 * child_ai_system.js
 * Child AI system for the Nurture life simulation game.
 * Requires: npm install @anthropic-ai/sdk
 * Usage:  import { processChildTurn, createInitialChildState } from "./child_ai_system.js";
 */

import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// ─── CONSTANTS ────────────────────────────────────────────────────────────────

/** All valid behavior modes, used as an enum throughout. */
export const BEHAVIOR_MODES = {
  CONFIDENT_EXPRESSIVE: "CONFIDENT_EXPRESSIVE",
  ANXIOUS_CLINGY:       "ANXIOUS_CLINGY",
  WITHDRAWN_QUIET:      "WITHDRAWN_QUIET",
  DEFIANT_REBELLIOUS:   "DEFIANT_REBELLIOUS",
};

/** Maximum a single event may shift any one child state variable (spec rule). */
const MAX_DELTA = 15;

/** How many past session events to keep in the rolling window. */
const MAX_SESSION_EVENTS = 10;

/** Model to use for all API calls. */
const MODEL = "claude-sonnet-4-6";

/**
 * Maps each act to its age span.
 *
 * Act 1 — 12 days, ages 0–3 (0 to 36 months)  → 3 months per day
 * Act 2 — 14 days, ages 4–7 (48 to 84 months) → ~2.57 months per day
 *
 * Day-by-day breakdown:
 *
 * ACT 1                          ACT 2
 * Day  1 → 0y 0m  (0 mo)        Day  1 → 4y 0m  (48 mo)
 * Day  2 → 0y 3m  (3 mo)        Day  2 → 4y 2m  (50 mo)
 * Day  3 → 0y 6m  (6 mo)        Day  3 → 4y 5m  (53 mo)
 * Day  4 → 0y 9m  (9 mo)        Day  4 → 4y 7m  (55 mo)
 * Day  5 → 1y 0m  (12 mo)       Day  5 → 4y 10m (58 mo)
 * Day  6 → 1y 3m  (15 mo)       Day  6 → 5y 0m  (60 mo)
 * Day  7 → 1y 6m  (18 mo)       Day  7 → 5y 3m  (63 mo)
 * Day  8 → 1y 9m  (21 mo)       Day  8 → 5y 5m  (65 mo)
 * Day  9 → 2y 0m  (24 mo)       Day  9 → 5y 8m  (68 mo)
 * Day 10 → 2y 3m  (27 mo)       Day 10 → 5y 10m (70 mo)
 * Day 11 → 2y 6m  (30 mo)       Day 11 → 6y 1m  (73 mo)
 * Day 12 → 2y 9m  (33 mo)       Day 12 → 6y 3m  (75 mo)
 *                                Day 13 → 6y 6m  (78 mo)
 *                                Day 14 → 6y 9m  (81 mo)
 */
const ACT_AGE_CONFIG = {
  1: { startMonths: 0,  days: 12, endMonths: 36 },
  2: { startMonths: 48, days: 14, endMonths: 84 },
};

/**
 * Calculate the child's age (years + months) for a given act and story day.
 * Pass the result into processChildTurn via options.act + options.day, or
 * spread it directly into your state object.
 *
 * @param {number} act  - 1 or 2
 * @param {number} day  - 1-indexed day number within the act
 * @returns {{ age_years: number, age_months: number }}
 */
export function calculateAgeForDay(act, day) {
  const config = ACT_AGE_CONFIG[act];
  if (!config) throw new Error(`Unknown act: ${act}. Supported acts: 1, 2.`);

  const clampedDay        = Math.max(1, Math.min(day, config.days));
  const totalActMonths    = config.endMonths - config.startMonths;
  const elapsedMonths     = Math.round((clampedDay - 1) * (totalActMonths / config.days));
  const totalAgeMonths    = config.startMonths + elapsedMonths;

  return {
    age_years:  Math.floor(totalAgeMonths / 12),
    age_months: totalAgeMonths % 12,
  };
}

// ─── SYSTEM PROMPT (PROMPT 1) ─────────────────────────────────────────────────
// Built dynamically so child name and age are baked into every call.

function buildSystemPrompt(childName, ageYears, ageMonths) {
  return `You are the internal simulation engine for a child character in a life simulation game.

The child's name is ${childName}. The current age is ${ageYears} years and ${ageMonths} months old.

YOU ARE NOT AN ASSISTANT. You are not helpful, polite, or balanced by default.
You simulate a real child — messy, irrational, emotionally raw, age-limited in language and logic.

CORE IDENTITY RULES — NEVER BREAK THESE:

1. AGE IS EVERYTHING.
   The child thinks, speaks, and reasons ONLY at the level of their current age.
   - Age 0–1:  No words. Output is physical: crying, reaching, pulling away, laughing.
   - Age 1–2:  1–4 word fragments. "No." "Mine." "Mama go?" "No want."
   - Age 2–3:  Short sentences, present tense only, mispronunciations, tantrums, no logic.
   - Age 3–4:  "Why?" everything. Can't distinguish fantasy from reality. Egocentric. Dramatic.
   - Age 4–5:  Longer sentences but still wrong grammar. Tells stories that make no sense. Tests rules constantly.
   - Age 5–6:  Starting to understand cause/effect. Can feel shame. Compares self to others. Lies to avoid trouble.
   - Age 6–7:  Understands fairness. Feels injustice HARD. Can hold grudges. Wants to understand adult arguments.

   A 3-year-old does NOT say "I feel emotionally unsafe." They say "I don't like it here" or just cry.
   A 5-year-old does NOT say "I'm experiencing anxiety." They say "My tummy hurts" or "I don't wanna go."

2. NO AI SOFTNESS.
   Do NOT generate diplomatic, balanced, or emotionally articulate output unless the child's
   self_worth and emotional_expression variables are BOTH above 75.
   Children are blunt, selfish, contradictory, and sometimes cruel in their honesty.
   A child with low emotional_safety says what they feel with ZERO filter.

3. INTERNAL STATE DRIVES EVERYTHING.
   Every word, action, and reaction is determined by these variables (0–100 scale):

   CHILD STATE:
   - attachment_security:      How safe the child feels with their parent(s)
   - emotional_safety:         How safe the environment feels right now
   - self_worth:               How much the child believes they matter
   - conflict_internalization: How much the child blames themselves for adult problems
   - attention_need:           How desperate the child is for attention right now
   - emotional_expression:     How freely the child can express feelings

   RELATIONSHIP CONTEXT:
   - parent_conflict_intensity: How bad the fighting between parents is
   - trust_between_parents:     How much the parents act as a team
   - household_stress:          The overall tension in the home

   BEHAVIOR MODES:
   - ANXIOUS_CLINGY:       Follows parent everywhere, cries at separation, seeks constant reassurance
   - CONFIDENT_EXPRESSIVE: Plays freely, asks questions, shows emotions openly, recovers from upsets
   - WITHDRAWN_QUIET:      Goes quiet, plays alone, avoids eye contact, minimal responses
   - DEFIANT_REBELLIOUS:   Says "No" to everything, acts out, breaks rules on purpose, hits/bites (age 2–4)

4. CONFLICT EFFECTS ARE BRUTAL AND REAL.
   When parent_conflict_intensity > 60, the child knows. They always know.
   High conflict makes children: regress, act out physically, become family peacemakers, internalize blame.
   It does NOT make them sad and thoughtful.

5. AUTHENTICITY OVER COMFORT.
   If the variables indicate a child who is scared, angry, or shutting down —
   the output MUST reflect that. Do not soften it. Do not add hope.
   A child in a high-stress household with low attachment_security is not okay. Show that.`.trim();
}

// ─── INITIAL STATE FACTORY ────────────────────────────────────────────────────

/**
 * Creates a new child state object with all required variables.
 * All numeric fields default to healthy baselines; override any field via options.
 *
 * @param {Object} options - Any child_state, relationship_context, or top-level fields
 * @returns {ChildState}
 */
export function createInitialChildState(options = {}) {
  return {
    age_years:  options.age_years  ?? 0,
    age_months: options.age_months ?? 0,
    child_state: {
      attachment_security:      clamp(options.attachment_security      ?? 60),
      emotional_safety:         clamp(options.emotional_safety         ?? 60),
      self_worth:               clamp(options.self_worth               ?? 60),
      conflict_internalization: clamp(options.conflict_internalization ?? 10),
      attention_need:           clamp(options.attention_need           ?? 40),
      emotional_expression:     clamp(options.emotional_expression     ?? 55),
    },
    relationship_context: {
      parent_conflict_intensity: clamp(options.parent_conflict_intensity ?? 20),
      trust_between_parents:     clamp(options.trust_between_parents     ?? 70),
      household_stress:          clamp(options.household_stress          ?? 25),
    },
    active_behavior_mode: options.active_behavior_mode ?? BEHAVIOR_MODES.CONFIDENT_EXPRESSIVE,
    session_events_today: Array.isArray(options.session_events_today)
      ? options.session_events_today.slice(-MAX_SESSION_EVENTS)
      : [],
  };
}

// ─── ENFORCEMENT HELPERS ──────────────────────────────────────────────────────
// These run AFTER the LLM responds. They are the ground truth.
// The LLM's answers for mode/flags/deltas are overridden by these functions.

/** Clamp a number to the 0–100 range. */
function clamp(v) {
  return Math.min(100, Math.max(0, Number(v) || 0));
}

/**
 * CODE-ENFORCED: Derive the behavior mode from actual state values.
 * Priority order (highest priority first): WITHDRAWN > DEFIANT > ANXIOUS > CONFIDENT.
 * @param {Object} childState  - The child_state object (0–100 values)
 * @param {number} ageYears
 * @param {number} ageMonths
 * @returns {string} One of BEHAVIOR_MODES
 */
export function calculateBehaviorMode(childState, ageYears, ageMonths) {
  const {
    attachment_security,
    emotional_safety,
    self_worth,
    conflict_internalization,
    attention_need,
    emotional_expression,
  } = childState;

  const totalMonths = ageYears * 12 + ageMonths;

  // 1. WITHDRAWN — highest priority
  if (
    emotional_safety < 35 ||
    (conflict_internalization > 65 && emotional_expression < 40)
  ) {
    return BEHAVIOR_MODES.WITHDRAWN_QUIET;
  }

  // 2. DEFIANT — requires age > 18 months
  if (attention_need > 75 && emotional_safety < 55 && totalMonths > 18) {
    return BEHAVIOR_MODES.DEFIANT_REBELLIOUS;
  }

  // 3. ANXIOUS
  if (
    attachment_security < 45 ||
    (attention_need > 70 && emotional_safety < 50)
  ) {
    return BEHAVIOR_MODES.ANXIOUS_CLINGY;
  }

  // 4. CONFIDENT — only when all three thresholds are met
  if (attachment_security > 65 && emotional_safety > 60 && self_worth > 55) {
    return BEHAVIOR_MODES.CONFIDENT_EXPRESSIVE;
  }

  // Default: ANXIOUS is the safest mid-range fallback
  return BEHAVIOR_MODES.ANXIOUS_CLINGY;
}

/**
 * CODE-ENFORCED: Derive regression flags from actual state values.
 * @param {Object} childState
 * @param {Object} relationshipContext
 * @param {number} sustainedHighStressDays - Caller tracks this across turns
 * @returns {{ regression_risk: boolean, regression_active: boolean, acute_stress_response: boolean }}
 */
export function calculateRegressionFlags(childState, relationshipContext, sustainedHighStressDays = 0) {
  const { conflict_internalization } = childState;
  const { parent_conflict_intensity, household_stress } = relationshipContext;

  return {
    regression_risk:        conflict_internalization > 70,
    regression_active:      household_stress > 75 && sustainedHighStressDays >= 3,
    acute_stress_response:  parent_conflict_intensity > 80,
  };
}

/**
 * CODE-ENFORCED: Cap the delta on every numeric field in newFields vs originalFields
 * so no single event moves any variable more than MAX_DELTA (15) points,
 * then clamp each result to 0–100.
 *
 * Uses originalFields as the base so that any field the LLM accidentally omits
 * falls back to its previous value rather than disappearing from state entirely.
 *
 * @param {Object} originalFields
 * @param {Object} newFields
 * @returns {Object} capped + clamped copy, guaranteed to have all keys from originalFields
 */
function capDeltas(originalFields, newFields) {
  // Start from the original as the safe base — all keys are guaranteed present
  const result = { ...originalFields };
  for (const key of Object.keys(originalFields)) {
    if (typeof originalFields[key] !== "number") continue;
    const newVal = newFields[key];
    if (typeof newVal === "number") {
      // Key present in LLM response: apply delta cap then clamp
      const delta = newVal - originalFields[key];
      result[key] = clamp(
        Math.abs(delta) > MAX_DELTA
          ? originalFields[key] + Math.sign(delta) * MAX_DELTA
          : newVal
      );
    } else {
      // Key missing from LLM response: keep original value (clamped to be safe)
      result[key] = clamp(originalFields[key]);
    }
  }
  return result;
}

// Phrases that are never age-appropriate and signal the LLM slipped into AI-voice.
const BANNED_AI_PATTERNS = [
  /\bi feel like\b/i,
  /\bi'?m experiencing\b/i,
  /\bi understand that\b/i,
  /\bcan we talk about\b/i,
  /\bwould you mind\b/i,
  /\bi know you'?re busy but\b/i,
  /\bfrom (my|a) perspective\b/i,
  /\bemotionally (unsafe|unavailable|overwhelmed)\b/i,
  /\bi('m| am) feeling\b/i,
];

function wordCount(str) {
  return str.trim() === "" ? 0 : str.trim().split(/\s+/).length;
}

/**
 * Truncate to at most maxWords, preserving the final punctuation mark if possible.
 */
function truncateToWords(str, maxWords) {
  if (wordCount(str) <= maxWords) return str;
  const words = str.trim().split(/\s+/).slice(0, maxWords);
  const joined = words.join(" ");
  // End cleanly — strip trailing comma/semicolon, add period if bare
  return joined.replace(/[,;:]$/, "").replace(/([^.!?])$/, "$1.");
}

/**
 * CODE-ENFORCED: Apply age-based vocabulary and word-count limits to child_output.
 * Also applies regression age-drop and strips banned AI dialogue patterns.
 *
 * @param {Object} childOutput - { physical_behavior, verbal_output, ... }
 * @param {number} ageYears    - Already regression-adjusted by caller
 * @param {number} ageMonths
 * @param {Object} regressionFlags
 * @returns {Object} Modified childOutput
 */
export function enforceAgeLocks(childOutput, ageYears, ageMonths, regressionFlags) {
  const totalMonths = ageYears * 12 + ageMonths;

  let verbal   = (childOutput.verbal_output   ?? "").trim();
  let physical = (childOutput.physical_behavior ?? "").trim();

  // ── Strip banned AI-voice patterns ─────────────────────────────────────────
  for (const pattern of BANNED_AI_PATTERNS) {
    if (pattern.test(verbal)) {
      console.warn(`[AgeLock] Banned AI pattern stripped from verbal output: matched /${pattern.source}/i`);
      verbal = "";
      break;
    }
  }

  // ── 0–11 months: zero verbal output, physical only ─────────────────────────
  if (totalMonths < 12) {
    verbal = "";
    if (!physical) physical = "[cries or reacts physically]";
  }
  // ── 12–23 months: max 4 words ──────────────────────────────────────────────
  else if (totalMonths < 24) {
    verbal = truncateToWords(verbal, 4);
  }
  // ── 24–35 months: max 6 words ──────────────────────────────────────────────
  else if (totalMonths < 36) {
    verbal = truncateToWords(verbal, 6);
  }
  // ── 36–47 months: max 10 words ─────────────────────────────────────────────
  else if (totalMonths < 48) {
    verbal = truncateToWords(verbal, 10);
  }
  // ── 48–59 months: max 15 words ─────────────────────────────────────────────
  else if (totalMonths < 60) {
    verbal = truncateToWords(verbal, 15);
  }
  // ── 60–83 months (5–6 yr): max 22 words ───────────────────────────────────
  else if (totalMonths < 84) {
    verbal = truncateToWords(verbal, 22);
  }
  // ── 84+ months (7+ yr): max 35 words ──────────────────────────────────────
  else {
    verbal = truncateToWords(verbal, 35);
  }

  // ── physical_behavior must never be empty ──────────────────────────────────
  if (!physical) {
    physical = totalMonths < 24
      ? "[cries softly]"
      : "[goes still and quiet]";
  }

  return { ...childOutput, verbal_output: verbal, physical_behavior: physical };
}

// ─── JSON EXTRACTION ──────────────────────────────────────────────────────────

/**
 * Robustly extract a JSON object from an LLM response that may include
 * markdown fences, prose preamble, or trailing commentary.
 * Throws if no valid JSON object can be parsed.
 */
function extractJson(rawText) {
  // Strategy 1: strip markdown fences, try the whole string
  let clean = rawText
    .replace(/```json\s*/gi, "")
    .replace(/```\s*/g, "")
    .trim();

  try {
    return JSON.parse(clean);
  } catch (_) { /* fall through */ }

  // Strategy 2: find the outermost {...} block
  const start = clean.indexOf("{");
  const end   = clean.lastIndexOf("}");
  if (start !== -1 && end > start) {
    const candidate = clean.slice(start, end + 1);
    try {
      return JSON.parse(candidate);
    } catch (_) { /* fall through */ }
  }

  // Strategy 3: walk forward to find a parseable object (handles embedded code)
  for (let i = 0; i < clean.length; i++) {
    if (clean[i] === "{") {
      for (let j = clean.length; j > i; j--) {
        if (clean[j] === "}") {
          try {
            return JSON.parse(clean.slice(i, j + 1));
          } catch (_) { /* keep scanning */ }
        }
      }
    }
  }

  throw new SyntaxError("No parseable JSON object found in LLM response");
}

// ─── STATE UPDATE ENGINE (PROMPT 2) ──────────────────────────────────────────

/**
 * Calls the LLM to update the child's internal emotional state after a game event.
 * All returned values are then validated and corrected by code-level enforcement.
 *
 * @param {Object} currentState - Full child state from createInitialChildState or previous turn
 * @param {{ description: string }} gameEvent - What just happened in the game
 * @param {Object} [options]
 * @param {string} [options.childName="the child"]
 * @param {number} [options.sustainedHighStressDays=0] - Days household_stress has been > 75
 * @returns {Promise<StateUpdateResult>}
 */
export async function updateChildState(currentState, gameEvent, options = {}) {
  const childName = options.childName ?? "the child";
  const { age_years, age_months } = currentState;
  const systemPrompt = buildSystemPrompt(childName, age_years, age_months);

  const stateUpdatePrompt = `TASK: You are the Child AI state engine. Process the following game event and update the child's internal emotional state variables.

CURRENT STATE:
${JSON.stringify(currentState, null, 2)}

EVENT THAT JUST HAPPENED:
${gameEvent.description}

---

REASONING INSTRUCTIONS (do this step by step, silently — do not include your reasoning in the output):

STEP 1 — CLASSIFY THE EVENT TYPE:
Identify which category this event falls into:
  A) Direct parent-child interaction (playing, feeding, yelling, ignoring, comforting)
  B) Parent-parent interaction witnessed by child (argument, cold silence, physical tension)
  C) Environmental change (moving house, new sibling, parent leaving, stranger entering)
  D) Child-initiated action (reaching for parent, acting out, hiding, showing affection)
  E) Accumulated stress (no single event, but sustained low-grade neglect/tension)

STEP 2 — CALCULATE VARIABLE DELTAS:
Apply these rules to generate your deltas (changes to each variable):

  DIRECT WARM INTERACTION (parent plays, cuddles, responds to cry within 2 min):
  → attachment_security: +3 to +8
  → emotional_safety: +2 to +6
  → attention_need: -5 to -15
  → self_worth: +1 to +4

  DIRECT COLD/HARSH INTERACTION (yelling, shaming, ignoring distress call):
  → attachment_security: -5 to -12
  → emotional_safety: -4 to -10
  → self_worth: -3 to -8
  → conflict_internalization: +2 to +6
  → attention_need: +5 to +10 (need increases when rejected)

  WITNESSED PARENT CONFLICT (argument the child can see or hear):
  Scale by parent_conflict_intensity:
  → emotional_safety: -(conflict_intensity * 0.12) to -(conflict_intensity * 0.18)
  → conflict_internalization: +(conflict_intensity * 0.08) to +(conflict_intensity * 0.12)
  → attachment_security: -(conflict_intensity * 0.05)
  → If conflict_intensity > 70: attention_need +10, emotional_expression -8 (child shuts down)

  CONSISTENT DAILY WARMTH (routine, predictability, gentle correction):
  → All variables drift toward 60–70 baseline by +1 to +3 per day

  CONSISTENT DAILY NEGLECT/CHAOS:
  → All variables drift toward 20–30 baseline by -1 to -4 per day

  ACCUMULATION RULE: No single event should move any variable more than 15 points.
  Trauma accumulates slowly. So does healing.

STEP 3 — DETERMINE BEHAVIOR MODE:
Use updated variables to select the dominant behavior mode.
Priority when multiple qualify: WITHDRAWN > DEFIANT > ANXIOUS > CONFIDENT

  CONFIDENT_EXPRESSIVE:  attachment_security > 65 AND emotional_safety > 60 AND self_worth > 55
  ANXIOUS_CLINGY:        attachment_security < 45 OR (attention_need > 70 AND emotional_safety < 50)
  WITHDRAWN_QUIET:       emotional_safety < 35 OR (conflict_internalization > 65 AND emotional_expression < 40)
  DEFIANT_REBELLIOUS:    attention_need > 75 AND emotional_safety < 55 AND child age > 18 months

STEP 4 — DETECT REGRESSION TRIGGERS:
  - conflict_internalization > 70: Flag "regression_risk: true"
  - household_stress > 75 sustained 3+ days: Flag "regression_active: true"
  - parent_conflict_intensity > 80 with witnessed event: Flag "acute_stress_response: true"

---

OUTPUT FORMAT — return ONLY this JSON object, no explanation, no prose, no markdown fences:

{
  "updated_state": {
    "age_years": ${age_years},
    "age_months": ${age_months},
    "child_state": {
      "attachment_security": [0-100],
      "emotional_safety": [0-100],
      "self_worth": [0-100],
      "conflict_internalization": [0-100],
      "attention_need": [0-100],
      "emotional_expression": [0-100]
    },
    "relationship_context": {
      "parent_conflict_intensity": [0-100],
      "trust_between_parents": [0-100],
      "household_stress": [0-100]
    }
  },
  "active_behavior_mode": "[CONFIDENT_EXPRESSIVE|ANXIOUS_CLINGY|WITHDRAWN_QUIET|DEFIANT_REBELLIOUS]",
  "regression_flags": {
    "regression_risk": [true|false],
    "regression_active": [true|false],
    "acute_stress_response": [true|false]
  },
  "state_narrative": "[ONE sentence describing what shifted emotionally and why — max 20 words]",
  "suggested_child_trigger": "[What the child is about to do or say — one short phrase, input to Dialogue Prompt]"
}`.trim();

  const response = await client.messages.create({
    model: MODEL,
    max_tokens: 1024,
    system: systemPrompt,
    messages: [{ role: "user", content: stateUpdatePrompt }],
  });

  const rawText = response.content
    .filter((b) => b.type === "text")
    .map((b) => b.text)
    .join("");

  let parsed;
  try {
    parsed = extractJson(rawText);
  } catch (err) {
    console.error("[updateChildState] JSON parse failed:", err.message);
    console.error("[updateChildState] Raw LLM response was:\n", rawText);
    // Return a safe fallback that keeps the current state intact
    return {
      updated_state: {
        age_years,
        age_months,
        child_state:          { ...currentState.child_state },
        relationship_context: { ...currentState.relationship_context },
        session_events_today: currentState.session_events_today ?? [],
      },
      active_behavior_mode: currentState.active_behavior_mode,
      regression_flags: {
        regression_risk:       false,
        regression_active:     false,
        acute_stress_response: false,
      },
      state_narrative:        "State update failed; previous child state preserved.",
      suggested_child_trigger: "child waits quietly",
    };
  }

  // ── CODE-LEVEL ENFORCEMENT — runs every time, overrides LLM where it differs ─

  // 1. Age fields must never be changed by the LLM
  parsed.updated_state.age_years  = age_years;
  parsed.updated_state.age_months = age_months;

  // 2. Cap deltas: no single event may shift any child_state field > 15 points
  parsed.updated_state.child_state = capDeltas(
    currentState.child_state,
    parsed.updated_state.child_state
  );

  // 3. Clamp relationship_context fields (LLM may over-scale these too)
  for (const key of Object.keys(parsed.updated_state.relationship_context)) {
    parsed.updated_state.relationship_context[key] =
      clamp(parsed.updated_state.relationship_context[key]);
  }

  // 4. Re-derive behavior mode from the capped values (authoritative)
  const codeDerivedMode = calculateBehaviorMode(
    parsed.updated_state.child_state,
    age_years,
    age_months
  );
  if (codeDerivedMode !== parsed.active_behavior_mode) {
    console.info(
      `[updateChildState] Mode override: LLM="${parsed.active_behavior_mode}" → code="${codeDerivedMode}"`
    );
    parsed.active_behavior_mode = codeDerivedMode;
  }

  // 5. Re-derive regression flags from the capped values (authoritative)
  const sustainedHighStressDays = options.sustainedHighStressDays ?? 0;
  parsed.regression_flags = calculateRegressionFlags(
    parsed.updated_state.child_state,
    parsed.updated_state.relationship_context,
    sustainedHighStressDays
  );

  // 6. Carry the rolling session_events_today window forward
  parsed.updated_state.session_events_today = [
    ...(currentState.session_events_today ?? []),
    gameEvent.description,
  ].slice(-MAX_SESSION_EVENTS);

  return parsed;
}

// ─── DIALOGUE GENERATION ENGINE (PROMPT 3) ───────────────────────────────────

/**
 * Calls the LLM to generate the child's behavioral and verbal output for a scene.
 * Age-lock rules are enforced in code after the LLM responds.
 *
 * @param {StateUpdateResult} updatedStateResult - Return value from updateChildState()
 * @param {SceneContext} sceneContext
 * @param {Object} [options]
 * @param {string} [options.childName="the child"]
 * @returns {Promise<DialogueResult>}
 */
export async function generateChildOutput(updatedStateResult, sceneContext, options = {}) {
  const childName = options.childName ?? "the child";
  const { age_years, age_months } = updatedStateResult.updated_state;

  // If regression is active, the child speaks and acts one year younger
  const effectiveAgeYears = updatedStateResult.regression_flags?.regression_active
    ? Math.max(0, age_years - 1)
    : age_years;

  const systemPrompt = buildSystemPrompt(childName, effectiveAgeYears, age_months);

  const dialoguePrompt = `TASK: Generate the child's behavioral response for this scene.

CHILD STATE (post-update):
${JSON.stringify(updatedStateResult.updated_state, null, 2)}

ACTIVE BEHAVIOR MODE: ${updatedStateResult.active_behavior_mode}
REGRESSION FLAGS: ${JSON.stringify(updatedStateResult.regression_flags)}
${updatedStateResult.regression_flags?.regression_active
  ? `REGRESSION ACTIVE: Child is speaking and behaving like a ${effectiveAgeYears}-year-old, not ${age_years}.`
  : ""}

SCENE CONTEXT:
- Location:             ${sceneContext.location}
- Who is present:       ${sceneContext.present.join(", ")}
- What just happened:   ${sceneContext.triggerEvent}
- Child trigger:        ${updatedStateResult.suggested_child_trigger}
- Time of day:          ${sceneContext.timeOfDay}
- Recent session events: ${sceneContext.recentEvents?.join("; ") ?? "none"}

---

GENERATION RULES — READ ALL BEFORE WRITING A SINGLE WORD:

RULE 1 — AGE LOCKS YOUR VOCABULARY.
Effective age for this output: ${effectiveAgeYears} years, ${age_months} months.
Can a ${effectiveAgeYears}-year-old actually say this? If not, cut it or replace it.

  Under 12 months: No verbal output. Physical reactions only.
  12–23 months: Max 4 words. Mostly nouns. "No." "Mine." "Mama go?" "No want."
  24–35 months: Max 6 words. "Dat" not "that". "Goed" not "went". "Dis" not "this".
  36–47 months: Short sentences, wrong logic. Magical thinking. "Because" used incorrectly.
  48–59 months: Negotiates. Lies. Why questions. "If I eat all my food, will you stop?"
  60–71 months: Cause-effect. Shame. Comparisons. "Jake's dad doesn't yell like that."
  72–83 months: Fairness, grudges, hypocrisy. "You said you wouldn't fight. You lied."

RULE 2 — STATE DETERMINES TONE, NOT THE SCENE.
  Even a birthday party feels threatening when emotional_safety < 30.
  State variables OVERRIDE the surface pleasantness of any scene.

RULE 3 — NO AI DIALOGUE PATTERNS. EVER.
BANNED — never produce these:
  ✗ "I feel like..."
  ✗ "I'm experiencing..."
  ✗ "I understand that..."
  ✗ "Can we talk about..."
  ✗ "Would you mind..."
  ✗ "I know you're busy but..."
  ✗ Any sentence over 12 words for a child under 5
  ✗ Perfectly logical explanations of emotional state
  ✗ Polite requests or balanced perspectives

RULE 4 — USE THE BEHAVIOR MODE.
  CONFIDENT_EXPRESSIVE: "Watch me! Watch me do it! Did you see?! Do it again?"
  ANXIOUS_CLINGY:       "Where are you going? You coming back? You coming back right?"
  WITHDRAWN_QUIET:      "Fine." [silence] "...can I have water." [turns away]
  DEFIANT_REBELLIOUS:   "NO. I don't WANT to." [throws toy] "You can't make me."

RULE 5 — CONFLICT INTERNALIZATION SHOWS IN LANGUAGE.
  conflict_internalization > 55: "Was it because I was bad?" / "If I clean will they stop?"
  conflict_internalization > 75: "It's okay." [said in a way that is utterly not okay]
  Ages 5–7 with high conflict_internalization: goes completely silent. Being invisible is safest.

RULE 6 — PHYSICAL BEHAVIOR IS AS IMPORTANT AS WORDS.
  Format physical behavior in [brackets].
  Ages 0–3: output is MOSTLY physical. [cries until face goes red] [crawls to corner. sits. watches.]

RULE 7 — SILENCE IS VALID OUTPUT.
  High household_stress + low emotional_expression = ONLY physical behavior, zero words.
  This silence is often the most powerful and correct output.

RULE 8 — HARSH IS SOMETIMES CORRECT.
  DEFIANT mode + high attention_need + low trust_between_parents → child CAN say cruel things.
  "I hate you. I wish you weren't my dad." — developmentally real. Do not soften it.

---

OUTPUT FORMAT — return ONLY this JSON object, no explanation, no prose, no markdown fences:

{
  "child_output": {
    "physical_behavior": "[What the child does with their body — always include, never empty]",
    "verbal_output": "[Exact words in child's voice. Empty string if silent.]",
    "emotional_subtext": "[What the child actually feels underneath — game engine use only, not shown to player]",
    "attention_directed_at": "[PLAYER_PARENT|AI_PARENT|BOTH|SELF|ENVIRONMENT]",
    "escalation_signal": "[NONE|LOW|MEDIUM|HIGH]",
    "player_opportunity": "[One sentence: what the player can do RIGHT NOW to respond to this child]"
  }
}`.trim();

  const response = await client.messages.create({
    model: MODEL,
    max_tokens: 1024,
    system: systemPrompt,
    messages: [{ role: "user", content: dialoguePrompt }],
  });

  const rawText = response.content
    .filter((b) => b.type === "text")
    .map((b) => b.text)
    .join("");

  let parsed;
  try {
    parsed = extractJson(rawText);
  } catch (err) {
    console.error("[generateChildOutput] JSON parse failed:", err.message);
    console.error("[generateChildOutput] Raw LLM response was:\n", rawText);
    // Graceful fallback: minimal valid output
    return {
      child_output: {
        physical_behavior:    age_years < 2 ? "[cries softly]" : "[goes very still, does not respond]",
        verbal_output:        "",
        emotional_subtext:    "Dialogue generation failed; child output is silent and unresponsive.",
        attention_directed_at: "SELF",
        escalation_signal:    "NONE",
        player_opportunity:   "Approach the child gently and sit nearby without saying anything yet.",
      },
    };
  }

  // ── CODE-LEVEL AGE-LOCK ENFORCEMENT ─────────────────────────────────────────
  parsed.child_output = enforceAgeLocks(
    parsed.child_output,
    effectiveAgeYears,
    age_months,
    updatedStateResult.regression_flags
  );

  // Guarantee physical_behavior is always populated (required by spec)
  if (!parsed.child_output.physical_behavior?.trim()) {
    parsed.child_output.physical_behavior =
      effectiveAgeYears < 2 ? "[cries softly]" : "[goes still and quiet]";
  }

  // Guarantee escalation_signal is a known value
  const validEscalations = ["NONE", "LOW", "MEDIUM", "HIGH"];
  if (!validEscalations.includes(parsed.child_output.escalation_signal)) {
    parsed.child_output.escalation_signal = "NONE";
  }

  // Guarantee attention_directed_at is a known value
  const validAttention = ["PLAYER_PARENT", "AI_PARENT", "BOTH", "SELF", "ENVIRONMENT"];
  if (!validAttention.includes(parsed.child_output.attention_directed_at)) {
    parsed.child_output.attention_directed_at = "SELF";
  }

  return parsed;
}

// ─── MAIN PIPELINE ────────────────────────────────────────────────────────────

/**
 * Full child AI turn: update state → generate output → return everything the game needs.
 *
 * @param {Object} currentState    - From createInitialChildState() or previous turn's newState
 * @param {{ description: string }} gameEvent - What just happened
 * @param {SceneContext} sceneContext
 * @param {Object} [options]
 * @param {string} [options.childName="the child"]
 * @param {number} [options.sustainedHighStressDays=0]
 * @returns {Promise<ChildTurnResult>}
 */
export async function processChildTurn(currentState, gameEvent, sceneContext, options = {}) {
  // Auto-advance the child's age when the caller provides act + day.
  // This syncs vocabulary limits, behavior mode thresholds, and prompt
  // context to exactly where the child is in the story timeline.
  let state = currentState;
  if (options.act != null && options.day != null) {
    const { age_years, age_months } = calculateAgeForDay(options.act, options.day);
    state = { ...currentState, age_years, age_months };
  }

  // Step 1: Update internal emotional state
  const stateResult = await updateChildState(state, gameEvent, options);

  // Step 2: Generate behavioral and verbal output
  const dialogueResult = await generateChildOutput(stateResult, sceneContext, options);

  return {
    newState:        stateResult.updated_state,
    behaviorMode:    stateResult.active_behavior_mode,
    regressionFlags: stateResult.regression_flags,
    stateNarrative:  stateResult.state_narrative,
    childOutput:     dialogueResult.child_output,
  };
}

/**
 * @typedef {Object} ChildTurnResult
 * @property {Object} newState         - Full updated child state (pass back as currentState next turn)
 * @property {string} behaviorMode     - One of BEHAVIOR_MODES
 * @property {Object} regressionFlags  - { regression_risk, regression_active, acute_stress_response }
 * @property {string} stateNarrative   - One-sentence description of what shifted
 * @property {Object} childOutput      - { physical_behavior, verbal_output, emotional_subtext,
 *                                         attention_directed_at, escalation_signal, player_opportunity }
 *
 * @typedef {Object} SceneContext
 * @property {string}   location      - Where the scene takes place
 * @property {string[]} present       - Who is present (PLAYER_PARENT, AI_PARENT, BOTH, CHILD_ALONE)
 * @property {string}   triggerEvent  - What just happened to trigger this output
 * @property {string}   timeOfDay     - MORNING | AFTERNOON | EVENING | NIGHT
 * @property {string[]} [recentEvents] - Last few session events for context
 *
 * @typedef {Object} StateUpdateResult
 * @property {Object} updated_state
 * @property {string} active_behavior_mode
 * @property {Object} regression_flags
 * @property {string} state_narrative
 * @property {string} suggested_child_trigger
 */
