import json
import random
from datetime import date

from src.paths import ASSETS, DATA


def _panorama_entries(location: dict) -> list[dict]:
    if "panoramas" in location:
        return location["panoramas"]
    if pan := location.get("panorama"):
        return [{"file": pan}]
    return []


def _has_local_panorama(entry: dict) -> bool:
    return (ASSETS / "panoramas" / entry["file"]).is_file()


def load_locations() -> list[dict]:
    data = json.loads((DATA / "locations.json").read_text(encoding="utf-8"))
    return data["locations"]


def available_locations() -> list[dict]:
    """Locations with at least one downloaded panorama on disk."""
    result = []
    for loc in load_locations():
        entries = _panorama_entries(loc)
        if any(_has_local_panorama(e) for e in entries):
            result.append(loc)
    return result


def pick_random_panorama(location: dict) -> dict | None:
    """Pick a random panorama file that exists locally, or any entry if none downloaded."""
    entries = _panorama_entries(location)
    if not entries:
        return None
    local = [e for e in entries if _has_local_panorama(e)]
    pool = local or entries
    return random.choice(pool)


def prepare_location(location: dict) -> dict:
    """Random view angle + random photo variant for GeoGuessr-like variety."""
    loc = dict(location)
    pan = pick_random_panorama(location)
    if pan:
        loc["panorama"] = pan["file"]
        loc["panorama_commons"] = pan.get("commons", "")
    loc["heading"] = random.uniform(0.0, 360.0)
    loc["pitch"] = random.uniform(-18.0, 18.0)
    loc["fov"] = random.uniform(72.0, 98.0)
    loc["intro_spin"] = random.uniform(-25.0, 25.0)
    return loc


def pick_round(locations: list[dict] | None = None, count: int = 5) -> list[dict]:
    pool = list(locations if locations is not None else available_locations())
    if not pool:
        pool = load_locations()
    random.shuffle(pool)
    chosen = pool[: min(count, len(pool))]
    return [prepare_location(loc) for loc in chosen]


def load_history() -> list[dict]:
    path = DATA / "history.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("games", [])


def append_history(mode: str, rounds: list[dict], total_score: int) -> None:
    path = DATA / "history.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {"games": []}
    data["games"].append(
        {
            "date": date.today().isoformat(),
            "mode": mode,
            "total_score": total_score,
            "rounds": rounds,
        }
    )
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
