"""
Story Data Structures and Act Definitions

Defines the narrative structure for all acts, including day-by-day scenarios,
choices, and hidden impacts that shape the child's development.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional


class ActPhase(Enum):
    """Game acts representing child development stages."""
    FOUNDATION = "ACT 1 — FOUNDATION (Age 0–3)"
    MIRROR = "ACT 2 — MIRROR (Age 4–7)"
    FRACTURE = "ACT 3 — FRACTURE (Age 8–12)"
    RECKONING = "ACT 4 — RECKONING (Age 13–18)"


@dataclass
class PlayerChoice:
    """A single choice available to the player."""
    choice_id: str
    text: str
    hidden_impact: List[str] = field(default_factory=list)
    impact_description: str = ""


@dataclass
class DayScenario:
    """A single day's scenario within an act."""
    day: int
    title: str
    description: str
    gameplay_time: str  # e.g., "~4 min"
    scenario_text: str  # What's happening
    choices: List[PlayerChoice] = field(default_factory=list)
    hidden_impact_intro: str = ""  # What this day teaches the AI


@dataclass
class ActData:
    """Complete data for an act."""
    phase: ActPhase
    age_range: str
    total_days: int
    total_gameplay_hours: str
    days: List[DayScenario] = field(default_factory=list)


# ============================================================================
# ACT 1: FOUNDATION (Age 0-3)
# ============================================================================

ACT_1_DAYS = [
    DayScenario(
        day=1,
        title="First Night Home",
        description="Baby crying nonstop at 2 AM. Both parents exhausted.",
        gameplay_time="~4 min",
        scenario_text="""Your newborn won't stop crying at 2 AM. You're both exhausted beyond belief.
The sound is piercing, the frustration is mounting. Something has to give.
Your partner stares at you from their side of the bed, eyes pleading for sleep.""",
        hidden_impact_intro="Begins forming child's attachment security. Sets early pattern of responsibility sharing.",
        choices=[
            PlayerChoice(
                choice_id="1_1_immediate",
                text="Get up immediately and handle the baby",
                hidden_impact=["responsibility_high", "presence_high", "attachment_security_positive"],
                impact_description="Shows immediate responsiveness. Child learns: parent is reliable."
            ),
            PlayerChoice(
                choice_id="1_1_wait",
                text="Wait and hope the other parent gets up",
                hidden_impact=["avoidance_low", "responsibility_low", "partnership_tension"],
                impact_description="Shows hesitation. Builds minor resentment with partner."
            ),
            PlayerChoice(
                choice_id="1_1_wake",
                text="Wake the other parent and insist they do it",
                hidden_impact=["assertiveness_high", "responsibility_shirking", "partnership_conflict"],
                impact_description="Shows lack of unity. Teaches child: parents don't cooperate under stress."
            ),
        ]
    ),
    
    DayScenario(
        day=2,
        title="Visitors",
        description="Relatives visit and give unsolicited advice. Partner becomes uncomfortable.",
        gameplay_time="~4 min",
        scenario_text="""Your mother-in-law has strong opinions about everything: feeding schedules, sleep training, 
parenting style. Your partner shifts uncomfortably. You can feel the tension rising.
'In our day, we just let babies cry it out,' she says, not unkindly.""",
        hidden_impact_intro="Changes partner's trust in you. Adds baseline household stress.",
        choices=[
            PlayerChoice(
                choice_id="1_2_defend",
                text="Defend your partner and set boundaries",
                hidden_impact=["partnership_unity", "boundary_setting", "family_trust"],
                impact_description="Shows you prioritize partner. Strengthens relationship foundation."
            ),
            PlayerChoice(
                choice_id="1_2_neutral",
                text="Stay neutral and quiet",
                hidden_impact=["avoidance_moderate", "partnership_slight_tension", "passivity"],
                impact_description="Shows reluctance to engage. Partner feels unsupported."
            ),
            PlayerChoice(
                choice_id="1_2_agree",
                text="Agree with the relatives' criticism",
                hidden_impact=["partnership_betrayal", "undermining", "family_influence_strong"],
                impact_description="Shows you side with outsiders. Damages trust significantly."
            ),
        ]
    ),
    
    DayScenario(
        day=3,
        title="Money Talk",
        description="Discussion about bills, savings, and future costs.",
        gameplay_time="~5 min",
        scenario_text="""Daycare costs, medical bills, future college savings. The numbers are real and scary.
One of you wants to work more hours. The other wants to stay more present.
Neither is wrong. Both feel the weight of impossible choices.""",
        hidden_impact_intro="Sets long-term work-family balance path. Affects future emotional availability.",
        choices=[
            PlayerChoice(
                choice_id="1_3_work_more",
                text="Take on more work hours",
                hidden_impact=["work_prioritized", "provider_role", "future_absence_pattern"],
                impact_description="Sets availability pattern. Future emotional moments may be missed."
            ),
            PlayerChoice(
                choice_id="1_3_reduce_spend",
                text="Reduce expenses and stay more present",
                hidden_impact=["presence_prioritized", "emotional_availability", "sacrifice_accepted"],
                impact_description="Shows willingness to sacrifice for presence. Strong early bonding pattern."
            ),
            PlayerChoice(
                choice_id="1_3_avoid",
                text="Avoid the discussion completely",
                hidden_impact=["avoidance_pattern", "conflict_avoidance", "unresolved_tension"],
                impact_description="Postpones problem. Stress simmers quietly in background."
            ),
        ]
    ),
    
    DayScenario(
        day=4,
        title="First Major Argument",
        description="Sleep deprivation leads to a real argument. Voices are raised.",
        gameplay_time="~6 min",
        scenario_text="""It starts small—a comment about dishes, about who did what yesterday. 
But you're both at the breaking point. The tiredness, the stress, the weight of new life.
Suddenly you're both shouting. And nearby, the baby cries.
This is real. This is happening. And your child will remember the feeling.""",
        hidden_impact_intro="First deep emotional imprint on child. Teaches AI parent your conflict style.",
        choices=[
            PlayerChoice(
                choice_id="1_4_calm_down",
                text="Stop the fight and calm things down",
                hidden_impact=["emotional_regulation", "responsibility_for_safety", "conflict_resolution_early"],
                impact_description="Shows maturity. Child learns: emotions can be managed."
            ),
            PlayerChoice(
                choice_id="1_4_continue",
                text="Continue arguing to prove your point",
                hidden_impact=["defensiveness_high", "ego_over_family", "conflict_normalized"],
                impact_description="Shows rigidity. Child absorbs: conflict is how we relate."
            ),
            PlayerChoice(
                choice_id="1_4_walk_away",
                text="Walk away and leave the room",
                hidden_impact=["avoidance_under_pressure", "emotional_abandonment_pattern", "unresolved"],
                impact_description="Shows escape over resolution. Leaves tension unhealed."
            ),
        ]
    ),
    
    DayScenario(
        day=5,
        title="Quiet Morning",
        description="Peaceful moment alone with the baby. Just you two.",
        gameplay_time="~3 min",
        scenario_text="""Early morning. Your partner is still asleep. It's just you and your child.
Sunlight coming through the window. The baby watches you with those eyes that don't yet judge.
You could talk to them, play gently, feel the connection.
Or you could just get through the care tasks. Either way, the day moves on.""",
        hidden_impact_intro="Subtle boost or drop in emotional bonding. Reinforces presence vs distance.",
        choices=[
            PlayerChoice(
                choice_id="1_5_engage",
                text="Gently play and talk to the child",
                hidden_impact=["presence_quality_high", "emotional_bonding", "attunement"],
                impact_description="Builds secure attachment. Child learns: I am worthy of attention."
            ),
            PlayerChoice(
                choice_id="1_5_mechanical",
                text="Perform care tasks mechanically",
                hidden_impact=["presence_quality_low", "efficiency_over_connection", "emotional_distance_slight"],
                impact_description="Care happens but connection waits. Child feels: I am a task."
            ),
            PlayerChoice(
                choice_id="1_5_distracted",
                text="Be distracted by phone/work while caring",
                hidden_impact=["presence_quality_minimal", "distraction_normalized", "emotional_distance_moderate"],
                impact_description="Child learns to compete for attention. Bonding moment lost."
            ),
        ]
    ),
    
    DayScenario(
        day=6,
        title="Return to Work",
        description="One parent resumes full workload. Guilt and insecurity surface.",
        gameplay_time="~5 min",
        scenario_text="""Your partner is going back to work full-time. You see them struggle with the decision.
Guilt written all over their face. 'I don't want to leave them,' they say quietly.
You need the income. You need the stability. But the cost is visible, and it hurts.""",
        hidden_impact_intro="AI learns how you justify absence. Affects future resentment or understanding.",
        choices=[
            PlayerChoice(
                choice_id="1_6_reassure",
                text="Reassure your partner emotionally",
                hidden_impact=["empathy_high", "partnership_support", "shared_burden"],
                impact_description="Shows you understand their pain. Builds alliance around difficult decision."
            ),
            PlayerChoice(
                choice_id="1_6_dismiss",
                text="Dismiss the concern as necessary reality",
                hidden_impact=["empathy_low", "practicality_over_feeling", "emotional_invalidation"],
                impact_description="Shuts down feeling. Partner feels alone in their guilt."
            ),
            PlayerChoice(
                choice_id="1_6_promise_later",
                text="Promise to make it up later with gifts/outsourcing",
                hidden_impact=["avoidance_of_emotion", "material_substitution", "unresolved_guilt"],
                impact_description="Avoids real conversation. Problem gets packaged as financial."
            ),
        ]
    ),
    
    DayScenario(
        day=7,
        title="Missed Milestone",
        description="Child does something important while you're away. Partner tells you later.",
        gameplay_time="~4 min",
        scenario_text="""'They smiled intentionally today. Not just gas. A real smile. At me,' your partner tells you.
You missed it. You were at work. The moment is gone forever.
Your partner sees your face fall. 'I know,' they say quietly. 'But someone should know.'""",
        hidden_impact_intro="Creates a lasting memory tag of absence or care. Alters child preference.",
        choices=[
            PlayerChoice(
                choice_id="1_7_apologize",
                text="Apologize sincerely and show regret",
                hidden_impact=["accountability_high", "presence_regret", "commitment_to_witness"],
                impact_description="Shows you value what you missed. Opens door to rebalancing."
            ),
            PlayerChoice(
                choice_id="1_7_excuse",
                text="Make excuses about responsibilities",
                hidden_impact=["rationalization", "avoidance_of_regret", "detachment_pattern"],
                impact_description="Protects yourself but distances from the moment's weight."
            ),
            PlayerChoice(
                choice_id="1_7_blame",
                text="Shift blame to circumstances or partner",
                hidden_impact=["externalization", "blame_deflection", "partnership_tension_increase"],
                impact_description="Avoids responsibility. Plants resentment seed."
            ),
        ]
    ),
    
    DayScenario(
        day=8,
        title="Sick Night",
        description="Child is ill and won't stop crying. Stress is high.",
        gameplay_time="~6 min",
        scenario_text="""Fever. Crying. No clear diagnosis yet. Your pediatrician is calm but you're not.
Your partner is terrified. You're both operating on raw instinct and fear.
In this moment, you either move as one team, or you fracture.""",
        hidden_impact_intro="Defines caregiving trust between parents. Strong effect on child's safety.",
        choices=[
            PlayerChoice(
                choice_id="1_8_cooperate",
                text="Cooperate calmly with your partner",
                hidden_impact=["teamwork_under_stress", "trust_in_crisis", "child_safety_priority"],
                impact_description="Child feels: both parents are here, both are steady. Safety is built."
            ),
            PlayerChoice(
                choice_id="1_8_control",
                text="Take over and control everything",
                hidden_impact=["control_tendency", "partnership_distrust", "independence_over_unity"],
                impact_description="Shows you don't trust partner's capability. Creates learned helplessness."
            ),
            PlayerChoice(
                choice_id="1_8_shut_down",
                text="Emotionally shut down and disengage",
                hidden_impact=["avoidance_of_fear", "emotional_numbness", "partnership_abandonment"],
                impact_description="Fear paralyzes you. Partner feels alone. Child feels unprotected."
            ),
        ]
    ),
    
    DayScenario(
        day=9,
        title="First Words",
        description="Child says their first word. Both parents react in the moment.",
        gameplay_time="~3 min",
        scenario_text="""'Mama.' Or 'Dada.' Out of nowhere, clear as day.
Your heart stops. This is a milestone you'll talk about forever.
Your partner looks at you. This is a moment you both own, or it becomes one parent's achievement.""",
        hidden_impact_intro="Sets unity vs rivalry tone between parents. Shapes how joy is shared.",
        choices=[
            PlayerChoice(
                choice_id="1_9_celebrate_together",
                text="Celebrate together with your partner",
                hidden_impact=["joy_shared", "partnership_celebration", "achievement_unity"],
                impact_description="Sets tone: we celebrate together. Joy multiplies in partnership."
            ),
            PlayerChoice(
                choice_id="1_9_compete",
                text="Compete for credit or attention",
                hidden_impact=["rivalry_introduction", "ego_over_moment", "fragmented_memory"],
                impact_description="Turns joy into competition. Child becomes object instead of subject."
            ),
            PlayerChoice(
                choice_id="1_9_casual",
                text="React casually and move on",
                hidden_impact=["milestone_minimized", "emotional_dampening", "significance_lost"],
                impact_description="Misses the weight of the moment. Child learns: first words aren't special."
            ),
        ]
    ),
    
    DayScenario(
        day=10,
        title="Emotional Distance",
        description="No big event, just emotional drift. Conversation feels forced.",
        gameplay_time="~4 min",
        scenario_text="""You haven't had a real conversation in weeks. Just logistics.
'How was your day?' 'Fine.' And then silence.
You sit next to each other but feel far apart. The distance is comfortable in a way that scares you.""",
        hidden_impact_intro="Locks in confrontation vs avoidance pattern. Influences how conflict surfaces.",
        choices=[
            PlayerChoice(
                choice_id="1_10_honest_talk",
                text="Start an honest, vulnerable talk",
                hidden_impact=["vulnerability_introduced", "intimacy_rebuild", "communication_pattern_positive"],
                impact_description="Bridges the gap. Teaches child: connection requires honesty."
            ),
            PlayerChoice(
                choice_id="1_10_avoid",
                text="Avoid the topic and change subject",
                hidden_impact=["avoidance_pattern_deepened", "intimacy_deferred", "emotional_distance_accepted"],
                impact_description="Comfortable numbness continues. Distance becomes normalized."
            ),
            PlayerChoice(
                choice_id="1_10_pretend",
                text="Pretend everything is fine",
                hidden_impact=["denial_pattern", "surface_stability_false", "unresolved_undercurrent"],
                impact_description="Everything looks good on surface. Tension simmers underneath."
            ),
        ]
    ),
    
    DayScenario(
        day=11,
        title="Public Embarrassment",
        description="Child misbehaves in public. Parents disagree instantly on discipline.",
        gameplay_time="~6 min",
        scenario_text="""The grocery store. Your toddler loses it over something small.
You react one way. Your partner reacts differently. The contradiction is instant and visible.
Other parents are watching. Your child is confused about who's in charge.""",
        hidden_impact_intro="Teaches child how authority works. Alters partner respect and unity.",
        choices=[
            PlayerChoice(
                choice_id="1_11_support",
                text="Support your partner's response",
                hidden_impact=["partnership_unity_public", "authority_consistency", "trust_foundation"],
                impact_description="Shows unified front. Child learns: we agree. Rules are stable."
            ),
            PlayerChoice(
                choice_id="1_11_correct",
                text="Correct your partner in front of the child",
                hidden_impact=["partnership_undermining_public", "authority_confusion", "partnership_damage"],
                impact_description="Teaches child: divide and conquer. Breaks partner trust publicly."
            ),
            PlayerChoice(
                choice_id="1_11_passive",
                text="Stay passive and let it unfold",
                hidden_impact=["passivity_in_conflict", "unclear_authority", "leadership_abdication"],
                impact_description="Shows uncertainty. Child feels: no one is really in charge."
            ),
        ]
    ),
    
    DayScenario(
        day=12,
        title="Emotional Fatigue",
        description="Both parents exhausted emotionally. Short tempers lead to small argument.",
        gameplay_time="~4 min",
        scenario_text="""Both of you wake emotionally depleted. The tiredness goes deeper than sleep.
Short tempers surface in small exchanges throughout the day.
A small argument starts from accumulated fatigue. Neither is really wrong, but tension rises anyway.""",
        hidden_impact_intro="Defines forgiveness and repair patterns. Sets stress recovery baseline.",
        choices=[
            PlayerChoice(
                choice_id="1_12_apologize",
                text="Apologize and attempt repair",
                hidden_impact=["forgiveness_high", "repair_pattern_positive", "emotional_closeness_restored"],
                impact_description="Shows humility under fatigue. Repair becomes part of routine."
            ),
            PlayerChoice(
                choice_id="1_12_justify",
                text="Justify your behavior",
                hidden_impact=["defensiveness_pattern", "repair_blocked", "emotional_distance_grows"],
                impact_description="Protects ego. Tension lingers without resolution."
            ),
            PlayerChoice(
                choice_id="1_12_ignore",
                text="Ignore the tension and move on",
                hidden_impact=["avoidance_pattern", "silent_retreat", "unresolved_stress"],
                impact_description="Tension left untouched. Builds quietly in the background."
            ),
        ]
    ),
    
    DayScenario(
        day=13,
        title="Small Reconnection",
        description="Unexpected calm day. Shared laughter and emotional opening.",
        gameplay_time="~4 min",
        scenario_text="""An unexpectedly calm day arrives. No crisis, no conflict waiting.
A brief moment of shared laughter happens naturally, out of nowhere.
Your partner opens up emotionally, testing the safety of the space you've created.""",
        hidden_impact_intro="Tests depth of trust. Opportunity to strengthen or dismiss vulnerability.",
        choices=[
            PlayerChoice(
                choice_id="1_13_engage",
                text="Engage deeply and connect",
                hidden_impact=["vulnerability_received", "trust_deepened", "communication_opened"],
                impact_description="Shows safety for intimacy. Bond strengthens meaningfully."
            ),
            PlayerChoice(
                choice_id="1_13_surface",
                text="Stay surface-level",
                hidden_impact=["vulnerability_avoided", "connection_shallow", "opportunity_missed"],
                impact_description="Keeps things comfortable but doesn't build. Moment passes."
            ),
            PlayerChoice(
                choice_id="1_13_dismiss",
                text="Dismiss their vulnerability",
                hidden_impact=["vulnerability_rejected", "trust_damaged", "emotional_wall_built"],
                impact_description="Partner learns: vulnerability isn't safe here. Door closes."
            ),
        ]
    ),
    
    DayScenario(
        day=14,
        title="Third Birthday (State Lock)",
        description="Birthday preparation and celebration. Final Act 1 state lock.",
        gameplay_time="~6–8 min",
        scenario_text="""Three years old. Birthday preparation begins with mixed feelings and history.
Celebration with relatives brings social pressure and observation.
Quiet reflection opens between parents as child sleeps peacefully.
So much has been built. So much will be locked in as foundation for what comes next.""",
        hidden_impact_intro="Final milestone of ACT 1. Locks attachment_security, conflict_intensity, AI conflict_style, relationship_trust baseline, and long_term flags.",
        choices=[
            PlayerChoice(
                choice_id="1_14_acknowledge",
                text="Acknowledge growth and challenges honestly",
                hidden_impact=["reflection_positive", "partnership_intentional", "foundation_solid"],
                impact_description="ACT 1 closes with honesty. You enter next stage with clear eyes."
            ),
            PlayerChoice(
                choice_id="1_14_minimize",
                text="Minimize the problems",
                hidden_impact=["reflection_avoided", "problems_buried", "foundation_fragile"],
                impact_description="You push through without examining. Cracks hidden but present."
            ),
            PlayerChoice(
                choice_id="1_14_blame",
                text="Blame stress or external factors",
                hidden_impact=["externalization_pattern", "victim_mentality", "responsibility_abdicated"],
                impact_description="Three years reduced to 'life just happened.' Opportunity lost."
            ),
        ]
    ),
]

ACT_1 = ActData(
    phase=ActPhase.FOUNDATION,
    age_range="0–3 years",
    total_days=14,
    total_gameplay_hours="~1.5 hours",
    days=ACT_1_DAYS,
)


# ============================================================================
# ACT 2: MIRROR (Age 4-7)
# ============================================================================

ACT_2_DAYS = [
    DayScenario(
        day=1,
        title="First Day of School",
        description="Child nervous about school. Behavior depends on attachment security.",
        gameplay_time="~4 min",
        scenario_text="""Your child is nervous about their first day of school.
If attachment_security is low, they show clingy behavior. If high, cautious but stable.
The teacher reports how the child adjusted throughout the afternoon.
That night, your child asks: "Will you be there tomorrow?\"""",
        hidden_impact_intro="References Act 1 attachment. Sets anxiety baseline for school years.",
        choices=[
            PlayerChoice(
                choice_id="2_1_reassure",
                text="Reassure warmly",
                hidden_impact=["attachment_reinforced", "emotional_safety_high", "anxiety_reduced"],
                impact_description="Child feels safe. School becomes manageable challenge."
            ),
            PlayerChoice(
                choice_id="2_1_minimize",
                text="Minimize their fear",
                hidden_impact=["fear_dismissed", "emotional_invalidation", "anxiety_baseline_increase"],
                impact_description="Child learns: my fears aren't valid. Anxiety grows quietly."
            ),
            PlayerChoice(
                choice_id="2_1_cold_independence",
                text="Encourage independence coldly",
                hidden_impact=["attachment_weakened", "emotional_distance", "anxiety_spike"],
                impact_description="Child feels abandoned to face world alone. Security drops."
            ),
        ]
    ),
    
    DayScenario(
        day=2,
        title="Copied Phrase",
        description="Teacher reports child said something harsh. Phrase matches past conflict.",
        gameplay_time="~4 min",
        scenario_text="""The teacher calls. Your child said something harsh in class.
The phrase sounds familiar—it matches something said during past parental conflict.
Your partner connects the dots. The child repeats the phrase during evening frustration.
Tension builds between you and your partner over who's responsible.""",
        hidden_impact_intro="References memory_tag from Act 1. Shows children mirror behavior.",
        choices=[
            PlayerChoice(
                choice_id="2_2_accept",
                text="Accept responsibility",
                hidden_impact=["accountability_high", "communication_open", "conflict_internalization_reduced"],
                impact_description="Ownership breaks the cycle. Child sees: adults can admit mistakes."
            ),
            PlayerChoice(
                choice_id="2_2_blame_others",
                text="Blame school or others",
                hidden_impact=["externalization_pattern", "communication_closed", "memory_reinforced"],
                impact_description="Deflection continues pattern. Child learns to blame others too."
            ),
            PlayerChoice(
                choice_id="2_2_correct_harsh",
                text="Correct child harshly",
                hidden_impact=["harshness_modeled", "self_worth_damaged", "conflict_internalization_increased"],
                impact_description="Harshness begets harshness. The cycle deepens."
            ),
        ]
    ),
    
    DayScenario(
        day=3,
        title="Homework Refusal",
        description="Child refuses homework. Parents disagree on discipline.",
        gameplay_time="~5 min",
        scenario_text="""Your child refuses to do their homework. The resistance is firm.
You and your partner begin to disagree on how to handle it.
Your child watches carefully, noting division or unity.
Later that night, the boundary is tested again.""",
        hidden_impact_intro="Tests parental unity. Affects authority structure and manipulation patterns.",
        choices=[
            PlayerChoice(
                choice_id="2_3_united",
                text="Present united front",
                hidden_impact=["authority_clear", "trust_maintained", "manipulation_reduced"],
                impact_description="Child learns: parents are aligned. Boundaries are real."
            ),
            PlayerChoice(
                choice_id="2_3_undermine",
                text="Undermine your partner",
                hidden_impact=["authority_fractured", "trust_damaged", "manipulation_learned"],
                impact_description="Child discovers: play parents against each other. Division exploited."
            ),
            PlayerChoice(
                choice_id="2_3_withdraw",
                text="Withdraw from decision",
                hidden_impact=["authority_unclear", "resentment_grows", "manipulation_tendency_up"],
                impact_description="Absence of leadership. Child tests limits more aggressively."
            ),
        ]
    ),
    
    DayScenario(
        day=4,
        title="Supermarket Tantrum",
        description="Child throws intense tantrum publicly. Parents discuss response.",
        gameplay_time="~5 min",
        scenario_text="""Routine outing to the supermarket. Something triggers your child.
An intense tantrum erupts publicly. Everyone is watching.
You and your partner discuss what happened on the way home.
Your child reacts emotionally to the tone of that discussion.""",
        hidden_impact_intro="Tests discipline approach in public. Affects self-worth and emotional safety.",
        choices=[
            PlayerChoice(
                choice_id="2_4_calm_private",
                text="Calm private correction",
                hidden_impact=["dignity_preserved", "emotional_safety_maintained", "trust_up"],
                impact_description="Child learns: mistakes happen, but I'm not humiliated for them."
            ),
            PlayerChoice(
                choice_id="2_4_public_humiliation",
                text="Public humiliation",
                hidden_impact=["shame_internalized", "self_worth_damaged", "emotional_safety_down"],
                impact_description="Public shaming creates lasting wound. Child learns to hide emotions."
            ),
            PlayerChoice(
                choice_id="2_4_ignore",
                text="Ignore behavior",
                hidden_impact=["boundaries_unclear", "confusion", "attachment_uncertain"],
                impact_description="No response is still a response. Child feels invisible or confused."
            ),
        ]
    ),
    
    DayScenario(
        day=5,
        title="The Drawing",
        description="You find a family drawing. Distance between figures reflects relationship.",
        gameplay_time="~4 min",
        scenario_text="""You find a drawing your child made of the family.
The distance between figures reflects the current relationship state.
You decide whether to ask about it or leave it alone.
Your child may explain or stay silent depending on your approach.""",
        hidden_impact_intro="Symbolic emotional expression. Tests parental curiosity vs dismissal.",
        choices=[
            PlayerChoice(
                choice_id="2_5_ask_gently",
                text="Ask gently",
                hidden_impact=["emotional_expression_encouraged", "bond_strengthened", "curiosity_welcomed"],
                impact_description="Child feels: my inner world matters. Expression becomes safer."
            ),
            PlayerChoice(
                choice_id="2_5_ignore",
                text="Ignore drawing",
                hidden_impact=["emotional_expression_discouraged", "distance_maintained", "silence_learned"],
                impact_description="Message received: don't share. Child closes off slightly."
            ),
            PlayerChoice(
                choice_id="2_5_criticize",
                text="Criticize drawing",
                hidden_impact=["expression_punished", "self_worth_damaged", "creativity_suppressed"],
                impact_description="Art becomes unsafe. Child hides emotional content."
            ),
        ]
    ),
    
    DayScenario(
        day=6,
        title="Parent Comparison",
        description="Child says one parent is 'nicer'. Emotional reaction follows.",
        gameplay_time="~4 min",
        scenario_text="""Your child says it plainly: "You're not as nice as [other parent]."
The words land hard. Emotional reactions surface.
You and your partner discuss it later, with varying degrees of honesty.
Resentment may shift, or reflection may deepen.""",
        hidden_impact_intro="Tests adult ego vs child development focus. Affects loyalty dynamics.",
        choices=[
            PlayerChoice(
                choice_id="2_6_reflect",
                text="Reflect calmly",
                hidden_impact=["maturity_shown", "resentment_avoided", "loyalty_bias_neutral"],
                impact_description="Adults don't compete for child's favor. Healthy modeling."
            ),
            PlayerChoice(
                choice_id="2_6_attack_partner",
                text="Attack your partner",
                hidden_impact=["resentment_spike", "emotional_closeness_damaged", "loyalty_bias_increased"],
                impact_description="Child's comment becomes weapon. Partnership suffers."
            ),
            PlayerChoice(
                choice_id="2_6_suppress",
                text="Suppress feelings silently",
                hidden_impact=["resentment_buried", "defensiveness_grows", "loyalty_bias_slight"],
                impact_description="Feelings don't disappear. They simmer and leak out later."
            ),
        ]
    ),
    
    DayScenario(
        day=7,
        title="Sick Evening",
        description="Child sick. Fever increases. Stress test for parental unity.",
        gameplay_time="~5 min",
        scenario_text="""Your child wakes slightly sick. By afternoon, the fever has increased.
Stress rises as routines break down. This is a test for parental unity.
Your child seeks comfort during the night.
How you and your partner work together matters.""",
        hidden_impact_intro="Crisis cooperation test. References Act 1 caregiving patterns.",
        choices=[
            PlayerChoice(
                choice_id="2_7_cooperate",
                text="Cooperate",
                hidden_impact=["unity_strengthened", "caregiving_trust_up", "attachment_reinforced"],
                impact_description="Child feels: both parents are here when it matters. Safety confirmed."
            ),
            PlayerChoice(
                choice_id="2_7_control",
                text="Control aggressively",
                hidden_impact=["unity_fractured", "caregiving_trust_down", "partner_excluded"],
                impact_description="Taking over pushes partner out. Child senses tension even when sick."
            ),
            PlayerChoice(
                choice_id="2_7_withdraw",
                text="Withdraw emotionally",
                hidden_impact=["absence_felt", "caregiving_trust_damaged", "attachment_shaken"],
                impact_description="Absence during crisis echoes. Child learns: parent isn't always there."
            ),
        ]
    ),
    
    DayScenario(
        day=8,
        title="The Lie",
        description="Broken object discovered. Child denies involvement. Truth revealed.",
        gameplay_time="~5 min",
        scenario_text="""A broken object is discovered. Your child denies involvement.
Later, the truth is revealed—they did break it.
The emotional aftermath depends on how you handle the dishonesty.
This moment shapes their relationship with truth.""",
        hidden_impact_intro="Defines honesty baseline. Tests emotional safety around mistakes.",
        choices=[
            PlayerChoice(
                choice_id="2_8_calm_discussion",
                text="Calm discussion",
                hidden_impact=["honesty_encouraged", "self_worth_protected", "emotional_safety_up"],
                impact_description="Truth becomes safer than hiding. Child learns: mistakes are fixable."
            ),
            PlayerChoice(
                choice_id="2_8_harsh_punishment",
                text="Harsh punishment",
                hidden_impact=["honesty_punished", "self_worth_damaged", "lying_incentivized"],
                impact_description="Punishment for honesty teaches: hide mistakes. Lying becomes strategic."
            ),
            PlayerChoice(
                choice_id="2_8_ignore",
                text="Ignore",
                hidden_impact=["boundaries_unclear", "honesty_baseline_dropped", "confusion"],
                impact_description="No consequence means no clarity. Truth and lies blend together."
            ),
        ]
    ),
    
    DayScenario(
        day=9,
        title="School Performance Drop",
        description="Teacher reports declining focus. Discussion of pressure vs support.",
        gameplay_time="~5 min",
        scenario_text="""The teacher reports your child's focus is declining.
A discussion begins: more pressure, or more support?
Your child reacts to the tone of expectations in the evening.
Silent withdrawal or emotional breakdown follows at night.""",
        hidden_impact_intro="Academic pressure test. Affects self-worth and anxiety trajectory.",
        choices=[
            PlayerChoice(
                choice_id="2_9_support_gently",
                text="Support gently",
                hidden_impact=["self_worth_protected", "anxiety_reduced", "trust_maintained"],
                impact_description="Child feels: struggle is okay. Help is available without judgment."
            ),
            PlayerChoice(
                choice_id="2_9_increase_pressure",
                text="Increase academic pressure",
                hidden_impact=["anxiety_increased", "self_worth_linked_to_performance", "stress_spike"],
                impact_description="Performance becomes identity. Failure becomes existential threat."
            ),
            PlayerChoice(
                choice_id="2_9_blame_partner",
                text="Blame your partner",
                hidden_impact=["resentment_grows", "child_caught_in_middle", "anxiety_up"],
                impact_description="Child's struggle becomes ammunition. Partnership suffers while child watches."
            ),
        ]
    ),
    
    DayScenario(
        day=10,
        title="Late Night Argument (Child Overhears)",
        description="Heated argument while child is awake. Child remains silent in room.",
        gameplay_time="~6 min",
        scenario_text="""Tension has been building all day. A minor disagreement escalates.
A heated argument erupts while your child is still awake.
You don't realize they're listening from their room.
The child remains silent, processing what they heard.""",
        hidden_impact_intro="Critical memory tag event. Deep impact on conflict internalization.",
        choices=[
            PlayerChoice(
                choice_id="2_10_deescalate",
                text="De-escalate",
                hidden_impact=["conflict_contained", "emotional_safety_preserved", "trust_up"],
                impact_description="Child sees: adults can stop. Conflict doesn't have to spiral."
            ),
            PlayerChoice(
                choice_id="2_10_escalate",
                text="Escalate",
                hidden_impact=["conflict_internalized_deeply", "emotional_safety_shattered", "memory_tag_set"],
                impact_description="Child absorbs: this is how relationships work. Damage is deep."
            ),
            PlayerChoice(
                choice_id="2_10_leave_house",
                text="Leave house",
                hidden_impact=["abandonment_felt", "conflict_unresolved", "trust_damaged"],
                impact_description="Walking away leaves wound open. Child learns: escape over resolution."
            ),
        ]
    ),
    
    DayScenario(
        day=11,
        title="Emotional Withdrawal",
        description="Child quieter than usual. Teacher notes isolation. Opportunity to connect.",
        gameplay_time="~4 min",
        scenario_text="""Your child has been quieter than usual lately.
The teacher notes signs of isolation at school.
An opportunity to connect appears in the evening.
But your child avoids conversation, testing whether you'll pursue.""",
        hidden_impact_intro="Tests parental pursuit. Affects emotional expression and withdrawal patterns.",
        choices=[
            PlayerChoice(
                choice_id="2_11_reach_out",
                text="Reach out vulnerably",
                hidden_impact=["connection_offered", "attachment_strengthened", "expression_opened"],
                impact_description="Pursuit without pressure. Child learns: someone will come for me."
            ),
            PlayerChoice(
                choice_id="2_11_demand",
                text="Demand communication",
                hidden_impact=["pressure_applied", "withdrawal_deepened", "expression_shut_down"],
                impact_description="Force backfires. Child learns: withdrawal is the safer path."
            ),
            PlayerChoice(
                choice_id="2_11_accept_distance",
                text="Accept distance",
                hidden_impact=["distance_normalized", "withdrawal_pattern_set", "bond_weakened"],
                impact_description="Space becomes permanent. Child learns: isolation is acceptable."
            ),
        ]
    ),
    
    DayScenario(
        day=12,
        title="Favoritism",
        description="Child prefers one parent. Other parent feels excluded. Subtle tension.",
        gameplay_time="~4 min",
        scenario_text="""Your child clearly prefers one parent over the other.
The excluded parent feels the sting of rejection.
Subtle tension builds throughout the evening.
Resentment may shift depending on how this is handled.""",
        hidden_impact_intro="Tests adult emotional maturity. Affects loyalty bias and resentment.",
        choices=[
            PlayerChoice(
                choice_id="2_12_encourage_balance",
                text="Encourage balance",
                hidden_impact=["loyalty_bias_neutral", "resentment_avoided", "emotional_closeness_up"],
                impact_description="Adults don't compete. Child doesn't have to choose sides."
            ),
            PlayerChoice(
                choice_id="2_12_compete",
                text="Compete for attention",
                hidden_impact=["loyalty_bias_increased", "resentment_grows", "child_caught_between"],
                impact_description="Competition for child's love. Everyone loses."
            ),
            PlayerChoice(
                choice_id="2_12_indifferent",
                text="Act indifferent",
                hidden_impact=["distance_maintained", "resentment_buried", "loyalty_bias_slight"],
                impact_description="Pretended indifference. Feelings leak out in other ways."
            ),
        ]
    ),
    
    DayScenario(
        day=13,
        title="Boundary Test",
        description="Child deliberately breaks rule. Consequence decision. Authority challenged.",
        gameplay_time="~5 min",
        scenario_text="""Your child deliberately breaks a rule they know well.
You must decide on a consequence in the moment.
That evening, they challenge your authority verbally.
The authority dynamic either stabilizes or weakens based on your response.""",
        hidden_impact_intro="Final authority test before state lock. Affects manipulation tendency.",
        choices=[
            PlayerChoice(
                choice_id="2_13_calm_consistent",
                text="Calm consistent consequence",
                hidden_impact=["authority_established", "honesty_baseline_up", "self_worth_protected"],
                impact_description="Boundaries are real and fair. Child feels: structure is safe."
            ),
            PlayerChoice(
                choice_id="2_13_overreaction",
                text="Emotional overreaction",
                hidden_impact=["authority_unstable", "self_worth_damaged", "manipulation_learned"],
                impact_description="Emotional response undermines authority. Child learns to trigger reactions."
            ),
            PlayerChoice(
                choice_id="2_13_inconsistent",
                text="Inconsistent response",
                hidden_impact=["authority_weak", "manipulation_tendency_up", "honesty_unclear"],
                impact_description="Inconsistency breeds manipulation. Rules become negotiable."
            ),
        ]
    ),
    
    DayScenario(
        day=14,
        title="Age 7 Reflection (State Shift)",
        description="Quiet day. Subtle signs of personality pattern. Family dinner feels different.",
        gameplay_time="~6 min",
        scenario_text="""A quiet breakfast opens the day with reflective mood.
Subtle signs of your child's emerging personality pattern appear.
Family dinner feels emotionally different than Act 1—things have shifted.
As your child sleeps, accumulated patterns begin to crystallize.""",
        hidden_impact_intro="Final ACT 2 state update. Child archetype classification: Anxious, Defiant, Withdrawn, or Balanced. Locks honesty_baseline, authority_structure, loyalty_bias, conflict_internalization, anxiety_baseline.",
        choices=[
            PlayerChoice(
                choice_id="2_14_acknowledge",
                text="Acknowledge patterns with honesty",
                hidden_impact=["reflection_positive", "communication_open", "archetype_toward_balanced"],
                impact_description="Honest acknowledgment of journey. Best foundation for what comes next."
            ),
            PlayerChoice(
                choice_id="2_14_avoid",
                text="Avoid reflection",
                hidden_impact=["reflection_avoided", "patterns_unexamined", "archetype_trajectory_unchanged"],
                impact_description="Patterns continue unexamined. Momentum carries forward unchecked."
            ),
            PlayerChoice(
                choice_id="2_14_blame_external",
                text="Blame external factors",
                hidden_impact=["externalization_continues", "communication_closed", "archetype_toward_anxious_defiant"],
                impact_description="Blame prevents growth. Child internalizes: problems come from outside."
            ),
        ]
    ),
]

ACT_2 = ActData(
    phase=ActPhase.MIRROR,
    age_range="4–7 years",
    total_days=14,
    total_gameplay_hours="~1.5 hours",
    days=ACT_2_DAYS,
)
