import math

from src.settings import MAX_SCORE


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p = math.pi / 180.0
    a = (
        math.sin((lat2 - lat1) * p / 2) ** 2
        + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))


def score_from_distance(km: float, max_score: int = MAX_SCORE) -> int:
    """GeoGuessr formula: 5000 * exp(-distance_m / 1492.07)."""
    from src.settings import SCORE_DECAY_M

    meters = km * 1000.0
    if meters <= 25:
        return max_score
    return max(0, int(round(max_score * math.exp(-meters / SCORE_DECAY_M))))


def pixel_to_latlon(mx: int, my: int, map_rect) -> tuple[float, float]:
    x = (mx - map_rect.x) / map_rect.width
    y = (my - map_rect.y) / map_rect.height
    x = max(0.0, min(1.0, x))
    y = max(0.0, min(1.0, y))
    lon = x * 360.0 - 180.0
    lat = 90.0 - y * 180.0
    return lat, lon


def latlon_to_pixel(lat: float, lon: float, map_rect) -> tuple[int, int]:
    x = (lon + 180.0) / 360.0
    y = (90.0 - lat) / 180.0
    px = int(map_rect.x + x * map_rect.width)
    py = int(map_rect.y + y * map_rect.height)
    return px, py
