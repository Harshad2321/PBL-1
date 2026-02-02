"""
Emotion Module
===============

Complete emotion-guided dialogue system for realistic AI parent responses.

Components:
- EmotionState: Tracks emotional dimensions (anger, stress, fatigue, trust, etc.)
- Perception: Analyzes user input for sentiment, intent, triggers
- ReactionPolicy: Decides reaction mode based on emotion + perception
- PromptBuilder: Creates controlled LLM prompts
- ParentAgent: Main orchestrator integrating all components
"""

from nurture.emotion.emotion_state import EmotionState, EmotionPresets
from nurture.emotion.perception import (
    Perception, 
    PerceptionResult, 
    Sentiment, 
    Intent, 
    TriggerType
)
from nurture.emotion.reaction_policy import (
    ReactionPolicy, 
    ReactionDecision, 
    ReactionMode,
    EmotionGate
)
from nurture.emotion.prompt_builder import PromptBuilder, BuiltPrompt
from nurture.emotion.parent_agent import ParentAgent, Memory, create_parent_agent

__all__ = [
    # Emotion State
    'EmotionState',
    'EmotionPresets',
    
    # Perception
    'Perception',
    'PerceptionResult',
    'Sentiment',
    'Intent',
    'TriggerType',
    
    # Reaction Policy
    'ReactionPolicy',
    'ReactionDecision',
    'ReactionMode',
    'EmotionGate',
    
    # Prompt Builder
    'PromptBuilder',
    'BuiltPrompt',
    
    # Parent Agent
    'ParentAgent',
    'Memory',
    'create_parent_agent',
]
