"""GeoGuessr-style panorama — drag look, scroll zoom, movement tracking."""

from __future__ import annotations

import math

import pygame
from PIL import Image


class PanoramaViewer:
    LOOK_SENS = 0.16
    ZOOM_SENS = 3.5
    INERTIA_DECAY = 0.91
    MIN_FOV = 30.0
    MAX_FOV = 100.0

    def __init__(
        self,
        rect: pygame.Rect,
        source: pygame.Surface,
        *,
        heading=0.0,
        pitch=0.0,
        fov=90.0,
        allow_zoom: bool = True,
        allow_look: bool = True,
    ):
        self.rect = pygame.Rect(rect)
        self.source = source
        self.heading = heading % 360
        self.pitch = max(-85.0, min(85.0, pitch))
        self.fov = max(self.MIN_FOV, min(self.MAX_FOV, fov))
        self.allow_zoom = allow_zoom
        self.allow_look = allow_look
        self._dragging = False
        self._vel_h = 0.0
        self._vel_p = 0.0
        self._surface: pygame.Surface | None = None
        self._dirty = True
        self._equirect = self._is_equirect(source)
        self._pil = self._to_pil(source) if self._equirect else None
        self._quality = 1.0
        self.movement_units = 0.0

        w, h = rect.size
        self._zoom_in = pygame.Rect(w - 56, h // 2 - 52, 40, 40)
        self._zoom_out = pygame.Rect(w - 56, h // 2 - 4, 40, 40)

    @staticmethod
    def _is_equirect(s: pygame.Surface) -> bool:
        w, h = s.get_size()
        return h > 0 and w >= h * 1.8

    @staticmethod
    def _to_pil(s: pygame.Surface) -> Image.Image:
        return Image.frombytes("RGB", s.get_size(), pygame.image.tostring(s, "RGB"))

    def zoom_in_rect(self) -> pygame.Rect:
        return self._zoom_in.move(self.rect.topleft)

    def zoom_out_rect(self) -> pygame.Rect:
        return self._zoom_out.move(self.rect.topleft)

    def contains_zoom(self, pos: tuple[int, int]) -> bool:
        return self.zoom_in_rect().collidepoint(pos) or self.zoom_out_rect().collidepoint(pos)

    def _render(self) -> pygame.Surface:
        vw, vh = self.rect.size
        rw = max(2, int(vw * self._quality))
        rh = max(2, int(vh * self._quality))
        if self._equirect and self._pil:
            view = self._render_equirect(rw, rh)
        else:
            view = self._render_flat(rw, rh)
        if self._quality < 1.0:
            view = pygame.transform.smoothscale(view, (vw, vh))
        return view

    def _render_flat(self, vw: int, vh: int) -> pygame.Surface:
        iw, ih = self.source.get_size()
        zoom = (90.0 / self.fov) * max(vw / iw, vh / ih)
        sw, sh = max(1, int(iw * zoom)), max(vh, int(ih * zoom))
        scaled = pygame.transform.smoothscale(self.source, (sw, sh))
        max_x, max_y = max(0, sw - vw), max(0, sh - vh)
        ox = int((self.heading / 360.0) * max_x) if max_x else 0
        oy = int(((self.pitch + 30.0) / 60.0) * max_y) if max_y else 0
        view = pygame.Surface((vw, vh))
        view.blit(scaled, (-ox, -oy))
        return view

    def _render_equirect(self, rw: int, rh: int) -> pygame.Surface:
        assert self._pil is not None
        sw, sh = self._pil.size
        h_rad, p_rad = math.radians(self.heading), math.radians(self.pitch)
        fov_rad = math.radians(self.fov)
        fx = (rw / 2) / math.tan(fov_rad / 2)
        px = self._pil.load()
        img = Image.new("RGB", (rw, rh))
        sp = img.load()
        cos_h, sin_h = math.cos(h_rad), math.sin(h_rad)
        cos_p, sin_p = math.cos(p_rad), math.sin(p_rad)
        step = 2 if self._quality < 0.85 else 1
        for y in range(0, rh, step):
            ny = (y - rh / 2) / fx
            for x in range(0, rw, step):
                nx = (x - rw / 2) / fx
                nz = 1.0
                ln = math.sqrt(nx * nx + ny * ny + nz * nz)
                nx, ny, nz = nx / ln, ny / ln, nz / ln
                cx = nx * cos_h + nz * sin_h
                cz = -nx * sin_h + nz * cos_h
                cy = ny * cos_p - cz * sin_p
                cz2 = ny * sin_p + cz * cos_p
                lon = math.atan2(cx, cz2)
                lat = math.asin(max(-1.0, min(1.0, cy)))
                u = int((lon / (2 * math.pi) + 0.5) * sw) % sw
                v = max(0, min(sh - 1, int((0.5 - lat / math.pi) * sh)))
                c = px[u, v]
                if step > 1:
                    for dy in range(step):
                        for dx in range(step):
                            if x + dx < rw and y + dy < rh:
                                sp[x + dx, y + dy] = c
                else:
                    sp[x, y] = c
        return pygame.image.frombytes(img.tobytes(), img.size, "RGB")

    def _apply_look(self, dh: float, dp: float) -> None:
        self.movement_units += abs(dh) + abs(dp)
        self.heading = (self.heading + dh) % 360
        self.pitch = max(-85, min(85, self.pitch + dp))
        self._quality = 0.65
        self._dirty = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.allow_zoom and self.zoom_in_rect().collidepoint(event.pos):
                self.fov = max(self.MIN_FOV, self.fov - 8)
                self._dirty = True
                return True
            if self.allow_zoom and self.zoom_out_rect().collidepoint(event.pos):
                self.fov = min(self.MAX_FOV, self.fov + 8)
                self._dirty = True
                return True
            if self.allow_look and self.rect.collidepoint(event.pos) and not self.contains_zoom(event.pos):
                self._dragging = True
                self._vel_h = self._vel_p = 0.0
                pygame.mouse.get_rel()
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)
                return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self._dragging:
            self._dragging = False
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)
            self._quality = 1.0
            self._dirty = True
            return True
        if event.type == pygame.MOUSEMOTION and self._dragging and self.allow_look:
            dx, dy = event.rel
            self._vel_h = -dx * self.LOOK_SENS
            self._vel_p = dy * self.LOOK_SENS * 0.7
            self._apply_look(self._vel_h, self._vel_p)
            return True
        if event.type == pygame.MOUSEWHEEL and self.allow_zoom and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.fov = max(self.MIN_FOV, min(self.MAX_FOV, self.fov - event.y * self.ZOOM_SENS))
            self._dirty = True
            return True
        if event.type == pygame.KEYDOWN and self.allow_look:
            step = 6
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self._apply_look(-step, 0)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._apply_look(step, 0)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self._apply_look(0, -3)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._apply_look(0, 3)
            else:
                return False
            return True
        return False

    def update(self, dt: float) -> None:
        if not self._dragging and self.allow_look and (abs(self._vel_h) > 0.01 or abs(self._vel_p) > 0.01):
            self._apply_look(self._vel_h, self._vel_p)
            self._vel_h *= self.INERTIA_DECAY
            self._vel_p *= self.INERTIA_DECAY
            self._quality = 0.78
        if self._dirty:
            self._surface = self._render()
            self._dirty = False

    def draw(self, surface: pygame.Surface, *, draw_controls: bool = True) -> None:
        if self._surface is None:
            self._surface = self._render()
        surface.blit(self._surface, self.rect.topleft)
        if self._dragging:
            cx, cy = pygame.mouse.get_pos()
            for d in (-14, 14):
                pygame.draw.line(surface, (255, 255, 255), (cx + d, cy), (cx - d, cy), 2)
                pygame.draw.line(surface, (255, 255, 255), (cx, cy + d), (cx, cy - d), 2)
