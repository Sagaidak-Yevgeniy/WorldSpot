import pygame

from src.i18n import tr_country, tr_region
from src.scenes.menu import MenuScene
from src.settings import COLORS, HEIGHT, WIDTH
from src.systems.locations import load_history
from src.ui.widgets import AnimatedButton, draw_background, draw_panel


class HistoryScene:
    def __init__(self, game: "Game"):
        self.game = game
        self.games = list(reversed(load_history()))
        self.selected = 0
        self.detail = False
        self.time = 0.0
        self.back_button = AnimatedButton((40, HEIGHT - 78, 180, 46), lambda: self.game.t("back"), self._back)
        self.detail_button = AnimatedButton(
            (WIDTH // 2 - 140, HEIGHT - 78, 280, 46),
            lambda: self.game.t("back"),
            self._close_detail,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._close_detail() if self.detail else self._back()
                return
            if not self.games:
                self._back()
                return
            if self.detail:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._close_detail()
                return
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.games)
                return
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.games)
                return
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.detail = True
                return

        if self.detail:
            self.detail_button.handle_event(event)
            return

        if self.back_button.handle_event(event):
            return
        if event.type == pygame.MOUSEMOTION:
            self._select_from_mouse(event.pos)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            index = self._index_at(event.pos)
            if index is not None:
                self.selected = index
                self.detail = True

    def _back(self) -> None:
        self.game.change_scene(MenuScene(self.game))

    def _close_detail(self) -> None:
        self.detail = False

    def _entry_rect(self, index: int) -> pygame.Rect:
        return pygame.Rect(210, 166 + index * 58, 1180, 46)

    def _index_at(self, pos: tuple[int, int]) -> int | None:
        for i in range(min(len(self.games), 10)):
            if self._entry_rect(i).collidepoint(pos):
                return i
        return None

    def _select_from_mouse(self, pos: tuple[int, int]) -> None:
        index = self._index_at(pos)
        if index is not None:
            self.selected = index

    def update(self, dt: float) -> None:
        self.time += dt
        self.back_button.update(dt)
        self.detail_button.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        draw_background(surface, self.time)
        title = self.game.title_font.render(self.game.t("history_title"), True, COLORS["accent_light"])
        surface.blit(title, (40, 38))

        if not self.games:
            card = pygame.Rect(260, 190, 1080, 240)
            draw_panel(surface, card)
            text = self.game.ui_font.render(self.game.t("no_history"), True, COLORS["muted"])
            surface.blit(text, text.get_rect(center=card.center))
            self.back_button.draw(surface, self.game.ui_font)
            return

        if self.detail:
            self._draw_detail(surface)
            self.detail_button.draw(surface, self.game.ui_font)
            return

        surface.blit(self.game.small_font.render(self.game.t("menu_controls"), True, COLORS["muted"]), (40, 80))
        for i, item in enumerate(self.games[:10]):
            rect = self._entry_rect(i)
            selected = i == self.selected
            fill = (29, 41, 53) if selected else (18, 23, 30)
            draw_panel(surface, rect, fill=fill)
            mode_key = "ranked_mode" if item["mode"] == "ranked" else "classic_mode"
            label = f"{item['date']}  |  {self.game.t(mode_key)}  |  {item['total_score']} {self.game.t('points')}"
            color = COLORS["accent_light"] if selected else COLORS["text"]
            surface.blit(self.game.ui_font.render(label, True, color), (rect.x + 22, rect.y + 12))

        self.back_button.draw(surface, self.game.ui_font)

    def _draw_detail(self, surface: pygame.Surface) -> None:
        item = self.games[self.selected]
        card = pygame.Rect(190, 136, 1220, 620)
        draw_panel(surface, card)
        mode_key = "ranked_mode" if item["mode"] == "ranked" else "classic_mode"
        header = f"{item['date']}  |  {self.game.t(mode_key)}  |  {item['total_score']} {self.game.t('points')}"
        surface.blit(self.game.ui_font.render(header, True, COLORS["accent_light"]), (card.x + 36, card.y + 32))
        y = card.y + 86
        for i, round_data in enumerate(item.get("rounds", []), 1):
            bonus = f" (+{round_data['time_bonus']})" if round_data.get("time_bonus") else ""
            line = (
                f"{i}. {tr_country(self.game.lang, round_data['country'])} "
                f"({tr_region(self.game.lang, round_data.get('region', '-'))}) — "
                f"{round_data['score']} {self.game.t('points')}, "
                f"{round_data['km']} {self.game.t('km')}{bonus}"
            )
            surface.blit(self.game.small_font.render(line, True, COLORS["text"]), (card.x + 36, y))
            y += 30


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game import Game
