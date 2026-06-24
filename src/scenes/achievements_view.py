import pygame

from src.scenes.menu import MenuScene
from src.settings import COLORS, HEIGHT
from src.systems.achievements import achievement_desc, achievement_title, load_achievements
from src.ui.widgets import AnimatedButton, draw_background, draw_panel


class AchievementsScene:
    def __init__(self, game: "Game"):
        self.game = game
        self.definitions = load_achievements()
        self.time = 0.0
        self.scroll = 0
        self.back_button = AnimatedButton((40, HEIGHT - 78, 180, 46), lambda: self.game.t("back"), self._back)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._back()
            return
        if event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, self.scroll - event.y * 30)
            return
        if self.back_button.handle_event(event):
            return

    def _back(self) -> None:
        self.game.change_scene(MenuScene(self.game))

    def update(self, dt: float) -> None:
        self.time += dt
        self.back_button.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        draw_background(surface, self.time)
        title = self.game.title_font.render(self.game.t("achievements_title"), True, COLORS["accent_light"])
        surface.blit(title, (40, 38))
        unlocked = self.game.achievements
        total = len(self.definitions)
        done = len(unlocked)
        subtitle = self.game.body_font.render(f"{self.game.t('unlocked')}: {done}/{total}", True, COLORS["text"])
        surface.blit(subtitle, (40, 82))

        start_x = 120
        card_h = 96
        gap_y = 20
        max_scroll = max(0, ((len(self.definitions) + 1) // 2) * (card_h + gap_y) - 520)
        self.scroll = max(0, min(self.scroll, max_scroll))
        start_y = 130 - self.scroll
        card_w = 660
        gap_x = 40

        for i, achievement in enumerate(self.definitions):
            col = i % 2
            row = i // 2
            rect = pygame.Rect(
                start_x + col * (card_w + gap_x),
                start_y + row * (card_h + gap_y),
                card_w,
                card_h,
            )
            if rect.bottom < 120 or rect.top > HEIGHT - 100:
                continue
            aid = achievement["id"]
            is_open = aid in unlocked
            fill = (24, 42, 36) if is_open else (20, 26, 34)
            draw_panel(surface, rect, fill=fill)
            icon_color = COLORS["accent_light"] if is_open else COLORS["muted"]
            icon = "★" if is_open else "○"
            title_text = self.game.ui_font.render(
                f"{icon}  {achievement_title(aid, self.game.lang)}",
                True,
                icon_color,
            )
            surface.blit(title_text, (rect.x + 24, rect.y + 18))
            desc = self.game.small_font.render(
                achievement_desc(aid, self.game.lang),
                True,
                COLORS["text"] if is_open else COLORS["muted"],
            )
            surface.blit(desc, (rect.x + 24, rect.y + 54))
            status = self.game.tiny_font.render(
                self.game.t("unlocked") if is_open else self.game.t("locked"),
                True,
                COLORS["accent"] if is_open else COLORS["muted"],
            )
            surface.blit(status, (rect.right - status.get_width() - 20, rect.y + 20))

        self.back_button.draw(surface, self.game.ui_font)


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game import Game
