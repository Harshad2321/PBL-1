# Implementation Plan: Mother AI Personality System

## Overview

This implementation plan modifies the existing Nurture game's Mother AI to implement sophisticated pattern-based personality dynamics. The existing codebase has:
- `AIParent` class in `nurture/agents/ai_parent.py` with basic personality and emotional modeling
- `EmotionalState` and `PersonalityProfile` in `nurture/core/data_structures.py`
- `MemoryStore` in `nurture/memory/memory_store.py`
- Basic trust tracking and response strategies

The approach: extend existing classes with new subsystems for pattern tracking, emotional memory, trust dynamics, and state-dependent responses. Each task builds on previous work, with property-based tests placed close to implementation to catch errors early.

## Tasks

- [x] 1. Extend core data structures with new personality types
  - Add new enumerations to `nurture/core/enums.py` (ActionType, ContextType, PatternType, WithdrawalLevel)
  - Add dataclasses to `nurture/core/data_structures.py` for PlayerAction, BehaviorPattern, EmotionalImpact, EmotionalMemory
  - Add dataclasses for ResponseModifiers and RelationshipMetrics
  - Set up Hypothesis testing framework in requirements.txt and create test directory structure
  - _Requirements: 1.4, 2.1, 2.2, 8.1, 15.3_

- [x] 1.1 Write property test for data structure serialization
  - **Property 46: Complete state persistence**
  - **Validates: Requirements 15.1, 15.3**

- [x] 2. Create PatternTracker subsystem
  - [x] 2.1 Create `nurture/personality/pattern_tracker.py` with PatternTracker class
    - Implement `record_action()` to store actions with timestamps
    - Implement `detect_patterns()` with sliding time window analysis
    - Implement `get_pattern_frequency()` for pattern frequency calculation
    - Implement `break_pattern()` and `get_pattern_weight()` for pattern weight management
    - Use 7-day default time window, 3-occurrence minimum threshold
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [x] 2.2 Write property test for pattern tracking completeness
    - **Property 3: Pattern tracking completeness**
    - **Validates: Requirements 1.4**

  - [x] 2.3 Write property test for pattern-based trust impact
    - **Property 1: Pattern-based trust impact**
    - **Validates: Requirements 1.1, 1.2, 1.3**

  - [x] 2.4 Write property test for pattern weight decay
    - **Property 2: Pattern weight decay**
    - **Validates: Requirements 1.5**

  - [x] 2.5 Write unit tests for pattern detection edge cases
    - Test insufficient data (< 3 actions)
    - Test empty time windows
    - Test pattern weight decay over time
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 3. Create EmotionalMemorySystem subsystem
  - [x] 3.1 Create `nurture/personality/emotional_memory.py` with EmotionalMemorySystem class
    - Implement `store_memory()` to store emotional impact without verbatim text
    - Implement `recall_similar()` with recency weighting
    - Implement `get_emotional_association()` for context-based associations
    - Implement `apply_temporal_decay()` with time-based weight reduction
    - Implement memory pruning when capacity exceeds 1000 entries
    - Integrate with existing MemoryStore in `nurture/memory/memory_store.py`
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 3.2 Write property test for emotional memory storage format
    - **Property 4: Emotional memory storage format**
    - **Validates: Requirements 2.1, 2.3**

  - [x] 3.3 Write property test for memory context categorization
    - **Property 5: Memory context categorization**
    - **Validates: Requirements 2.2**

  - [x] 3.4 Write property test for temporal memory weighting
    - **Property 6: Temporal memory weighting**
    - **Validates: Requirements 2.4**

  - [x] 3.5 Write property test for response adaptation from emotional history
    - **Property 7: Response adaptation from emotional history**
    - **Validates: Requirements 2.5**

  - [x] 3.6 Write unit tests for memory system edge cases
    - Test memory capacity overflow and pruning
    - Test recall with no matching memories
    - Test temporal decay application
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4. Checkpoint - Ensure pattern and memory subsystems work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Create TrustDynamicsEngine subsystem
  - [x] 5.1 Create `nurture/personality/trust_dynamics.py` with TrustDynamicsEngine class
    - Implement `update_trust()` with context-based multipliers and asymmetric rates
    - Implement `update_resentment()` with pattern-based accumulation
    - Implement `get_trust_score()` and `get_resentment_score()` accessors
    - Implement `is_in_withdrawal()` based on trust thresholds
    - Implement apology tracking: `record_apology()`, `record_behavior_recurrence()`, `get_apology_effectiveness()`
    - Apply all trust dynamics rules (2x erosion, diminishing returns, resilience, etc.)
    - Replace simple `_trust_in_partner` float in AIParent with this engine
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.4, 4.5, 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 5.2 Write property test for asymmetric trust dynamics
    - **Property 8: Asymmetric trust dynamics**
    - **Validates: Requirements 3.1, 3.2**

  - [x] 5.3 Write property test for diminishing returns
    - **Property 9: Diminishing returns on rapid positive actions**
    - **Validates: Requirements 3.3**

  - [x] 5.4 Write property test for withdrawal state transition
    - **Property 10: Withdrawal state transition**
    - **Validates: Requirements 3.4**

  - [x] 5.5 Write property test for high trust resilience
    - **Property 11: High trust resilience**
    - **Validates: Requirements 3.5**

  - [x] 5.6 Write property test for pattern-based resentment accumulation
    - **Property 12: Pattern-based resentment accumulation**
    - **Validates: Requirements 4.1**

  - [x] 5.7 Write property test for slow resentment decay
    - **Property 14: Slow resentment decay**
    - **Validates: Requirements 4.4**

  - [x] 5.8 Write property test for resentment impact on trust recovery
    - **Property 15: Resentment impact on trust recovery**
    - **Validates: Requirements 4.5**

  - [x] 5.9 Write property test for apology tracking
    - **Property 18: Apology tracking**
    - **Validates: Requirements 6.1**

  - [x] 5.10 Write property test for apology effectiveness decay
    - **Property 19: Apology effectiveness decay**
    - **Validates: Requirements 6.2, 6.3**

  - [x] 5.11 Write property test for apology effectiveness recovery
    - **Property 20: Apology effectiveness recovery**
    - **Validates: Requirements 6.4**

  - [x] 5.12 Write property test for apology type differentiation
    - **Property 21: Apology type differentiation**
    - **Validates: Requirements 6.5**

  - [x] 5.13 Write unit tests for trust dynamics edge cases
    - Test trust/resentment clamping to valid ranges
    - Test withdrawal threshold boundary conditions
    - Test apology effectiveness minimum values
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.4, 4.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 6. Extend ResponseGenerator in AIParent
  - [ ] 6.1 Modify `nurture/agents/ai_parent.py` ResponseGenerator methods
    - Extend `generate_response()` to use state-dependent response selection
    - Add `calculate_response_length()` with withdrawal multipliers
    - Extend `should_initiate_interaction()` with trust-based probability (currently not implemented)
    - Modify `_select_strategy()` to incorporate interpretation bias
    - Apply interpretation bias (charitable at high trust, negative at high resentment)
    - Modify `_generate_template_response()` to respect withdrawal state
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 8.1, 8.2, 8.3, 8.4, 8.5, 13.1, 13.2, 13.3, 14.1, 14.2, 14.3, 14.4, 14.5_

  - [ ] 6.2 Write property test for comprehensive withdrawal behavior
    - **Property 16: Comprehensive withdrawal behavior**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**

  - [ ] 6.3 Write property test for civil withdrawal responses
    - **Property 13: Civil withdrawal responses**
    - **Validates: Requirements 4.2, 4.3**

  - [ ] 6.4 Write property test for state-dependent response variation
    - **Property 27: State-dependent response variation**
    - **Validates: Requirements 8.1, 8.5**

  - [ ] 6.5 Write property test for interpretation bias
    - **Property 28: Interpretation bias**
    - **Validates: Requirements 8.2, 8.3**

  - [ ] 6.6 Write property test for response consistency within state
    - **Property 29: Response consistency within state**
    - **Validates: Requirements 8.4**

  - [ ] 6.7 Write property test for trust-based initiation frequency
    - **Property 43: Trust-based initiation frequency**
    - **Validates: Requirements 13.1, 13.2, 13.3**

  - [ ] 6.8 Write property test for subtle emotional distance
    - **Property 45: Subtle emotional distance**
    - **Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5**

  - [ ] 6.9 Write unit tests for response generation edge cases
    - Test invalid state modifiers (clamping)
    - Test missing response templates (fallback)
    - Test response length boundaries
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 7. Checkpoint - Ensure trust dynamics and response generation work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Create PersonalityStateManager coordinator
  - [ ] 8.1 Create `nurture/personality/personality_state_manager.py` with PersonalityStateManager class
    - Initialize with PatternTracker, EmotionalMemorySystem, TrustDynamicsEngine dependencies
    - Implement `update_state()` to process actions through all subsystems
    - Implement `get_current_state()` to return comprehensive PersonalityState
    - Implement `get_response_modifiers()` to calculate modifiers from current state
    - Calculate emotional safety from trust and stress acknowledgment
    - Calculate parenting unity from public context interactions
    - Determine withdrawal severity from trust/resentment thresholds
    - Calculate interpretation bias from trust/resentment levels
    - _Requirements: 7.5, 12.2, 12.4, 5.1, 5.2, 5.3, 8.1, 8.2, 8.3_

  - [ ] 8.2 Write property test for public context multiplier
    - **Property 22: Public context multiplier**
    - **Validates: Requirements 7.1**

  - [ ] 8.3 Write property test for public contradiction penalty
    - **Property 23: Public contradiction penalty**
    - **Validates: Requirements 7.2**

  - [ ] 8.4 Write property test for public support bonus
    - **Property 24: Public support bonus**
    - **Validates: Requirements 7.3**

  - [ ] 8.5 Write property test for private correction standard handling
    - **Property 25: Private correction standard handling**
    - **Validates: Requirements 7.4**

  - [ ] 8.6 Write property test for parenting unity tracking
    - **Property 26: Parenting unity tracking**
    - **Validates: Requirements 7.5**

  - [ ] 8.7 Write property test for gradual recovery from withdrawal
    - **Property 17: Gradual recovery from withdrawal**
    - **Validates: Requirements 5.5**

  - [ ] 8.8 Write unit tests for state manager coordination
    - Test state calculation with various subsystem states
    - Test response modifier calculation
    - Test emotional safety and parenting unity calculations
    - _Requirements: 7.5, 12.2, 12.4, 5.5_

- [ ] 9. Implement conflict and parenting behavior tracking
  - [ ] 9.1 Extend PersonalityStateManager with conflict tracking
    - Track conflict engagement vs avoidance patterns
    - Differentiate productive conflict from destructive arguing
    - Track empathy presence in solutions
    - Apply resentment changes based on conflict behavior
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [ ] 9.2 Extend PersonalityStateManager with parenting tracking
    - Track parenting involvement frequency and consistency
    - Differentiate consistent presence from sporadic involvement
    - Track control-taking vs supportive behavior
    - Apply trust changes based on parenting patterns
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 11.1, 11.2, 11.3, 11.4, 11.5_

  - [ ] 9.3 Extend PersonalityStateManager with stress acknowledgment tracking
    - Track shared stress scenarios
    - Track player acknowledgment vs dismissal
    - Update emotional safety based on stress handling
    - Apply resilience modifiers when emotional safety is high
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

  - [ ] 9.4 Extend PersonalityStateManager with initiation tracking
    - Track player responsiveness to Mother AI initiations
    - Adjust initiation frequency based on responsiveness patterns
    - _Requirements: 13.4, 13.5_

  - [ ] 9.5 Write property test for conflict engagement benefit
    - **Property 30: Conflict engagement benefit**
    - **Validates: Requirements 9.1**

  - [ ] 9.6 Write property test for avoidance penalty
    - **Property 31: Avoidance penalty**
    - **Validates: Requirements 9.2, 9.3**

  - [ ] 9.7 Write property test for empathy requirement
    - **Property 32: Empathy requirement**
    - **Validates: Requirements 9.4**

  - [ ] 9.8 Write property test for conflict type differentiation
    - **Property 33: Conflict type differentiation**
    - **Validates: Requirements 9.5**

  - [ ] 9.9 Write property test for parenting tracking
    - **Property 34: Parenting tracking**
    - **Validates: Requirements 10.1**

  - [ ] 9.10 Write property test for consistency over intensity
    - **Property 35: Consistency over intensity**
    - **Validates: Requirements 10.2, 10.3, 10.5**

  - [ ] 9.11 Write property test for absence penalty
    - **Property 36: Absence penalty**
    - **Validates: Requirements 10.4**

  - [ ] 9.12 Write property test for control-taking penalty
    - **Property 37: Control-taking penalty**
    - **Validates: Requirements 11.1, 11.3**

  - [ ] 9.13 Write property test for supportive autonomy reward
    - **Property 38: Supportive autonomy reward**
    - **Validates: Requirements 11.2, 11.5**

  - [ ] 9.14 Write property test for control pattern consequences
    - **Property 39: Control pattern consequences**
    - **Validates: Requirements 11.4**

  - [ ] 9.15 Write property test for stress acknowledgment tracking
    - **Property 40: Stress acknowledgment tracking**
    - **Validates: Requirements 12.1**

  - [ ] 9.16 Write property test for acknowledgment vs dismissal impact
    - **Property 41: Acknowledgment vs dismissal impact**
    - **Validates: Requirements 12.2, 12.3, 12.5**

  - [ ] 9.17 Write property test for emotional safety resilience
    - **Property 42: Emotional safety resilience**
    - **Validates: Requirements 12.4**

  - [ ] 9.18 Write property test for responsiveness-based initiation adjustment
    - **Property 44: Responsiveness-based initiation adjustment**
    - **Validates: Requirements 13.4, 13.5**

- [ ] 10. Checkpoint - Ensure all behavioral tracking works correctly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Implement state persistence
  - [ ] 11.1 Create `nurture/personality/persistence_layer.py` with PersistenceLayer class
    - Implement `save_state()` to serialize PersonalityStateManager to JSON
    - Implement `load_state()` to deserialize JSON to state dictionary
    - Implement `get_default_state()` to return safe default values
    - Add validation for all numeric ranges on load
    - Add error handling for I/O failures
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

  - [ ] 11.2 Implement state serialization in PersonalityStateManager
    - Implement `serialize()` method to convert all subsystem state to dictionary
    - Implement `deserialize()` method to restore all subsystem state from dictionary
    - Ensure all required fields are included (trust, resentment, patterns, memories, etc.)
    - _Requirements: 15.1, 15.2, 15.3, 15.5_

  - [ ] 11.3 Write property test for state persistence round-trip
    - **Property 47: State persistence round-trip**
    - **Validates: Requirements 15.2, 15.5**

  - [ ] 11.4 Write unit tests for persistence error handling
    - Test corrupted state recovery (edge case from 15.4)
    - Test I/O failure handling
    - Test validation of numeric ranges
    - Test default state initialization
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

- [ ] 12. Integrate with existing AIParent system
  - [ ] 12.1 Extend AIParent class in `nurture/agents/ai_parent.py` with PersonalityStateManager
    - Add PersonalityStateManager as a member of AIParent
    - Initialize all subsystems in AIParent `__init__`
    - Load personality state on AIParent initialization
    - Save personality state in `to_dict()` method
    - Extend `from_dict()` to restore personality state
    - _Requirements: 15.1, 15.2_

  - [ ] 12.2 Modify AIParent.process_input() to route through personality system
    - Convert player interactions to PlayerAction objects
    - Call PersonalityStateManager.update_state() for each action
    - Get response modifiers from PersonalityStateManager
    - Pass modifiers to response generation methods
    - Update existing `_analyze_incoming_message()` to create PlayerAction
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 3.1, 3.2, 8.1_

  - [ ] 12.3 Update AIParent emotional state integration
    - Keep existing EmotionalState in `nurture/core/data_structures.py`
    - Add withdrawal state tracking to EmotionalState
    - Add emotional safety metric to EmotionalState
    - Integrate PersonalityStateManager state updates with EmotionalState
    - Maintain backward compatibility with existing emotional state interface
    - _Requirements: 3.4, 5.1, 5.2, 5.3, 12.2_

  - [ ] 12.4 Update AIParent relationship tracking
    - Replace simple `_trust_in_partner` with TrustDynamicsEngine.get_trust_score()
    - Add resentment tracking alongside trust
    - Add parenting unity metric
    - Update `get_relationship_summary()` to include new metrics
    - _Requirements: 3.1, 3.2, 4.1, 7.5, 12.2_

  - [ ] 12.5 Write integration tests for full interaction flows
    - Test new relationship → trust building → erosion → recovery
    - Test pattern formation → breaking → new pattern formation
    - Test apology → behavior change → effectiveness recovery
    - Test public contradiction → resentment → withdrawal → recovery
    - Test consistent parenting → trust building → sporadic involvement
    - _Requirements: All requirements_

- [ ] 13. Final checkpoint and validation
  - [ ] 13.1 Run all unit tests and property tests
    - Verify all tests pass
    - Check test coverage meets goals (>90% unit, 100% properties)
    - _Requirements: All requirements_

  - [ ] 13.2 Run integration tests with existing game systems
    - Test full game session with personality system active
    - Verify save/load cycles work correctly
    - Test interaction with existing LearningSystem and MemoryStore
    - _Requirements: 15.1, 15.2, 15.5_

  - [ ] 13.3 Performance validation
    - Benchmark pattern detection, memory recall, state updates
    - Verify all operations meet performance targets
    - Optimize if any operations exceed targets
    - _Requirements: All requirements_

  - [ ] 13.4 Final checkpoint - Ensure all tests pass
    - Ensure all tests pass, ask the user if questions arise.

## Notes

- All tasks are required for comprehensive implementation with full test coverage
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at major milestones
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end flows
- The implementation extends existing AIParent class rather than building from scratch
- New subsystems are created in `nurture/personality/` directory
- All subsystems are tested independently before integration
- Persistence is implemented after all subsystems are complete
- Integration with existing AIParent system is the final step
- Backward compatibility with existing game code is maintained throughout
