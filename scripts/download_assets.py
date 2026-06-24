#!/usr/bin/env python3
"""Download high-quality panorama photos from Wikimedia Commons (free, one-time)."""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PANORAMAS = ROOT / "assets" / "panoramas"
WEB_PANORAMAS = ROOT / "web" / "public" / "panoramas"
WEB_DATA = ROOT / "web" / "public" / "data"
LOCATIONS = ROOT / "data" / "locations.json"
USER_AGENT = "WorldSpot/1.0 (educational geography game; offline cache)"
# 2560 px wide — sharp on fullscreen panorama.
DOWNLOAD_WIDTH = 2560


def load_panorama_catalog() -> list[tuple[str, str]]:
    """Return (local_filename, commons_title) pairs from locations.json."""
    data = json.loads(LOCATIONS.read_text(encoding="utf-8"))
    seen: set[str] = set()
    items: list[tuple[str, str]] = []
    for loc in data["locations"]:
        for pan in loc.get("panoramas", []):
            fname = pan["file"]
            commons = pan.get("commons")
            if not commons or fname in seen:
                continue
            seen.add(fname)
            items.append((fname, commons))
    return items


def commons_thumb_url(filename: str, width: int = DOWNLOAD_WIDTH) -> str | None:
    title = f"File:{filename}"
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": str(width),
            "format": "json",
        }
    )
    api = f"https://commons.wikimedia.org/w/api.php?{params}"
    req = urllib.request.Request(api, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    page = next(iter(data["query"]["pages"].values()))
    if "missing" in page:
        return None
    info = page.get("imageinfo", [{}])[0]
    return info.get("thumburl") or info.get("url")


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  {dest.name} ...", end=" ", flush=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())
    kb = dest.stat().st_size // 1024
    print(f"OK ({kb} KB)")


def main() -> None:
    catalog = load_panorama_catalog()
    print(f"WorldSpot — загрузка {len(catalog)} панорам ({DOWNLOAD_WIDTH}px, Wikimedia Commons)")
    ok, skip, fail = 0, 0, 0
    for name, commons_name in catalog:
        dest = PANORAMAS / name
        if dest.exists() and dest.stat().st_size > 50_000:
            print(f"  {name} ... уже есть")
            skip += 1
            continue
        try:
            url = commons_thumb_url(commons_name)
            if not url:
                print(f"  {name} ... не найден: {commons_name}")
                fail += 1
                continue
            download(url, dest)
            ok += 1
        except Exception as e:
            print(f"  {name} ... ОШИБКА: {e}")
            fail += 1
        time.sleep(1.5)
    print(f"\nГотово: {ok} скачано, {skip} пропущено, {fail} ошибок.")
    # Sync to web app
    WEB_PANORAMAS.mkdir(parents=True, exist_ok=True)
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    import shutil
    for f in PANORAMAS.glob("*.jpg"):
        shutil.copy2(f, WEB_PANORAMAS / f.name)
    shutil.copy2(LOCATIONS, WEB_DATA / "locations.json")
    print("Веб-версия: cd web && npm run dev")


if __name__ == "__main__":
    main()
