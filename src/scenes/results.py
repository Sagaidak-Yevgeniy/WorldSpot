import pygame

from src.i18n import tr_country, tr_region
from src.settings import COLORS, WIDTH, HEIGHT
from src.systems.difficulty import get_difficulty
from src.ui.geoguessr import (
    GUESS_BTN_RECT,
    draw_guess_button,
    draw_result_panel,
    draw_round_counter,
    draw_session_score,
    fmt_distance,
)
from src.ui.osm_map_view import OsmResultMapView


class ResultsScene:
    REVEAL_DUR = 1.8

    def __init__(self, game, location, guess, distance_km, score, round_index, time_bonus=0):
        self.game = game
        self.location = location
        self.guess = guess
        self.km = distance_km
        self.score = score
        self.round_index = round_index
        self.bonus = time_bonus
        self.time = 0.0
        self._btn_hover = 0.0
        self.cfg = get_difficulty(game.difficulty)
        truth = (location["lat"], location["lon"])
        map_rect = pygame.Rect(32, 150, WIDTH - 64, HEIGHT - 240)
        self.map = OsmResultMapView(map_rect, guess, truth, game.small_font)
        self.map.set_screen_size((WIDTH, HEIGHT))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._menu()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_n):
                self._next()
            return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if GUESS_BTN_RECT.collidepoint(event.pos) and self.time >= 0.4:
                self._next()

    def _menu(self):
        from src.scenes.menu import MenuScene
        self.game.change_scene(MenuScene(self.game))

    def _next(self):
        n = self.round_index + 1
        if n < len(self.game.session_locations):
            from src.scenes.round import RoundScene
            self.game.change_scene(RoundScene(self.game, self.game.session_locations[n], n))
        else:
            from src.scenes.summary import SummaryScene
            self.game.finish_session()
            self.game.change_scene(SummaryScene(self.game))

    def update(self, dt):
        self.time += dt
        self.map.update(dt)
        mouse = pygame.mouse.get_pos()
        t = 1.0 if GUESS_BTN_RECT.collidepoint(mouse) else 0.0
        self._btn_hover += (t - self._btn_hover) * min(1.0, dt * 14)

    def draw(self, surface):
        surface.fill(COLORS["bg_dark"])
        self.map.draw(surface)

        total = len(self.game.session_locations)
        draw_round_counter(surface, self.game.ui_font, self.round_index + 1, total)
        draw_session_score(surface, self.game.ui_font, self.game.session_score, self.game.t("pts_short"))

        dist = fmt_distance(self.km, m_label=self.game.t("m_short"), km_label=self.game.t("km"))
        loc_name = ""
        if self.cfg.show_country_after:
            loc_name = (
                f"{tr_country(self.game.lang, self.location['country'])}"
                f" — {tr_region(self.game.lang, self.location.get('region', ''))}"
            )

        t = min(1.0, self.time / self.REVEAL_DUR)
        ease = 1 - (1 - t) ** 3
        anim_score = int(self.score * ease)

        draw_result_panel(
            surface,
            distance=dist,
            score=self.score,
            location_name=loc_name,
            title_font=self.game.title_font,
            ui_font=self.game.ui_font,
            small_font=self.game.small_font,
            anim_score=anim_score,
        )

        label = self.game.t("result_next") if self.round_index + 1 < total else self.game.t("see_results")
        draw_guess_button(
            surface,
            GUESS_BTN_RECT,
            label,
            self.game.ui_font,
            enabled=self.time >= 0.3,
            hover=self._btn_hover,
        )


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.game import Game
