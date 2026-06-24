import random

import pygame

from src.paths import ASSETS
from src.settings import COLORS

_map_cache: dict[tuple[int, int], pygame.Surface] = {}
_world_map_source: pygame.Surface | None = None
_panorama_source_cache: dict[str, pygame.Surface] = {}


def _load_world_map_source() -> pygame.Surface | None:
    global _world_map_source
    if _world_map_source is not None:
        return _world_map_source
    path = ASSETS / "world_map.jpg"
    if not path.exists():
        return None
    img = pygame.image.load(str(path))
    if pygame.display.get_surface() is not None:
        img = img.convert()
    _world_map_source = img
    return _world_map_source


def get_scaled_map(size: tuple[int, int]) -> pygame.Surface | None:
    if size in _map_cache:
        return _map_cache[size]
    source = _load_world_map_source()
    if source is None:
        return None
    scaled = pygame.transform.smoothscale(source, size)
    _map_cache[size] = scaled
    return scaled


def draw_world_map(surface: pygame.Surface, rect: pygame.Rect) -> None:
    map_img = get_scaled_map(rect.size)
    if map_img:
        surface.blit(map_img, rect.topleft)
    else:
        pygame.draw.rect(surface, COLORS["ocean"], rect)
        land = [
            (0.18, 0.35, 0.22, 0.45),
            (0.48, 0.28, 0.18, 0.35),
            (0.72, 0.32, 0.20, 0.40),
            (0.78, 0.72, 0.12, 0.18),
        ]
        for lx, ly, lw, lh in land:
            r = pygame.Rect(
                rect.x + int(lx * rect.width),
                rect.y + int(ly * rect.height),
                int(lw * rect.width),
                int(lh * rect.height),
            )
            pygame.draw.ellipse(surface, COLORS["land"], r)
    pygame.draw.rect(surface, COLORS["text"], rect, 2)


def draw_marker(
    surface: pygame.Surface,
    pos: tuple[int, int],
    color: tuple,
    label: str,
    font,
    *,
    radius: int = 9,
) -> None:
    x, y = pos
    pygame.draw.circle(surface, (0, 0, 0, 120), (x, y), radius + 2)
    pygame.draw.circle(surface, color, (x, y), radius)
    pygame.draw.circle(surface, (255, 255, 255), (x, y), radius, 2)
    pygame.draw.line(surface, (255, 255, 255), (x - radius - 4, y), (x + radius + 4, y), 1)
    pygame.draw.line(surface, (255, 255, 255), (x, y - radius - 4), (x, y + radius + 4), 1)
    if label:
        t = font.render(label, True, color)
        bg = pygame.Surface((t.get_width() + 8, t.get_height() + 4), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        surface.blit(bg, (x + 12, y - 10))
        surface.blit(t, (x + 16, y - 8))


def draw_line(surface: pygame.Surface, a: tuple[int, int], b: tuple[int, int]) -> None:
    pygame.draw.line(surface, (20, 24, 30), a, b, 5)
    pygame.draw.line(surface, COLORS["line"], a, b, 3)


def draw_guess_pin(surface: pygame.Surface, pos: tuple[int, int], *, color: tuple | None = None) -> None:
    """GeoGuessr red teardrop pin."""
    color = color or COLORS["guess_pin"]
    x, y = pos
    tip_y = y
    head_y = y - 32
    head_r = 11
    pygame.draw.polygon(surface, (0, 0, 0), [(x - 2, tip_y + 2), (x + 2, tip_y + 2), (x, head_y + head_r)])
    pygame.draw.polygon(surface, color, [(x - 1, tip_y), (x + 1, tip_y), (x, head_y + head_r)])
    pygame.draw.circle(surface, (0, 0, 0), (x, head_y), head_r + 2)
    pygame.draw.circle(surface, color, (x, head_y), head_r)
    pygame.draw.circle(surface, (255, 255, 255), (x, head_y), head_r, 2)
    pygame.draw.circle(surface, (255, 255, 255), (x, head_y - 3), 4)


def draw_result_pin(surface: pygame.Surface, pos: tuple[int, int], *, color: tuple | None = None) -> None:
    """GeoGuessr green correct-location marker."""
    color = color or COLORS["truth"]
    x, y = pos
    cy = y - 14
    pygame.draw.circle(surface, (0, 0, 0), (x, cy), 14)
    pygame.draw.circle(surface, color, (x, cy), 12)
    pygame.draw.circle(surface, (255, 255, 255), (x, cy), 12, 2)
    pygame.draw.polygon(surface, color, [(x, y), (x - 7, cy + 6), (x + 7, cy + 6)])
    pygame.draw.circle(surface, (255, 255, 255), (x, cy - 2), 4)


def load_panorama_source(location: dict) -> pygame.Surface:
    pan_file = location.get("panorama", "")
    cache_key = f"{location.get('id', 'unknown')}:{pan_file}"
    if cache_key in _panorama_source_cache:
        return _panorama_source_cache[cache_key]

    if pan_file:
        path = ASSETS / "panoramas" / pan_file
        if path.is_file():
            img = pygame.image.load(str(path))
            if pygame.display.get_surface() is not None:
                img = img.convert()
            _panorama_source_cache[cache_key] = img
            return img

    return _placeholder_panorama(location)


def load_panorama(location: dict, size: tuple[int, int]) -> pygame.Surface:
    source = load_panorama_source(location)
    return pygame.transform.smoothscale(source, size)


def _placeholder_panorama(location: dict, *, no_photo: str = "No panorama photo", hint: str = "") -> pygame.Surface:
    surf = pygame.Surface((1920, 1080))
    hue = hash(location["id"]) % 360
    base = pygame.Color(0)
    base.hsva = (hue, 35, 45, 100)
    surf.fill(base)
    for i in range(0, 1920, 120):
        shade = pygame.Color(0)
        shade.hsva = (hue, 25, 35 + (i % 240) // 20, 60)
        pygame.draw.rect(surf, shade, (i, 0, 60, 1080))
    from src.ui.fonts import get_font

    font = get_font(32, bold=True)
    small = get_font(22)
    t1 = font.render(no_photo, True, (255, 255, 255))
    t2 = small.render(hint, True, (230, 235, 240))
    surf.blit(t1, (48, 48))
    if hint:
        surf.blit(t2, (48, 96))
    return surf
