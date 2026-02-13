from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from collections import defaultdict
import json
from pathlib import Path

@dataclass
class UserPattern:
    pattern_type: str
    pattern_value: str
    frequency: int = 0
    last_observed: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0

    def update(self, boost: float = 0.1) -> None:
        self.frequency += 1
        self.last_observed = datetime.now()
        self.confidence = min(1.0, self.confidence + boost)

    def decay(self) -> None:
        hours_passed = (datetime.now() - self.last_observed).total_seconds() / 3600
        decay_factor = 0.99 ** hours_passed
        self.confidence *= decay_factor

class LearningSystem:

    def __init__(self, user_id: str = "player"):
        self.user_id = user_id

        self.patterns: Dict[str, UserPattern] = {}

        self.interaction_history: List[Dict[str, Any]] = []

        self.story_decisions: List[Dict[str, Any]] = []

        self.topics_discussed: Set[str] = set()

        self.sentiment_history: List[float] = []

        self.decision_style: Dict[str, float] = {
            "collaborative": 0.5,
            "assertive": 0.5,
            "compromising": 0.5,
            "empathetic": 0.5,
            "practical": 0.5,
        }

        self.adaptation_level = 0.0
        self.total_interactions = 0

    def learn_from_input(self, user_input: str) -> None:
        self.total_interactions += 1

        sentiment = self._analyze_sentiment(user_input)
        self.sentiment_history.append(sentiment)

        topics = self._extract_topics(user_input)
        self.topics_discussed.update(topics)

        style = self._detect_decision_style(user_input)
        if style:
            self.decision_style[style] = min(1.0, self.decision_style[style] + 0.1)

        self.interaction_history.append({
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "sentiment": sentiment,
            "topics": list(topics),
            "decision_style": style,
        })

        self.adaptation_level = min(1.0, self.adaptation_level + 0.02)

    def learn_from_outcome(self, ai_response: str, user_satisfaction: float) -> None:
        if not self.interaction_history:
            return

        last_interaction = self.interaction_history[-1]
        last_interaction["ai_response"] = ai_response
        last_interaction["satisfaction"] = user_satisfaction

        if user_satisfaction > 0.3:
            self.adaptation_level = min(1.0, self.adaptation_level + 0.03)

    def record_story_decision(self, choice: str, impact: str, outcome: float) -> None:
        self.story_decisions.append({
            "timestamp": datetime.now().isoformat(),
            "choice": choice,
            "impact": impact,
            "outcome": outcome,
        })

    def _analyze_sentiment(self, text: str) -> float:
        text_lower = text.lower()

        positive_words = {
            "yes", "agree", "love", "great", "good", "excellent",
            "perfect", "happy", "wonderful", "amazing", "awesome"
        }
        negative_words = {
            "no", "disagree", "hate", "bad", "terrible", "awful",
            "angry", "frustrated", "upset", "horrible", "stupid"
        }

        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        total = pos_count + neg_count
        if total == 0:
            return 0.0

        return (pos_count - neg_count) / total

    def _extract_topics(self, text: str) -> Set[str]:
        text_lower = text.lower()
        topics = set()

        topic_keywords = {
            "education": ["school", "homework", "learning", "study", "grades"],
            "health": ["sleep", "exercise", "healthy", "diet", "doctor"],
            "discipline": ["rules", "punishment", "behavior", "discipline"],
            "screen_time": ["phone", "video", "game", "screen", "app"],
            "emotions": ["feel", "upset", "sad", "angry", "happy", "scared"],
            "family": ["together", "family", "parent", "brother", "sister"],
            "friends": ["friend", "social", "play", "group", "team"],
            "future": ["career", "college", "future", "dream", "goal"],
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.add(topic)

        return topics

    def _detect_decision_style(self, text: str) -> Optional[str]:
        text_lower = text.lower()

        style_indicators = {
            "collaborative": ["we", "together", "both", "partner", "team", "agree"],
            "assertive": ["i", "must", "have to", "need", "should", "right"],
            "compromising": ["maybe", "could", "perhaps", "try", "consider"],
            "empathetic": ["feel", "understand", "care", "love", "concern", "hurt"],
            "practical": ["solve", "fix", "plan", "strategy", "solution", "work"],
        }

        max_style = None
        max_count = 0

        for style, indicators in style_indicators.items():
            count = sum(1 for indicator in indicators if indicator in text_lower)
            if count > max_count:
                max_count = count
                max_style = style

        return max_style if max_count > 0 else None

    def get_dominant_style(self) -> str:
        return max(self.decision_style, key=self.decision_style.get)

    def get_ai_personality_adjustments(self) -> Dict[str, float]:
        if self.adaptation_level < 0.1:
            return {}

        adjustments = {}

        dominant_style = self.get_dominant_style()
        adjustments[f"increase_{dominant_style}"] = self.adaptation_level * 0.5

        if self.sentiment_history:
            avg_sentiment = sum(self.sentiment_history) / len(self.sentiment_history)
            adjustments["warmth"] = avg_sentiment * 0.3

        if "emotions" in self.topics_discussed:
            adjustments["empathy"] = 0.3
        if "family" in self.topics_discussed:
            adjustments["family_focus"] = 0.3

        return adjustments

    def get_learning_summary(self) -> Dict[str, Any]:
        return {
            "total_interactions": self.total_interactions,
            "adaptation_level": self.adaptation_level,
            "dominant_decision_style": self.get_dominant_style(),
            "topics_discussed": list(self.topics_discussed),
            "average_sentiment": sum(self.sentiment_history) / len(self.sentiment_history) if self.sentiment_history else 0.0,
            "story_decisions_made": len(self.story_decisions),
            "personality_adjustments": self.get_ai_personality_adjustments(),
        }

    def save(self, filepath: Path) -> None:
        data = {
            "user_id": self.user_id,
            "adaptation_level": self.adaptation_level,
            "total_interactions": self.total_interactions,
            "decision_style": self.decision_style,
            "topics_discussed": list(self.topics_discussed),
            "sentiment_history": self.sentiment_history,
            "interaction_history": self.interaction_history,
            "story_decisions": self.story_decisions,
        }
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: Path) -> 'LearningSystem':
        with open(filepath, 'r') as f:
            data = json.load(f)

        system = cls(user_id=data.get("user_id", "player"))
        system.adaptation_level = data.get("adaptation_level", 0.0)
        system.total_interactions = data.get("total_interactions", 0)
        system.decision_style = data.get("decision_style", system.decision_style)
        system.topics_discussed = set(data.get("topics_discussed", []))
        system.sentiment_history = data.get("sentiment_history", [])
        system.interaction_history = data.get("interaction_history", [])
        system.story_decisions = data.get("story_decisions", [])

        return system
