"""Weighted highscore calculation.

The score starts at :data:`BASE_SCORE` and loses points for every minute spent, with exploration time penalised
three times as heavily as assembly time.

Attributes:
    BASE_SCORE: Perfect score.
    EXPLORATION_POINTS_PER_MINUTE: Penalty per minute of exploration.
    ASSEMBLY_POINTS_PER_MINUTE: Penalty per minute of assembly.
"""

from datetime import timedelta

BASE_SCORE = 1000
EXPLORATION_POINTS_PER_MINUTE = 12
ASSEMBLY_POINTS_PER_MINUTE = 4


def calculate_score(exploration: timedelta, assembly: timedelta) -> int:
    """Return a 0-1000 score; longer exploration and assembly times reduce it.

    Args:
        exploration: Time spent in the exploration phase.
        assembly: Time spent in the assembly phase.

    Returns:
        ``BASE_SCORE`` minus the weighted time penalty, rounded and never below 0.
    """
    penalty = (
        exploration.total_seconds() / 60 * EXPLORATION_POINTS_PER_MINUTE
        + assembly.total_seconds() / 60 * ASSEMBLY_POINTS_PER_MINUTE
    )
    # Clamp so very slow runs bottom out at 0 instead of going negative.
    return max(0, round(BASE_SCORE - penalty))
