from typing import Dict, List, Any

def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    return max(min_val, min(value, max_val))

def normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    total = sum(scores.values())
    if total == 0:
        return {k: 1.0 / len(scores) for k in scores}
    return {k: v / total for k, v in scores.items()}

def weighted_random_choice(choices: Dict[str, float]) -> str:
    import random

    items = list(choices.items())
    weights = [weight for _, weight in items]
    selected = random.choices(items, weights=weights, k=1)[0]
    return selected[0]

def lerp(a: float, b: float, t: float) -> float:
    return a + t * (b - a)
