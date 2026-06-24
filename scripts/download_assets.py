#!/usr/bin/env python3
"""Download panorama photos from Wikimedia Commons + sync web data."""

from __future__ import annotations

import json
import subprocess
import time
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PANORAMAS = ROOT / "assets" / "panoramas"
LOCATIONS = ROOT / "data" / "locations.json"
USER_AGENT = "WorldSpot/1.0 (educational geography game; github.com/Sagaidak-Yevgeniy/WorldSpot)"
DOWNLOAD_WIDTH = 2560
REQUEST_DELAY = 4.0


def load_data() -> dict:
    return json.loads(LOCATIONS.read_text(encoding="utf-8"))


def save_data(data: dict) -> None:
    LOCATIONS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def api_request(params: dict) -> dict:
    params = dict(params, format="json")
    url = f"https://commons.wikimedia.org/w/api.php?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 5:
                time.sleep(REQUEST_DELAY * (attempt + 2))
                continue
            raise
    raise RuntimeError("Wikimedia API unavailable")


def commons_exists(filename: str) -> bool:
    title = f"File:{filename}"
    data = api_request({"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url"})
    page = next(iter(data["query"]["pages"].values()))
    return "missing" not in page


def search_commons(query: str) -> str | None:
    data = api_request(
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {query}",
            "gsrlimit": 8,
            "gsrnamespace": 6,
            "prop": "imageinfo",
            "iiprop": "size",
        }
    )
    best, score = None, 0
    for page in data.get("query", {}).get("pages", {}).values():
        title = page.get("title", "").replace("File:", "")
        info = page.get("imageinfo", [{}])[0]
        w, h = info.get("width", 0), info.get("height", 0)
        if w < 1200:
            continue
        ratio = w / max(h, 1)
        s = w + (6000 if ratio >= 2.0 else 3000 if ratio >= 1.6 else 0)
        if s > score:
            score, best = s, title
    return best


def commons_thumb_url(filename: str, width: int = DOWNLOAD_WIDTH) -> str | None:
    title = f"File:{filename}"
    data = api_request(
        {
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": str(width),
        }
    )
    page = next(iter(data["query"]["pages"].values()))
    if "missing" in page:
        return None
    info = page.get("imageinfo", [{}])[0]
    return info.get("thumburl") or info.get("url")


def resolve_commons(data: dict, fname: str, commons: str, loc: dict) -> str:
    if commons and commons_exists(commons):
        return commons
    city = loc["id"].rsplit("_", 1)[0].replace("_", " ")
    query = f"{city} {loc.get('country', '')} panorama"
    print(f"    поиск: {query!r}...", end=" ", flush=True)
    found = search_commons(query)
    time.sleep(REQUEST_DELAY)
    if not found:
        raise ValueError(f"не найдено на Commons: {commons or fname}")
    print(f"→ {found!r}")
    for loc_entry in data["locations"]:
        for pan in loc_entry.get("panoramas", []):
            if pan["file"] == fname:
                pan["commons"] = found
    save_data(data)
    return found


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                body = resp.read()
            if len(body) < 50_000:
                raise ValueError(f"file too small ({len(body)} bytes)")
            dest.write_bytes(body)
            return
        except urllib.error.HTTPError as e:
            if e.code in (429, 404) and attempt < 4:
                time.sleep(REQUEST_DELAY * (attempt + 2))
                continue
            raise


def main() -> None:
    data = load_data()
    seen: set[str] = set()
    catalog: list[tuple[str, str, dict]] = []
    for loc in data["locations"]:
        for pan in loc.get("panoramas", []):
            fname = pan["file"]
            if fname in seen:
                continue
            seen.add(fname)
            catalog.append((fname, pan.get("commons", ""), loc))

    print(f"WorldSpot — загрузка {len(catalog)} панорам ({DOWNLOAD_WIDTH}px)")
    ok, skip, fail = 0, 0, 0
    for name, commons_name, loc in catalog:
        dest = PANORAMAS / name
        if dest.exists() and dest.stat().st_size > 50_000:
            print(f"  {name} ... уже есть")
            skip += 1
            continue
        print(f"  {name} ...", end=" ", flush=True)
        try:
            commons_name = resolve_commons(data, name, commons_name, loc)
            url = commons_thumb_url(commons_name)
            if not url:
                raise ValueError("нет URL на Commons")
            download(url, dest)
            kb = dest.stat().st_size // 1024
            print(f"OK ({kb} KB)")
            ok += 1
        except Exception as e:
            print(f"ОШИБКА: {e}")
            fail += 1
        time.sleep(REQUEST_DELAY)

    print(f"\nГотово: {ok} скачано, {skip} пропущено, {fail} ошибок.")
    subprocess.run(["python3", str(ROOT / "scripts" / "sync_web_data.py")], check=True)
    print("Веб: cd web && npm run dev")


if __name__ == "__main__":
    main()
