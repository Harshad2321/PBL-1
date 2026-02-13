from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict
import re

from nurture.core.enums import EmotionType, PersonalityTrait, ResponseStrategy

@dataclass
class LearnedPattern:
    pattern_type: str
    value: str
    frequency: int = 0
    last_seen: datetime = field(default_factory=datetime.now)
    associated_emotions: Dict[EmotionType, float] = field(default_factory=dict)
    effectiveness_score: float = 0.5

    def decay_frequency(self, steps: int = 1) -> None:
        self.frequency = max(0, self.frequency - steps)

class UserProfileAnalyzer:

    def __init__(self):
        self.sentiment_keywords = {
            "positive": ["good", "great", "love", "excellent", "happy", "agree", "yes", "perfect"],
            "negative": ["bad", "hate", "terrible", "awful", "angry", "disagree", "no", "wrong"],
            "neutral": ["ok", "maybe", "think", "perhaps", "could", "would"]
        }

        self.communication_styles = {
            "direct": ["i think", "i want", "we should", "must", "need to"],
            "indirect": ["maybe we", "could we", "would you", "seems like"],
            "emotional": ["feel", "feel", "heart", "love", "hate", "upset"],
            "logical": ["because", "reason", "logic", "evidence", "fact"]
        }

    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        text_lower = text.lower()

        pos_count = sum(1 for word in self.sentiment_keywords["positive"] if word in text_lower)
        neg_count = sum(1 for word in self.sentiment_keywords["negative"] if word in text_lower)

        if pos_count > neg_count:
            intensity = min(1.0, pos_count / 5.0)
            return "positive", intensity
        elif neg_count > pos_count:
            intensity = min(1.0, neg_count / 5.0)
            return "negative", intensity
        else:
            return "neutral", 0.5

    def extract_topics(self, text: str) -> List[str]:
        topics = []

        topic_map = {
            "screen_time": ["screen", "game", "device", "phone", "tv", "video"],
            "discipline": ["punishment", "discipline", "ground", "consequence"],
            "education": ["school", "homework", "study", "learn", "education"],
            "health": ["health", "sleep", "exercise", "eat", "nutrition"],
            "relationship": ["love", "care", "bond", "trust", "support"],
            "money": ["money", "allowance", "spend", "cost", "budget"],
            "free_time": ["free time", "play", "fun", "relax", "hobby"],
        }

        text_lower = text.lower()
        for topic, keywords in topic_map.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)

        return topics if topics else ["general"]

    def extract_communication_style(self, text: str) -> str:
        text_lower = text.lower()

        style_scores = {}
        for style, phrases in self.communication_styles.items():
            style_scores[style] = sum(1 for phrase in phrases if phrase in text_lower)

        if not any(style_scores.values()):
            return "neutral"

        return max(style_scores, key=style_scores.get)

    def extract_preferences(self, text: str) -> Dict[str, Any]:
        return {
            "sentiment": self.analyze_sentiment(text),
            "topics": self.extract_topics(text),
            "style": self.extract_communication_style(text),
            "text_length": len(text.split()),
            "formality": self._estimate_formality(text),
        }

    def _estimate_formality(self, text: str) -> str:
        casual_words = ["hey", "lol", "yeah", "dude", "gonna", "wanna", "don't"]
        formal_words = ["however", "furthermore", "consequently", "therefore"]

        casual_count = sum(1 for word in casual_words if word.lower() in text.lower())
        formal_count = sum(1 for word in formal_words if word.lower() in text.lower())

        if casual_count > formal_count:
            return "casual"
        elif formal_count > casual_count:
            return "formal"
        else:
            return "neutral"

class AdaptiveLearningEngine:

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.analyzer = UserProfileAnalyzer()

        self.learned_patterns: Dict[str, List[LearnedPattern]] = defaultdict(list)
        self.user_profile: Dict[str, Any] = {}
        self.interaction_history: List[Dict[str, Any]] = []
        self.topic_preferences: Dict[str, float] = defaultdict(float)
        self.strategy_effectiveness: Dict[ResponseStrategy, float] = defaultdict(lambda: 0.5)

        self.learning_rate = 0.1
        self.max_patterns = 100
        self.interaction_count = 0

    def learn_from_interaction(
        self,
        user_input: str,
        ai_response: str,
        outcome_quality: float = 0.5
    ) -> None:
        self.interaction_count += 1

        preferences = self.analyzer.extract_preferences(user_input)

        sentiment, intensity = preferences["sentiment"]
        self._learn_sentiment_pattern(sentiment, intensity, outcome_quality)

        topics = preferences["topics"]
        self._learn_topic_preferences(topics, outcome_quality)

        communication_style = preferences["style"]
        self._learn_communication_style(communication_style, outcome_quality)

        self.interaction_history.append({
            "timestamp": datetime.now(),
            "input": user_input,
            "response": ai_response,
            "preferences": preferences,
            "outcome": outcome_quality
        })

        self._update_user_profile()

    def _learn_sentiment_pattern(self, sentiment: str, intensity: float, quality: float) -> None:
        key = f"sentiment_{sentiment}"

        patterns = self.learned_patterns.get(key, [])
        pattern = next((p for p in patterns if p.value == sentiment), None)

        if pattern is None:
            pattern = LearnedPattern(
                pattern_type="sentiment",
                value=sentiment,
                effectiveness_score=quality
            )
            self.learned_patterns[key].append(pattern)
        else:
            pattern.effectiveness_score = (
                pattern.effectiveness_score * (1 - self.learning_rate) +
                quality * self.learning_rate
            )

        pattern.frequency += 1
        pattern.last_seen = datetime.now()

    def _learn_topic_preferences(self, topics: List[str], quality: float) -> None:
        for topic in topics:
            self.topic_preferences[topic] = (
                self.topic_preferences[topic] * (1 - self.learning_rate) +
                quality * self.learning_rate
            )

    def _learn_communication_style(self, style: str, quality: float) -> None:
        key = f"style_{style}"
        patterns = self.learned_patterns.get(key, [])
        pattern = next((p for p in patterns if p.value == style), None)

        if pattern is None:
            pattern = LearnedPattern(
                pattern_type="communication_style",
                value=style,
                effectiveness_score=quality
            )
            self.learned_patterns[key].append(pattern)
        else:
            pattern.effectiveness_score = (
                pattern.effectiveness_score * (1 - self.learning_rate) +
                quality * self.learning_rate
            )

        pattern.frequency += 1

    def _update_user_profile(self) -> None:
        recent_interactions = self.interaction_history[-10:]

        if recent_interactions:
            avg_quality = sum(i["outcome"] for i in recent_interactions) / len(recent_interactions)

            sentiments = [i["preferences"]["sentiment"][0] for i in recent_interactions]
            most_common_sentiment = max(set(sentiments), key=sentiments.count) if sentiments else "neutral"

            styles = [i["preferences"]["style"] for i in recent_interactions]
            most_common_style = max(set(styles), key=styles.count) if styles else "neutral"

            self.user_profile = {
                "avg_satisfaction": avg_quality,
                "dominant_sentiment": most_common_sentiment,
                "dominant_style": most_common_style,
                "total_interactions": self.interaction_count,
                "favorite_topics": sorted(
                    self.topic_preferences.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
            }

    def get_personality_adjustments(self) -> Dict[PersonalityTrait, float]:
        adjustments = {}

        if self.user_profile.get("dominant_style") == "emotional":
            adjustments[PersonalityTrait.WARMTH] = 0.15
            adjustments[PersonalityTrait.STRICTNESS] = -0.1
        elif self.user_profile.get("dominant_style") == "logical":
            adjustments[PersonalityTrait.STRICTNESS] = 0.1
            adjustments[PersonalityTrait.FLEXIBILITY] = -0.1

        if self.user_profile.get("dominant_sentiment") == "positive":
            adjustments[PersonalityTrait.WARMTH] = 0.1
        elif self.user_profile.get("dominant_sentiment") == "negative":
            adjustments[PersonalityTrait.PATIENCE] = 0.15

        fav_topics = self.user_profile.get("favorite_topics", [])
        if fav_topics and fav_topics[0][0] == "relationship":
            adjustments[PersonalityTrait.WARMTH] = 0.1

        return adjustments

    def get_recommended_strategies(self, n: int = 3) -> List[ResponseStrategy]:
        if self.user_profile.get("dominant_style") == "emotional":
            return [
                ResponseStrategy.SUPPORTIVE,
                ResponseStrategy.EMPATHETIC,
                ResponseStrategy.COMPROMISING
            ]
        elif self.user_profile.get("dominant_style") == "logical":
            return [
                ResponseStrategy.PRACTICAL,
                ResponseStrategy.ASSERTIVE,
                ResponseStrategy.COMPROMISING
            ]
        else:
            return [
                ResponseStrategy.SUPPORTIVE,
                ResponseStrategy.PRACTICAL,
                ResponseStrategy.COMPROMISING
            ]

    def get_learning_summary(self) -> Dict[str, Any]:
        return {
            "total_interactions": self.interaction_count,
            "user_profile": self.user_profile,
            "learned_patterns_count": sum(len(v) for v in self.learned_patterns.values()),
            "top_topics": dict(sorted(
                self.topic_preferences.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
            "recommended_strategies": [s.value for s in self.get_recommended_strategies()]
        }

    def decay_learning(self, steps: int = 1) -> None:
        for patterns_list in self.learned_patterns.values():
            for pattern in patterns_list:
                pattern.decay_frequency(steps)

        for key in list(self.learned_patterns.keys()):
            self.learned_patterns[key] = [
                p for p in self.learned_patterns[key] if p.frequency > 0
            ]
            if not self.learned_patterns[key]:
                del self.learned_patterns[key]
