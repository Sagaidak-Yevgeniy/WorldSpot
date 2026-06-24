import pygame

from src.settings import COLORS, HEIGHT, WIDTH
from src.ui.geoguessr import GUESS_BTN_RECT, draw_guess_button, draw_menu_hero
from src.ui.widgets import AnimatedButton


class MenuScene:
    def __init__(self, game: "Game"):
        self.game = game
        self.selected = 0
        self.time = 0.0
        self.items = [
            ("classic", self._play),
            ("ranked", self._ranked),
            ("stats", self._stats),
            ("history", self._history),
            ("achievements", self._achievements),
            ("exit", self._exit),
        ]
        self._side_btns = self._make_side_buttons()
        self._play_hover = 0.0

    def _make_side_buttons(self):
        x, w, h, gap = WIDTH // 2 + 220, 280, 44, 10
        y0 = 320
        return [
            AnimatedButton((x, y0 + i * (h + gap), w, h), lambda k=k: self.game.t(k), act, variant="secondary")
            for i, (k, act) in enumerate(self.items[2:])
        ]

    def _play(self):
        from src.scenes.difficulty_select import DifficultyScene
        self.game.change_scene(DifficultyScene(self.game, ranked=False))

    def _ranked(self):
        from src.scenes.difficulty_select import DifficultyScene
        self.game.change_scene(DifficultyScene(self.game, ranked=True))

    def _stats(self):
        from src.scenes.stats import StatsScene
        self.game.change_scene(StatsScene(self.game))

    def _history(self):
        from src.scenes.history import HistoryScene
        self.game.change_scene(HistoryScene(self.game))

    def _achievements(self):
        from src.scenes.achievements_view import AchievementsScene
        self.game.change_scene(AchievementsScene(self.game))

    def _exit(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_event(self, event):
        play_rect = pygame.Rect(WIDTH // 2 - 300, 300, 480, 200)
        ranked_rect = pygame.Rect(WIDTH // 2 - 300, 520, 480, 72)

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._play()
            elif event.key == pygame.K_ESCAPE:
                self._exit()
            return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if play_rect.collidepoint(event.pos):
                self._play()
                return
            if ranked_rect.collidepoint(event.pos):
                self._ranked()
                return

        for b in self._side_btns:
            if b.handle_event(event):
                return

    def update(self, dt):
        self.time += dt
        mouse = pygame.mouse.get_pos()
        play_rect = pygame.Rect(WIDTH // 2 - 300, 300, 480, 200)
        t = 1.0 if play_rect.collidepoint(mouse) else 0.0
        self._play_hover += (t - self._play_hover) * min(1.0, dt * 12)
        for b in self._side_btns:
            b.update(dt)

    def draw(self, surface):
        draw_menu_hero(surface, self.game.title_font, self.game.body_font, "WorldSpot", self.game.t("menu_tagline"))

        play_card = pygame.Rect(WIDTH // 2 - 300, 300, 480, 200)
        h = play_card.collidepoint(pygame.mouse.get_pos())
        fill = (28, 32, 40) if not h else (34, 40, 50)
        pygame.draw.rect(surface, (0, 0, 0), play_card.move(0, 5), border_radius=16)
        pygame.draw.rect(surface, fill, play_card, border_radius=16)
        pygame.draw.rect(surface, COLORS["brand"] if h else (70, 78, 92), play_card, 2, border_radius=16)

        t1 = self.game.title_font.render(self.game.t("classic"), True, (255, 255, 255))
        surface.blit(t1, t1.get_rect(midleft=(play_card.x + 36, play_card.centery - 20)))
        t2 = self.game.small_font.render(self.game.t("classic_subtitle"), True, COLORS["text_dim"])
        surface.blit(t2, t2.get_rect(midleft=(play_card.x + 36, play_card.centery + 22)))
        arrow = self.game.title_font.render("→", True, COLORS["accent"])
        surface.blit(arrow, arrow.get_rect(center=(play_card.right - 48, play_card.centery)))

        ranked_card = pygame.Rect(WIDTH // 2 - 300, 520, 480, 72)
        rh = ranked_card.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(surface, (24, 28, 34) if not rh else (32, 38, 46), ranked_card, border_radius=12)
        pygame.draw.rect(surface, (60, 68, 80), ranked_card, 1, border_radius=12)
        rt = self.game.ui_font.render(self.game.t("ranked"), True, (255, 255, 255))
        surface.blit(rt, rt.get_rect(midleft=(ranked_card.x + 28, ranked_card.centery)))
        rs = self.game.small_font.render(self.game.t("ranked_subtitle"), True, COLORS["text_dim"])
        surface.blit(rs, rs.get_rect(midright=(ranked_card.right - 28, ranked_card.centery)))

        for i, b in enumerate(self._side_btns):
            b.draw(surface, self.game.small_font, selected=False)

        foot = self.game.tiny_font.render(self.game.t("menu_footer"), True, COLORS["text_dim"])
        surface.blit(foot, foot.get_rect(center=(WIDTH // 2, HEIGHT - 28)))


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.game import Game
