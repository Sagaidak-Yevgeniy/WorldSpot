import json

from src.i18n import tr_achievement
from src.paths import DATA

_DEFAULT_ACHIEVEMENTS = [
    {"id": "first_5000", "title": "Идеально!", "desc": "5000 очков в раунде"},
    {"id": "globe_trotter", "title": "Глобус", "desc": "5 разных стран за сессию"},
    {"id": "region_ace", "title": "Мастер региона", "desc": "80% в любом регионе"},
    {"id": "marathon", "title": "Марафонец", "desc": "Завершить 5 раундов"},
    {"id": "sharp_eye", "title": "Острый глаз", "desc": "Ближе 50 км"},
    {"id": "world_traveler", "title": "Путешественник", "desc": "10 раундов суммарно"},
]


def load_achievements() -> list[dict]:
    path = DATA / "achievements.json"
    if not path.exists():
        return list(_DEFAULT_ACHIEVEMENTS)
    try:
        return json.loads(path.read_text(encoding="utf-8"))["achievements"]
    except (json.JSONDecodeError, KeyError):
        return list(_DEFAULT_ACHIEVEMENTS)


def achievement_title(aid: str, lang: str = "ru") -> str:
    localized = tr_achievement(lang, aid, "title")
    if not localized.startswith("ach_"):
        return localized
    for ach in load_achievements():
        if ach["id"] == aid:
            return ach["title"]
    return aid


def achievement_desc(aid: str, lang: str = "ru") -> str:
    localized = tr_achievement(lang, aid, "desc")
    if not localized.startswith("ach_"):
        return localized
    for ach in load_achievements():
        if ach["id"] == aid:
            return ach["desc"]
    return ""


def load_progress() -> dict:
    path = DATA / "player_progress.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "achievements": [],
        "records": {"best_session_score": 0, "best_avg_km": None},
        "total_rounds": 0,
    }


def save_progress(data: dict) -> None:
    path = DATA / "player_progress.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def check_achievements(
    unlocked: set[str],
    *,
    score: int,
    countries: set[str],
    stats,
    km: float | None = None,
    session_round: int | None = None,
    total_rounds: int = 0,
) -> list[str]:
    new: list[str] = []
    if "first_5000" not in unlocked and score >= 5000:
        new.append("first_5000")
    if "globe_trotter" not in unlocked and len(countries) >= 5:
        new.append("globe_trotter")
    best, _ = stats.top_and_bottom(stats.by_region, 1)
    if "region_ace" not in unlocked and best and best[0][1] >= 80:
        new.append("region_ace")
    if "sharp_eye" not in unlocked and km is not None and km < 50:
        new.append("sharp_eye")
    if "world_traveler" not in unlocked and total_rounds >= 10:
        new.append("world_traveler")
    return new


def check_session_achievements(unlocked: set[str], *, rounds_played: int) -> list[str]:
    new: list[str] = []
    if "marathon" not in unlocked and rounds_played >= 5:
        new.append("marathon")
    return new


def update_records(records: dict, session_score: int, rounds: list[dict]) -> dict:
    records = dict(records)
    if session_score > records.get("best_session_score", 0):
        records["best_session_score"] = session_score
    if rounds:
        avg_km = round(sum(r["km"] for r in rounds) / len(rounds))
        best = records.get("best_avg_km")
        if best is None or avg_km < best:
            records["best_avg_km"] = avg_km
    return records
