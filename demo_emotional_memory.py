"""
Demo: Emotional Memory Integration
====================================

Shows how the Mother AI now remembers how interactions FELT,
not just what was said.
"""

from nurture.agents.ai_parent import AIParent
from nurture.core.data_structures import ParentState
from nurture.core.enums import ParentRole

def main():
    print("\n" + "="*70)
    print("  EMOTIONAL MEMORY DEMO")
    print("  The Mother AI now remembers how conversations make her feel")
    print("="*70 + "\n")
    
    # Create Mother AI
    state = ParentState.create_ai(ParentRole.MOTHER, "Sarah")
    mother = AIParent(state)
    
    print("Created Mother AI: Sarah")
    print(f"Initial emotional state: {mother.emotional_state.get_dominant_emotion()[0].value}\n")
    
    # Simulate a series of interactions
    interactions = [
        ("I really appreciate everything you do for our family", "positive support"),
        ("You're always so patient with the baby", "positive support"),
        ("Why didn't you do the dishes? You never help!", "negative conflict"),
        ("I'm sorry, I was stressed. Thank you for being there", "positive support"),
        ("You're overreacting again", "negative conflict"),
    ]
    
    print("Simulating 5 interactions...\n")
    
    for i, (message, description) in enumerate(interactions, 1):
        print(f"{i}. Player: \"{message}\"")
        print(f"   Context: {description}")
        
        # Process the message
        mother.process_input(message)
        
        # Show emotional response
        emotion, intensity = mother.emotional_state.get_dominant_emotion()
        print(f"   Mother feels: {emotion.value} (intensity: {intensity:.2f})")
        print()
    
    # Show emotional memory summary
    print("="*70)
    print("EMOTIONAL MEMORY SUMMARY")
    print("="*70 + "\n")
    
    stats = mother._emotional_memory.get_memory_stats()
    print(f"Total memories stored: {stats['total_memories']}")
    print(f"Average emotional valence: {stats['average_valence']:.2f}")
    print(f"  (1.0 = very positive, -1.0 = very negative)\n")
    
    # Show how different contexts feel
    from nurture.core.enums import ContextCategory
    
    print("How different types of interactions feel:")
    support_feeling = mother._emotional_memory.get_average_valence(ContextCategory.SUPPORT)
    conflict_feeling = mother._emotional_memory.get_average_valence(ContextCategory.CONFLICT)
    
    print(f"  Support moments: {support_feeling:+.2f} ({'warm' if support_feeling > 0 else 'cold'})")
    print(f"  Conflict moments: {conflict_feeling:+.2f} ({'resolved' if conflict_feeling > 0 else 'hurtful'})")
    print()
    
    # Show relationship summary
    print("="*70)
    print("RELATIONSHIP STATUS")
    print("="*70 + "\n")
    
    relationship = mother.get_relationship_summary()
    print(f"Trust in partner: {relationship['trust_in_partner']:.2f}")
    print(f"Agreement streak: {relationship['agreement_streak']}")
    print(f"Disagreement streak: {relationship['disagreement_streak']}")
    print(f"Support feeling: {relationship['support_feeling']:+.2f}")
    print(f"Conflict feeling: {relationship['conflict_feeling']:+.2f}")
    print()
    
    print("="*70)
    print("KEY INSIGHT:")
    print("="*70)
    print("The Mother AI doesn't store 'You never help!' verbatim.")
    print("Instead, she remembers: 'That conflict felt hurtful and draining.'")
    print("This shapes how she responds to future interactions!")
    print()

if __name__ == "__main__":
    main()
