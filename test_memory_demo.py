"""
Demo script for EmotionalMemorySystem

Shows how the new emotional memory system stores and recalls memories.
"""
from datetime import datetime, timedelta
from nurture.personality.emotional_memory import EmotionalMemorySystem
from nurture.core.data_structures import EmotionalImpact
from nurture.core.enums import EmotionType, ContextType, ContextCategory

def main():
    print("\n" + "="*70)
    print("  EMOTIONAL MEMORY SYSTEM DEMO")
    print("  Testing the new Mother AI memory subsystem")
    print("="*70 + "\n")
    
    # Create memory system
    memory_system = EmotionalMemorySystem()
    
    # Simulate some interactions
    print("Simulating interactions...\n")
    
    # Positive support interaction
    impact1 = EmotionalImpact(
        primary_emotion=EmotionType.TRUST,
        intensity=0.8,
        valence=0.7,
        context_category=ContextCategory.SUPPORT
    )
    memory_system.store_memory(
        interaction_id="interaction_1",
        emotional_impact=impact1,
        context=ContextType.PRIVATE,
        timestamp=datetime.now() - timedelta(hours=2)
    )
    print("✓ Stored: Supportive conversation (2 hours ago)")
    print(f"  Emotion: {impact1.primary_emotion.value}, Valence: {impact1.valence}")
    
    # Conflict interaction
    impact2 = EmotionalImpact(
        primary_emotion=EmotionType.RESENTMENT,
        intensity=0.6,
        valence=-0.5,
        context_category=ContextCategory.CONFLICT
    )
    memory_system.store_memory(
        interaction_id="interaction_2",
        emotional_impact=impact2,
        context=ContextType.PRIVATE,
        timestamp=datetime.now() - timedelta(days=1)
    )
    print("✓ Stored: Conflict (1 day ago)")
    print(f"  Emotion: {impact2.primary_emotion.value}, Valence: {impact2.valence}")
    
    # Public parenting interaction
    impact3 = EmotionalImpact(
        primary_emotion=EmotionType.CONTENTMENT,
        intensity=0.9,
        valence=0.8,
        context_category=ContextCategory.PARENTING
    )
    memory_system.store_memory(
        interaction_id="interaction_3",
        emotional_impact=impact3,
        context=ContextType.PUBLIC,
        timestamp=datetime.now() - timedelta(hours=5)
    )
    print("✓ Stored: Parenting moment (5 hours ago)")
    print(f"  Emotion: {impact3.primary_emotion.value}, Valence: {impact3.valence}")
    
    # Old memory
    impact4 = EmotionalImpact(
        primary_emotion=EmotionType.STRESS,
        intensity=0.7,
        valence=-0.6,
        context_category=ContextCategory.CONFLICT
    )
    memory_system.store_memory(
        interaction_id="interaction_4",
        emotional_impact=impact4,
        context=ContextType.PRIVATE,
        timestamp=datetime.now() - timedelta(days=10)
    )
    print("✓ Stored: Stressful argument (10 days ago)")
    print(f"  Emotion: {impact4.primary_emotion.value}, Valence: {impact4.valence}")
    
    # Test memory recall
    print("\n" + "-"*70)
    print("MEMO