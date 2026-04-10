/**
 * test_child_ai.js
 * Test runner for the Child AI system.
 * Usage: node --env-file=../.env test_child_ai.js
 *
 * Runs three scenarios that cover the main edge cases:
 *   1. SPEC EXAMPLE  — Act 2 Day 2  (4y 2m)  ANXIOUS_CLINGY, witnessed argument
 *   2. INFANT        — Act 1 Day 4  (0y 9m)  pre-verbal, warm interaction
 *   3. REGRESSION    — Act 2 Day 11 (6y 1m)  WITHDRAWN, active regression → speaks like 5yr
 */

import {
  processChildTurn,
  createInitialChildState,
  calculateAgeForDay,
  calculateBehaviorMode,
  calculateRegressionFlags,
  enforceAgeLocks,
  BEHAVIOR_MODES,
} from "./child_ai_system.js";

// ─── PRETTY PRINTER ───────────────────────────────────────────────────────────

function printResult(label, result) {
  const div = "─".repeat(60);
  console.log(`\n${"═".repeat(60)}`);
  console.log(`  ${label}`);
  console.log(`${"═".repeat(60)}`);
  console.log(`  Age:              ${result.newState.age_years}y ${result.newState.age_months}m`);
  console.log(`  Behavior Mode:    ${result.behaviorMode}`);
  console.log(`  Regression Flags: ${JSON.stringify(result.regressionFlags)}`);
  console.log(`  State Narrative:  ${result.stateNarrative}`);
  console.log(div);
  console.log(`  Physical:  ${result.childOutput.physical_behavior}`);
  console.log(`  Verbal:    ${result.childOutput.verbal_output || "[silence]"}`);
  console.log(`  Subtext:   ${result.childOutput.emotional_subtext}`);
  console.log(`  Directed:  ${result.childOutput.attention_directed_at}`);
  console.log(`  Escalation: ${result.childOutput.escalation_signal}`);
  console.log(`  Player Opportunity: ${result.childOutput.player_opportunity}`);
  console.log(div);
  console.log(`  Updated child_state:`);
  for (const [k, v] of Object.entries(result.newState.child_state)) {
    console.log(`    ${k.padEnd(26)} ${v}`);
  }
}

function printUnitResults(passed, failed) {
  const total = passed + failed;
  console.log(`\n${"═".repeat(60)}`);
  console.log(`  UNIT TESTS: ${passed}/${total} passed${failed > 0 ? ` (${failed} FAILED)` : ""}`);
  console.log(`${"═".repeat(60)}`);
}

// ─── UNIT TESTS (no API calls) ────────────────────────────────────────────────

function runUnitTests() {
  let passed = 0;
  let failed = 0;

  function assert(description, condition) {
    if (condition) {
      console.log(`  ✓ ${description}`);
      passed++;
    } else {
      console.error(`  ✗ FAIL: ${description}`);
      failed++;
    }
  }

  console.log("\n── calculateAgeForDay ───────────────────────────────────────");

  // Act 1 anchors
  const a1d1  = calculateAgeForDay(1, 1);
  const a1d5  = calculateAgeForDay(1, 5);
  const a1d9  = calculateAgeForDay(1, 9);
  const a1d12 = calculateAgeForDay(1, 12);

  assert("Act1 Day1  → 0y 0m  (newborn)",        a1d1.age_years  === 0 && a1d1.age_months  === 0);
  assert("Act1 Day5  → 1y 0m  (first words)",     a1d5.age_years  === 1 && a1d5.age_months  === 0);
  assert("Act1 Day9  → 2y 0m  (2-word sentences)", a1d9.age_years  === 2 && a1d9.age_months  === 0);
  assert("Act1 Day12 → 2y 9m  (end of act 1)",    a1d12.age_years === 2 && a1d12.age_months === 9);

  // Act 2 anchors
  const a2d1  = calculateAgeForDay(2, 1);
  const a2d6  = calculateAgeForDay(2, 6);
  const a2d11 = calculateAgeForDay(2, 11);
  const a2d14 = calculateAgeForDay(2, 14);

  assert("Act2 Day1  → 4y 0m  (school entry)",    a2d1.age_years  === 4 && a2d1.age_months  === 0);
  assert("Act2 Day6  → 5y 0m  (cause-effect)",    a2d6.age_years  === 5 && a2d6.age_months  === 0);
  assert("Act2 Day11 → 6y 1m  (fairness/grudges)", a2d11.age_years === 6 && a2d11.age_months === 1);
  assert("Act2 Day14 → 6y 9m  (end of act 2)",    a2d14.age_years === 6 && a2d14.age_months === 9);

  // Clamp: day 0 treated as day 1, day 99 treated as last valid day
  const clampLow  = calculateAgeForDay(1, 0);
  const clampHigh = calculateAgeForDay(2, 99);
  assert("calculateAgeForDay clamps day 0  → same as day 1",  clampLow.age_years  === 0 && clampLow.age_months  === 0);
  assert("calculateAgeForDay clamps day 99 → same as day 14", clampHigh.age_years === 6 && clampHigh.age_months === 9);

  // Error on unknown act
  let threw = false;
  try { calculateAgeForDay(3, 1); } catch (_) { threw = true; }
  assert("calculateAgeForDay throws on unknown act", threw);

  // Word limits align with act/day progression
  // Act 1 Day 4 (0y 9m) → pre-verbal, enforceAgeLocks must zero verbal
  const a1d4Age = calculateAgeForDay(1, 4);   // { age_years: 0, age_months: 9 }
  const preVerbal = enforceAgeLocks(
    { verbal_output: "Mama no go", physical_behavior: "[reaches]" },
    a1d4Age.age_years, a1d4Age.age_months, {}
  );
  assert("Act1 Day4 (0y 9m): verbal zeroed by age-lock", preVerbal.verbal_output === "");

  // Act 1 Day 5 (1y 0m) → 4-word cap unlocks
  const a1d5Age = calculateAgeForDay(1, 5);   // { age_years: 1, age_months: 0 }
  const firstWords = enforceAgeLocks(
    { verbal_output: "Mama don't go please stay", physical_behavior: "[clings]" },
    a1d5Age.age_years, a1d5Age.age_months, {}
  );
  const firstWordsCount = firstWords.verbal_output.trim().split(/\s+/).filter(Boolean).length;
  assert(`Act1 Day5 (1y 0m): verbal capped at 4 words (got ${firstWordsCount})`, firstWordsCount <= 4);

  // Act 2 Day 2 (4y 2m) → 15-word cap
  const a2d2Age = calculateAgeForDay(2, 2);   // { age_years: 4, age_months: 2 }
  const longSentence = enforceAgeLocks(
    { verbal_output: "If I eat all my food and clean my room and be really really really good will you and daddy stop fighting please", physical_behavior: "[stands still]" },
    a2d2Age.age_years, a2d2Age.age_months, {}
  );
  const longCount = longSentence.verbal_output.trim().split(/\s+/).filter(Boolean).length;
  assert(`Act2 Day2 (4y 2m): verbal capped at 15 words (got ${longCount})`, longCount <= 15);

  console.log("\n── calculateBehaviorMode ────────────────────────────────────");

  assert(
    "WITHDRAWN beats ANXIOUS (priority test)",
    calculateBehaviorMode(
      { attachment_security: 30, emotional_safety: 25, self_worth: 40,
        conflict_internalization: 80, attention_need: 85, emotional_expression: 30 },
      4, 0
    ) === BEHAVIOR_MODES.WITHDRAWN_QUIET
  );

  assert(
    "DEFIANT fires when age > 18 months",
    calculateBehaviorMode(
      { attachment_security: 55, emotional_safety: 45, self_worth: 50,
        conflict_internalization: 30, attention_need: 80, emotional_expression: 50 },
      2, 0
    ) === BEHAVIOR_MODES.DEFIANT_REBELLIOUS
  );

  assert(
    "DEFIANT does NOT fire under 18 months",
    calculateBehaviorMode(
      { attachment_security: 55, emotional_safety: 45, self_worth: 50,
        conflict_internalization: 30, attention_need: 80, emotional_expression: 50 },
      1, 0
    ) !== BEHAVIOR_MODES.DEFIANT_REBELLIOUS
  );

  assert(
    "CONFIDENT fires when all thresholds met",
    calculateBehaviorMode(
      { attachment_security: 80, emotional_safety: 75, self_worth: 70,
        conflict_internalization: 10, attention_need: 30, emotional_expression: 65 },
      5, 6
    ) === BEHAVIOR_MODES.CONFIDENT_EXPRESSIVE
  );

  console.log("\n── calculateRegressionFlags ─────────────────────────────────");

  const f1 = calculateRegressionFlags({ conflict_internalization: 75 }, { parent_conflict_intensity: 50, household_stress: 60 }, 0);
  assert("regression_risk=true  when conflict_internalization > 70", f1.regression_risk === true);
  assert("regression_active=false when sustained_days < 3",         f1.regression_active === false);

  const f2 = calculateRegressionFlags({ conflict_internalization: 50 }, { parent_conflict_intensity: 40, household_stress: 80 }, 3);
  assert("regression_active=true when stress > 75 for 3+ days",     f2.regression_active === true);

  const f3 = calculateRegressionFlags({ conflict_internalization: 30 }, { parent_conflict_intensity: 85, household_stress: 50 }, 0);
  assert("acute_stress_response=true when conflict > 80",            f3.acute_stress_response === true);

  console.log("\n── enforceAgeLocks ──────────────────────────────────────────");

  const infant = enforceAgeLocks({ verbal_output: "No don't go away", physical_behavior: "[cries]" }, 0, 9, {});
  assert("0–11 months: verbal stripped to empty string", infant.verbal_output === "");
  assert("0–11 months: physical_behavior preserved",     infant.physical_behavior === "[cries]");

  const toddler = enforceAgeLocks({ verbal_output: "Mama come back please stay here", physical_behavior: "[reaches]" }, 1, 6, {});
  const tw = toddler.verbal_output.trim().split(/\s+/).filter(Boolean).length;
  assert(`12–23 months: capped at 4 words (got ${tw})`, tw <= 4);

  const aiVoice = enforceAgeLocks({ verbal_output: "I feel like you don't care.", physical_behavior: "[sits]" }, 5, 0, {});
  assert("Banned pattern 'I feel like' stripped to empty", aiVoice.verbal_output === "");

  const regressed = enforceAgeLocks({ verbal_output: "Mama don't go please come back to me", physical_behavior: "[clings]" }, 1, 0, { regression_active: true });
  const rw = regressed.verbal_output.trim().split(/\s+/).filter(Boolean).length;
  assert(`Regressed 1y 0m: capped at 4 words (got ${rw})`, rw <= 4);

  const noPhys = enforceAgeLocks({ verbal_output: "ok", physical_behavior: "" }, 5, 0, {});
  assert("Empty physical_behavior gets fallback",         noPhys.physical_behavior.length > 0);

  console.log("\n── createInitialChildState ──────────────────────────────────");

  const dflt = createInitialChildState();
  assert("All defaults in 0–100 range", Object.values(dflt.child_state).every(v => v >= 0 && v <= 100));

  const custom = createInitialChildState({ attachment_security: 25, age_years: 3 });
  assert("Override attachment_security=25 applied", custom.child_state.attachment_security === 25);
  assert("Override age_years=3 applied",            custom.age_years === 3);

  const clamped = createInitialChildState({ attachment_security: 150, self_worth: -10 });
  assert("attachment_security=150 clamped to 100",  clamped.child_state.attachment_security === 100);
  assert("self_worth=-10 clamped to 0",              clamped.child_state.self_worth === 0);

  printUnitResults(passed, failed);
  return failed;
}

// ─── SCENARIO 1: SPEC EXAMPLE ─────────────────────────────────────────────────
// Act 2 Day 2 → 4y 2m automatically via calculateAgeForDay(2, 2)
// ANXIOUS_CLINGY, witnessed a loud argument, left alone.

async function runScenario1() {
  console.log("\n── Scenario 1: Act 2 Day 2 (auto-age: 4y 2m) ──────────────");

  const state = createInitialChildState({
    attachment_security:      38,
    emotional_safety:         29,
    self_worth:               44,
    conflict_internalization: 68,
    attention_need:           82,
    emotional_expression:     35,
    parent_conflict_intensity: 74,
    trust_between_parents:    22,
    household_stress:         71,
    session_events_today: [
      "parents argued at dinner",
      "player parent left room without explaining",
    ],
  });

  const gameEvent = {
    description:
      "The AI Parent and Player Parent had a loud argument about money in the kitchen. " +
      "The child was in the adjacent living room and could hear raised voices and things being slammed. " +
      "The argument lasted about 8 minutes and ended with one parent leaving the house. " +
      "The child is now alone in the living room.",
  };

  const sceneContext = {
    location:     "Living room",
    present:      ["CHILD_ALONE"],
    triggerEvent: "Heard parents fighting, one parent just slammed the front door and left",
    timeOfDay:    "EVENING",
    recentEvents: [
      "parents argued at dinner",
      "child tried to show drawing but was ignored",
      "player parent left room without explanation",
    ],
  };

  // act + day → age auto-calculated: calculateAgeForDay(2, 2) = 4y 2m
  const result = await processChildTurn(state, gameEvent, sceneContext, {
    childName: "Lily",
    act: 2, day: 2,
    sustainedHighStressDays: 2,
  });

  printResult("SCENARIO 1 — Act 2 Day 2 (4y 2m, ANXIOUS_CLINGY)", result);
  return result;
}

// ─── SCENARIO 2: INFANT ───────────────────────────────────────────────────────
// Act 1 Day 4 → 0y 9m automatically. Fully pre-verbal. Warm interaction.
// Verifies the hard age-lock: verbal_output must be empty string.

async function runScenario2() {
  console.log("\n── Scenario 2: Act 1 Day 4 (auto-age: 0y 9m, pre-verbal) ──");

  const state = createInitialChildState({
    attachment_security:       55,
    emotional_safety:          48,
    self_worth:                60,
    conflict_internalization:  15,
    attention_need:            65,
    emotional_expression:      50,
    parent_conflict_intensity: 40,
    trust_between_parents:     60,
    household_stress:          35,
    session_events_today: ["baby was left in crib longer than usual"],
  });

  const gameEvent = {
    description:
      "The player parent picks up the baby immediately when she starts crying, " +
      "holds her close, makes soothing sounds, and rocks her gently for several minutes. " +
      "The baby calms down and is now looking at the parent's face.",
  };

  const sceneContext = {
    location:     "Nursery",
    present:      ["PLAYER_PARENT"],
    triggerEvent: "Player parent picked up and comforted the crying baby",
    timeOfDay:    "NIGHT",
    recentEvents: ["baby was left in crib longer than usual", "baby cried and eventually stopped"],
  };

  // act + day → age auto-calculated: calculateAgeForDay(1, 4) = 0y 9m
  const result = await processChildTurn(state, gameEvent, sceneContext, {
    childName: "Lily",
    act: 1, day: 4,
    sustainedHighStressDays: 0,
  });

  printResult("SCENARIO 2 — Act 1 Day 4 (0y 9m, pre-verbal)", result);

  if (result.childOutput.verbal_output !== "") {
    console.error(`  ✗ AGE-LOCK VIOLATION: 0y 9m infant produced verbal: "${result.childOutput.verbal_output}"`);
  } else {
    console.log("  ✓ Age-lock confirmed: verbal_output is empty for 9-month infant");
  }

  return result;
}

// ─── SCENARIO 3: REGRESSION ───────────────────────────────────────────────────
// Act 2 Day 11 → 6y 1m automatically. Regression active → speaks like 5yr.
// WITHDRAWN mode, 4-day sustained stress, hears word "divorce" for first time.

async function runScenario3() {
  console.log("\n── Scenario 3: Act 2 Day 11 (auto-age: 6y 1m, regression) ─");

  const state = createInitialChildState({
    attachment_security:       32,
    emotional_safety:          20,
    self_worth:                38,
    conflict_internalization:  78,
    attention_need:            55,
    emotional_expression:      22,
    parent_conflict_intensity: 85,
    trust_between_parents:     15,
    household_stress:          82,
    session_events_today: [
      "parents argued at breakfast",
      "child ate alone",
      "player parent was on phone all evening",
      "parents argued again before bed",
    ],
  });

  const gameEvent = {
    description:
      "For the fourth day in a row, the parents had a loud argument at night. " +
      "The child was in their room but could hear everything through the walls. " +
      "The argument was about whether to separate. The child heard the word 'divorce' for the first time. " +
      "After the argument, complete silence fell. Neither parent came to check on the child.",
  };

  const sceneContext = {
    location:     "Child's bedroom",
    present:      ["CHILD_ALONE"],
    triggerEvent: "Child heard the word 'divorce', then total silence",
    timeOfDay:    "NIGHT",
    recentEvents: [
      "parents argued at breakfast",
      "child ate alone and didn't speak",
      "player parent was on phone all evening",
      "parents argued again at dinner",
      "child started making their own bed without being asked",
    ],
  };

  // act + day → age auto-calculated: calculateAgeForDay(2, 11) = 6y 1m
  // regression_active will be true (household_stress > 75, sustainedHighStressDays = 4)
  // → child will speak like a 5-year-old
  const result = await processChildTurn(state, gameEvent, sceneContext, {
    childName: "Lily",
    act: 2, day: 11,
    sustainedHighStressDays: 4,
  });

  printResult("SCENARIO 3 — Act 2 Day 11 (6y 1m → regressed to 5yr speech)", result);

  if (result.regressionFlags.regression_active)  console.log("  ✓ regression_active confirmed");
  if (result.regressionFlags.acute_stress_response) console.log("  ✓ acute_stress_response confirmed");

  return result;
}

// ─── AGE PROGRESSION TABLE ────────────────────────────────────────────────────

function printAgeProgressionTable() {
  console.log("\n── Age Progression Reference ────────────────────────────────");
  console.log("  Act 1 (12 days, ages 0–3):");
  for (let d = 1; d <= 12; d++) {
    const { age_years, age_months } = calculateAgeForDay(1, d);
    const totalMo = age_years * 12 + age_months;
    const limit =
      totalMo < 12  ? "0 words (pre-verbal)" :
      totalMo < 24  ? "4 words max" :
      totalMo < 36  ? "6 words max" :
                      "10 words max";
    console.log(`    Day ${String(d).padStart(2)}  →  ${age_years}y ${String(age_months).padStart(2)}m  |  ${limit}`);
  }
  console.log("  Act 2 (14 days, ages 4–7):");
  for (let d = 1; d <= 14; d++) {
    const { age_years, age_months } = calculateAgeForDay(2, d);
    const totalMo = age_years * 12 + age_months;
    const limit =
      totalMo < 60  ? "15 words max" :
      totalMo < 84  ? "22 words max" :
                      "35 words max";
    console.log(`    Day ${String(d).padStart(2)}  →  ${age_years}y ${String(age_months).padStart(2)}m  |  ${limit}`);
  }
}

// ─── MAIN ─────────────────────────────────────────────────────────────────────

async function main() {
  console.log("╔══════════════════════════════════════════════════════════╗");
  console.log("║           CHILD AI SYSTEM — TEST RUNNER                 ║");
  console.log("╚══════════════════════════════════════════════════════════╝");

  printAgeProgressionTable();

  const unitFailures = runUnitTests();

  if (!process.env.ANTHROPIC_API_KEY) {
    console.warn("\n⚠  ANTHROPIC_API_KEY not set — skipping API scenarios.");
    console.warn("   Set it in a .env file and run: node --env-file=../.env test_child_ai.js\n");
    process.exit(unitFailures > 0 ? 1 : 0);
  }

  try {
    await runScenario1();
    await runScenario2();
    await runScenario3();
    console.log("\n✓ All scenarios complete.\n");
  } catch (err) {
    console.error("\n✗ Scenario failed:", err.message);
    console.error(err.stack);
    process.exit(1);
  }

  process.exit(unitFailures > 0 ? 1 : 0);
}

main();
