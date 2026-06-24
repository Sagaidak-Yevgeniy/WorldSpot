"""Slippy map tiles — OpenStreetMap with local/Russian labels (free, no API key)."""

from __future__ import annotations

import io
import threading
import time
import urllib.error
import urllib.request
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

import pygame

from src.mercator import clamp_lat, latlon_to_world_pixel, normalize_lon, world_pixel_to_latlon

TILE_SIZE = 256
# OSM shows Cyrillic/local names — best free option for Russian map.
TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
TILE_ATTRIBUTION = "© OpenStreetMap"
MAX_ZOOM = 19
MIN_ZOOM = 1
MAX_CACHE = 900

_executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="maptile")
_cache: OrderedDict[tuple[int, int, int], pygame.Surface] = OrderedDict()
_pending: set[tuple[int, int, int]] = set()
_cache_lock = threading.Lock()
_placeholder: pygame.Surface | None = None


def _placeholder_tile() -> pygame.Surface:
    global _placeholder
    if _placeholder is not None:
        return _placeholder
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    surf.fill((236, 240, 244))
    _placeholder = surf
    return _placeholder


def _cache_put(key: tuple[int, int, int], surf: pygame.Surface) -> None:
    with _cache_lock:
        if key in _cache:
            _cache.move_to_end(key)
            return
        _cache[key] = surf
        while len(_cache) > MAX_CACHE:
            _cache.popitem(last=False)


def peek_tile(z: int, x: int, y: int) -> pygame.Surface | None:
    n = 2**z
    x = x % n
    if y < 0 or y >= n:
        return _placeholder_tile()
    with _cache_lock:
        t = _cache.get((z, x, y))
        if t is not None:
            _cache.move_to_end((z, x, y))
        return t


def queue_tile(z: int, x: int, y: int) -> None:
    n = 2**z
    x = x % n
    if y < 0 or y >= n:
        return
    key = (z, x, y)
    with _cache_lock:
        if key in _cache or key in _pending:
            return
        _pending.add(key)
    _executor.submit(_download_tile, z, x, y)


def _download_tile(z: int, x: int, y: int) -> None:
    key = (z, x, y)
    try:
        url = TILE_URL.format(z=z, x=x, y=y)
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "WorldSpot/1.0 (GeoGuessr-style; educational)"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        img = pygame.image.load(io.BytesIO(data))
        if pygame.display.get_surface():
            img = img.convert()
        if img.get_size() != (TILE_SIZE, TILE_SIZE):
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        _cache_put(key, img)
    except (urllib.error.URLError, pygame.error, TimeoutError, OSError, ValueError):
        pass
    finally:
        with _cache_lock:
            _pending.discard(key)


def visible_tile_range(width: int, height: int, clat: float, clon: float, zoom: int):
    zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom))
    clat, clon = clamp_lat(clat), normalize_lon(clon)
    cx, cy = latlon_to_world_pixel(clat, clon, zoom)
    tlx, tly = cx - width / 2, cy - height / 2
    return (
        int(tlx // TILE_SIZE),
        int(tly // TILE_SIZE),
        int((tlx + width) // TILE_SIZE),
        int((tly + height) // TILE_SIZE),
        tlx,
        tly,
    )


def _is_placeholder(tile: pygame.Surface) -> bool:
    return tile.get_at((0, 0))[:3] == (236, 240, 244)


def draw_map_tiles(
    surface: pygame.Surface,
    rect: pygame.Rect,
    center_lat: float,
    center_lon: float,
    zoom: int,
    *,
    allow_fetch: bool = True,
    max_fetch: int = 6,
) -> int:
    zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom))
    x0, y0, x1, y1, tlx, tly = visible_tile_range(rect.width, rect.height, center_lat, center_lon, zoom)
    loading = 0
    queued = 0
    synced = 0
    clip = surface.get_clip()
    surface.set_clip(rect)
    surface.fill((210, 225, 235), rect)
    for tx in range(x0, x1 + 1):
        for ty in range(y0, y1 + 1):
            tile = peek_tile(zoom, tx, ty)
            if tile is None or _is_placeholder(tile):
                loading += 1
                if allow_fetch and synced < 2:
                    _download_tile(zoom, tx, ty)
                    tile = peek_tile(zoom, tx, ty)
                    synced += 1
                if tile is None or _is_placeholder(tile):
                    if allow_fetch and queued < max_fetch:
                        queue_tile(zoom, tx, ty)
                        queued += 1
                    tile = _placeholder_tile()
            surface.blit(tile, (int(rect.x + tx * TILE_SIZE - tlx), int(rect.y + ty * TILE_SIZE - tly)))
    surface.set_clip(clip)
    return loading


def pixel_to_latlon(px, py, rect, clat, clon, zoom):
    cx, cy = latlon_to_world_pixel(clamp_lat(clat), normalize_lon(clon), zoom)
    return world_pixel_to_latlon(cx - rect.width / 2 + px - rect.x, cy - rect.height / 2 + py - rect.y, zoom)


def latlon_to_pixel(lat, lon, rect, clat, clon, zoom):
    cx, cy = latlon_to_world_pixel(clamp_lat(clat), normalize_lon(clon), zoom)
    wx, wy = latlon_to_world_pixel(clamp_lat(lat), normalize_lon(lon), zoom)
    return int(rect.x + rect.width / 2 + wx - cx), int(rect.y + rect.height / 2 + wy - cy)


def pan_center_by_pixels(clat, clon, zoom, dx, dy):
    cx, cy = latlon_to_world_pixel(clamp_lat(clat), normalize_lon(clon), zoom)
    return world_pixel_to_latlon(cx - dx, cy - dy, zoom)


def zoom_at_point(clat, clon, old_z, new_z, point, rect):
    if old_z == new_z:
        return clamp_lat(clat), normalize_lon(clon)
    lat, lon = pixel_to_latlon(point[0], point[1], rect, clat, clon, old_z)
    cx, cy = latlon_to_world_pixel(lat, lon, new_z)
    return world_pixel_to_latlon(
        cx - rect.width / 2 + point[0] - rect.x,
        cy - rect.height / 2 + point[1] - rect.y,
        new_z,
    )


def wait_for_visible_tiles(
    width: int,
    height: int,
    center_lat: float,
    center_lon: float,
    zoom: int,
    *,
    timeout: float = 12.0,
) -> int:
    """Block until visible tiles are cached (or timeout). Returns tiles loaded."""
    x0, y0, x1, y1, _, _ = visible_tile_range(width, height, center_lat, center_lon, zoom)
    needed: list[tuple[int, int, int]] = []
    for tx in range(x0, x1 + 1):
        for ty in range(y0, y1 + 1):
            needed.append((zoom, tx, ty))
            queue_tile(zoom, tx, ty)

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        ready = 0
        for key in needed:
            tile = peek_tile(*key)
            if tile is not None and not _is_placeholder(tile):
                ready += 1
        if ready == len(needed):
            return ready
        time.sleep(0.05)
    return sum(
        1
        for key in needed
        if (t := peek_tile(*key)) is not None and not _is_placeholder(t)
    )


def prefetch_view(w, h, clat, clon, zoom):
    x0, y0, x1, y1, _, _ = visible_tile_range(w, h, clat, clon, zoom)
    for tx in range(x0, x1 + 1):
        for ty in range(y0, y1 + 1):
            queue_tile(zoom, tx, ty)
