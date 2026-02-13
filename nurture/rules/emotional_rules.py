from typing import Dict, Any, List
from nurture.rules.rule_engine import Rule, RuleCategory, RulePriority

class EmotionalRules:

    @staticmethod
    def get_all_rules() -> List[Rule]:
        rules = []


        rules.append(Rule(
            id="emotional_regulation_capacity",
            name="Emotional Regulation",
            description="High regulation capacity dampens extreme emotions",
            category=RuleCategory.EMOTIONAL,
            priority=RulePriority.HIGH,
            condition=lambda ctx: (
                ctx.get("regulation_capacity", 0.5) > 0.7 and
                ctx.get("max_emotion_intensity", 0) > 0.8
            ),
            action=lambda ctx: {
                "dampen_emotions": True,
                "dampen_factor": 0.2,
                "maintain_composure": True
            }
        ))

        rules.append(Rule(
            id="low_regulation_volatility",
            name="Low Regulation Volatility",
            description="Low regulation leads to stronger emotional swings",
            category=RuleCategory.EMOTIONAL,
            priority=RulePriority.HIGH,
            condition=lambda ctx: ctx.get("regulation_capacity", 0.5) < 0.3,
            action=lambda ctx: {
                "amplify_emotions": True,
                "amplify_factor": 1.3,
                "volatility_warning": True
            }
        ))


        rules.append(Rule(
            id="anger_suppresses_fear",
            name="Anger Suppresses Fear",
            description="High anger reduces fear response",
            category=RuleCategory.EMOTIONAL,
            priority=RulePriority.MEDIUM,
            condition=lambda ctx: ctx.get("anger", 0) > 0.6,
            action=lambda ctx: {
                "fear_reduction": 0.2,
                "anxiety_reduction": 0.1
            }
        ))

        rules.append(Rule(
            id="trust_reduces_anxiety",
            name="Trust Reduces Anxiety",
            description="High trust in partner reduces anxiety",
            category=RuleCategory.EMOTIONAL,
            priority=RulePriority.MEDIUM,
            condition=lambda ctx: ctx.get("trust_emotion", 0) > 0.7,
            action=lambda ctx: {
                "anxiety_reduction": 0.15,
                "fear_reduction": 0.1,
                "security_feeling": True
            }
        ))

        rules.append(Rule(
            id="sadness_reduces_anger",
            name="Sadness Reduces Anger",
            description="Deep sadness can reduce active anger",
            category=RuleCategory.EMOTIONAL,
            priority=RulePriority.MEDIUM,
            condition=lambda ctx: ctx.get("sadness", 0) > 0.7,
            action=lambda ctx: {
                "anger_reduction": 0.15,
                "withdrawal_tendency": True
            }
        ))

        rules.append(Rule(
            id="joy_reduces_negative_emotions",
            name="Joy Reduces Negative Emotions",
            description="High joy reduces various negative emotions",
            category=RuleCategory.EMOTIONAL,
            priority=RulePriority.MEDIUM,
            condition=lambda ctx: ctx.get("joy", 0) > 0.7,
            action=lambda ctx: {
                "anger_reduction": 0.1,
                "sadness_reduction": 0.15,
                "anxiety_reduction": 0.1,
                "positive_outlook": True
            }
        ))


        rules.append(Rule(
            id="chronic_stress_effects",
            name="Chronic Stress Effects",
            description="Sustained high stress has cascading effects",
            category=RuleCategory.EMOTIONAL,
            priority=RulePriority.HIGH,
            condition=lambda ctx: (
                ctx.get("stress_level", 0) > 0.7 and
                ctx.get("stress_duration", 0) > 3
            ),
            action=lambda ctx: {
                "patience_penalty": 0.2,
                "irritability_boost": 0.15,
                "joy_reduction": 0.1,
                "exhaustion_flag": True
            }
        ))

        rules.append(Rule(
            id="stress_recovery",
            name="Stress Recovery",
            description="Low stress allows emotional recovery",
            category=RuleCategory.EMOTIONAL,
            priority=RulePriority.LOW,
            condition=lambda ctx: ctx.get("stress_level", 0) < 0.3,
            action=lambda ctx: {
                "allow_recovery": True,
                "recovery_rate": 1.2,
                "contentment_boost": 0.05
            }
        ))


        rules.append(Rule(
            id="negative_memory_activation",
            name="Negative Memory Activation",
            description="Current negative state activates negative memories",
            category=RuleCategory.EMOTIONAL,
            priority=RulePriority.MEDIUM,
            condition=lambda ctx: ctx.get("emotional_valence", 0) < -0.4,
            action=lambda ctx: {
                "bias_memory_retrieval": "negative",
                "memory_valence_preference": (-1.0, -0.2),
                "rumination_risk": True
            }
        ))

        rules.append(Rule(
            id="positive_memory_activation",
            name="Positive Memory Activation",
            description="Positive state makes positive memories more accessible",
            category=RuleCategory.EMOTIONAL,
            priority=RulePriority.MEDIUM,
            condition=lambda ctx: ctx.get("emotional_valence", 0) > 0.4,
            action=lambda ctx: {
                "bias_memory_retrieval": "positive",
                "memory_valence_preference": (0.2, 1.0),
                "optimism_boost": True
            }
        ))


        rules.append(Rule(
            id="emotional_contagion_positive",
            name="Positive Emotional Contagion",
            description="Partner's positive emotions can spread",
            category=RuleCategory.EMOTIONAL,
            priority=RulePriority.LOW,
            condition=lambda ctx: (
                ctx.get("partner_valence", 0) > 0.5 and
                ctx.get("empathy_level", 0.5) > 0.5
            ),
            action=lambda ctx: {
                "joy_boost": ctx.get("partner_valence", 0) * 0.2,
                "contagion_type": "positive"
            }
        ))

        rules.append(Rule(
            id="emotional_contagion_negative",
            name="Negative Emotional Contagion",
            description="Partner's negative emotions can affect mood",
            category=RuleCategory.EMOTIONAL,
            priority=RulePriority.LOW,
            condition=lambda ctx: (
                ctx.get("partner_valence", 0) < -0.3 and
                ctx.get("empathy_level", 0.5) > 0.6
            ),
            action=lambda ctx: {
                "sadness_boost": abs(ctx.get("partner_valence", 0)) * 0.15,
                "contagion_type": "negative",
                "support_urge": True
            }
        ))


        rules.append(Rule(
            id="emotional_overflow",
            name="Emotional Overflow",
            description="Too many strong emotions cause overwhelm",
            category=RuleCategory.EMOTIONAL,
            priority=RulePriority.HIGH,
            condition=lambda ctx: ctx.get("total_emotion_intensity", 0) > 3.0,
            action=lambda ctx: {
                "overwhelmed": True,
                "reduce_all_emotions": 0.1,
                "need_pause": True,
                "coherence_penalty": 0.2
            }
        ))

        return rules

    @staticmethod
    def calculate_emotion_interaction(
        emotions: Dict[str, float]
    ) -> Dict[str, float]:
        modifications = {}

        anger = emotions.get("anger", 0)
        sadness = emotions.get("sadness", 0)
        joy = emotions.get("joy", 0)
        fear = emotions.get("fear", 0)
        trust = emotions.get("trust", 0)

        if anger > 0.5 and sadness > 0.5:
            if anger > sadness:
                modifications["sadness"] = -0.1
            else:
                modifications["anger"] = -0.1

        if joy > 0.6:
            modifications["anger"] = -joy * 0.15
            modifications["sadness"] = -joy * 0.15
            modifications["fear"] = -joy * 0.1

        if fear > 0.4 and anger > 0.4:
            modifications["anxiety"] = 0.1

        if trust > 0.7:
            modifications["fear"] = -trust * 0.2
            modifications["anxiety"] = -trust * 0.15

        return modifications
