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
        title="The First Fight",
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
        title="Back to Work",
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
        title="Unspoken Distance",
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
        title="Third Birthday",
        description="Small birthday gathering at home. Warm moments mixed with quiet tension.",
        gameplay_time="~6–8 min",
        scenario_text="""Three years old. The age flies by. You're hosting a small party at home.
Candles, cake, relatives. Your child is laughing.
But late at night, after everyone leaves, you and your partner sit quietly.
So much has happened in these three years. So much has been built. So much has been left unsaid.""",
        hidden_impact_intro="Final milestone of ACT 1. Locks in foundational patterns for years to come.",
        choices=[
            PlayerChoice(
                choice_id="1_12_reconnect",
                text="Acknowledge changes and reconnect",
                hidden_impact=["reflection_positive", "partnership_intentional", "foundation_solid"],
                impact_description="ACT 1 closes with intention. You enter next stage with clear eyes."
            ),
            PlayerChoice(
                choice_id="1_12_minimize",
                text="Minimize problems and keep things surface-level",
                hidden_impact=["reflection_avoided", "problems_buried", "foundation_fragile"],
                impact_description="You push through without examining. Cracks hidden but present."
            ),
            PlayerChoice(
                choice_id="1_12_blame",
                text="Blame stress, money, or bad luck",
                hidden_impact=["externalization_pattern", "victim_mentality", "responsibility_abdicated"],
                impact_description="Three years reduced to 'life just happened.' Opportunity lost."
            ),
        ]
    ),
]

ACT_1 = ActData(
    phase=ActPhase.FOUNDATION,
    age_range="0–3 years",
    total_days=12,
    total_gameplay_hours="~1 hour",
    days=ACT_1_DAYS,
)
