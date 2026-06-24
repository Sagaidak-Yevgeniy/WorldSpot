"""GeoGuessr-accurate UI primitives — layout, colors, buttons, HUD."""

from __future__ import annotations

import math

import pygame

from src.settings import COLORS, HEIGHT, WIDTH

# GeoGuessr 2024 gameplay palette
GG_GREEN = (16, 172, 132)       # #10AC84 guess button
GG_GREEN_HOVER = (20, 195, 150)
GG_GREEN_DARK = (13, 140, 108)
GG_DISABLED = (74, 85, 104)     # #4A5568
GG_DISABLED_TEXT = (160, 174, 192)
GG_RED_PIN = (234, 67, 53)      # player guess
GG_GREEN_PIN = (52, 168, 83)    # correct location
GG_LINE = (255, 193, 7)         # gold distance line
GG_PURPLE = (121, 85, 242)      # branding accent
GG_OVERLAY = (10, 12, 16, 200)

GUESS_BTN_W, GUESS_BTN_H = 360, 54
GUESS_BTN_RECT = pygame.Rect(WIDTH // 2 - GUESS_BTN_W // 2, HEIGHT - 88, GUESS_BTN_W, GUESS_BTN_H)


def fmt_score(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def fmt_distance(km: float, *, m_label: str = "m", km_label: str = "km") -> str:
    meters = km * 1000.0
    if meters < 1000:
        return f"{int(round(meters))} {m_label}"
    if km < 10:
        return f"{km:.1f} {km_label}"
    return f"{int(round(km)):,} {km_label}".replace(",", " ")


def draw_text_shadow(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    pos: tuple[int, int],
    color: tuple = (255, 255, 255),
    *,
    anchor: str = "topleft",
) -> pygame.Rect:
    shadow = font.render(text, True, (0, 0, 0))
    main = font.render(text, True, color)
    rect = main.get_rect(**{anchor: pos})
    surface.blit(shadow, rect.move(1, 1))
    surface.blit(main, rect)
    return rect


def draw_round_counter(surface: pygame.Surface, font: pygame.font.Font, current: int, total: int) -> None:
    draw_text_shadow(surface, font, f"{current} / {total}", (24, 20))


def draw_session_score(surface: pygame.Surface, font: pygame.font.Font, score: int, label: str = "") -> None:
    text = fmt_score(score)
    if label:
        text = f"{text} {label}"
    t = font.render(text, True, (255, 255, 255))
    surface.blit(t, (WIDTH - t.get_width() - 24, 20))


def draw_timer_badge(surface: pygame.Surface, font: pygame.font.Font, seconds: float) -> None:
    secs = max(0, int(math.ceil(seconds)))
    m, s = divmod(secs, 60)
    text = f"{m}:{s:02d}"
    cx, cy = WIDTH - 80, 52
    pygame.draw.circle(surface, (0, 0, 0), (cx, cy), 30)
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 30, 2)
    color = (255, 100, 100) if secs <= 30 else (255, 255, 255)
    t = font.render(text, True, color)
    surface.blit(t, t.get_rect(center=(cx, cy)))


def draw_guess_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    font: pygame.font.Font,
    *,
    enabled: bool,
    hover: float = 0.0,
) -> None:
    r = pygame.Rect(rect)
    lift = -2 if enabled and hover > 0.2 else 0
    r = r.move(0, lift)

    if enabled:
        fill = GG_GREEN_HOVER if hover > 0.15 else GG_GREEN
        border = (255, 255, 255)
        text_color = (255, 255, 255)
        shadow_a = 80
    else:
        fill = GG_DISABLED
        border = (90, 100, 115)
        text_color = GG_DISABLED_TEXT
        shadow_a = 50

    sh = r.move(0, 4)
    pygame.draw.rect(surface, (0, 0, 0), sh, border_radius=r.height // 2)
    pygame.draw.rect(surface, fill, r, border_radius=r.height // 2)
    pygame.draw.rect(surface, border, r, 2, border_radius=r.height // 2)

    text = font.render(label.upper(), True, text_color)
    surface.blit(text, text.get_rect(center=r.center))


def draw_panorama_zoom_controls(
    surface: pygame.Surface,
    *,
    zoom_in_rect: pygame.Rect,
    zoom_out_rect: pygame.Rect,
    mouse_pos: tuple[int, int],
) -> None:
    for r, sym in ((zoom_in_rect, "+"), (zoom_out_rect, "−")):
        h = r.collidepoint(mouse_pos)
        pygame.draw.circle(surface, (0, 0, 0), r.center, r.width // 2 + 1)
        pygame.draw.circle(surface, (255, 255, 255) if h else (240, 242, 245), r.center, r.width // 2)
        pygame.draw.circle(surface, (180, 185, 195), r.center, r.width // 2, 1)
        f = pygame.font.SysFont("arial", 24, bold=True)
        t = f.render(sym, True, (40, 45, 55))
        surface.blit(t, t.get_rect(center=r.center))


def draw_compass(surface: pygame.Surface, heading: float, *, x: int = 32, y: int | None = None) -> None:
    if y is None:
        y = HEIGHT - 100
    pygame.draw.circle(surface, (0, 0, 0), (x, y), 28)
    pygame.draw.circle(surface, (255, 255, 255), (x, y), 28, 2)
    rad = math.radians(heading)
    tip = (x + int(math.sin(rad) * 16), y - int(math.cos(rad) * 16))
    pygame.draw.line(surface, GG_RED_PIN, (x, y), tip, 3)
    n = pygame.font.SysFont("arial", 11, bold=True).render("N", True, (255, 255, 255))
    surface.blit(n, (x - 4, y - 26))


def draw_result_panel(
    surface: pygame.Surface,
    *,
    distance: str,
    score: int,
    location_name: str,
    title_font: pygame.font.Font,
    ui_font: pygame.font.Font,
    small_font: pygame.font.Font,
    anim_score: int | None = None,
) -> pygame.Rect:
    panel = pygame.Rect(WIDTH // 2 - 280, 16, 560, 130)
    bg = pygame.Surface(panel.size, pygame.SRCALPHA)
    bg.fill((15, 17, 22, 235))
    pygame.draw.rect(bg, (55, 60, 70), bg.get_rect(), 1, border_radius=8)
    surface.blit(bg, panel.topleft)

    dist_surf = title_font.render(distance, True, (255, 255, 255))
    surface.blit(dist_surf, dist_surf.get_rect(midtop=(panel.centerx, panel.y + 12)))

    pts = anim_score if anim_score is not None else score
    pts_text = fmt_score(pts)
    pts_surf = ui_font.render(f"{pts_text} pts", True, GG_GREEN)
    surface.blit(pts_surf, pts_surf.get_rect(midtop=(panel.centerx, panel.y + 58)))

    if location_name:
        loc_surf = small_font.render(location_name, True, (180, 185, 195))
        surface.blit(loc_surf, loc_surf.get_rect(midtop=(panel.centerx, panel.y + 98)))

    return panel


def draw_map_chrome(surface: pygame.Surface, outer: pygame.Rect, *, expanded: bool = False) -> None:
    """White GeoGuessr map frame."""
    border = 4 if not expanded else 5
    shadow = outer.inflate(8, 8).move(2, 4)
    pygame.draw.rect(surface, (0, 0, 0), shadow, border_radius=10)
    pygame.draw.rect(surface, (255, 255, 255), outer.inflate(border, border), border_radius=8)


def draw_menu_hero(surface: pygame.Surface, title_font: pygame.font.Font, subtitle_font: pygame.font.Font, title: str, subtitle: str) -> None:
    surface.fill(COLORS["bg_dark"])
    grad = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        c = int(14 + t * 8)
        grad.fill((c, c + 2, c + 6), (0, y, WIDTH, 1))
    surface.blit(grad, (0, 0))
    logo = title_font.render(title, True, GG_PURPLE)
    surface.blit(logo, logo.get_rect(center=(WIDTH // 2, 140)))
    sub = subtitle_font.render(subtitle, True, COLORS["text_dim"])
    surface.blit(sub, sub.get_rect(center=(WIDTH // 2, 195)))
