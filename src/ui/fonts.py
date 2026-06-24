"""System font loading with Cyrillic/Kazakh-friendly fallbacks."""

from __future__ import annotations

import pygame

# Ordered by readability on macOS / Windows / Linux.
_FONT_FAMILIES = (
    "segoe ui",
    "sf pro display",
    "sf pro text",
    "helvetica neue",
    "helvetica",
    "arial",
    "noto sans",
    "dejavu sans",
    "liberation sans",
    "ubuntu",
    "cantarell",
)

_cache: dict[tuple[str, int, bool], pygame.font.Font] = {}


def _pick_family() -> str:
    pygame.font.init()
    available = {name.lower() for name in pygame.font.get_fonts()}
    for family in _FONT_FAMILIES:
        token = family.replace(" ", "")
        if token in available or family.replace(" ", "") in available:
            return family
        parts = family.split()
        if all(p in available for p in parts):
            return family
    return "arial"


_FAMILY = _pick_family()


def get_font(size: int, *, bold: bool = False) -> pygame.font.Font:
    key = (_FAMILY, size, bold)
    if key not in _cache:
        _cache[key] = pygame.font.SysFont(_FAMILY, size, bold=bold)
    return _cache[key]


def load_game_fonts() -> dict[str, pygame.font.Font]:
    return {
        "title": get_font(36, bold=True),
        "ui": get_font(22, bold=True),
        "body": get_font(20),
        "small": get_font(16),
        "tiny": get_font(13),
    }
