"""Choose difficulty — GeoGuessr game setup screen."""

from __future__ import annotations

import pygame

from src.scenes.menu import MenuScene
from src.settings import COLORS, HEIGHT, WIDTH
from src.systems.difficulty import ORDER, get_difficulty
from src.ui.geoguessr import GUESS_BTN_RECT, draw_guess_button, draw_menu_hero
from src.ui.widgets import AnimatedButton


class DifficultyScene:
    def __init__(self, game: "Game", *, ranked: bool = False):
        self.game = game
        self.ranked = ranked
        self.selected = 1
        self.time = 0.0
        self.cards: list[pygame.Rect] = []
        self._play_hover = 0.0
        self._layout()
        self.back_btn = AnimatedButton((40, HEIGHT - 70, 120, 44), lambda: self.game.t("back"), self._back, variant="secondary")

    def _layout(self):
        self.cards = []
        cw, ch, gap = 300, 140, 16
        total_w = len(ORDER) * cw + (len(ORDER) - 1) * gap
        x0 = WIDTH // 2 - total_w // 2
        y = 260
        for i in range(len(ORDER)):
            self.cards.append(pygame.Rect(x0 + i * (cw + gap), y, cw, ch))

    def _back(self):
        self.game.change_scene(MenuScene(self.game))

    def _play(self):
        from src.scenes.round import start_game
        start_game(self.game, difficulty=ORDER[self.selected], ranked=self.ranked)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._back()
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % len(ORDER)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % len(ORDER)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._play()
            return
        if event.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.cards):
                if r.collidepoint(event.pos):
                    self.selected = i
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for i, r in enumerate(self.cards):
                if r.collidepoint(event.pos):
                    self.selected = i
                    self._play()
                    return
            if GUESS_BTN_RECT.collidepoint(event.pos):
                self._play()
                return
        if self.back_btn.handle_event(event):
            return

    def update(self, dt):
        self.time += dt
        self.back_btn.update(dt)
        mouse = pygame.mouse.get_pos()
        t = 1.0 if GUESS_BTN_RECT.collidepoint(mouse) else 0.0
        self._play_hover += (t - self._play_hover) * min(1.0, dt * 14)

    def draw(self, surface):
        mode = self.game.t("ranked") if self.ranked else self.game.t("classic")
        draw_menu_hero(surface, self.game.title_font, self.game.body_font, self.game.t("difficulty_pick"), mode)

        mouse = pygame.mouse.get_pos()
        for i, (diff_id, card) in enumerate(zip(ORDER, self.cards)):
            cfg = get_difficulty(diff_id)
            sel = i == self.selected
            hov = card.collidepoint(mouse)
            fill = (22, 26, 32)
            if sel:
                fill = (18, 48, 40)
            elif hov:
                fill = (30, 34, 42)
            pygame.draw.rect(surface, (0, 0, 0), card.move(0, 4), border_radius=12)
            pygame.draw.rect(surface, fill, card, border_radius=12)
            border = COLORS["accent"] if sel else (60, 68, 80)
            pygame.draw.rect(surface, border, card, 3 if sel else 1, border_radius=12)

            surface.blit(
                self.game.ui_font.render(self.game.t(f"diff_{diff_id}"), True, (255, 255, 255)),
                (card.x + 20, card.y + 18),
            )
            desc = self.game.t(f"diff_{diff_id}_desc")
            y = card.y + 52
            for line in _wrap(desc, self.game.small_font, card.width - 36)[:2]:
                surface.blit(self.game.small_font.render(line, True, COLORS["text_dim"]), (card.x + 20, y))
                y += 20

            meta = f"{cfg.rounds} {self.game.t('rounds').lower()}"
            if self.ranked and cfg.timer_ranked:
                meta += f" · {cfg.timer_ranked}s"
            surface.blit(self.game.tiny_font.render(meta, True, COLORS["accent_light"]), (card.x + 20, card.bottom - 26))

        self.back_btn.draw(surface, self.game.small_font)
        draw_guess_button(
            surface, GUESS_BTN_RECT, self.game.t("play"), self.game.ui_font,
            enabled=True, hover=self._play_hover,
        )


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
    return lines


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.game import Game
