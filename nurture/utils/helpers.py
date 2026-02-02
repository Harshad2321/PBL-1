"""
Helper Functions for Nurture Simulation
======================================

Utility functions used across the system.
"""

from typing import Dict, List, Any


def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """
    Clamp a value between min and max bounds.
    
    Args:
        value: Value to clamp
        min_val: Minimum bound
        max_val: Maximum bound
        
    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))


def normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize a dictionary of scores to sum to 1.0.
    
    Args:
        scores: Dictionary of scores
        
    Returns:
        Normalized scores dictionary
    """
    total = sum(scores.values())
    if total == 0:
        return {k: 1.0 / len(scores) for k in scores}
    return {k: v / total for k, v in scores.items()}


def weighted_random_choice(choices: Dict[str, float]) -> str:
    """
    Make a weighted random choice from a dictionary.
    
    Args:
        choices: Dictionary of choice -> weight
        
    Returns:
        Selected choice
    """
    import random
    
    items = list(choices.items())
    weights = [weight for _, weight in items]
    selected = random.choices(items, weights=weights, k=1)[0]
    return selected[0]


def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation between two values.
    
    Args:
        a: Start value
        b: End value
        t: Interpolation factor (0.0 to 1.0)
        
    Returns:
        Interpolated value
    """
    return a + t * (b - a)
