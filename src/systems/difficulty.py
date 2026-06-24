"""Difficulty presets — GeoGuessr-style game modes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Difficulty:
    id: str
    timer_ranked: int | None
    timer_casual: int | None
    start_zoom: int
    max_zoom: int
    score_multiplier: float
    show_region: bool
    show_country_after: bool
    rounds: int
    moving_penalty: bool


DIFFICULTIES: dict[str, Difficulty] = {
    "easy": Difficulty(
        id="easy",
        timer_ranked=None,
        timer_casual=None,
        start_zoom=3,
        max_zoom=12,
        score_multiplier=0.9,
        show_region=True,
        show_country_after=True,
        rounds=5,
        moving_penalty=False,
    ),
    "medium": Difficulty(
        id="medium",
        timer_ranked=180,
        timer_casual=None,
        start_zoom=2,
        max_zoom=15,
        score_multiplier=1.0,
        show_region=False,
        show_country_after=True,
        rounds=5,
        moving_penalty=False,
    ),
    "hard": Difficulty(
        id="hard",
        timer_ranked=120,
        timer_casual=None,
        start_zoom=2,
        max_zoom=11,
        score_multiplier=1.2,
        show_region=False,
        show_country_after=True,
        rounds=5,
        moving_penalty=True,
    ),
    "impossible": Difficulty(
        id="impossible",
        timer_ranked=60,
        timer_casual=75,
        start_zoom=1,
        max_zoom=8,
        score_multiplier=1.5,
        show_region=False,
        show_country_after=False,
        rounds=5,
        moving_penalty=True,
    ),
}

ORDER = ("easy", "medium", "hard", "impossible")


def get_difficulty(diff_id: str) -> Difficulty:
    return DIFFICULTIES.get(diff_id, DIFFICULTIES["medium"])
