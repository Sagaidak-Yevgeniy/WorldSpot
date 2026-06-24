import pygame

from src.i18n import tr_country
from src.scenes.menu import MenuScene
from src.settings import COLORS, WIDTH, HEIGHT
from src.systems.achievements import achievement_title
from src.ui.geoguessr import GUESS_BTN_RECT, draw_guess_button, fmt_score


class SummaryScene:
    def __init__(self, game: "Game"):
        self.game = game
        self.time = 0.0
        self._btn_hover = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
            self._to_menu()
            return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if GUESS_BTN_RECT.collidepoint(event.pos):
                self._to_menu()

    def _to_menu(self) -> None:
        self.game.change_scene(MenuScene(self.game))

    def update(self, dt: float) -> None:
        self.time += dt
        mouse = pygame.mouse.get_pos()
        t = 1.0 if GUESS_BTN_RECT.collidepoint(mouse) else 0.0
        self._btn_hover += (t - self._btn_hover) * min(1.0, dt * 14)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLORS["bg_dark"])
        grad = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y / HEIGHT
            c = int(12 + t * 10)
            grad.fill((c, c + 2, c + 5), (0, y, WIDTH, 1))
        surface.blit(grad, (0, 0))

        t = min(1.0, self.time / 1.5)
        ease = 1 - (1 - t) ** 3
        shown = int(self.game.session_score * ease)

        title = self.game.title_font.render(self.game.t("game_complete"), True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 100)))

        score_text = fmt_score(shown)
        big = self.game.title_font.render(score_text, True, COLORS["accent"])
        surface.blit(big, big.get_rect(center=(WIDTH // 2, 175)))
        pts = self.game.ui_font.render(self.game.t("pts_short"), True, COLORS["text_dim"])
        surface.blit(pts, pts.get_rect(midtop=(WIDTH // 2, 220)))

        n = len(self.game.session_rounds)
        bar_w = min(900, WIDTH - 120)
        x0 = WIDTH // 2 - bar_w // 2
        y = 280
        slot = bar_w // max(n, 1)

        for i, r in enumerate(self.game.session_rounds):
            cx = x0 + i * slot + slot // 2
            pct = r["score"] / 5000.0
            h = int(80 + 100 * pct)
            col = COLORS["accent"] if r["score"] >= 4000 else COLORS["accent_dark"] if r["score"] >= 2000 else COLORS["btn_disabled"]
            pygame.draw.rect(surface, col, (cx - 28, y + 120 - h, 56, h), border_radius=6)
            s = self.game.small_font.render(str(r["score"]), True, (255, 255, 255))
            surface.blit(s, s.get_rect(center=(cx, y + 130)))
            c = self.game.tiny_font.render(tr_country(self.game.lang, r["country"])[:8], True, COLORS["text_dim"])
            surface.blit(c, c.get_rect(center=(cx, y + 155)))

        y = 460
        records = self.game.records
        if records.get("best_session_score", 0) > 0:
            line = f"{self.game.t('best_session')}: {fmt_score(records['best_session_score'])}"
            surface.blit(self.game.small_font.render(line, True, COLORS["accent_light"]), (WIDTH // 2 - 200, y))
            y += 28

        if self.game.new_achievements:
            surface.blit(self.game.ui_font.render(self.game.t("new_achievements"), True, COLORS["text"]), (WIDTH // 2 - 200, y))
            y += 32
            for aid in self.game.new_achievements:
                title = achievement_title(aid, self.game.lang)
                surface.blit(self.game.small_font.render(f"★ {title}", True, COLORS["accent_light"]), (WIDTH // 2 - 200, y))
                y += 24

        draw_guess_button(
            surface,
            GUESS_BTN_RECT,
            self.game.t("return_menu"),
            self.game.ui_font,
            enabled=True,
            hover=self._btn_hover,
        )


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.game import Game
