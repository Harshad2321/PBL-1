"""
Memory Module for Nurture Simulation
=====================================

Two memory implementations available:
- MemoryStore: Original full-featured implementation
- FastMemoryStore: Optimized O(1) lookups (recommended!)
"""

from nurture.memory.memory_store import MemoryStore, Memory
from nurture.memory.fast_memory import FastMemoryStore, FastMemory, LRUCache
from nurture.memory.state_manager import StateManager

__all__ = [
    # Original (compatible)
    "MemoryStore", 
    "Memory", 
    # Fast version (recommended)
    "FastMemoryStore",
    "FastMemory",
    "LRUCache",
    # State management
    "StateManager"
]
