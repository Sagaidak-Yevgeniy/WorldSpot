"""GeoGuessr mini-map — corner widget + fullscreen expand modal."""

from __future__ import annotations

import pygame

from src.mercator import clamp_lat, normalize_lon
from src.osm_tiles import (
    MIN_ZOOM,
    TILE_ATTRIBUTION,
    _is_placeholder,
    draw_map_tiles,
    latlon_to_pixel,
    pan_center_by_pixels,
    peek_tile,
    pixel_to_latlon,
    prefetch_view,
    visible_tile_range,
    wait_for_visible_tiles,
    zoom_at_point,
)
from src.settings import COLORS, HEIGHT, MAP_EXPANDED_H, MAP_EXPANDED_W, WIDTH
from src.ui.geoguessr import draw_map_chrome
from src.ui.map_view import draw_guess_pin, draw_line, draw_result_pin


class OsmMapView:
    def __init__(
        self,
        rect: pygame.Rect,
        *,
        zoom: int = 2,
        max_zoom: int = 16,
        fonts: dict | None = None,
    ):
        self.base_rect = pygame.Rect(rect)
        self.rect = pygame.Rect(rect)
        self.center_lat, self.center_lon = 20.0, 0.0
        self.zoom = zoom
        self.max_zoom = max_zoom
        self.fonts = fonts or {}
        self.guess_latlon = None
        self.guess_pixel = None
        self.expanded = False
        self._dragging = False
        self._moved = False
        self._last: tuple[int, int] | None = None
        self._screen = (WIDTH, HEIGHT)
        self._layer: pygame.Surface | None = None
        self._layer_key = ""
        self._expand = pygame.Rect(0, 0, 0, 0)
        self._zoom_in = pygame.Rect(0, 0, 0, 0)
        self._zoom_out = pygame.Rect(0, 0, 0, 0)
        self._close = pygame.Rect(0, 0, 0, 0)
        self._layout_controls()
        self._prime_tiles()

    def _map_rect(self) -> pygame.Rect:
        return self._inner()

    def _prime_tiles(self) -> None:
        inner = self._inner()
        wait_for_visible_tiles(inner.width, inner.height, self.center_lat, self.center_lon, self.zoom, timeout=5.0)

    def set_screen_size(self, s):
        self._screen = s

    def _inner(self) -> pygame.Rect:
        return self.rect.inflate(-8, -8)

    def _expanded_rect(self) -> pygame.Rect:
        w, h = self._screen
        return pygame.Rect(w // 2 - MAP_EXPANDED_W // 2, h // 2 - MAP_EXPANDED_H // 2 - 20, MAP_EXPANDED_W, MAP_EXPANDED_H)

    def _layout_controls(self):
        m = 10
        inner = self._inner()
        self._expand = pygame.Rect(inner.x + m, inner.bottom - m - 36, 36, 36)
        if self.expanded:
            outer = self.rect
            self._close = pygame.Rect(outer.x + 12, outer.y + 12, 36, 36)
            x = outer.right - m - 38
            y = outer.y + m + 40
            self._zoom_in = pygame.Rect(x, y, 38, 38)
            self._zoom_out = pygame.Rect(x, y + 44, 38, 38)
        else:
            self._close = pygame.Rect(0, 0, 0, 0)
            self._zoom_in = pygame.Rect(0, 0, 0, 0)
            self._zoom_out = pygame.Rect(0, 0, 0, 0)

    def contains(self, pos) -> bool:
        if self.expanded:
            return (
                self.rect.collidepoint(pos)
                or self._close.collidepoint(pos)
                or self._zoom_in.collidepoint(pos)
                or self._zoom_out.collidepoint(pos)
            )
        return self.rect.collidepoint(pos) or self._expand.collidepoint(pos)

    def toggle_expand(self):
        self.expanded = not self.expanded
        self.rect = self._expanded_rect() if self.expanded else pygame.Rect(self.base_rect)
        self._invalidate()
        self._layout_controls()
        self._prime_tiles()
        if self.guess_latlon:
            self.guess_pixel = latlon_to_pixel(
                *self.guess_latlon, self._map_rect(), self.center_lat, self.center_lon, self.zoom
            )

    def set_guess(self, lat, lon):
        self.guess_latlon = (lat, lon)
        self.guess_pixel = latlon_to_pixel(lat, lon, self._map_rect(), self.center_lat, self.center_lon, self.zoom)

    def _invalidate(self):
        self._layer_key = ""
        self._layer = None

    def _zoom(self, delta, at=None):
        old = self.zoom
        self.zoom = max(MIN_ZOOM, min(self.max_zoom, self.zoom + delta))
        if at and self.zoom != old:
            self.center_lat, self.center_lon = zoom_at_point(
                self.center_lat, self.center_lon, old, self.zoom, at, self._map_rect()
            )
        self.center_lat, self.center_lon = clamp_lat(self.center_lat), normalize_lon(self.center_lon)
        self._invalidate()
        prefetch_view(self._inner().width, self._inner().height, self.center_lat, self.center_lon, self.zoom)
        if self.guess_latlon:
            self.guess_pixel = latlon_to_pixel(
                *self.guess_latlon, self._map_rect(), self.center_lat, self.center_lon, self.zoom
            )

    def _all_tiles_ready(self) -> bool:
        inner = self._inner()
        x0, y0, x1, y1, _, _ = visible_tile_range(
            inner.width, inner.height, self.center_lat, self.center_lon, self.zoom
        )
        for tx in range(x0, x1 + 1):
            for ty in range(y0, y1 + 1):
                tile = peek_tile(self.zoom, tx, ty)
                if tile is None or _is_placeholder(tile):
                    return False
        return True

    def handle_event(self, event) -> bool:
        mrect = self._map_rect()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.expanded and self._close.collidepoint(event.pos):
                self.toggle_expand()
                return True
            if self.expanded and self._zoom_in.collidepoint(event.pos):
                self._zoom(1, event.pos)
                return True
            if self.expanded and self._zoom_out.collidepoint(event.pos):
                self._zoom(-1, event.pos)
                return True
            if not self.expanded and self._expand.collidepoint(event.pos):
                self.toggle_expand()
                return True
            if mrect.collidepoint(event.pos):
                self._dragging, self._moved, self._last = True, False, event.pos
                return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging:
                if not self._moved and mrect.collidepoint(event.pos):
                    self.set_guess(
                        *pixel_to_latlon(
                            event.pos[0], event.pos[1], mrect, self.center_lat, self.center_lon, self.zoom
                        )
                    )
                elif self._moved:
                    prefetch_view(mrect.width, mrect.height, self.center_lat, self.center_lon, self.zoom)
                self._dragging = False
                return True
        if event.type == pygame.MOUSEMOTION and self._dragging and self._last:
            dx, dy = event.pos[0] - self._last[0], event.pos[1] - self._last[1]
            if abs(dx) + abs(dy) > 2:
                self._moved = True
            self.center_lat, self.center_lon = pan_center_by_pixels(
                self.center_lat, self.center_lon, self.zoom, dx, dy
            )
            self.center_lat, self.center_lon = clamp_lat(self.center_lat), normalize_lon(self.center_lon)
            self._invalidate()
            if self.guess_latlon:
                self.guess_pixel = latlon_to_pixel(
                    *self.guess_latlon, mrect, self.center_lat, self.center_lon, self.zoom
                )
            self._last = event.pos
            return True
        if event.type == pygame.MOUSEWHEEL and self.contains(pygame.mouse.get_pos()):
            self._zoom(event.y, pygame.mouse.get_pos())
            return True
        return False

    def update(self, dt):
        self._layout_controls()
        if not self._dragging:
            inner = self._inner()
            prefetch_view(inner.width, inner.height, self.center_lat, self.center_lon, self.zoom)
            if not self._all_tiles_ready():
                self._invalidate()

    def _blit_tiles(self, target, inner, *, fetch: bool) -> int:
        local = pygame.Rect(0, 0, inner.width, inner.height)
        return draw_map_tiles(
            target, local, self.center_lat, self.center_lon, self.zoom,
            allow_fetch=fetch, max_fetch=14 if fetch else 0,
        )

    def draw(self, surface):
        if self.expanded:
            dim = pygame.Surface(self._screen, pygame.SRCALPHA)
            dim.fill((0, 0, 0, 210))
            surface.blit(dim, (0, 0))

        draw_map_chrome(surface, self.rect, expanded=self.expanded)
        inner = self._inner()
        pygame.draw.rect(surface, (218, 225, 232), inner, border_radius=4)

        key = f"{self.center_lat:.3f}:{self.center_lon:.3f}:{self.zoom}:{inner.size}"
        tiles_ready = self._all_tiles_ready()
        if not self._dragging and tiles_ready and self._layer is not None and key == self._layer_key:
            surface.blit(self._layer, inner.topleft)
        else:
            layer = pygame.Surface(inner.size)
            loading = self._blit_tiles(layer, inner, fetch=not self._dragging)
            surface.blit(layer, inner.topleft)
            if not self._dragging and loading == 0 and tiles_ready:
                self._layer, self._layer_key = layer, key

        if self.guess_pixel:
            draw_guess_pin(surface, self.guess_pixel)

        self._draw_controls(surface)
        f = self.fonts.get("tiny") or pygame.font.SysFont("arial", 10)
        attr = f.render(TILE_ATTRIBUTION, True, (90, 98, 110))
        surface.blit(attr, (inner.x + 8, inner.bottom - 18))

    def _draw_controls(self, surface):
        mouse = pygame.mouse.get_pos()
        if not self.expanded:
            er = self._expand
            h = er.collidepoint(mouse)
            pygame.draw.rect(surface, (255, 255, 255), er, border_radius=6)
            pygame.draw.rect(surface, (120, 130, 145) if h else (90, 100, 115), er, 2, border_radius=6)
            surface.blit(pygame.font.SysFont("arial", 20).render("⤢", True, (40, 45, 55)), (er.x + 8, er.y + 6))
            return

        cr = self._close
        pygame.draw.circle(surface, (255, 255, 255), cr.center, cr.width // 2)
        pygame.draw.circle(surface, (80, 90, 105), cr.center, cr.width // 2, 2)
        x = pygame.font.SysFont("arial", 22, bold=True).render("×", True, (40, 45, 55))
        surface.blit(x, x.get_rect(center=cr.center))

        for r, sym in ((self._zoom_in, "+"), (self._zoom_out, "−")):
            if r.width == 0:
                continue
            h = r.collidepoint(mouse)
            pygame.draw.rect(surface, (255, 255, 255), r, border_radius=8)
            pygame.draw.rect(surface, (140, 150, 165) if h else (100, 110, 125), r, 2, border_radius=8)
            t = pygame.font.SysFont("arial", 22, bold=True).render(sym, True, (40, 45, 55))
            surface.blit(t, t.get_rect(center=r.center))


class OsmResultMapView(OsmMapView):
    def __init__(self, rect, guess, truth, font):
        super().__init__(rect, zoom=2, max_zoom=14)
        self.guess, self.truth = guess, truth
        self.center_lat = (guess[0] + truth[0]) / 2
        self.center_lon = (guess[1] + truth[1]) / 2
        span = max(abs(guess[0] - truth[0]), abs(guess[1] - truth[1]), 4)
        self.zoom = 1 if span > 80 else 2 if span > 40 else 3 if span > 15 else 4 if span > 5 else 5 if span > 1 else 7
        self._invalidate()
        self._prime_tiles()

    def draw(self, surface):
        inner = self._inner()
        layer = pygame.Surface(inner.size)
        self._blit_tiles(layer, inner, fetch=True)
        draw_map_chrome(surface, self.rect, expanded=True)
        surface.blit(layer, inner.topleft)
        mrect = self._map_rect()
        gp = latlon_to_pixel(*self.guess, mrect, self.center_lat, self.center_lon, self.zoom)
        tp = latlon_to_pixel(*self.truth, mrect, self.center_lat, self.center_lon, self.zoom)
        draw_line(surface, gp, tp)
        draw_guess_pin(surface, gp, color=COLORS["guess_pin"])
        draw_result_pin(surface, tp, color=COLORS["truth"])
        f = self.fonts.get("tiny") or pygame.font.SysFont("arial", 10)
        surface.blit(f.render(TILE_ATTRIBUTION, True, (90, 98, 110)), (inner.x + 8, inner.bottom - 18))
