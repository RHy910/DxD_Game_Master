import random
from typing import Tuple


def roll_d20() -> int:
    """Return a d20 roll (1-20)."""
    return random.randint(1, 20)


def ability_modifier(score: int) -> int:
    """Simple D&D 5e ability modifier calculation.

    Modifier = floor((score - 10) / 2)
    """
    return (score - 10) // 2


def resolve_check(ability_score: int, dc: int, roll_override: int = None) -> Tuple[int, int, bool, bool]:
    """Resolve a d20 check using an ability score and target DC.

    Returns: (roll, modifier, success, critical)
    - roll: d20 roll value
    - modifier: ability modifier
    - success: whether (roll + modifier) >= dc
    - critical: True for nat20, False for nat1 or normal
    """
    roll = roll_override if roll_override is not None else roll_d20()
    mod = ability_modifier(ability_score)
    total = roll + mod
    critical = False
    success = total >= dc

    # Natural 20 always succeeds and is a critical success
    if roll == 20:
        critical = True
        success = True

    # Natural 1 always fails (fumble)
    if roll == 1:
        success = False

    return roll, mod, success, critical
