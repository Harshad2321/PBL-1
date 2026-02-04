"""
Simple Chat with Mother AI
===========================

Direct chat interface to test emotional memory system with Ollama LLM.
"""

import sys
sys.path.insert(0, '.')

from nurture.agents.ai_parent import AIParent
from nurture.core.data_structures import ParentState
from nurture.core.enums import ParentRole
from nurture.utils.llm_interface import create_llm_generator

def main():
    print("\n" + "="*70)
    print("  CHAT WITH MOTHER AI")
    print("  Now with Emotional Memory + Ollama AI!")
    print("="*70)
    print("\nCommands:")
    print("  /status - See emotional memory and relationship stats")
    print("  /quit   - Exit chat")
    print("="*70 + "\n")
    
    # Create Mother AI
    state = ParentState.create_ai(ParentRole.MOTHER, "Sarah")
    mother = AIParent(state)
    
    # Set up Ollama LLM with longer timeout
    print("Connecting to Ollama...")
    try:
        llm_generator = create_llm_generator(
            provider="ollama",
            model_name="mistral:7b-instruct-v0.3-q4_K_M",
            timeout=60  # Increase timeout to 60 seconds
        )
        mother.set_llm_generator(llm_generator)
        print("✓ Ollama connected! (Note: First response may be slow)")
        print("  Responses will be natural and context-aware.\n")
    except Exception as e:
        print(f"⚠ Could not connect to Ollama: {e}")
        print("Using template responses instead.\n")
    
    print("Mother AI: Hi! I'm here. What's on your mind?\n")
    
    conversation_count = 0
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() == '/quit':
                print("\nMother AI: Take care.\n")
                break
            
            elif user_input.lower() == '/status':
                print("\n" + "="*70)
                print("EMOTIONAL MEMORY & RELATIONSHIP STATUS")
                print("="*70)
                
                stats = mother._emotional_memory.get_memory_stats()
                relationship = mother.get_relationship_summary()
                
                print(f"\nConversations: {conversation_count}")
                print(f"Emotional memories stored: {stats['total_memories']}")
                print(f"Average emotional valence: {stats['average_valence']:+.2f}")
                print(f"  (1.0 = very positive, -1.0 = very negative)")
                
                print(f"\nHow interactions feel:")
                print(f"  Support moments: {relationship['support_feeling']:+.2f}")
                print(f"  Conflict moments: {relationship['conflict_feeling']:+.2f}")
                
                print(f"\nRelationship metrics:")
                print(f"  Trust: {relationship['trust_in_partner']:.2f}")
                print(f"  Agreement streak: {relationship['agreement_streak']}")
                print(f"  Disagreement streak: {relationship['disagreement_streak']}")
                
                emotion, intensity = mother.emotional_state.get_dominant_emotion()
                print(f"\nCurrent emotional state:")
                print(f"  Feeling: {emotion.value} (intensity: {intensity:.2f})")
                print(f"  Stress level: {mother.emotional_state.stress_level:.2f}")
                
                print("="*70 + "\n")
                continue
            
            # Process message
            mother.process_input(user_input)
            conversation_count += 1
            
            # Process message
            mother.process_input(user_input)
            conversation_count += 1
            
            # Generate response
            response = mother.generate_response()
            
            print(f"\nMother AI: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nMother AI: Take care.\n")
            break
        except EOFError:
            print("\n\nMother AI: Take care.\n")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Continuing...\n")

if __name__ == "__main__":
    main()
