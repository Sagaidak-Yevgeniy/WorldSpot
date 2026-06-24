import json
from pathlib import Path

from src.paths import DATA
from src.settings import SUCCESS_KM, SUCCESS_SCORE


class RegionStats:
    def __init__(self) -> None:
        self.by_country: dict[str, dict] = {}
        self.by_region: dict[str, dict] = {}

    def _bucket(self, store: dict, key: str) -> dict:
        return store.setdefault(key, {"ok": 0, "n": 0, "km_sum": 0.0})

    def record(self, country: str, region: str, distance_km: float, score: int) -> None:
        success = distance_km < SUCCESS_KM or score >= SUCCESS_SCORE
        for store, key in ((self.by_country, country), (self.by_region, region)):
            b = self._bucket(store, key)
            b["n"] += 1
            b["km_sum"] += distance_km
            if success:
                b["ok"] += 1

    def percent(self, store: dict, key: str) -> int:
        b = store.get(key)
        if not b or b["n"] == 0:
            return 0
        return round(100 * b["ok"] / b["n"])

    def avg_km(self, store: dict, key: str) -> int:
        b = store.get(key)
        if not b or b["n"] == 0:
            return 0
        return round(b["km_sum"] / b["n"])

    def top_and_bottom(self, store: dict, n: int = 3) -> tuple[list, list]:
        items = [(k, self.percent(store, k)) for k in store if store[k]["n"] > 0]
        items.sort(key=lambda x: x[1], reverse=True)
        return items[:n], items[-n:][::-1] if len(items) >= n else items

    def to_dict(self) -> dict:
        return {"by_country": self.by_country, "by_region": self.by_region}

    def load_dict(self, data: dict) -> None:
        self.by_country = data.get("by_country", {})
        self.by_region = data.get("by_region", {})


def load_stats() -> RegionStats:
    path = DATA / "player_stats.json"
    stats = RegionStats()
    if path.exists():
        stats.load_dict(json.loads(path.read_text(encoding="utf-8")))
    return stats


def save_stats(stats: RegionStats) -> None:
    path = DATA / "player_stats.json"
    path.write_text(json.dumps(stats.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
