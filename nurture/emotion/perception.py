"""
Perception Module
==================

Classifies user input into sentiment, intent, and severity.
Detects emotional triggers like insults, neglect, avoidance, or empathy.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Set
import re


class Sentiment(Enum):
    """Overall sentiment of the message."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    HOSTILE = "hostile"


class Intent(Enum):
    """What the speaker is trying to do."""
    APOLOGIZE = "apologize"
    ATTACK = "attack"
    DISMISS = "dismiss"
    DEFLECT = "deflect"
    CONNECT = "connect"
    EXPLAIN = "explain"
    QUESTION = "question"
    JOKE = "joke"
    WITHDRAW = "withdraw"
    BLAME = "blame"
    SUPPORT = "support"
    NEUTRAL = "neutral"


class TriggerType(Enum):
    """Emotional triggers detected in input."""
    INSULT = "insult"
    NEGLECT = "neglect"
    AVOIDANCE = "avoidance"
    EMPATHY = "empathy"
    AFFECTION = "affection"
    BLAME = "blame"
    DISMISSAL = "dismissal"
    SARCASM = "sarcasm"
    THREAT = "threat"
    APPRECIATION = "appreciation"
    NONE = "none"


@dataclass
class PerceptionResult:
    """Result of analyzing user input."""
    raw_input: str
    sentiment: Sentiment
    intent: Intent
    severity: float  # 0-1, how intense the message is
    triggers: List[TriggerType]
    keywords_found: List[str]
    
    def has_trigger(self, trigger: TriggerType) -> bool:
        return trigger in self.triggers
    
    def is_hostile(self) -> bool:
        return self.sentiment == Sentiment.HOSTILE or TriggerType.INSULT in self.triggers
    
    def is_affectionate(self) -> bool:
        return TriggerType.AFFECTION in self.triggers or TriggerType.APPRECIATION in self.triggers


class Perception:
    """
    Analyzes user input to extract emotional meaning.
    
    Uses keyword matching and pattern detection for fast,
    consistent classification without requiring ML models.
    """
    
    # Keyword dictionaries
    INSULT_PATTERNS = [
        r'\bhate\s+(you|u)\b', r'\bdon\'?t\s+like\s+(you|u)\b',
        r'\bidiot\b', r'\bstupid\b', r'\bdumb\b', r'\buseless\b',
        r'\bshut\s+up\b', r'\bleave\s+me\s+alone\b',
        r'\bworst\b', r'\bterrible\b', r'\bpathetic\b',
        r'\bselfish\b', r'\blazy\b', r'\bnagging\b',
    ]
    
    AFFECTION_KEYWORDS = [
        'love you', 'love u', 'i love', 'miss you', 'miss u',
        'care about', 'need you', 'need u', 'appreciate',
        'thank you', 'thanks', 'grateful', 'lucky to have',
        'beautiful', 'amazing', 'wonderful', 'best',
    ]
    
    APOLOGY_KEYWORDS = [
        'sorry', 'apologize', 'my fault', 'my bad',
        'forgive me', 'i was wrong', 'shouldn\'t have',
        'regret', 'feel bad', 'messed up',
    ]
    
    DISMISSAL_KEYWORDS = [
        'whatever', 'don\'t care', 'doesn\'t matter',
        'not my problem', 'deal with it', 'get over it',
        'calm down', 'overreacting', 'dramatic',
        'fine', 'ok fine', 'okay fine',
    ]
    
    BLAME_KEYWORDS = [
        'your fault', 'you always', 'you never',
        'because of you', 'you made me', 'you did this',
        'if you had', 'you should have', 'why didn\'t you',
    ]
    
    AVOIDANCE_KEYWORDS = [
        'not now', 'later', 'busy', 'tired',
        'don\'t want to talk', 'leave me alone',
        'can\'t deal', 'whatever', 'i don\'t know',
        'maybe', 'we\'ll see', 'i guess',
    ]
    
    EMPATHY_KEYWORDS = [
        'understand', 'i get it', 'i know how',
        'must be hard', 'i hear you', 'that\'s tough',
        'how are you', 'are you okay', 'what do you need',
        'here for you', 'we\'re in this together',
    ]
    
    SARCASM_PATTERNS = [
        r'\boh\s+great\b', r'\bwow\s+thanks\b', r'\byeah\s+right\b',
        r'\bsure\s+you\s+are\b', r'\bof\s+course\b.*not',
        r'\bhow\s+nice\b', r'\bperfect\b.*sarcasm',
    ]
    
    QUESTION_PATTERNS = [
        r'\?$', r'^(what|why|how|when|where|who|can|will|do|does|is|are)\b',
    ]
    
    def __init__(self):
        """Initialize the perception module."""
        # Compile regex patterns for efficiency
        self._insult_patterns = [re.compile(p, re.IGNORECASE) for p in self.INSULT_PATTERNS]
        self._sarcasm_patterns = [re.compile(p, re.IGNORECASE) for p in self.SARCASM_PATTERNS]
        self._question_patterns = [re.compile(p, re.IGNORECASE) for p in self.QUESTION_PATTERNS]
    
    def analyze(self, message: str) -> PerceptionResult:
        """
        Analyze a message and return perception result.
        
        Args:
            message: User input text
            
        Returns:
            PerceptionResult with sentiment, intent, triggers, etc.
        """
        if not message or not message.strip():
            return PerceptionResult(
                raw_input=message,
                sentiment=Sentiment.NEUTRAL,
                intent=Intent.NEUTRAL,
                severity=0.0,
                triggers=[TriggerType.NONE],
                keywords_found=[],
            )
        
        msg_lower = message.lower().strip()
        
        # Detect triggers
        triggers = self._detect_triggers(msg_lower)
        keywords = self._find_keywords(msg_lower)
        
        # Determine sentiment
        sentiment = self._classify_sentiment(msg_lower, triggers)
        
        # Determine intent
        intent = self._classify_intent(msg_lower, triggers, keywords)
        
        # Calculate severity
        severity = self._calculate_severity(msg_lower, triggers, sentiment)
        
        return PerceptionResult(
            raw_input=message,
            sentiment=sentiment,
            intent=intent,
            severity=severity,
            triggers=triggers if triggers else [TriggerType.NONE],
            keywords_found=keywords,
        )
    
    def _detect_triggers(self, msg: str) -> List[TriggerType]:
        """Detect emotional triggers in the message."""
        triggers = []
        
        # Check for insults
        for pattern in self._insult_patterns:
            if pattern.search(msg):
                triggers.append(TriggerType.INSULT)
                break
        
        # Check for affection
        if any(kw in msg for kw in self.AFFECTION_KEYWORDS):
            triggers.append(TriggerType.AFFECTION)
        
        # Check for dismissal
        if any(kw in msg for kw in self.DISMISSAL_KEYWORDS):
            triggers.append(TriggerType.DISMISSAL)
        
        # Check for blame
        if any(kw in msg for kw in self.BLAME_KEYWORDS):
            triggers.append(TriggerType.BLAME)
        
        # Check for avoidance
        if any(kw in msg for kw in self.AVOIDANCE_KEYWORDS):
            triggers.append(TriggerType.AVOIDANCE)
        
        # Check for empathy
        if any(kw in msg for kw in self.EMPATHY_KEYWORDS):
            triggers.append(TriggerType.EMPATHY)
        
        # Check for appreciation
        if any(kw in msg for kw in ['thank', 'appreciate', 'grateful']):
            triggers.append(TriggerType.APPRECIATION)
        
        # Check for sarcasm
        for pattern in self._sarcasm_patterns:
            if pattern.search(msg):
                triggers.append(TriggerType.SARCASM)
                break
        
        return triggers
    
    def _find_keywords(self, msg: str) -> List[str]:
        """Find matching keywords in message."""
        found = []
        all_keywords = (
            self.AFFECTION_KEYWORDS + self.APOLOGY_KEYWORDS +
            self.DISMISSAL_KEYWORDS + self.BLAME_KEYWORDS +
            self.AVOIDANCE_KEYWORDS + self.EMPATHY_KEYWORDS
        )
        for kw in all_keywords:
            if kw in msg:
                found.append(kw)
        return found
    
    def _classify_sentiment(self, msg: str, triggers: List[TriggerType]) -> Sentiment:
        """Classify overall sentiment."""
        # Hostile if insults present
        if TriggerType.INSULT in triggers:
            return Sentiment.HOSTILE
        
        # Negative if blame, dismissal, or avoidance
        if any(t in triggers for t in [TriggerType.BLAME, TriggerType.DISMISSAL]):
            return Sentiment.NEGATIVE
        
        # Positive if affection or empathy
        if any(t in triggers for t in [TriggerType.AFFECTION, TriggerType.EMPATHY, TriggerType.APPRECIATION]):
            return Sentiment.POSITIVE
        
        # Check for apology (mixed - acknowledging wrong)
        if any(kw in msg for kw in self.APOLOGY_KEYWORDS):
            return Sentiment.POSITIVE  # Apologies are positive gestures
        
        return Sentiment.NEUTRAL
    
    def _classify_intent(self, msg: str, triggers: List[TriggerType], keywords: List[str]) -> Intent:
        """Classify speaker's intent."""
        # Check for apology
        if any(kw in msg for kw in self.APOLOGY_KEYWORDS):
            return Intent.APOLOGIZE
        
        # Check for attack
        if TriggerType.INSULT in triggers:
            return Intent.ATTACK
        
        # Check for blame
        if TriggerType.BLAME in triggers:
            return Intent.BLAME
        
        # Check for dismissal
        if TriggerType.DISMISSAL in triggers:
            return Intent.DISMISS
        
        # Check for avoidance
        if TriggerType.AVOIDANCE in triggers:
            return Intent.WITHDRAW
        
        # Check for connection/support
        if TriggerType.AFFECTION in triggers or TriggerType.EMPATHY in triggers:
            return Intent.CONNECT
        
        # Check for question
        for pattern in self._question_patterns:
            if pattern.search(msg):
                return Intent.QUESTION
        
        # Check for explanation (long messages with reasoning)
        if len(msg.split()) > 15 and any(w in msg for w in ['because', 'since', 'reason', 'why']):
            return Intent.EXPLAIN
        
        return Intent.NEUTRAL
    
    def _calculate_severity(self, msg: str, triggers: List[TriggerType], sentiment: Sentiment) -> float:
        """Calculate how severe/intense the message is (0-1)."""
        severity = 0.3  # Base severity
        
        # Hostile messages are severe
        if sentiment == Sentiment.HOSTILE:
            severity += 0.4
        elif sentiment == Sentiment.NEGATIVE:
            severity += 0.2
        
        # Insults add severity
        if TriggerType.INSULT in triggers:
            severity += 0.3
        
        # Blame adds severity
        if TriggerType.BLAME in triggers:
            severity += 0.2
        
        # Caps lock indicates intensity
        caps_ratio = sum(1 for c in msg if c.isupper()) / max(len(msg), 1)
        if caps_ratio > 0.5:
            severity += 0.2
        
        # Exclamation marks indicate intensity
        exclaim_count = msg.count('!')
        severity += min(exclaim_count * 0.1, 0.3)
        
        # Short, blunt messages can be severe
        word_count = len(msg.split())
        if word_count <= 3 and sentiment != Sentiment.POSITIVE:
            severity += 0.1
        
        return min(1.0, severity)


# Convenience function
def perceive(message: str) -> PerceptionResult:
    """Quick perception of a message."""
    return Perception().analyze(message)
