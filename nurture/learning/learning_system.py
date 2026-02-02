"""
Learning System for Nurture Simulation
=======================================

Enables AI to learn from user inputs and adapt behavior over time.
Tracks patterns in user decisions, sentiment, preferences, and adjusts
AI responses accordingly.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from collections import defaultdict
import json
from pathlib import Path


@dataclass
class UserPattern:
    """Represents a learned pattern about the user."""
    pattern_type: str  # "sentiment", "topic", "decision", "preference"
    pattern_value: str  # The actual pattern (e.g., "prefers_collaboration")
    frequency: int = 0  # How many times observed
    last_observed: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0  # 0.0 to 1.0, how confident in this pattern
    
    def update(self, boost: float = 0.1) -> None:
        """Update pattern with new observation."""
        self.frequency += 1
        self.last_observed = datetime.now()
        # Increase confidence with each observation
        self.confidence = min(1.0, self.confidence + boost)
    
    def decay(self) -> None:
        """Reduce confidence over time (forgetting)."""
        hours_passed = (datetime.now() - self.last_observed).total_seconds() / 3600
        decay_factor = 0.99 ** hours_passed  # Exponential decay
        self.confidence *= decay_factor


class LearningSystem:
    """
    Tracks user behavior and AI learning over time.
    
    Learns from:
    - User input sentiment (positive, negative, neutral)
    - Topics user cares about
    - Decision patterns (collaborative vs assertive)
    - Preferences and dislikes
    - Story choices and their impact
    
    Features:
    - Pattern recognition
    - Adaptive AI personality
    - Memory of user preferences
    - Story progression tracking
    """
    
    def __init__(self, user_id: str = "player"):
        """Initialize learning system."""
        self.user_id = user_id
        
        # Learned patterns about the user
        self.patterns: Dict[str, UserPattern] = {}
        
        # Interaction history for analysis
        self.interaction_history: List[Dict[str, Any]] = []
        
        # Story decisions and their outcomes
        self.story_decisions: List[Dict[str, Any]] = []
        
        # Topics mentioned by user
        self.topics_discussed: Set[str] = set()
        
        # Sentiment tracking
        self.sentiment_history: List[float] = []  # -1 to 1
        
        # Decision style preferences
        self.decision_style: Dict[str, float] = {
            "collaborative": 0.5,  # Works well with others
            "assertive": 0.5,      # Takes charge
            "compromising": 0.5,   # Finds middle ground
            "empathetic": 0.5,     # Focuses on emotions
            "practical": 0.5,      # Focus on solutions
        }
        
        # AI adaptation stats
        self.adaptation_level = 0.0  # How much AI has learned (0-1)
        self.total_interactions = 0
    
    def learn_from_input(self, user_input: str) -> None:
        """Learn from user input."""
        self.total_interactions += 1
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(user_input)
        self.sentiment_history.append(sentiment)
        
        # Detect topics
        topics = self._extract_topics(user_input)
        self.topics_discussed.update(topics)
        
        # Detect decision style from input
        style = self._detect_decision_style(user_input)
        if style:
            self.decision_style[style] = min(1.0, self.decision_style[style] + 0.1)
        
        # Record interaction
        self.interaction_history.append({
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "sentiment": sentiment,
            "topics": list(topics),
            "decision_style": style,
        })
        
        # Update adaptation level
        self.adaptation_level = min(1.0, self.adaptation_level + 0.02)
    
    def learn_from_outcome(self, ai_response: str, user_satisfaction: float) -> None:
        """
        Learn from interaction outcome.
        
        Args:
            ai_response: What the AI said
            user_satisfaction: -1 (bad) to 1 (good)
        """
        if not self.interaction_history:
            return
        
        last_interaction = self.interaction_history[-1]
        last_interaction["ai_response"] = ai_response
        last_interaction["satisfaction"] = user_satisfaction
        
        # Strengthen patterns that led to good outcomes
        if user_satisfaction > 0.3:
            self.adaptation_level = min(1.0, self.adaptation_level + 0.03)
    
    def record_story_decision(self, choice: str, impact: str, outcome: float) -> None:
        """
        Record a story decision and its outcome.
        
        Args:
            choice: What the user chose
            impact: Description of impact
            outcome: How good the outcome was (-1 to 1)
        """
        self.story_decisions.append({
            "timestamp": datetime.now().isoformat(),
            "choice": choice,
            "impact": impact,
            "outcome": outcome,
        })
    
    def _analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of user input.
        
        Returns: -1.0 (very negative) to 1.0 (very positive)
        """
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
        """Extract topics from user input."""
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
        """Detect user's decision-making style from input."""
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
        """Get the user's most dominant decision style."""
        return max(self.decision_style, key=self.decision_style.get)
    
    def get_ai_personality_adjustments(self) -> Dict[str, float]:
        """
        Get adjustments AI should make based on learned user patterns.
        
        Returns: Dict of personality trait adjustments
        """
        if self.adaptation_level < 0.1:
            return {}  # Not enough data yet
        
        adjustments = {}
        
        # Adapt to user's preferred decision style
        dominant_style = self.get_dominant_style()
        adjustments[f"increase_{dominant_style}"] = self.adaptation_level * 0.5
        
        # If user shows positive sentiment, AI becomes warmer
        if self.sentiment_history:
            avg_sentiment = sum(self.sentiment_history) / len(self.sentiment_history)
            adjustments["warmth"] = avg_sentiment * 0.3
        
        # Topics user cares about should be addressed
        if "emotions" in self.topics_discussed:
            adjustments["empathy"] = 0.3
        if "family" in self.topics_discussed:
            adjustments["family_focus"] = 0.3
        
        return adjustments
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of what AI has learned about the user."""
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
        """Save learning data to file."""
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
        """Load learning data from file."""
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
