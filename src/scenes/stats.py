import pygame

from src.i18n import tr_country, tr_region
from src.scenes.menu import MenuScene
from src.settings import COLORS, HEIGHT, WIDTH
from src.systems.locations import load_history
from src.ui.widgets import AnimatedButton, draw_background, draw_panel


class StatsScene:
    def __init__(self, game: "Game"):
        self.game = game
        self.time = 0.0
        self.back_button = AnimatedButton((40, HEIGHT - 78, 180, 46), lambda: self.game.t("back"), self._back)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._back()
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
        stats = self.game.stats
        title = self.game.title_font.render(self.game.t("stats_title"), True, COLORS["accent_light"])
        surface.blit(title, (40, 36))
        subtitle = self.game.small_font.render(self.game.t("stats_subtitle"), True, COLORS["muted"])
        surface.blit(subtitle, (40, 76))

        left = pygame.Rect(40, 120, 680, 640)
        right = pygame.Rect(760, 120, 800, 640)
        draw_panel(surface, left)
        draw_panel(surface, right)
        self._draw_country_stats(surface, left, stats)
        self._draw_region_stats(surface, right, stats)
        self._draw_progress_chart(surface, right.x + 34, right.y + 318)
        self.back_button.draw(surface, self.game.ui_font)

    def _draw_country_stats(self, surface: pygame.Surface, rect: pygame.Rect, stats) -> None:
        x = rect.x + 34
        y = rect.y + 30
        surface.blit(self.game.ui_font.render(self.game.t("by_country"), True, COLORS["text"]), (x, y))
        y += 42
        countries = sorted(
            stats.by_country.items(),
            key=lambda item: stats.percent(stats.by_country, item[0]),
            reverse=True,
        )
        if not countries:
            surface.blit(self.game.small_font.render(self.game.t("no_data"), True, COLORS["muted"]), (x, y))
            return
        for country, data in countries[:12]:
            pct = stats.percent(stats.by_country, country)
            avg = stats.avg_km(stats.by_country, country)
            self._draw_bar(surface, x, y, 330, pct)
            label = (
                f"{tr_country(self.game.lang, country)}  {pct}%  n={data['n']}  "
                f"{self.game.t('avg')} {avg} {self.game.t('km')}"
            )
            surface.blit(self.game.small_font.render(label, True, COLORS["text"]), (x + 350, y - 2))
            y += 36

    def _draw_region_stats(self, surface: pygame.Surface, rect: pygame.Rect, stats) -> None:
        x = rect.x + 34
        y = rect.y + 30
        best, worst = stats.top_and_bottom(stats.by_region, 5)
        surface.blit(self.game.ui_font.render(self.game.t("best_regions"), True, COLORS["text"]), (x, y))
        y += 42
        if not best:
            surface.blit(self.game.small_font.render(self.game.t("no_data"), True, COLORS["muted"]), (x, y))
            y += 30
        for region, pct in best:
            self._draw_bar(surface, x, y, 260, pct)
            surface.blit(self.game.small_font.render(f"{tr_region(self.game.lang, region)}: {pct}%", True, COLORS["accent_light"]), (x + 282, y - 2))
            y += 34

        y += 18
        surface.blit(self.game.ui_font.render(self.game.t("hard_regions"), True, COLORS["text"]), (x, y))
        y += 42
        for region, pct in worst:
            self._draw_bar(surface, x, y, 260, pct, color=COLORS["guess"])
            surface.blit(self.game.small_font.render(f"{tr_region(self.game.lang, region)}: {pct}%", True, COLORS["text"]), (x + 282, y - 2))
            y += 34

    def _draw_bar(self, surface: pygame.Surface, x: int, y: int, width: int, pct: int, *, color=None) -> None:
        color = color or COLORS["accent"]
        pygame.draw.rect(surface, (35, 43, 54), (x, y, width, 16), border_radius=8)
        pygame.draw.rect(surface, color, (x, y, int(width * pct / 100), 16), border_radius=8)

    def _draw_progress_chart(self, surface: pygame.Surface, x: int, y: int) -> None:
        games = load_history()[-10:]
        surface.blit(self.game.ui_font.render(self.game.t("progress"), True, COLORS["text"]), (x, y))
        y += 42
        if not games:
            surface.blit(self.game.small_font.render(self.game.t("no_history"), True, COLORS["muted"]), (x, y))
            return
        chart_w, chart_h = 680, 190
        pygame.draw.rect(surface, (18, 23, 30), (x, y, chart_w, chart_h), border_radius=8)
        max_score = max(g["total_score"] for g in games) or 1
        bar_w = max(24, chart_w // len(games) - 10)
        for i, game in enumerate(games):
            h = int((chart_h - 24) * game["total_score"] / max_score)
            bx = x + 12 + i * (bar_w + 8)
            by = y + chart_h - h - 12
            color = COLORS["accent_light"] if game["mode"] == "ranked" else COLORS["accent"]
            pygame.draw.rect(surface, color, (bx, by, bar_w, h), border_radius=6)
            surface.blit(self.game.small_font.render(game["date"][5:], True, COLORS["muted"]), (bx, y + chart_h + 8))


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game import Game
