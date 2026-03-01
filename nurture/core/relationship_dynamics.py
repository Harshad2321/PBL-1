"""
relationship_dynamics.py  –  Message-level updater for RelationshipState
                              and AIPersonalityState.

Called after every player message. Analyses sentiment / intent of the
message and applies deltas to both state objects so that the AI partner's
next response is shaped by the evolving relationship.
"""

from __future__ import annotations

from typing import Dict, Any, Optional

from nurture.core.data_structures import RelationshipState, AIPersonalityState


# ── word-lists for lightweight sentiment / intent detection ──────────────

_POSITIVE_WORDS = {
    "love", "appreciate", "thank", "thanks", "sorry", "agree",
    "understand", "support", "together", "help", "care", "amazing",
    "beautiful", "proud", "grateful", "happy", "glad", "respect",
    "listen", "team", "forgive", "trust", "kind", "gentle",
}

_NEGATIVE_WORDS = {
    "hate", "fault", "blame", "wrong", "stupid", "useless", "never",
    "always", "annoyed", "frustrated", "angry", "tired", "exhausted",
    "sick", "lazy", "pathetic", "worthless", "hopeless",
    "whatever", "fuck", "fucking", "shit", "damn", "stfu",
    "idiot", "dumb", "terrible", "horrible", "awful", "worst",
    "toxic", "selfish", "disgusting", "trash", "garbage", "loser",
    "disappointing", "ridiculous", "incompetent", "crap", "suck",
    "sucks", "ass", "asshole", "bitch", "dick", "piss",
}

_ACCUSATION_PATTERNS = [
    "you always", "you never", "your fault", "because of you",
    "you don't", "you should", "you're wrong", "you ruined",
    "you made me", "it's your", "you can't even",
]

_SUPPORTIVE_PATTERNS = [
    "i understand", "i'm sorry", "im sorry", "let me help",
    "we can", "together", "i appreciate", "thank you",
    "i love", "i care", "my fault", "i was wrong",
    "i'll try", "let's work", "i forgive",
]

_CONTROLLING_PATTERNS = [
    "you need to", "you should", "you must", "i decided",
    "i'll handle", "let me do", "you can't", "my way",
    "i'm in charge", "do what i say", "listen to me",
]

_VULNERABLE_PATTERNS = [
    "i'm scared", "im scared", "i feel", "i miss",
    "i need you", "i'm worried", "im worried", "i don't know",
    "help me", "hold me", "i'm lost", "i'm afraid",
]

_AVOIDANT_PATTERNS = [
    "whatever", "fine", "i don't care", "doesn't matter",
    "let's not", "drop it", "forget it", "not now",
    "i'm done", "leave it", "change the subject",
]

# Multi-word negative phrases checked via substring matching
_NEGATIVE_PHRASES = [
    "shut up", "shut the fuck", "go away", "leave me alone",
    "don't care", "piss off", "fuck off", "fuck you",
    "get lost", "i hate you", "screw you", "go to hell",
    "back off", "get out",
]


# ── public API ───────────────────────────────────────────────────────────

def analyse_message(message: str) -> Dict[str, Any]:
    """Return a lightweight analysis dict used by ``update_dynamics``."""
    msg = message.lower().strip()
    words = set(msg.split())

    positive_hits = len(words & _POSITIVE_WORDS)
    negative_hits = len(words & _NEGATIVE_WORDS)

    # Also check multi-word negative phrases via substring
    for phrase in _NEGATIVE_PHRASES:
        if phrase in msg:
            negative_hits += 2  # phrases are stronger signals

    is_accusation = any(p in msg for p in _ACCUSATION_PATTERNS)
    is_supportive = any(p in msg for p in _SUPPORTIVE_PATTERNS)
    is_controlling = any(p in msg for p in _CONTROLLING_PATTERNS)
    is_vulnerable = any(p in msg for p in _VULNERABLE_PATTERNS)
    is_avoidant = any(p in msg for p in _AVOIDANT_PATTERNS)

    # sentiment in [-1, 1]
    raw = (positive_hits - negative_hits) * 0.25
    if is_supportive:
        raw += 0.35
    if is_accusation:
        raw -= 0.4
    if is_controlling:
        raw -= 0.2
    if is_vulnerable:
        raw += 0.15
    if is_avoidant:
        raw -= 0.15

    # shouting (ALL CAPS) or exclamation marks add intensity
    intensity = 0.5
    if message.isupper() and len(message) > 3:
        intensity += 0.3
    intensity += message.count("!") * 0.08
    intensity = min(1.0, intensity)

    sentiment = max(-1.0, min(1.0, raw))

    return {
        "sentiment": sentiment,
        "intensity": intensity,
        "positive_hits": positive_hits,
        "negative_hits": negative_hits,
        "is_accusation": is_accusation,
        "is_supportive": is_supportive,
        "is_controlling": is_controlling,
        "is_vulnerable": is_vulnerable,
        "is_avoidant": is_avoidant,
    }


def update_dynamics(
    rel: RelationshipState,
    personality: AIPersonalityState,
    analysis: Dict[str, Any],
    scenario_stress: float = 0.0,
) -> Dict[str, float]:
    """Apply deltas to *rel* and *personality* in-place.

    Returns a dict of ``{variable_name: delta}`` for logging / display.
    """
    deltas: Dict[str, float] = {}
    sent = analysis["sentiment"]
    intense = analysis["intensity"]

    # ── RELATIONSHIP STATE updates ───────────────────────────────────

    # --- trust ---
    if analysis["is_supportive"]:
        d = 3.0 + sent * 2.0
    elif analysis["is_accusation"]:
        d = -4.0 * intense
    elif analysis["is_controlling"]:
        d = -2.5 * intense
    elif analysis["is_vulnerable"]:
        d = 2.0        # vulnerability builds trust
    else:
        d = sent * 2.0  # gentle drift
    # forgiveness helps trust recover
    d *= (1.0 + personality.forgiveness_rate / 200.0)
    rel.trust += d
    deltas["trust"] = round(d, 2)

    # --- emotional_closeness ---
    if analysis["is_supportive"] or analysis["is_vulnerable"]:
        d = 3.5 * (0.5 + sent)
    elif analysis["is_avoidant"]:
        d = -3.0
    elif analysis["is_accusation"]:
        d = -3.5 * intense
    else:
        d = sent * 2.5
    rel.emotional_closeness += d
    deltas["emotional_closeness"] = round(d, 2)

    # --- resentment ---
    if analysis["is_accusation"] or analysis["is_controlling"]:
        d = 4.0 * intense
    elif analysis["is_supportive"]:
        d = -3.0
    elif analysis["is_avoidant"]:
        d = 1.5  # avoidance breeds resentment slowly
    else:
        d = -sent * 1.5  # positive messages reduce resentment
    rel.resentment += d
    deltas["resentment"] = round(d, 2)

    # --- conflict_intensity ---
    if analysis["is_accusation"]:
        d = 5.0 * intense
    elif analysis["is_avoidant"]:
        d = -2.0  # avoiding cools things down short-term
    elif analysis["is_supportive"]:
        d = -4.0
    else:
        d = -sent * 2.0
    # scenario stress adds to conflict
    d += scenario_stress * 2.0
    rel.conflict_intensity += d
    deltas["conflict_intensity"] = round(d, 2)

    # --- communication_openness ---
    if analysis["is_vulnerable"]:
        d = 4.0
    elif analysis["is_supportive"]:
        d = 2.5
    elif analysis["is_avoidant"]:
        d = -4.0
    elif analysis["is_accusation"]:
        d = -2.0
    else:
        d = sent * 1.5
    rel.communication_openness += d
    deltas["communication_openness"] = round(d, 2)

    # --- power_balance --- (positive = player dominates)
    if analysis["is_controlling"]:
        d = 3.0 * intense
    elif analysis["is_vulnerable"]:
        d = -2.0   # showing weakness shifts balance toward AI
    elif analysis["is_supportive"]:
        d = -0.5   # gentle move toward equal
    else:
        d = 0.0
    rel.power_balance += d
    deltas["power_balance"] = round(d, 2)

    rel.clamp()

    # ── AI PERSONALITY STATE updates ─────────────────────────────────

    # --- stress_level ---
    if analysis["is_accusation"]:
        d = 5.0 * intense
    elif analysis["is_supportive"]:
        d = -3.0
    elif analysis["is_avoidant"]:
        d = 1.0  # unresolved tension is stressful
    else:
        d = -sent * 2.0
    d += scenario_stress * 1.5
    personality.stress_level += d
    deltas["ai_stress_level"] = round(d, 2)

    # --- patience ---
    if analysis["is_accusation"] or analysis["is_controlling"]:
        d = -4.0 * intense
    elif analysis["is_supportive"]:
        d = 2.0
    elif analysis["is_avoidant"]:
        d = -1.0  # draining
    else:
        d = sent * 1.5
    personality.patience += d
    deltas["ai_patience"] = round(d, 2)

    # --- supportiveness ---
    if analysis["is_supportive"] or analysis["is_vulnerable"]:
        d = 2.5
    elif analysis["is_accusation"]:
        d = -3.0 * intense
    elif analysis["is_avoidant"]:
        d = -1.5
    else:
        d = sent * 1.0
    personality.supportiveness += d
    deltas["ai_supportiveness"] = round(d, 2)

    # --- defensiveness ---
    if analysis["is_accusation"]:
        d = 5.0 * intense
    elif analysis["is_controlling"]:
        d = 3.0 * intense
    elif analysis["is_supportive"]:
        d = -3.0
    elif analysis["is_vulnerable"]:
        d = -2.0
    else:
        d = -sent * 1.5
    personality.defensiveness += d
    deltas["ai_defensiveness"] = round(d, 2)

    # --- forgiveness_rate ---
    if analysis["is_supportive"]:
        d = 2.0
    elif analysis["is_accusation"]:
        d = -3.0
    elif analysis["is_vulnerable"]:
        d = 1.5
    else:
        d = sent * 1.0
    personality.forgiveness_rate += d
    deltas["ai_forgiveness_rate"] = round(d, 2)

    personality.clamp()
    personality.auto_update_conflict_style()

    return deltas


def get_relationship_prompt_context(
    rel: RelationshipState,
    personality: AIPersonalityState,
) -> str:
    """Build a compact prompt section that tells the LLM how the AI parent
    currently feels, so its reply tone matches the live state."""

    lines = []

    # ── overall mood ──
    lines.append(f"RELATIONSHIP STATUS: {rel.get_mood_label()}")

    # ── relationship numbers (give the LLM numeric guidance) ──
    lines.append(f"  Trust in partner: {rel.trust:.0f}/100")
    lines.append(f"  Emotional closeness: {rel.emotional_closeness:.0f}/100")
    lines.append(f"  Resentment level: {rel.resentment:.0f}/100")
    lines.append(f"  Conflict intensity: {rel.conflict_intensity:.0f}/100")
    lines.append(f"  Communication openness: {rel.communication_openness:.0f}/100")
    pb = rel.power_balance
    if pb > 10:
        lines.append(f"  Power balance: partner dominates (+{pb:.0f})")
    elif pb < -10:
        lines.append(f"  Power balance: you dominate ({pb:.0f})")
    else:
        lines.append(f"  Power balance: roughly equal ({pb:.0f})")

    # ── personality / mood ──
    lines.append(f"YOUR PERSONALITY RIGHT NOW:")
    lines.append(f"  Stress: {personality.stress_level:.0f}/100")
    lines.append(f"  Patience left: {personality.patience:.0f}/100")
    lines.append(f"  Conflict style: {personality.conflict_style.value}")
    lines.append(f"  Supportiveness: {personality.supportiveness:.0f}/100")
    lines.append(f"  Defensiveness: {personality.defensiveness:.0f}/100")
    lines.append(f"  Forgiveness rate: {personality.forgiveness_rate:.0f}/100")

    # ── behavioural instructions derived from state ──
    lines.append("")
    lines.append("HOW THIS AFFECTS YOUR TONE:")

    if rel.trust < 30:
        lines.append("- You are guarded and suspicious. You don't believe what they say easily.")
    elif rel.trust > 75:
        lines.append("- You trust your partner. You're open and cooperative.")

    if rel.resentment > 60:
        lines.append("- You're harbouring resentment. You may be passive-aggressive or bring up old issues.")
    
    if rel.emotional_closeness < 30:
        lines.append("- You feel emotionally distant. Your replies are short and cold.")
    elif rel.emotional_closeness > 75:
        lines.append("- You feel emotionally close. You're warm and affectionate.")

    if rel.conflict_intensity > 60:
        lines.append("- Tensions are HIGH. Small things set you off. You escalate quickly.")
    
    if rel.communication_openness < 30:
        lines.append("- You avoid deep conversations. You give surface-level answers.")

    if personality.stress_level > 65:
        lines.append("- You are very stressed. You snap easily and overreact.")
    
    if personality.patience < 25:
        lines.append("- Your patience is almost gone. You are short-tempered and irritable.")

    if personality.defensiveness > 60:
        lines.append("- You are very defensive. You shift blame and make excuses.")

    if personality.supportiveness < 30:
        lines.append("- You are emotionally unavailable. You don't offer comfort.")
    elif personality.supportiveness > 70:
        lines.append("- You are emotionally available and caring.")

    return "\n".join(lines)
