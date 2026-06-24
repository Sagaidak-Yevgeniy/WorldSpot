import pygame

from src.i18n import tr
from src.scenes.menu import MenuScene
from src.settings import WIDTH
from src.systems.achievements import (
    check_achievements,
    check_session_achievements,
    load_progress,
    save_progress,
    update_records,
)
from src.ui.fonts import load_game_fonts
from src.systems.locations import append_history
from src.systems.stats_engine import save_stats
from src.ui.widgets import AnimatedButton


class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.scene = None
        from src.systems.stats_engine import load_stats

        self.stats = load_stats()
        progress = load_progress()
        self.achievements = set(progress.get("achievements", []))
        self.records = progress.get("records", {"best_session_score": 0, "best_avg_km": None})
        self.total_rounds = int(progress.get("total_rounds", 0))
        self.session_locations: list[dict] = []
        self.session_rounds: list[dict] = []
        self.session_score = 0
        self.session_countries: set[str] = set()
        self.ranked = False
        self.difficulty = "medium"
        self.new_achievements: list[str] = []
        self.lang = "ru"

        fonts = load_game_fonts()
        self.title_font = fonts["title"]
        self.ui_font = fonts["ui"]
        self.body_font = fonts["body"]
        self.small_font = fonts["small"]
        self.tiny_font = fonts["tiny"]
        self.language_button = AnimatedButton(
            (WIDTH - 118, 18, 86, 36),
            lambda: self.lang.upper(),
            self.toggle_language,
            variant="secondary",
        )

        self.change_scene(MenuScene(self))

    def change_scene(self, scene) -> None:
        self.scene = scene

    def toggle_language(self) -> None:
        if self.lang == "ru":
            self.lang = "en"
        elif self.lang == "en":
            self.lang = "kk"
        else:
            self.lang = "ru"

    def t(self, key: str) -> str:
        return tr(self.lang, key)

    def start_session(self, locations: list[dict], ranked: bool, difficulty: str = "medium") -> None:
        self.session_locations = locations
        self.session_rounds = []
        self.session_score = 0
        self.session_countries = set()
        self.ranked = ranked
        self.difficulty = difficulty
        self.new_achievements = []

    def _save_progress(self) -> None:
        save_progress(
            {
                "achievements": sorted(self.achievements),
                "records": self.records,
                "total_rounds": self.total_rounds,
            }
        )

    def record_round(
        self,
        location: dict,
        guess,
        km: float,
        score: int,
        *,
        time_bonus: int = 0,
    ) -> None:
        country = location["country"]
        region = location.get("region", "-")
        self.stats.record(country, region, km, score)
        save_stats(self.stats)
        self.session_score += score
        self.session_countries.add(country)
        self.session_rounds.append(
            {
                "country": country,
                "region": region,
                "km": round(km),
                "score": score,
                "time_bonus": time_bonus,
            }
        )
        self.total_rounds += 1
        for aid in check_achievements(
            self.achievements,
            score=score,
            countries=self.session_countries,
            stats=self.stats,
            km=km,
            total_rounds=self.total_rounds,
        ):
            self.achievements.add(aid)
            self.new_achievements.append(aid)
        self._save_progress()

    def finish_session(self) -> None:
        append_history("ranked" if self.ranked else "casual", self.session_rounds, self.session_score)
        self.records = update_records(self.records, self.session_score, self.session_rounds)
        for aid in check_session_achievements(self.achievements, rounds_played=len(self.session_rounds)):
            self.achievements.add(aid)
            self.new_achievements.append(aid)
        self._save_progress()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            self.toggle_language()
            return
        if self.language_button.handle_event(event):
            return
        if self.scene:
            self.scene.handle_event(event)

    def update(self, dt: float) -> None:
        self.language_button.update(dt)
        if self.scene:
            self.scene.update(dt)

    def draw(self) -> None:
        if self.scene:
            self.scene.draw(self.screen)
        from src.scenes.round import RoundScene

        if not isinstance(self.scene, RoundScene):
            self.language_button.draw(self.screen, self.small_font)
