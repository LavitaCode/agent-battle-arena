"""ELO rating calculation (K=32, FIDE standard)."""
from __future__ import annotations


K = 32
DEFAULT_RATING = 1200.0


def expected(rating_a: float, rating_b: float) -> float:
    """Expected score for player A against player B."""
    return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))


def update(
    rating_a: float,
    rating_b: float,
    score_a: float,
) -> tuple[float, float]:
    """Return updated (rating_a, rating_b) after a match.

    score_a: 1.0 = A wins, 0.5 = draw, 0.0 = B wins.
    """
    ea = expected(rating_a, rating_b)
    new_a = rating_a + K * (score_a - ea)
    new_b = rating_b + K * ((1.0 - score_a) - (1.0 - ea))
    return new_a, new_b
