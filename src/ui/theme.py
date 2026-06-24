"""GeoGuessr-style UI primitives."""

from __future__ import annotations

import pygame

from src.settings import COLORS, PANEL_RADIUS, WIDTH


def draw_top_bar(surface: pygame.Surface, font: pygame.font.Font, *, left: str, center: str = "", right: str = "") -> None:
    bar_h = 52
    bar = pygame.Surface((WIDTH, bar_h), pygame.SRCALPHA)
    bar.fill((*COLORS["hud_bar"], 220))
    surface.blit(bar, (0, 0))
    pygame.draw.line(surface, (50, 54, 62), (0, bar_h), (WIDTH, bar_h), 1)
    if left:
        surface.blit(font.render(left, True, COLORS["text"]), (20, 16))
    if center:
        t = font.render(center, True, COLORS["text_dim"])
        surface.blit(t, t.get_rect(center=(WIDTH // 2, bar_h // 2)))
    if right:
        t = font.render(right, True, COLORS["accent_light"])
        surface.blit(t, (WIDTH - t.get_width() - 20, 16))


def draw_guess_cta(
    surface: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    font: pygame.font.Font,
    *,
    enabled: bool,
    hover: float,
    pulse: float,
) -> None:
    r = pygame.Rect(rect)
    if enabled:
        glow = r.inflate(int(16 + 12 * pulse), int(10 + 8 * pulse))
        g = pygame.Surface(glow.size, pygame.SRCALPHA)
        pygame.draw.rect(g, (*COLORS["accent"], int(50 + 40 * pulse)), g.get_rect(), border_radius=glow.height // 2)
        surface.blit(g, glow.topleft)

    lift = -2 if enabled and hover > 0.2 else 0
    r = r.move(0, lift)
    fill = COLORS["btn_guess_hover"] if enabled and hover > 0.15 else COLORS["btn_guess"]
    if not enabled:
        fill = COLORS["btn_disabled"]
    pygame.draw.rect(surface, (0, 0, 0), r.move(0, 4), border_radius=r.height // 2)
    pygame.draw.rect(surface, fill, r, border_radius=r.height // 2)
    pygame.draw.rect(surface, (255, 255, 255) if enabled else (120, 125, 135), r, 2, border_radius=r.height // 2)
    color = (255, 255, 255) if enabled else (160, 165, 175)
    text = font.render(label, True, color)
    surface.blit(text, text.get_rect(center=r.center))


def draw_difficulty_card(
    surface: pygame.Surface,
    rect: pygame.Rect,
    title: str,
    desc: str,
    title_font: pygame.font.Font,
    body_font: pygame.font.Font,
    *,
    selected: bool,
    hover: float,
) -> None:
    fill = (42, 46, 54) if not selected else (50, 90, 65)
    if hover > 0.1 and not selected:
        fill = (48, 52, 60)
    pygame.draw.rect(surface, (0, 0, 0), rect.move(0, 4), border_radius=12)
    pygame.draw.rect(surface, fill, rect, border_radius=12)
    border = COLORS["accent"] if selected else (65, 70, 80)
    pygame.draw.rect(surface, border, rect, 2 if selected else 1, border_radius=12)
    surface.blit(title_font.render(title, True, COLORS["text"]), (rect.x + 20, rect.y + 16))
    y = rect.y + 52
    for line in _wrap(desc, body_font, rect.width - 40):
        surface.blit(body_font.render(line, True, COLORS["text_dim"]), (rect.x + 20, y))
        y += 22


def _wrap(text: str, font: pygame.font.Font, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        test = f"{cur} {w}".strip()
        if font.size(test)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:3]
