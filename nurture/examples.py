"""
Nurture - Usage Examples
========================

Example scripts demonstrating how to use the Nurture parent agent system.
"""

from nurture.core.enums import ParentRole, EmotionType, PersonalityTrait
from nurture.core.data_structures import PersonalityProfile, EmotionalState
from nurture.core.events import get_event_bus, EventType
from nurture.core.interaction_manager import InteractionManager, ScenarioContext

from nurture.agents.player_parent import PlayerParent
from nurture.agents.ai_parent import AIParent

from nurture.memory.memory_store import MemoryStore, Memory
from nurture.memory.state_manager import StateManager

from nurture.rules.rule_engine import RuleEngine, create_default_rules
from nurture.rules.emotional_rules import EmotionalRules
from nurture.rules.behavioral_constraints import BehavioralConstraints

from nurture.utils.llm_interface import create_llm_generator


def example_basic_conversation():
    """
    Basic example: Simple conversation between player and AI parent.
    """
    print("\n" + "="*60)
    print("Example 1: Basic Conversation")
    print("="*60)
    
    # 1. Create player parent (Father)
    player = PlayerParent(
        agent_id="player",
        role=ParentRole.FATHER
    )
    
    # 2. Create AI parent (Mother) with balanced personality
    ai = AIParent(
        agent_id="ai_partner",
        role=ParentRole.MOTHER,
        personality=PersonalityProfile.create_balanced()
    )
    
    # 3. Set up mock LLM for testing
    llm = create_llm_generator(provider="mock")
    ai.set_llm_generator(llm)
    
    # 4. Create rule engine
    rule_engine = RuleEngine()
    for rule in create_default_rules():
        rule_engine.add_rule(rule)
    
    # 5. Create constraints
    constraints = BehavioralConstraints()
    constraints.add_default_constraints()
    
    # 6. Create interaction manager
    manager = InteractionManager(
        player_parent=player,
        ai_parent=ai,
        rule_engine=rule_engine,
        constraints=constraints
    )
    
    # 7. Set up a scenario
    manager.set_scenario(ScenarioContext(
        scenario_id="homework_001",
        title="Homework Habits",
        description="Discussing child's homework routine",
        topic="education"
    ))
    
    # 8. Simulate conversation
    messages = [
        "I think we should set a fixed homework time for our child.",
        "Maybe right after school, before any screen time?",
        "What do you think about helping with difficult subjects?"
    ]
    
    for msg in messages:
        print(f"\nFather: {msg}")
        result = manager.process_player_message(msg)
        print(f"Mother: {result.response_text}")
    
    # Show relationship status
    print("\n--- Relationship Status ---")
    status = manager.get_relationship_status()
    for key, value in status.items():
        print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")


def example_personality_differences():
    """
    Example: How different personalities affect AI responses.
    """
    print("\n" + "="*60)
    print("Example 2: Personality Differences")
    print("="*60)
    
    # Create different personality types
    personalities = {
        "Warm": PersonalityProfile.create_warm(),
        "Strict": PersonalityProfile.create_strict(),
        "Balanced": PersonalityProfile.create_balanced()
    }
    
    player = PlayerParent("player", ParentRole.FATHER)
    
    test_message = "I think we're being too lenient with our child's bedtime."
    
    for name, personality in personalities.items():
        print(f"\n--- {name} Personality ---")
        print(f"Traits: {personality.get_dominant_traits()}")
        
        ai = AIParent("ai", ParentRole.MOTHER, personality=personality)
        ai.set_llm_generator(create_llm_generator(provider="mock"))
        
        rule_engine = RuleEngine()
        constraints = BehavioralConstraints()
        constraints.add_default_constraints()
        
        manager = InteractionManager(
            player_parent=player,
            ai_parent=ai,
            rule_engine=rule_engine,
            constraints=constraints
        )
        
        print(f"\nFather: {test_message}")
        result = manager.process_player_message(test_message)
        print(f"Mother ({name}): {result.response_text}")


def example_memory_system():
    """
    Example: Using the memory system to track interactions.
    """
    print("\n" + "="*60)
    print("Example 3: Memory System")
    print("="*60)
    
    # Create memory store
    memory_store = MemoryStore(agent_id="example_agent")
    
    # Add some memories
    memories = [
        Memory(
            content="Agreed on 8pm bedtime rule",
            tags=["parenting", "bedtime", "agreement"],
            emotional_valence=0.7,
            importance=0.8
        ),
        Memory(
            content="Disagreed about screen time limits",
            tags=["parenting", "screen_time", "conflict"],
            emotional_valence=-0.3,
            importance=0.6
        ),
        Memory(
            content="Celebrated child's good grades together",
            tags=["parenting", "education", "celebration"],
            emotional_valence=0.9,
            importance=0.9
        )
    ]
    
    for memory in memories:
        memory_store.add(memory)
    
    print(f"Total memories stored: {len(memory_store)}")
    
    # Retrieve memories by tag
    print("\n--- Memories tagged 'parenting' ---")
    parenting_memories = memory_store.get_by_tag("parenting")
    for m in parenting_memories:
        print(f"  • {m.content} (importance: {m.importance})")
    
    # Retrieve positive memories
    print("\n--- Positive memories (valence > 0.5) ---")
    positive = memory_store.get_by_emotion(min_valence=0.5)
    for m in positive:
        print(f"  • {m.content} (valence: {m.emotional_valence})")
    
    # Get most relevant memories
    print("\n--- Most relevant memories ---")
    relevant = memory_store.get_most_relevant(n=2)
    for m in relevant:
        strength = memory_store._calculate_strength(m)
        print(f"  • {m.content} (relevance: {strength:.2f})")


def example_emotional_states():
    """
    Example: Working with emotional states.
    """
    print("\n" + "="*60)
    print("Example 4: Emotional States")
    print("="*60)
    
    # Create initial emotional state
    state = EmotionalState()
    print(f"Initial state - Valence: {state.valence:.2f}")
    print(f"Dominant emotions: {state.get_dominant_emotions(n=3)}")
    
    # Simulate emotional changes during conversation
    changes = [
        (EmotionType.HAPPINESS, 0.3, "Partner agrees with suggestion"),
        (EmotionType.FRUSTRATION, 0.2, "Minor disagreement"),
        (EmotionType.HOPE, 0.4, "Finding common ground"),
    ]
    
    for emotion, intensity, reason in changes:
        state.update(emotion, intensity)
        print(f"\nAfter '{reason}':")
        print(f"  Updated {emotion.value} by {intensity}")
        print(f"  New valence: {state.valence:.2f}")
        print(f"  Dominant: {state.get_dominant_emotions(n=2)}")
    
    # Apply decay (simulates time passing)
    print("\n--- After time passes (decay applied) ---")
    state.apply_decay(steps=3)
    print(f"Valence after decay: {state.valence:.2f}")
    print(f"Dominant emotions: {state.get_dominant_emotions(n=3)}")


def example_rule_engine():
    """
    Example: Rule-based decision making.
    """
    print("\n" + "="*60)
    print("Example 5: Rule Engine")
    print("="*60)
    
    from nurture.rules.rule_engine import Rule
    
    # Create rule engine
    rule_engine = RuleEngine()
    
    # Add custom rules
    custom_rules = [
        Rule(
            rule_id="support_partner",
            name="Support During Stress",
            condition=lambda ctx: ctx.get("partner_stress", 0) > 0.7,
            action=lambda ctx: {"response_modifier": "supportive", "priority_boost": 0.2},
            priority=90
        ),
        Rule(
            rule_id="calm_discussion",
            name="Stay Calm in Conflict",
            condition=lambda ctx: ctx.get("conflict_level", 0) > 0.5,
            action=lambda ctx: {"tone": "calm", "suggest_break": ctx.get("conflict_level", 0) > 0.8},
            priority=85
        )
    ]
    
    for rule in custom_rules:
        rule_engine.add_rule(rule)
    
    print(f"Total rules: {len(rule_engine.rules)}")
    
    # Test rule evaluation
    test_contexts = [
        {"partner_stress": 0.8, "conflict_level": 0.3},
        {"partner_stress": 0.4, "conflict_level": 0.9},
        {"partner_stress": 0.2, "conflict_level": 0.2},
    ]
    
    for i, context in enumerate(test_contexts, 1):
        print(f"\n--- Scenario {i} ---")
        print(f"Context: {context}")
        actions = rule_engine.evaluate(context)
        if actions:
            print("Triggered rules:")
            for rule_id, action_result in actions.items():
                print(f"  • {rule_id}: {action_result}")
        else:
            print("No rules triggered")


def example_event_system():
    """
    Example: Using the event system.
    """
    print("\n" + "="*60)
    print("Example 6: Event System")
    print("="*60)
    
    # Get event bus
    event_bus = get_event_bus()
    
    # Clear any existing subscriptions for clean demo
    event_bus.clear()
    
    # Subscribe to events
    def on_dialogue(event):
        print(f"  [Dialogue Event] {event.data}")
    
    def on_emotion(event):
        print(f"  [Emotion Event] {event.data}")
    
    event_bus.subscribe(EventType.DIALOGUE, on_dialogue)
    event_bus.subscribe(EventType.EMOTION_CHANGE, on_emotion)
    
    # Publish some events
    print("\nPublishing events...")
    
    from nurture.core.events import Event
    
    event_bus.publish(Event(
        event_type=EventType.DIALOGUE,
        data={"speaker": "player", "message": "Hello!"}
    ))
    
    event_bus.publish(Event(
        event_type=EventType.EMOTION_CHANGE,
        data={"agent": "ai", "emotion": "happiness", "delta": 0.2}
    ))
    
    # Show event history
    print(f"\nEvent history count: {len(event_bus.history)}")


def example_state_management():
    """
    Example: Saving and loading game state.
    """
    print("\n" + "="*60)
    print("Example 7: State Management")
    print("="*60)
    
    import tempfile
    import os
    
    # Use temp directory for demo
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create state manager
        state_manager = StateManager(save_directory=tmpdir)
        
        # Start new session
        state_manager.start_new_session()
        print(f"Session started: {state_manager._current_session.session_id}")
        
        # Record some interactions
        interactions = [
            ("dialogue", {"speaker": "player", "message": "Let's discuss bedtime"}),
            ("choice", {"choice": "agree", "context": "bedtime_rule"}),
            ("dialogue", {"speaker": "ai", "message": "I think 8pm is good"}),
        ]
        
        for int_type, data in interactions:
            state_manager.record_interaction(int_type, data)
        
        print(f"Recorded {len(interactions)} interactions")
        
        # Save session
        save_path = state_manager.save_session()
        print(f"Saved to: {os.path.basename(save_path)}")
        
        # Create new state manager and load
        new_manager = StateManager(save_directory=tmpdir)
        if new_manager.load_session(save_path):
            session = new_manager.get_current_session()
            print(f"Loaded session: {session.session_id}")
            print(f"Interactions loaded: {len(session.interactions)}")


def run_all_examples():
    """Run all examples."""
    example_basic_conversation()
    example_personality_differences()
    example_memory_system()
    example_emotional_states()
    example_rule_engine()
    example_event_system()
    example_state_management()
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == "__main__":
    run_all_examples()
