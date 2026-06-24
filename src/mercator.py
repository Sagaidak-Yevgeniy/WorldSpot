"""Web Mercator projection (used by OpenStreetMap)."""

from __future__ import annotations

import math

# Web Mercator is only valid inside these bounds.
MAX_MERCATOR_LAT = 85.0511287798


def clamp_lat(lat: float) -> float:
    if not math.isfinite(lat):
        return 0.0
    return max(-MAX_MERCATOR_LAT, min(MAX_MERCATOR_LAT, lat))


def normalize_lon(lon: float) -> float:
    if not math.isfinite(lon):
        return 0.0
    return ((lon + 180.0) % 360.0) - 180.0


def latlon_to_world_pixel(lat: float, lon: float, zoom: int) -> tuple[float, float]:
    lat = clamp_lat(lat)
    lon = normalize_lon(lon)
    scale = 256 * (2**zoom)
    x = (lon + 180.0) / 360.0 * scale
    sin_lat = math.sin(math.radians(lat))
    sin_lat = max(-0.999999, min(0.999999, sin_lat))
    y = (0.5 - math.log((1 + sin_lat) / (1 - sin_lat)) / (4 * math.pi)) * scale
    return x, y


def world_pixel_to_latlon(x: float, y: float, zoom: int) -> tuple[float, float]:
    scale = 256 * (2**zoom)
    lon = x / scale * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / scale)))
    lat = clamp_lat(math.degrees(lat_rad))
    return lat, normalize_lon(lon)
