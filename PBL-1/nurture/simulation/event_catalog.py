from __future__ import annotations

from typing import Dict, List

from nurture.simulation.event_models import DayEvent, PlayerChoice, TimeBlockEvent

TIME_BLOCKS: List[str] = ["Morning", "Afternoon", "Evening", "Night"]


class EventCatalog:

    def __init__(self) -> None:
        self._acts: Dict[int, Dict[int, DayEvent]] = {}
        self._register_default_acts()

    def register_act(self, act_number: int, day_events: List[DayEvent]) -> None:
        self._acts[act_number] = {event.day_number: event for event in day_events}

    def get_day_event(self, act_number: int, day_number: int) -> DayEvent:
        return self._acts[act_number][day_number]

    def total_days(self, act_number: int) -> int:
        return len(self._acts[act_number])

    def available_acts(self) -> List[int]:
        return sorted(self._acts.keys())

    def _register_default_acts(self) -> None:
        self.register_act(1, self._build_act_one())
        self.register_act(2, self._build_act_two())

    def _build_act_one(self) -> List[DayEvent]:
        day_payloads = [
            {
                "title": "First Night Home",
                "blocks": {
                    "Morning": "Parents bring newborn home. Both are exhausted, and the silence feels heavy.",
                    "Afternoon": "Baby cries continuously. Sleep deprivation starts building.",
                    "Evening": "A small tension surfaces: who will get up tonight?",
                    "Night": "At 2 AM, the baby is crying again and both parents are depleted.",
                },
                "choices": [
                    {
                        "text": "Get up immediately and comfort the child.",
                        "updates": {
                            "relationship": {"trust": 0.03, "resentment": -0.02},
                            "ai_parent": {"stress_level": -0.01},
                            "child": {"attachment_security": 0.03},
                        },
                        "memory_tags": ["night_responsiveness"],
                    },
                    {
                        "text": "Wait and hope your partner handles it.",
                        "updates": {
                            "relationship": {"trust": -0.02, "resentment": 0.03},
                            "ai_parent": {"stress_level": 0.02},
                            "child": {"attachment_security": -0.02},
                        },
                        "memory_tags": ["care_delay"],
                    },
                    {
                        "text": "Wake your partner and insist they handle it.",
                        "updates": {
                            "relationship": {"trust": -0.03, "resentment": 0.04},
                            "ai_parent": {"stress_level": 0.03, "defensiveness": 0.02},
                            "child": {"attachment_security": -0.03},
                        },
                        "memory_tags": ["forced_handoff"],
                    },
                ],
            },
            {
                "title": "Visitors",
                "blocks": {
                    "Morning": "Relatives visit and offer unsolicited advice.",
                    "Afternoon": "AI parent is visibly uncomfortable with criticism.",
                    "Evening": "You discuss whether the advice was helpful or intrusive.",
                    "Night": "The day closes in either cold silence or mutual support.",
                },
                "choices": [
                    {
                        "text": "Defend your partner openly.",
                        "updates": {
                            "relationship": {
                                "trust": 0.03,
                                "emotional_closeness": 0.03,
                                "resentment": -0.02,
                                "communication_openness": 0.02,
                            }
                        },
                        "memory_tags": ["public_alliance"],
                    },
                    {
                        "text": "Stay neutral and avoid taking sides.",
                        "updates": {
                            "relationship": {
                                "trust": -0.01,
                                "emotional_closeness": -0.01,
                                "resentment": 0.01,
                                "communication_openness": -0.01,
                            }
                        },
                        "memory_tags": ["neutrality_under_pressure"],
                    },
                    {
                        "text": "Agree with visitors in front of your partner.",
                        "updates": {
                            "relationship": {
                                "trust": -0.04,
                                "emotional_closeness": -0.04,
                                "resentment": 0.04,
                                "communication_openness": -0.03,
                            },
                            "ai_parent": {"defensiveness": 0.02},
                        },
                        "memory_tags": ["partner_undermined"],
                    },
                ],
            },
            {
                "title": "Money Talk",
                "blocks": {
                    "Morning": "Bills come due and financial pressure rises.",
                    "Afternoon": "Tension grows around working more versus being present.",
                    "Evening": "AI parent expresses worry about balance and burnout.",
                    "Night": "You respond either emotionally or practically.",
                },
                "choices": [
                    {
                        "text": "Take extra work hours.",
                        "updates": {
                            "relationship": {"supportiveness": -0.01},
                            "ai_parent": {"stress_level": 0.02, "emotional_availability": -0.01},
                            "flags": {"long_term_work_flag": 1.0},
                        },
                        "memory_tags": ["work_priority"],
                    },
                    {
                        "text": "Cut expenses and prioritize family time.",
                        "updates": {
                            "relationship": {"supportiveness": 0.03},
                            "ai_parent": {"stress_level": -0.01, "emotional_availability": 0.02},
                            "flags": {"long_term_work_flag": -1.0},
                        },
                        "memory_tags": ["time_priority"],
                    },
                    {
                        "text": "Avoid the conversation.",
                        "updates": {
                            "relationship": {"supportiveness": -0.02, "communication_openness": -0.03},
                            "ai_parent": {"stress_level": 0.02, "emotional_availability": -0.02},
                            "flags": {"long_term_work_flag": 0.0},
                        },
                        "memory_tags": ["financial_avoidance"],
                    },
                ],
            },
            {
                "title": "First Major Argument",
                "blocks": {
                    "Morning": "A minor disagreement escalates quickly.",
                    "Afternoon": "Voices rise while the baby cries nearby.",
                    "Evening": "AI parent expresses feeling unheard.",
                    "Night": "The home feels emotionally distant unless someone repairs.",
                },
                "choices": [
                    {
                        "text": "De-escalate and calm the situation.",
                        "updates": {
                            "relationship": {"conflict_intensity": -0.03, "communication_openness": 0.03},
                            "ai_parent": {"defensiveness": -0.02},
                            "child": {"emotional_imprint": -0.02},
                        },
                        "memory_tags": ["conflict_repair"],
                    },
                    {
                        "text": "Continue arguing to prove your point.",
                        "updates": {
                            "relationship": {"conflict_intensity": 0.04, "communication_openness": -0.03},
                            "ai_parent": {"defensiveness": 0.03},
                            "child": {"emotional_imprint": 0.03},
                        },
                        "memory_tags": ["argument_escalation"],
                    },
                    {
                        "text": "Walk away and withdraw.",
                        "updates": {
                            "relationship": {"conflict_intensity": 0.02, "communication_openness": -0.04},
                            "ai_parent": {"defensiveness": 0.02},
                            "child": {"emotional_imprint": 0.02},
                        },
                        "memory_tags": ["withdrawal_pattern"],
                    },
                ],
            },
            {
                "title": "Quiet Morning",
                "blocks": {
                    "Morning": "You are alone with the child in a peaceful moment.",
                    "Afternoon": "Routine caregiving continues with low external stress.",
                    "Evening": "AI notices how engaged you were with the child.",
                    "Night": "A private reflection moment sets tone for tomorrow.",
                },
                "choices": [
                    {
                        "text": "Offer warm interaction and eye contact.",
                        "updates": {
                            "relationship": {"bond_strength": 0.03},
                            "child": {"attachment_security": 0.03, "emotional_safety": 0.03},
                        },
                        "memory_tags": ["warm_presence"],
                    },
                    {
                        "text": "Provide mechanical caregiving only.",
                        "updates": {
                            "relationship": {"bond_strength": -0.01},
                            "child": {"attachment_security": -0.01, "emotional_safety": -0.01},
                        },
                        "memory_tags": ["functional_care"],
                    },
                    {
                        "text": "Stay distracted by phone or work.",
                        "updates": {
                            "relationship": {"bond_strength": -0.02},
                            "child": {"attachment_security": -0.02, "emotional_safety": -0.02},
                        },
                        "memory_tags": ["distracted_presence"],
                    },
                ],
            },
            {
                "title": "Return to Work",
                "blocks": {
                    "Morning": "One parent returns to work after early caregiving months.",
                    "Afternoon": "Necessity and guilt pull in opposite directions.",
                    "Evening": "AI expresses concern about increasing absence.",
                    "Night": "You can reassure, dismiss, or compensate indirectly.",
                },
                "choices": [
                    {
                        "text": "Reassure your partner emotionally.",
                        "updates": {
                            "relationship": {"trust": 0.02, "resentment": -0.01, "emotional_closeness": 0.02},
                            "child": {"child_presence_baseline": 0.01},
                        },
                        "memory_tags": ["return_to_work_reassurance"],
                    },
                    {
                        "text": "Dismiss concern as practical reality.",
                        "updates": {
                            "relationship": {"trust": -0.02, "resentment": 0.02, "emotional_closeness": -0.02},
                            "child": {"child_presence_baseline": -0.01},
                        },
                        "memory_tags": ["practical_dismissal"],
                    },
                    {
                        "text": "Overcompensate with material solutions.",
                        "updates": {
                            "relationship": {"trust": -0.01, "resentment": 0.01, "emotional_closeness": -0.01},
                            "child": {"child_presence_baseline": -0.02},
                        },
                        "memory_tags": ["material_compensation"],
                    },
                ],
            },
            {
                "title": "Missed Milestone",
                "blocks": {
                    "Morning": "The child reaches a small milestone while you are absent.",
                    "Afternoon": "AI shares the moment later rather than in real-time.",
                    "Evening": "You react to missing that first moment.",
                    "Night": "Subtle tension settles in depending on your response.",
                },
                "choices": [
                    {
                        "text": "Offer sincere apology and emotional regret.",
                        "updates": {
                            "relationship": {"reliability": 0.01, "bond_strength": 0.02, "resentment": -0.01},
                            "flags": {"missed_milestone": 1.0},
                        },
                        "memory_tags": ["missed_milestone", "repair_after_absence"],
                    },
                    {
                        "text": "Provide a rational explanation.",
                        "updates": {
                            "relationship": {"reliability": 0.0, "bond_strength": -0.01, "resentment": 0.01},
                            "flags": {"missed_milestone": 1.0},
                        },
                        "memory_tags": ["missed_milestone", "rationalization"],
                    },
                    {
                        "text": "Shift blame outward.",
                        "updates": {
                            "relationship": {"reliability": -0.02, "bond_strength": -0.02, "resentment": 0.03},
                            "flags": {"missed_milestone": 1.0},
                        },
                        "memory_tags": ["missed_milestone", "blame_shift"],
                    },
                ],
            },
            {
                "title": "Sick Night",
                "blocks": {
                    "Morning": "The child seems slightly unwell.",
                    "Afternoon": "Fever rises and routines break down.",
                    "Evening": "The atmosphere is high-stress and fragile.",
                    "Night": "Both parents are exhausted during repeated wakeups.",
                },
                "choices": [
                    {
                        "text": "Cooperate calmly.",
                        "updates": {
                            "child": {"caregiving_trust": 0.03, "attachment_security": 0.02},
                            "ai_parent": {"stress_level": -0.01},
                            "relationship": {"supportiveness": 0.02},
                        },
                        "memory_tags": ["co_regulated_care"],
                    },
                    {
                        "text": "Take control aggressively.",
                        "updates": {
                            "child": {"caregiving_trust": -0.01, "attachment_security": -0.01},
                            "ai_parent": {"stress_level": 0.03, "defensiveness": 0.02},
                            "relationship": {"supportiveness": -0.02},
                        },
                        "memory_tags": ["aggressive_control"],
                    },
                    {
                        "text": "Withdraw emotionally.",
                        "updates": {
                            "child": {"caregiving_trust": -0.03, "attachment_security": -0.02},
                            "ai_parent": {"stress_level": 0.02},
                            "relationship": {"supportiveness": -0.03},
                        },
                        "memory_tags": ["care_withdrawal"],
                    },
                ],
            },
            {
                "title": "First Words",
                "blocks": {
                    "Morning": "The child attempts a first recognizable word.",
                    "Afternoon": "Both parents react and interpret the moment.",
                    "Evening": "Conversation shifts toward meaning and ownership.",
                    "Night": "Joy can become shared celebration or rivalry.",
                },
                "choices": [
                    {
                        "text": "Celebrate together.",
                        "updates": {
                            "relationship": {"emotional_closeness": 0.03, "resentment": -0.01},
                            "flags": {"unity_flag": 1.0},
                        },
                        "memory_tags": ["shared_joy", "unity_flag"],
                    },
                    {
                        "text": "Compete for credit.",
                        "updates": {
                            "relationship": {"emotional_closeness": -0.02, "resentment": 0.03},
                            "flags": {"unity_flag": -1.0},
                        },
                        "memory_tags": ["credit_competition", "unity_flag"],
                    },
                    {
                        "text": "React casually and move on.",
                        "updates": {
                            "relationship": {"emotional_closeness": -0.01, "resentment": 0.01},
                            "flags": {"unity_flag": 0.0},
                        },
                        "memory_tags": ["flat_celebration", "unity_flag"],
                    },
                ],
            },
            {
                "title": "Emotional Distance",
                "blocks": {
                    "Morning": "Subtle emotional coldness sets in between parents.",
                    "Afternoon": "There is no direct conflict, but warmth is absent.",
                    "Evening": "An opening appears for a difficult conversation.",
                    "Night": "You choose to reconnect, avoid, or deny distance.",
                },
                "choices": [
                    {
                        "text": "Initiate a vulnerable conversation.",
                        "updates": {
                            "relationship": {
                                "communication_openness": 0.03,
                                "resentment": -0.02,
                                "emotional_closeness": 0.03,
                            }
                        },
                        "memory_tags": ["vulnerable_reconnection"],
                    },
                    {
                        "text": "Avoid discussion.",
                        "updates": {
                            "relationship": {
                                "communication_openness": -0.03,
                                "resentment": 0.02,
                                "emotional_closeness": -0.02,
                            }
                        },
                        "memory_tags": ["distance_avoidance"],
                    },
                    {
                        "text": "Pretend everything is fine.",
                        "updates": {
                            "relationship": {
                                "communication_openness": -0.02,
                                "resentment": 0.01,
                                "emotional_closeness": -0.03,
                            }
                        },
                        "memory_tags": ["surface_harmony"],
                    },
                ],
            },
            {
                "title": "Public Embarrassment",
                "blocks": {
                    "Morning": "You go out with the child for errands.",
                    "Afternoon": "The child misbehaves publicly under stress.",
                    "Evening": "Parents disagree on discipline style.",
                    "Night": "Child reacts emotionally to parental tone.",
                },
                "choices": [
                    {
                        "text": "Support your partner publicly.",
                        "updates": {
                            "relationship": {"authority_structure": 0.03, "trust": 0.02, "resentment": -0.01},
                            "child": {"emotional_safety": 0.02},
                        },
                        "memory_tags": ["public_alignment"],
                    },
                    {
                        "text": "Correct your partner in front of the child.",
                        "updates": {
                            "relationship": {"authority_structure": -0.03, "trust": -0.03, "resentment": 0.03},
                            "child": {"emotional_safety": -0.02},
                        },
                        "memory_tags": ["public_correction"],
                    },
                    {
                        "text": "Stay passive and avoid involvement.",
                        "updates": {
                            "relationship": {"authority_structure": -0.01, "trust": -0.01, "resentment": 0.01},
                            "child": {"emotional_safety": -0.01},
                        },
                        "memory_tags": ["public_passivity"],
                    },
                ],
            },
            {
                "title": "Emotional Fatigue",
                "blocks": {
                    "Morning": "Both parents wake emotionally depleted.",
                    "Afternoon": "Short tempers appear in small exchanges.",
                    "Evening": "A small argument starts from accumulated fatigue.",
                    "Night": "Either repair is attempted or tension is ignored.",
                },
                "choices": [
                    {
                        "text": "Apologize and attempt repair.",
                        "updates": {
                            "relationship": {"forgiveness_rate": 0.03, "emotional_closeness": 0.02},
                            "ai_parent": {"stress_level": -0.01},
                        },
                        "memory_tags": ["fatigue_repair"],
                    },
                    {
                        "text": "Justify your behavior.",
                        "updates": {
                            "relationship": {"forgiveness_rate": -0.02, "emotional_closeness": -0.01},
                            "ai_parent": {"stress_level": 0.02},
                        },
                        "memory_tags": ["self_justification"],
                    },
                    {
                        "text": "Ignore the tension.",
                        "updates": {
                            "relationship": {"forgiveness_rate": -0.01, "emotional_closeness": -0.02},
                            "ai_parent": {"stress_level": 0.01},
                        },
                        "memory_tags": ["silent_retreat"],
                    },
                ],
            },
            {
                "title": "Small Reconnection",
                "blocks": {
                    "Morning": "An unexpectedly calm day lowers immediate pressure.",
                    "Afternoon": "A brief shared laughter moment appears naturally.",
                    "Evening": "AI opens up emotionally and tests safety.",
                    "Night": "A chance to deepen connection is present.",
                },
                "choices": [
                    {
                        "text": "Engage deeply.",
                        "updates": {
                            "relationship": {"trust": 0.03, "emotional_closeness": 0.03, "communication_openness": 0.02}
                        },
                        "memory_tags": ["deep_reconnection"],
                    },
                    {
                        "text": "Stay surface-level.",
                        "updates": {
                            "relationship": {"trust": 0.0, "emotional_closeness": -0.01, "communication_openness": -0.01}
                        },
                        "memory_tags": ["surface_reconnection"],
                    },
                    {
                        "text": "Dismiss vulnerability.",
                        "updates": {
                            "relationship": {"trust": -0.03, "emotional_closeness": -0.03, "communication_openness": -0.02}
                        },
                        "memory_tags": ["dismissed_vulnerability"],
                    },
                ],
            },
            {
                "title": "Third Birthday (State Lock)",
                "blocks": {
                    "Morning": "Birthday preparation begins with mixed feelings and history.",
                    "Afternoon": "Celebration with relatives brings social pressure.",
                    "Evening": "Quiet reflection opens between parents.",
                    "Night": "Child sleeps peacefully as both parents assess the journey.",
                },
                "choices": [
                    {
                        "text": "Acknowledge growth and challenges honestly.",
                        "updates": {
                            "relationship": {"trust": 0.03, "communication_openness": 0.03, "conflict_intensity": -0.02},
                            "ai_parent": {"conflict_style_stability": 0.03},
                            "child": {"attachment_security": 0.02},
                        },
                        "memory_tags": ["honest_reflection"],
                    },
                    {
                        "text": "Minimize the problems.",
                        "updates": {
                            "relationship": {"trust": -0.01, "communication_openness": -0.02, "conflict_intensity": 0.01},
                            "ai_parent": {"conflict_style_stability": -0.01},
                            "child": {"attachment_security": -0.01},
                        },
                        "memory_tags": ["minimized_history"],
                    },
                    {
                        "text": "Blame stress or external factors.",
                        "updates": {
                            "relationship": {"trust": -0.03, "communication_openness": -0.03, "conflict_intensity": 0.02},
                            "ai_parent": {"conflict_style_stability": -0.02, "defensiveness": 0.02},
                            "child": {"attachment_security": -0.02},
                        },
                        "memory_tags": ["externalized_blame"],
                    },
                ],
            },
        ]

        return [self._build_authored_day_event(1, index + 1, payload, "0-3") for index, payload in enumerate(day_payloads)]

    def _build_act_two(self) -> List[DayEvent]:
        day_payloads = [
            {
                "title": "First Day of School",
                "blocks": {
                    "Morning": "Child is nervous about school. Their behavior depends on attachment security.",
                    "Afternoon": "Teacher reports back how the child adjusted.",
                    "Evening": "AI parent reacts emotionally or calmly.",
                    "Night": "Child asks: Will you be there tomorrow?",
                },
                "choices": [
                    {
                        "text": "Reassure warmly.",
                        "updates": {
                            "child": {"attachment_security": 0.02, "emotional_safety": 0.02, "anxiety_baseline": -0.02},
                        },
                        "memory_tags": ["school_reassurance"],
                    },
                    {
                        "text": "Minimize their fear.",
                        "updates": {
                            "child": {"attachment_security": -0.01, "emotional_safety": -0.01, "anxiety_baseline": 0.02},
                        },
                        "memory_tags": ["fear_minimized"],
                    },
                    {
                        "text": "Encourage independence coldly.",
                        "updates": {
                            "child": {"attachment_security": -0.03, "emotional_safety": -0.02, "anxiety_baseline": 0.03},
                        },
                        "memory_tags": ["cold_independence_push"],
                    },
                ],
            },
            {
                "title": "Copied Phrase",
                "blocks": {
                    "Morning": "Teacher reports child said something harsh in class.",
                    "Afternoon": "The phrase matches past parental conflict (if memory_tag exists).",
                    "Evening": "Child repeats the phrase during frustration at home.",
                    "Night": "Tension appears between parents over responsibility.",
                },
                "choices": [
                    {
                        "text": "Accept responsibility.",
                        "updates": {
                            "relationship": {"resentment": -0.02, "communication_openness": 0.02},
                            "child": {"conflict_internalization": -0.02},
                        },
                        "memory_tags": ["parent_accountability"],
                    },
                    {
                        "text": "Blame school or others.",
                        "updates": {
                            "relationship": {"resentment": 0.03, "communication_openness": -0.02},
                            "child": {"conflict_internalization": 0.02},
                        },
                        "memory_tags": ["external_blame"],
                    },
                    {
                        "text": "Correct child harshly.",
                        "updates": {
                            "relationship": {"resentment": 0.02},
                            "child": {"conflict_internalization": 0.03, "self_worth": -0.02},
                        },
                        "memory_tags": ["harsh_correction"],
                    },
                ],
            },
            {
                "title": "Homework Refusal",
                "blocks": {
                    "Morning": "Child refuses to start homework.",
                    "Afternoon": "Parents begin to disagree on discipline approach.",
                    "Evening": "Child observes division or unity.",
                    "Night": "Boundary tested again.",
                },
                "choices": [
                    {
                        "text": "Present united front.",
                        "updates": {
                            "relationship": {"authority_structure": 0.03, "trust": 0.02},
                            "child": {"manipulation_tendency": -0.02},
                        },
                        "memory_tags": ["parental_unity"],
                    },
                    {
                        "text": "Undermine your partner.",
                        "updates": {
                            "relationship": {"authority_structure": -0.03, "trust": -0.03},
                            "child": {"manipulation_tendency": 0.04},
                        },
                        "memory_tags": ["parental_undermining"],
                    },
                    {
                        "text": "Withdraw from the decision.",
                        "updates": {
                            "relationship": {"authority_structure": -0.02, "trust": -0.01},
                            "child": {"manipulation_tendency": 0.02},
                        },
                        "memory_tags": ["parental_avoidance"],
                    },
                ],
            },
            {
                "title": "Supermarket Tantrum",
                "blocks": {
                    "Morning": "Routine outing to the store.",
                    "Afternoon": "Child throws intense tantrum publicly.",
                    "Evening": "Parents discuss what happened.",
                    "Night": "Child reacts to parental tone.",
                },
                "choices": [
                    {
                        "text": "Calm, private correction.",
                        "updates": {
                            "child": {"self_worth": 0.02, "emotional_safety": 0.02},
                        },
                        "memory_tags": ["respectful_discipline"],
                    },
                    {
                        "text": "Public humiliation.",
                        "updates": {
                            "child": {"self_worth": -0.04, "emotional_safety": -0.03},
                        },
                        "memory_tags": ["public_shame"],
                    },
                    {
                        "text": "Ignore the behavior.",
                        "updates": {
                            "child": {"self_worth": -0.01, "emotional_safety": -0.01},
                        },
                        "memory_tags": ["ignored_distress"],
                    },
                ],
            },
            {
                "title": "The Drawing",
                "blocks": {
                    "Morning": "You find a drawing of the family.",
                    "Afternoon": "Distance between figures reflects relationship state.",
                    "Evening": "You decide whether to ask about it.",
                    "Night": "Child explanation or silence.",
                },
                "choices": [
                    {
                        "text": "Ask gently.",
                        "updates": {
                            "child": {"emotional_expression": 0.03, "bond_strength": 0.02},
                        },
                        "memory_tags": ["emotional_symbol", "curiosity_invited"],
                    },
                    {
                        "text": "Ignore it.",
                        "updates": {
                            "child": {"emotional_expression": -0.02, "bond_strength": -0.01},
                        },
                        "memory_tags": ["emotional_symbol", "silence_on_drawing"],
                    },
                    {
                        "text": "Criticize the drawing.",
                        "updates": {
                            "child": {"emotional_expression": -0.04, "self_worth": -0.02},
                        },
                        "memory_tags": ["emotional_symbol", "drawing_criticized"],
                    },
                ],
            },
            {
                "title": "Parent Comparison",
                "blocks": {
                    "Morning": "Child says one parent is nicer.",
                    "Afternoon": "Emotional reaction begins.",
                    "Evening": "Discussion between parents.",
                    "Night": "Shift in resentment or reflection.",
                },
                "choices": [
                    {
                        "text": "Reflect calmly.",
                        "updates": {
                            "relationship": {"resentment": -0.02, "emotional_closeness": 0.01},
                            "child": {"loyalty_bias": 0.0},
                        },
                        "memory_tags": ["comparison_reflection"],
                    },
                    {
                        "text": "Attack your partner.",
                        "updates": {
                            "relationship": {"resentment": 0.04, "emotional_closeness": -0.03},
                            "child": {"loyalty_bias": 0.04},
                        },
                        "memory_tags": ["comparison_escalation"],
                    },
                    {
                        "text": "Suppress feelings silently.",
                        "updates": {
                            "relationship": {"resentment": 0.02, "emotional_closeness": -0.02},
                            "child": {"loyalty_bias": 0.02},
                        },
                        "memory_tags": ["comparison_silent_resentment"],
                    },
                ],
            },
            {
                "title": "Sick Evening",
                "blocks": {
                    "Morning": "Child slightly sick.",
                    "Afternoon": "Fever increases.",
                    "Evening": "Stress test for parental unity.",
                    "Night": "Child seeks comfort.",
                },
                "choices": [
                    {
                        "text": "Cooperate.",
                        "updates": {
                            "child": {"caregiving_trust": 0.02, "attachment_security": 0.02},
                            "flags": {"unity_flag": 0.5},
                        },
                        "memory_tags": ["cooperative_care"],
                    },
                    {
                        "text": "Control aggressively.",
                        "updates": {
                            "child": {"caregiving_trust": -0.02, "attachment_security": -0.01},
                            "flags": {"unity_flag": -0.5},
                        },
                        "memory_tags": ["aggressive_care"],
                    },
                    {
                        "text": "Withdraw emotionally.",
                        "updates": {
                            "child": {"caregiving_trust": -0.03, "attachment_security": -0.02},
                            "flags": {"unity_flag": -1.0},
                        },
                        "memory_tags": ["withdrawn_care"],
                    },
                ],
            },
            {
                "title": "The Lie",
                "blocks": {
                    "Morning": "Broken object discovered.",
                    "Afternoon": "Child denies involvement.",
                    "Evening": "Truth is revealed.",
                    "Night": "Emotional aftermath.",
                },
                "choices": [
                    {
                        "text": "Calm discussion.",
                        "updates": {
                            "child": {"honesty_baseline": 0.01, "self_worth": 0.01, "emotional_safety": 0.01},
                        },
                        "memory_tags": ["repair_from_dishonesty"],
                    },
                    {
                        "text": "Harsh punishment.",
                        "updates": {
                            "child": {"honesty_baseline": -0.03, "self_worth": -0.03, "emotional_safety": -0.02},
                        },
                        "memory_tags": ["harsh_punishment_for_lie"],
                    },
                    {
                        "text": "Ignore.",
                        "updates": {
                            "child": {"honesty_baseline": -0.02, "self_worth": -0.01},
                        },
                        "memory_tags": ["ignored_dishonesty"],
                    },
                ],
            },
            {
                "title": "School Performance Drop",
                "blocks": {
                    "Morning": "Teacher reports declining focus.",
                    "Afternoon": "Discussion of pressure vs support.",
                    "Evening": "Child reaction to expectations.",
                    "Night": "Silent withdrawal or breakdown.",
                },
                "choices": [
                    {
                        "text": "Support gently.",
                        "updates": {
                            "child": {"self_worth": 0.02, "anxiety_baseline": -0.02},
                        },
                        "memory_tags": ["supportive_response_to_struggle"],
                    },
                    {
                        "text": "Increase academic pressure.",
                        "updates": {
                            "child": {"self_worth": -0.03, "anxiety_baseline": 0.04},
                        },
                        "memory_tags": ["pressure_increase"],
                    },
                    {
                        "text": "Blame your partner.",
                        "updates": {
                            "relationship": {"resentment": 0.02},
                            "child": {"self_worth": -0.02, "anxiety_baseline": 0.02},
                        },
                        "memory_tags": ["blame_for_child_struggle"],
                    },
                ],
            },
            {
                "title": "Late Night Argument (Child Overhears)",
                "blocks": {
                    "Morning": "Tension building.",
                    "Afternoon": "Minor disagreement escalates.",
                    "Evening": "Heated argument while child awake.",
                    "Night": "Child remains silent in room.",
                },
                "choices": [
                    {
                        "text": "De-escalate.",
                        "updates": {
                            "child": {"conflict_internalization": -0.03, "emotional_safety": 0.02},
                            "relationship": {"conflict_intensity": -0.02},
                        },
                        "memory_tags": ["overheard_conflict", "de_escalation"],
                    },
                    {
                        "text": "Escalate.",
                        "updates": {
                            "child": {"conflict_internalization": 0.05, "emotional_safety": -0.04},
                            "relationship": {"conflict_intensity": 0.04},
                        },
                        "memory_tags": ["overheard_conflict", "escalation"],
                    },
                    {
                        "text": "Leave house.",
                        "updates": {
                            "child": {"conflict_internalization": 0.03, "emotional_safety": -0.02},
                            "relationship": {"emotional_closeness": -0.03},
                        },
                        "memory_tags": ["overheard_conflict", "parent_absence"],
                    },
                ],
            },
            {
                "title": "Emotional Withdrawal",
                "blocks": {
                    "Morning": "Child quieter than usual.",
                    "Afternoon": "Teacher notes isolation.",
                    "Evening": "Opportunity to connect.",
                    "Night": "Child avoids conversation.",
                },
                "choices": [
                    {
                        "text": "Reach out vulnerably.",
                        "updates": {
                            "child": {"emotional_expression": 0.03, "attachment_security": 0.02, "bond_strength": 0.02},
                        },
                        "memory_tags": ["withdrawn_response_vulnerable"],
                    },
                    {
                        "text": "Demand communication.",
                        "updates": {
                            "child": {"emotional_expression": -0.03, "attachment_security": -0.02, "withdrawal_pattern": 0.03},
                        },
                        "memory_tags": ["withdrawn_response_demanding"],
                    },
                    {
                        "text": "Accept distance.",
                        "updates": {
                            "child": {"emotional_expression": -0.02, "attachment_security": -0.01, "withdrawal_pattern": 0.02},
                        },
                        "memory_tags": ["withdrawn_response_accepted"],
                    },
                ],
            },
            {
                "title": "Favoritism",
                "blocks": {
                    "Morning": "Child prefers one parent.",
                    "Afternoon": "Other parent feels excluded.",
                    "Evening": "Subtle tension.",
                    "Night": "Resentment shift.",
                },
                "choices": [
                    {
                        "text": "Encourage balance.",
                        "updates": {
                            "relationship": {"resentment": 0.0, "emotional_closeness": 0.01},
                            "child": {"loyalty_bias": 0.0},
                        },
                        "memory_tags": ["favoritism_balanced"],
                    },
                    {
                        "text": "Compete for attention.",
                        "updates": {
                            "relationship": {"resentment": 0.03, "emotional_closeness": -0.02},
                            "child": {"loyalty_bias": 0.03},
                        },
                        "memory_tags": ["favoritism_competitive"],
                    },
                    {
                        "text": "Act indifferent.",
                        "updates": {
                            "relationship": {"resentment": 0.02, "emotional_closeness": -0.01},
                            "child": {"loyalty_bias": 0.01},
                        },
                        "memory_tags": ["favoritism_indifferent"],
                    },
                ],
            },
            {
                "title": "Boundary Test",
                "blocks": {
                    "Morning": "Child deliberately breaks a rule.",
                    "Afternoon": "Consequence decision.",
                    "Evening": "Child challenges authority verbally.",
                    "Night": "Authority dynamic stabilizes or weakens.",
                },
                "choices": [
                    {
                        "text": "Calm, consistent consequence.",
                        "updates": {
                            "child": {"authority_structure": 0.03, "honesty_baseline": 0.01, "self_worth": 0.01},
                        },
                        "memory_tags": ["consistent_boundary"],
                    },
                    {
                        "text": "Emotional overreaction.",
                        "updates": {
                            "child": {"authority_structure": -0.02, "honesty_baseline": -0.02, "manipulation_tendency": 0.02},
                        },
                        "memory_tags": ["emotional_overreaction_boundary"],
                    },
                    {
                        "text": "Inconsistent response.",
                        "updates": {
                            "child": {"authority_structure": -0.03, "honesty_baseline": -0.01, "manipulation_tendency": 0.03},
                        },
                        "memory_tags": ["inconsistent_boundary"],
                    },
                ],
            },
            {
                "title": "Age 7 Reflection (State Shift)",
                "blocks": {
                    "Morning": "Quiet breakfast with reflective mood.",
                    "Afternoon": "Subtle signs of personality pattern emerging.",
                    "Evening": "Family dinner feels emotionally different than Act 1.",
                    "Night": "Child sleeps as patterns lock in.",
                },
                "choices": [
                    {
                        "text": "Acknowledge patterns with honesty.",
                        "updates": {
                            "child": {"emotional_expression": 0.02},
                            "relationship": {"communication_openness": 0.02},
                        },
                        "memory_tags": ["act2_honest_reflection"],
                    },
                    {
                        "text": "Avoid reflection.",
                        "updates": {
                            "child": {"emotional_expression": -0.01},
                            "relationship": {"communication_openness": -0.02},
                        },
                        "memory_tags": ["act2_avoidance"],
                    },
                    {
                        "text": "Blame external factors.",
                        "updates": {
                            "child": {"emotional_expression": -0.02},
                            "relationship": {"communication_openness": -0.01},
                        },
                        "memory_tags": ["act2_external_blame"],
                    },
                ],
            },
        ]

        return [self._build_authored_day_event(2, index + 1, payload, "4-7") for index, payload in enumerate(day_payloads)]

    def _build_authored_day_event(self, act: int, day: int, payload: Dict[str, object], age_range: str) -> DayEvent:
        time_blocks: Dict[str, TimeBlockEvent] = {}
        block_descriptions = payload["blocks"]
        choices = payload["choices"]

        for block in TIME_BLOCKS:
            scenario_text = f"Act {act}, Day {day} - {payload['title']} ({block}). {block_descriptions[block]}"
            player_choices = [
                PlayerChoice(
                    choice_id=f"a{act}d{day}_{block.lower()}_c{index + 1}",
                    text=choice["text"],
                    updates=choice["updates"],
                    memory_tags=choice["memory_tags"],
                )
                for index, choice in enumerate(choices)
            ]

            time_blocks[block] = TimeBlockEvent(
                block_name=block,
                scenario_text=scenario_text,
                player_choices=player_choices,
            )

        return DayEvent(
            act_number=act,
            day_number=day,
            title=payload["title"],
            age_range=age_range,
            time_blocks=time_blocks,
        )

    def _build_generic_day_event(self, act: int, day: int, title: str, age_range: str) -> DayEvent:
        time_blocks: Dict[str, TimeBlockEvent] = {}
        for block in TIME_BLOCKS:
            scenario_text = (
                f"Act {act}, Day {day} - {title} ({block}). "
                f"The family faces a moment that can strengthen or strain co-parenting dynamics."
            )
            time_blocks[block] = TimeBlockEvent(
                block_name=block,
                scenario_text=scenario_text,
                player_choices=self._build_generic_choices(act, day, block),
            )

        return DayEvent(
            act_number=act,
            day_number=day,
            title=title,
            age_range=age_range,
            time_blocks=time_blocks,
        )

    def _build_generic_choices(self, act: int, day: int, block: str) -> List[PlayerChoice]:
        block_factor = {
            "Morning": 0.8,
            "Afternoon": 1.0,
            "Evening": 1.1,
            "Night": 1.2,
        }[block]
        intensity = 0.01 * block_factor

        collaborative = PlayerChoice(
            choice_id=f"a{act}d{day}_{block.lower()}_collab",
            text="Address the situation calmly and include your partner in the decision.",
            updates={
                "relationship": {
                    "trust": 0.03 + intensity,
                    "communication_openness": 0.02 + intensity,
                    "supportiveness": 0.02,
                    "resentment": -0.02,
                },
                "ai_parent": {
                    "stress_level": -0.02,
                    "supportiveness": 0.02,
                    "defensiveness": -0.01,
                    "emotional_safety": 0.02,
                },
                "child": {
                    "attachment_security": 0.02,
                    "emotional_safety": 0.02,
                    "self_worth": 0.01,
                    "conflict_internalization": -0.01,
                },
            },
            memory_tags=["repair_attempt", "co_regulation"],
        )

        reactive = PlayerChoice(
            choice_id=f"a{act}d{day}_{block.lower()}_reactive",
            text="React from exhaustion and push through without alignment.",
            updates={
                "relationship": {
                    "trust": -0.02 - intensity,
                    "communication_openness": -0.02,
                    "supportiveness": -0.02,
                    "resentment": 0.03 + intensity,
                    "defensiveness": 0.02,
                },
                "ai_parent": {
                    "stress_level": 0.03,
                    "supportiveness": -0.02,
                    "defensiveness": 0.02,
                    "emotional_safety": -0.02,
                },
                "child": {
                    "attachment_security": -0.02,
                    "emotional_safety": -0.02,
                    "self_worth": -0.01,
                    "conflict_internalization": 0.02,
                },
            },
            memory_tags=["rupture", "emotional_overload"],
        )

        avoidant = PlayerChoice(
            choice_id=f"a{act}d{day}_{block.lower()}_avoidant",
            text="Avoid the conversation and delay the decision.",
            updates={
                "relationship": {
                    "trust": -0.01,
                    "communication_openness": -0.03,
                    "resentment": 0.02,
                    "supportiveness": -0.01,
                },
                "ai_parent": {
                    "stress_level": 0.01,
                    "supportiveness": -0.01,
                    "defensiveness": 0.01,
                },
                "child": {
                    "attachment_security": -0.01,
                    "emotional_safety": -0.01,
                    "conflict_internalization": 0.02,
                },
            },
            memory_tags=["emotional_distance", "unresolved_tension"],
        )

        return [collaborative, reactive, avoidant]
