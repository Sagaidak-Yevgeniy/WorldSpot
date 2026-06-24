from __future__ import annotations

import math

from collections.abc import Callable

import pygame

from src.settings import COLORS, HEIGHT, PANEL_RADIUS, WIDTH

Color = tuple[int, int, int]


def _mix(a: Color, b: Color, t: float) -> Color:
    t = max(0.0, min(1.0, t))
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def draw_background(surface: pygame.Surface, time: float = 0.0) -> None:
    surface.fill(COLORS["bg"])
    width, height = surface.get_size()
    grad = pygame.Surface((width, height))
    for y in range(0, height, 4):
        t = y / max(1, height)
        c = int(12 + t * 14)
        pygame.draw.rect(grad, (c, c + 4, c + 8), (0, y, width, 4))
    surface.blit(grad, (0, 0))
    glow = pygame.Surface((width, height), pygame.SRCALPHA)
    cx = width // 2 + int(80 * pygame.math.Vector2(1, 0).rotate(time * 25).x)
    pygame.draw.circle(glow, (20, 80, 55, 35), (cx, height // 3), 280)
    surface.blit(glow, (0, 0))


def draw_panorama_overlay(surface: pygame.Surface) -> None:
    """Subtle top/bottom gradients so HUD text is readable on panorama."""
    w, h = surface.get_size()
    top = pygame.Surface((w, 120), pygame.SRCALPHA)
    for y in range(120):
        a = int(180 * (1 - y / 120))
        pygame.draw.line(top, (0, 0, 0, a), (0, y), (w, y))
    surface.blit(top, (0, 0))
    bottom = pygame.Surface((w, 140), pygame.SRCALPHA)
    for y in range(140):
        a = int(200 * (y / 140))
        pygame.draw.line(bottom, (0, 0, 0, a), (0, y), (w, y))
    surface.blit(bottom, (0, h - 140))


def draw_hud_chip(surface: pygame.Surface, rect: pygame.Rect, text: str, font: pygame.font.Font) -> None:
    chip = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    chip.fill((0, 0, 0, 160))
    pygame.draw.rect(chip, (255, 255, 255, 40), chip.get_rect(), 1, border_radius=rect.height // 2)
    surface.blit(chip, rect.topleft)
    label = font.render(text, True, COLORS["text"])
    surface.blit(label, label.get_rect(center=rect.center))


def draw_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    *,
    fill: Color = (22, 28, 36),
    border: Color = (70, 82, 96),
    radius: int = PANEL_RADIUS,
) -> None:
    shadow = rect.move(0, 6)
    sh = pygame.Surface(shadow.size, pygame.SRCALPHA)
    sh.fill((0, 0, 0, 80))
    surface.blit(sh, shadow.topleft)
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    pygame.draw.rect(surface, border, rect, 1, border_radius=radius)


class AnimatedButton:
    def __init__(
        self,
        rect: pygame.Rect | tuple[int, int, int, int],
        label: str | Callable[[], str],
        on_click: Callable[[], None],
        *,
        variant: str = "secondary",
        enabled: bool = True,
        pill: bool = False,
    ):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.on_click = on_click
        self.variant = variant
        self.enabled = enabled
        self.pill = pill
        self.hover = 0.0
        self.pressed = False

    def text(self) -> str:
        return self.label() if callable(self.label) else self.label

    def contains(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            self.pressed = False
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.contains(event.pos):
            self.pressed = True
            return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            if was_pressed and self.contains(event.pos):
                self.on_click()
                return True
        return False

    def update(self, dt: float) -> None:
        target = 1.0 if self.enabled and self.contains(pygame.mouse.get_pos()) else 0.0
        speed = min(1.0, dt * 14.0)
        self.hover += (target - self.hover) * speed

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, *, selected: bool = False) -> None:
        radius = self.rect.height // 2 if self.pill else PANEL_RADIUS

        if self.variant == "primary":
            base = COLORS["button_guess"] if self.pill else COLORS["accent"]
            hot = COLORS["accent_hot"]
            text_color = (255, 255, 255)
        elif self.variant == "danger":
            base = (95, 35, 44)
            hot = COLORS["guess"]
            text_color = COLORS["text"]
        elif self.variant == "ghost":
            base = (0, 0, 0)
            hot = (40, 40, 40)
            text_color = COLORS["text"]
        else:
            base = (28, 35, 45)
            hot = (52, 66, 82)
            text_color = COLORS["text"]

        if not self.enabled:
            fill = COLORS["button_guess_disabled"] if self.pill else (35, 38, 43)
            text_color = (200, 205, 210) if self.pill else COLORS["muted"]
        else:
            fill = _mix(base, hot, max(self.hover, 1.0 if selected else 0.0))

        lift = -2 if self.hover > 0.15 and self.enabled else 0
        rect = self.rect.move(0, lift)

        if self.variant != "ghost":
            sh = pygame.Surface(rect.size, pygame.SRCALPHA)
            sh.fill((0, 0, 0, 90))
            surface.blit(sh, rect.move(0, 4).topleft)

        if self.variant == "ghost":
            chip = pygame.Surface(rect.size, pygame.SRCALPHA)
            chip.fill((0, 0, 0, int(120 + 60 * self.hover)))
            pygame.draw.rect(chip, (255, 255, 255, 50), chip.get_rect(), 1, border_radius=radius)
            surface.blit(chip, rect.topleft)
        else:
            pygame.draw.rect(surface, fill, rect, border_radius=radius)
            if selected:
                pygame.draw.rect(surface, COLORS["accent_light"], rect, 2, border_radius=radius)

        text = font.render(self.text(), True, text_color)
        surface.blit(text, text.get_rect(center=rect.center))


def draw_submit_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    font: pygame.font.Font,
    *,
    enabled: bool,
    hover: float,
    time: float,
) -> None:
    """Large pulsing GeoGuessr-style guess button — always highly visible."""
    r = pygame.Rect(rect)
    if enabled:
        pulse = 0.5 + 0.5 * math.sin(time * 5.5)
        glow_size = r.inflate(int(18 + 10 * pulse), int(12 + 8 * pulse))
        glow = pygame.Surface(glow_size.size, pygame.SRCALPHA)
        alpha = int(55 + 45 * pulse)
        pygame.draw.rect(glow, (*COLORS["button_guess_glow"], alpha), glow.get_rect(), border_radius=glow_size.height // 2)
        surface.blit(glow, glow_size.topleft)

    lift = -3 if enabled and hover > 0.1 else 0
    r = r.move(0, lift)
    fill = COLORS["button_guess"] if enabled else COLORS["button_guess_disabled"]
    if enabled and hover > 0.1:
        fill = (
            min(255, fill[0] + 20),
            min(255, fill[1] + 30),
            min(255, fill[2] + 15),
        )

    shadow = r.move(0, 6)
    pygame.draw.rect(surface, (0, 0, 0), shadow, border_radius=r.height // 2)
    pygame.draw.rect(surface, fill, r, border_radius=r.height // 2)
    border_color = (255, 255, 255) if enabled else (120, 128, 140)
    pygame.draw.rect(surface, border_color, r, 3, border_radius=r.height // 2)

    text_color = (255, 255, 255) if enabled else (190, 195, 200)
    text = font.render(label.upper() if enabled else label, True, text_color)
    surface.blit(text, text.get_rect(center=r.center))
