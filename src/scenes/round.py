import math

import pygame

from src.i18n import tr_region
from src.settings import HEIGHT, MAP_RECT, PANORAMA_RECT, WIDTH
from src.systems.difficulty import get_difficulty
from src.systems.scoring import haversine_km, score_from_distance
from src.ui.geoguessr import (
    GUESS_BTN_RECT,
    draw_compass,
    draw_guess_button,
    draw_panorama_zoom_controls,
    draw_round_counter,
    draw_session_score,
    draw_timer_badge,
)
from src.ui.map_view import load_panorama_source
from src.ui.osm_map_view import OsmMapView
from src.ui.panorama_viewer import PanoramaViewer

INTRO_DUR = 1.2
MOVEMENT_PENALTY_THRESHOLD = 400.0


def start_game(game: "Game", *, difficulty: str = "medium", ranked: bool = False) -> None:
    from src.systems.locations import available_locations, pick_round

    cfg = get_difficulty(difficulty)
    pool = available_locations()
    locations = pick_round(pool, count=cfg.rounds)
    game.start_session(locations, ranked=ranked, difficulty=difficulty)
    game.change_scene(RoundScene(game, locations[0], 0))


class RoundScene:
    def __init__(self, game: "Game", location: dict, round_index: int):
        self.game = game
        self.location = location
        self.round_index = round_index
        self.time = 0.0
        self.intro = 0.0
        self.cfg = get_difficulty(game.difficulty)
        self._guess_hover = 0.0

        h0 = float(location.get("heading", 0))
        spin = float(location.get("intro_spin", 0))
        self._h_tgt, self._fov_tgt = h0, float(location.get("fov", 88))
        self._h0 = (h0 + spin) % 360
        self._fov0 = min(105.0, self._fov_tgt + 20)

        no_look = self.cfg.id == "impossible" and self.cfg.moving_penalty
        self.panorama = PanoramaViewer(
            pygame.Rect(PANORAMA_RECT),
            load_panorama_source(location),
            heading=self._h0,
            pitch=float(location.get("pitch", 0)),
            fov=self._fov0,
            allow_zoom=not no_look,
            allow_look=not no_look,
        )
        self.map = OsmMapView(
            pygame.Rect(MAP_RECT),
            zoom=self.cfg.start_zoom,
            max_zoom=self.cfg.max_zoom,
            fonts={"tiny": game.tiny_font},
        )
        self.map.set_screen_size((WIDTH, HEIGHT))

        self.guess = None
        self.done = False
        if game.ranked and self.cfg.timer_ranked:
            self.timer = float(self.cfg.timer_ranked)
        elif self.cfg.timer_casual:
            self.timer = float(self.cfg.timer_casual)
        else:
            self.timer = None

    @property
    def _over_map(self):
        return self.map.contains(pygame.mouse.get_pos()) or self.map._dragging

    @property
    def _can_guess(self):
        return self.guess is not None and self.intro >= INTRO_DUR and not self.done

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.map.expanded:
                self.map.toggle_expand()
            else:
                self._menu()
            return
        if self.done:
            return

        if self._can_guess and GUESS_BTN_RECT.collidepoint(pygame.mouse.get_pos()):
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._submit()
                return
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._submit()
                return

        if self._over_map:
            if self.map.handle_event(event):
                if self.map.guess_latlon:
                    self.guess = self.map.guess_latlon
            return

        if self.intro >= INTRO_DUR and not self._over_map:
            if not GUESS_BTN_RECT.collidepoint(event.pos if hasattr(event, "pos") else pygame.mouse.get_pos()):
                self.panorama.handle_event(event)

    def _menu(self):
        from src.scenes.menu import MenuScene
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        self.game.change_scene(MenuScene(self.game))

    def _submit(self):
        if not self.guess:
            return
        loc = self.location
        km = haversine_km(self.guess[0], self.guess[1], loc["lat"], loc["lon"])
        score = score_from_distance(km)
        if self.cfg.moving_penalty and self.panorama.movement_units > MOVEMENT_PENALTY_THRESHOLD:
            score = int(score * 0.65)
        score = int(score * self.cfg.score_multiplier)
        bonus = 0
        if self.timer is not None and self.timer > 0:
            bonus = int(self.timer * 2)
            score += bonus
        self.done = True
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        self.game.record_round(loc, self.guess, km, score, time_bonus=bonus)
        from src.scenes.results import ResultsScene
        self.game.change_scene(ResultsScene(self.game, loc, self.guess, km, score, self.round_index, bonus))

    def update(self, dt):
        self.time += dt
        if self.intro < INTRO_DUR:
            self.intro += dt
            t = min(1, self.intro / INTRO_DUR)
            t = 1 - (1 - t) ** 3
            d = ((self._h_tgt - self._h0 + 180) % 360) - 180
            self.panorama.heading = (self._h0 + d * t) % 360
            self.panorama.fov = self._fov0 + (self._fov_tgt - self._fov0) * t
            self.panorama._dirty = True

        mouse = pygame.mouse.get_pos()
        target = 1.0 if self._can_guess and GUESS_BTN_RECT.collidepoint(mouse) else 0.0
        self._guess_hover += (target - self._guess_hover) * min(1.0, dt * 14)

        self.panorama.update(dt)
        self.map.update(dt)

        if self.timer is not None and not self.done:
            self.timer -= dt
            if self.timer <= 0:
                if not self.guess:
                    self.guess = (self.map.center_lat, self.map.center_lon)
                    self.map.set_guess(*self.guess)
                self._submit()

    def draw(self, surface):
        surface.fill((0, 0, 0))
        self.panorama.draw(surface)

        if self.intro < INTRO_DUR:
            a = int(255 * (1 - self.intro / INTRO_DUR))
            f = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            f.fill((0, 0, 0, a))
            surface.blit(f, (0, 0))
            if self.intro < 0.35:
                t = self.game.ui_font.render(self.game.t("loading_location"), True, (255, 255, 255))
                surface.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        total = len(self.game.session_locations)
        draw_round_counter(surface, self.game.ui_font, self.round_index + 1, total)

        if self.round_index > 0 or self.game.session_score > 0:
            draw_session_score(surface, self.game.ui_font, self.game.session_score, self.game.t("pts_short"))

        if self.timer is not None and self.intro >= INTRO_DUR:
            draw_timer_badge(surface, self.game.small_font, self.timer)

        if self.cfg.show_region and self.intro >= INTRO_DUR:
            reg = tr_region(self.game.lang, self.location.get("region", ""))
            draw_compass(surface, self.panorama.heading, x=32, y=HEIGHT - 88)
            hint = self.game.small_font.render(f"{self.game.t('hint_region')}: {reg}", True, (255, 255, 255))
            bg = pygame.Surface((hint.get_width() + 20, hint.get_height() + 10), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 150))
            surface.blit(bg, (88, HEIGHT - 98))
            surface.blit(hint, (98, HEIGHT - 93))
        else:
            draw_compass(surface, self.panorama.heading, x=32, y=HEIGHT - 88)

        if self.panorama.allow_zoom and self.intro >= INTRO_DUR:
            draw_panorama_zoom_controls(
                surface,
                zoom_in_rect=self.panorama.zoom_in_rect(),
                zoom_out_rect=self.panorama.zoom_out_rect(),
                mouse_pos=pygame.mouse.get_pos(),
            )

        self.map.draw(surface)

        if self.intro >= INTRO_DUR * 0.5:
            draw_guess_button(
                surface,
                GUESS_BTN_RECT,
                self.game.t("guess"),
                self.game.ui_font,
                enabled=self._can_guess,
                hover=self._guess_hover,
            )


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.game import Game
